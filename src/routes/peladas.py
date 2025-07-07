from flask import Blueprint, request, jsonify, session
from src.models.pelada import Pelada, MembroPelada, SolicitacaoEntrada, ConfirmacaoPresenca, db
from src.models.jogador import Jogador
from src.models.partida import Partida, EstatisticaPartida, Voto
from src.utils.pontuacao import calcular_pontuacao_partida, obter_rankings_pelada
from datetime import datetime

peladas_bp = Blueprint("peladas", __name__)

def require_auth():
    """Verifica se o usuário está autenticado"""
    jogador_id = session.get("jogador_id")
    print(f"DEBUG: Session data: {dict(session)}")  # Debug
    print(f"DEBUG: jogador_id from session: {jogador_id}")  # Debug
    
    if not jogador_id:
        print("DEBUG: No jogador_id in session")  # Debug
        return None
    
    jogador = Jogador.query.get(jogador_id)
    print(f"DEBUG: Found jogador: {jogador}")  # Debug
    return jogador

def is_admin_pelada(jogador_id, pelada_id):
    """Verifica se o jogador é admin da pelada"""
    membro = MembroPelada.query.filter_by(id_jogador=jogador_id, id_pelada=pelada_id).first()
    return membro and membro.papel == "admin"

def is_membro_pelada(jogador_id, pelada_id):
    """Verifica se o jogador é membro da pelada"""
    membro = MembroPelada.query.filter_by(id_jogador=jogador_id, id_pelada=pelada_id).first()
    return membro is not None

