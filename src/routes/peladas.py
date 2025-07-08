from flask import Blueprint, request, jsonify, session
from src.models.jogador import Jogador, db
from src.models.pelada import Pelada, MembroPelada, SolicitacaoEntrada, MovimentacaoFinanceira
from src.models.partida import Partida, ConfirmacaoPresenca, EstatisticaPartida, Voto
from src.utils.rankings import calcular_ranking_pelada, calcular_destaques_partida
from datetime import datetime
import os

peladas_bp = Blueprint('peladas', __name__)

def require_auth():
    """Verifica se o usuário está autenticado"""
    jogador_id = session.get("jogador_id")
    if not jogador_id:
        return None
    return Jogador.query.get(jogador_id)

def is_admin_pelada(jogador_id, pelada_id):
    """Verifica se o jogador é admin da pelada"""
    membro = MembroPelada.query.filter_by(
        id_jogador=jogador_id, 
        id_pelada=pelada_id, 
        papel='admin'
    ).first()
    return membro is not None

def is_membro_pelada(jogador_id, pelada_id):
    """Verifica se o jogador é membro da pelada"""
    membro = MembroPelada.query.filter_by(
        id_jogador=jogador_id, 
        id_pelada=pelada_id,
        ativo=True
    ).first()
    return membro is not None

# ==================== ROTAS DE PELADAS ====================