@peladas_bp.route("/peladas", methods=["POST"])
def criar_pelada():
    """Endpoint para criar uma nova pelada"""
    try:
        print("DEBUG: Iniciando criação de pelada")  # Debug
        print(f"DEBUG: Request headers: {dict(request.headers)}")  # Debug
        print(f"DEBUG: Request content_type: {request.content_type}")  # Debug
        
        jogador = require_auth()
        if not jogador:
            print("DEBUG: Falha na autenticação")  # Debug
            return jsonify({"error": "Não autenticado"}), 401
        
        print(f"DEBUG: Jogador autenticado: {jogador.nome}")  # Debug
        
        # Verificar se é JSON ou FormData
        if request.content_type and 'application/json' in request.content_type:
            # Dados JSON (sem foto)
            data = request.get_json()
            foto_url = data.get("foto_url")
        else:
            # Dados FormData (com possível foto)
            data = request.form.to_dict()
            foto = request.files.get("foto")
            foto_url = None
            
            # Processar upload da foto se existir
            if foto and foto.filename:
                import os
                filename = f"{os.urandom(16).hex()}_{foto.filename}"
                foto_path = os.path.join(os.getcwd(), "src", "uploads", filename)
                foto.save(foto_path)
                foto_url = f"/uploads/{filename}"
        
        if not data or not data.get("nome"):
            return jsonify({"error": "Nome da pelada é obrigatório"}), 400
        
        # Criar nova pelada
        pelada = Pelada(
            nome=data["nome"],
            descricao=data.get("descricao", ""),
            local=data.get("local", ""),  # Campo local adicionado
            foto_url=foto_url,  # URL da foto da pelada
            id_criador=jogador.id
        )
        
        db.session.add(pelada)
        db.session.flush()  # Para obter o ID da pelada
        
        # Adicionar o criador como admin da pelada
        membro_admin = MembroPelada(
            id_pelada=pelada.id,
            id_jogador=jogador.id,
            papel="admin"
        )
        
        db.session.add(membro_admin)
        db.session.commit()
        
        session.modified = True # Garante que a sessão seja salva após modificação

        return jsonify({
            "message": "Pelada criada com sucesso",
            "pelada": pelada.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@peladas_bp.route("/peladas", methods=["GET"])
def listar_peladas():
    """Endpoint para listar peladas que o jogador faz parte"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        # Buscar peladas onde o jogador é membro
        membros = MembroPelada.query.filter_by(id_jogador=jogador.id).all()
        peladas_ids = [m.id_pelada for m in membros]
        
        peladas = Pelada.query.filter(Pelada.id.in_(peladas_ids), Pelada.ativa == True).all()
        
        # Adicionar informações de papel do jogador
        resultado = []
        for pelada in peladas:
            pelada_dict = pelada.to_dict()
            membro = next((m for m in membros if m.id_pelada == pelada.id), None)
            pelada_dict["papel"] = membro.papel if membro else "membro"
            resultado.append(pelada_dict)
        
        return jsonify({"peladas": resultado}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@peladas_bp.route("/peladas/buscar", methods=["GET"])
def buscar_peladas():
    """Endpoint para buscar peladas por nome"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        nome = request.args.get("nome", "")
        
        if not nome:
            return jsonify({"error": "Nome da pelada é obrigatório"}), 400
        
        # Buscar peladas por nome (que o jogador não faz parte)
        peladas = Pelada.query.filter(
            Pelada.nome.ilike(f"%{nome}%"),
            Pelada.ativa == True
        ).all()
        
        # Filtrar peladas onde o jogador não é membro
        resultado = []
        for pelada in peladas:
            if not is_membro_pelada(jogador.id, pelada.id):
                pelada_dict = pelada.to_dict()
                # Verificar se há solicitação pendente
                solicitacao = SolicitacaoEntrada.query.filter_by(
                    id_pelada=pelada.id,
                    id_jogador=jogador.id,
                    status="pendente"
                ).first()
                pelada_dict["solicitacao_pendente"] = solicitacao is not None
                resultado.append(pelada_dict)
        
        return jsonify({"peladas": resultado}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@peladas_bp.route("/peladas/<int:pelada_id>", methods=["GET"])
def obter_pelada(pelada_id):
    """Endpoint para obter detalhes de uma pelada"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        pelada = Pelada.query.get(pelada_id)
        
        if not pelada:
            return jsonify({"error": "Pelada não encontrada"}), 404
        
        # Verificar se o jogador é membro da pelada
        if not is_membro_pelada(jogador.id, pelada_id):
            return jsonify({"error": "Acesso negado"}), 403
        
        # Obter membros da pelada
        membros = MembroPelada.query.filter_by(id_pelada=pelada_id).all()
        jogadores_ids = [m.id_jogador for m in membros]
        jogadores = {j.id: j.to_dict() for j in Jogador.query.filter(Jogador.id.in_(jogadores_ids)).all()}
        
        # Adicionar papel aos jogadores
        for membro in membros:
            if membro.id_jogador in jogadores:
                jogadores[membro.id_jogador]["papel"] = membro.papel
                jogadores[membro.id_jogador]["data_entrada"] = membro.data_entrada.isoformat() if membro.data_entrada else None
        
        # Obter solicitações pendentes (apenas para admins)
        solicitacoes = []
        if is_admin_pelada(jogador.id, pelada_id):
            solicitacoes_pendentes = SolicitacaoEntrada.query.filter_by(
                id_pelada=pelada_id,
                status="pendente"
            ).all()
            
            solicitantes_ids = [s.id_jogador for s in solicitacoes_pendentes]
            solicitantes = {j.id: j.to_dict() for j in Jogador.query.filter(Jogador.id.in_(solicitantes_ids)).all()}
            
            for solicitacao in solicitacoes_pendentes:
                solicitacao_dict = solicitacao.to_dict()
                solicitacao_dict["jogador"] = solicitantes.get(solicitacao.id_jogador)
                solicitacoes.append(solicitacao_dict)
        
        return jsonify({
            "pelada": pelada.to_dict(),
            "membros": list(jogadores.values()),
            "solicitacoes": solicitacoes,
            "papel_usuario": next((m.papel for m in membros if m.id_jogador == jogador.id), "membro")
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@peladas_bp.route("/peladas/<int:pelada_id>/solicitar_entrada", methods=["POST"])
def solicitar_entrada(pelada_id):
    """Endpoint para solicitar entrada em uma pelada"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        pelada = Pelada.query.get(pelada_id)
        
        if not pelada or not pelada.ativa:
            return jsonify({"error": "Pelada não encontrada"}), 404
        
        # Verificar se já é membro
        if is_membro_pelada(jogador.id, pelada_id):
            return jsonify({"error": "Você já é membro desta pelada"}), 400
        
        # Verificar se já tem solicitação pendente
        solicitacao_existente = SolicitacaoEntrada.query.filter_by(
            id_pelada=pelada_id,
            id_jogador=jogador.id,
            status="pendente"
        ).first()
        
        if solicitacao_existente:
            return jsonify({"error": "Você já tem uma solicitação pendente para esta pelada"}), 400
        
        # Criar nova solicitação
        solicitacao = SolicitacaoEntrada(
            id_pelada=pelada_id,
            id_jogador=jogador.id
        )
        
        db.session.add(solicitacao)
        db.session.commit()
        
        return jsonify({
            "message": "Solicitação enviada com sucesso",
            "solicitacao": solicitacao.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@peladas_bp.route("/peladas/<int:pelada_id>/aprovar_solicitacao", methods=["POST"])
def aprovar_solicitacao(pelada_id):
    """Endpoint para aprovar solicitação de entrada"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        # Verificar se é admin da pelada
        if not is_admin_pelada(jogador.id, pelada_id):
            return jsonify({"error": "Apenas admins podem aprovar solicitações"}), 403
        
        data = request.get_json()
        solicitacao_id = data.get("solicitacao_id")
        
        if not solicitacao_id:
            return jsonify({"error": "ID da solicitação é obrigatório"}), 400
        
        solicitacao = SolicitacaoEntrada.query.filter_by(
            id=solicitacao_id,
            id_pelada=pelada_id,
            status="pendente"
        ).first()
        
        if not solicitacao:
            return jsonify({"error": "Solicitação não encontrada"}), 404
        
        # Aprovar solicitação
        solicitacao.status = "aprovada"
        
        # Adicionar como membro da pelada
        membro = MembroPelada(
            id_pelada=pelada_id,
            id_jogador=solicitacao.id_jogador,
            papel="membro"
        )
        
        db.session.add(membro)
        db.session.commit()
        
        return jsonify({
            "message": "Solicitação aprovada com sucesso"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@peladas_bp.route("/peladas/<int:pelada_id>/rejeitar_solicitacao", methods=["POST"])
def rejeitar_solicitacao(pelada_id):
    """Endpoint para rejeitar solicitação de entrada"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        # Verificar se é admin da pelada
        if not is_admin_pelada(jogador.id, pelada_id):
            return jsonify({"error": "Apenas admins podem rejeitar solicitações"}), 403
        
        data = request.get_json()
        solicitacao_id = data.get("solicitacao_id")
        
        if not solicitacao_id:
            return jsonify({"error": "ID da solicitação é obrigatório"}), 400
        
        solicitacao = SolicitacaoEntrada.query.filter_by(
            id=solicitacao_id,
            id_pelada=pelada_id,
            status="pendente"
        ).first()
        
        if not solicitacao:
            return jsonify({"error": "Solicitação não encontrada"}), 404
        
        # Rejeitar solicitação
        solicitacao.status = "rejeitada"
        db.session.commit()
        
        return jsonify({
            "message": "Solicitação rejeitada"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