@peladas_bp.route("/peladas", methods=["POST"])
def criar_pelada():
    """Criar nova pelada"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        # Obter dados do formulário
        nome = request.form.get('nome')
        local = request.form.get('local')
        descricao = request.form.get('descricao', '')
        foto = request.files.get('foto')
        
        if not nome or not local:
            return jsonify({"error": "Nome e local são obrigatórios"}), 400
        
        # Processar foto se existir
        foto_url = None
        if foto and foto.filename:
            try:
                filename = f"{os.urandom(16).hex()}_{foto.filename}"
                foto_path = os.path.join(os.getcwd(), "src", "uploads", filename)
                foto.save(foto_path)
                foto_url = f"/uploads/{filename}"
            except Exception as e:
                print(f"Erro ao salvar foto: {str(e)}")
        
        # Criar pelada
        pelada = Pelada(
            nome=nome,
            local=local,
            descricao=descricao,
            foto_url=foto_url,
            id_criador=jogador.id
        )
        
        db.session.add(pelada)
        db.session.flush()
        
        # Adicionar criador como admin
        membro_admin = MembroPelada(
            id_pelada=pelada.id,
            id_jogador=jogador.id,
            papel="admin"
        )
        
        db.session.add(membro_admin)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Pelada criada com sucesso",
            "pelada": pelada.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@peladas_bp.route("/peladas/minhas", methods=["GET"])
def listar_minhas_peladas():
    """Listar peladas do usuário"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        # Buscar peladas onde o jogador é membro
        membros = MembroPelada.query.filter_by(
            id_jogador=jogador.id, 
            ativo=True
        ).all()
        
        peladas = []
        for membro in membros:
            pelada_dict = membro.pelada.to_dict()
            pelada_dict["papel"] = membro.papel
            peladas.append(pelada_dict)
        
        return jsonify({"peladas": peladas}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@peladas_bp.route("/peladas/buscar", methods=["GET"])
def buscar_peladas():
    """Buscar peladas por nome"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        termo = request.args.get('q', '')
        
        if not termo:
            return jsonify({"peladas": []}), 200
        
        # Buscar peladas que não fazem parte
        peladas_membro = db.session.query(MembroPelada.id_pelada).filter_by(
            id_jogador=jogador.id, 
            ativo=True
        ).subquery()
        
        peladas = Pelada.query.filter(
            Pelada.nome.ilike(f'%{termo}%'),
            Pelada.ativa == True,
            ~Pelada.id.in_(peladas_membro)
        ).limit(10).all()
        
        resultado = [pelada.to_dict() for pelada in peladas]
        
        return jsonify({"peladas": resultado}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@peladas_bp.route("/peladas/<int:pelada_id>/solicitar", methods=["POST"])
def solicitar_entrada(pelada_id):
    """Solicitar entrada em uma pelada"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        data = request.get_json()
        mensagem = data.get('mensagem', '')
        
        # Verificar se pelada existe
        pelada = Pelada.query.get(pelada_id)
        if not pelada:
            return jsonify({"error": "Pelada não encontrada"}), 404
        
        # Verificar se já é membro
        if is_membro_pelada(jogador.id, pelada_id):
            return jsonify({"error": "Você já é membro desta pelada"}), 400
        
        # Verificar se já tem solicitação pendente
        solicitacao_existente = SolicitacaoEntrada.query.filter_by(
            id_pelada=pelada_id,
            id_jogador=jogador.id,
            status='pendente'
        ).first()
        
        if solicitacao_existente:
            return jsonify({"error": "Você já tem uma solicitação pendente"}), 400
        
        # Criar solicitação
        solicitacao = SolicitacaoEntrada(
            id_pelada=pelada_id,
            id_jogador=jogador.id,
            mensagem=mensagem
        )
        
        db.session.add(solicitacao)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Solicitação enviada com sucesso"
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@peladas_bp.route("/peladas/<int:pelada_id>", methods=["GET"])
def obter_pelada(pelada_id):
    """Obter detalhes de uma pelada"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        # Verificar se é membro
        if not is_membro_pelada(jogador.id, pelada_id):
            return jsonify({"error": "Acesso negado"}), 403
        
        pelada = Pelada.query.get(pelada_id)
        if not pelada:
            return jsonify({"error": "Pelada não encontrada"}), 404
        
        # Dados da pelada
        pelada_dict = pelada.to_dict()
        
        # Verificar se é admin
        pelada_dict["is_admin"] = is_admin_pelada(jogador.id, pelada_id)
        
        # Estatísticas gerais
        total_partidas = Partida.query.filter_by(
            id_pelada=pelada_id, 
            finalizada=True
        ).count()
        
        pelada_dict["estatisticas"] = {
            "total_partidas": total_partidas,
            "total_membros": len(pelada.membros)
        }
        
        return jsonify({"pelada": pelada_dict}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== ROTAS DE MEMBROS ====================

@peladas_bp.route("/peladas/<int:pelada_id>/membros", methods=["GET"])
def listar_membros(pelada_id):
    """Listar membros da pelada"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        if not is_membro_pelada(jogador.id, pelada_id):
            return jsonify({"error": "Acesso negado"}), 403
        
        membros = MembroPelada.query.filter_by(
            id_pelada=pelada_id, 
            ativo=True
        ).all()
        
        resultado = [membro.to_dict() for membro in membros]
        
        return jsonify({"membros": resultado}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@peladas_bp.route("/peladas/<int:pelada_id>/solicitacoes", methods=["GET"])
def listar_solicitacoes(pelada_id):
    """Listar solicitações pendentes (apenas admins)"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        if not is_admin_pelada(jogador.id, pelada_id):
            return jsonify({"error": "Apenas admins podem ver solicitações"}), 403
        
        solicitacoes = SolicitacaoEntrada.query.filter_by(
            id_pelada=pelada_id,
            status='pendente'
        ).order_by(SolicitacaoEntrada.data_solicitacao.desc()).all()
        
        resultado = [solicitacao.to_dict() for solicitacao in solicitacoes]
        
        return jsonify({"solicitacoes": resultado}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@peladas_bp.route("/peladas/<int:pelada_id>/solicitacoes/<int:solicitacao_id>/responder", methods=["POST"])
def responder_solicitacao(pelada_id, solicitacao_id):
    """Responder solicitação de entrada (apenas admins)"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        if not is_admin_pelada(jogador.id, pelada_id):
            return jsonify({"error": "Apenas admins podem responder solicitações"}), 403
        
        data = request.get_json()
        aprovado = data.get('aprovado', False)
        
        solicitacao = SolicitacaoEntrada.query.get(solicitacao_id)
        if not solicitacao or solicitacao.id_pelada != pelada_id:
            return jsonify({"error": "Solicitação não encontrada"}), 404
        
        if solicitacao.status != 'pendente':
            return jsonify({"error": "Solicitação já foi respondida"}), 400
        
        # Atualizar solicitação
        solicitacao.status = 'aprovada' if aprovado else 'rejeitada'
        solicitacao.data_resposta = datetime.utcnow()
        solicitacao.id_admin_resposta = jogador.id
        
        # Se aprovado, adicionar como membro
        if aprovado:
            membro = MembroPelada(
                id_pelada=pelada_id,
                id_jogador=solicitacao.id_jogador,
                papel='membro'
            )
            db.session.add(membro)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Solicitação {'aprovada' if aprovado else 'rejeitada'} com sucesso"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ==================== ROTAS DE RANKINGS ====================

@peladas_bp.route("/peladas/<int:pelada_id>/ranking", methods=["GET"])
def obter_ranking_pelada(pelada_id):
    """Obter ranking da pelada"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        if not is_membro_pelada(jogador.id, pelada_id):
            return jsonify({"error": "Acesso negado"}), 403
        
        tipo = request.args.get('tipo', 'geral')  # 'geral', 'ano', 'ultimo_mes'
        ano = request.args.get('ano', type=int)
        
        ranking = calcular_ranking_pelada(pelada_id, tipo, ano)
        
        return jsonify({"ranking": ranking}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

