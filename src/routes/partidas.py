from flask import Blueprint, request, jsonify, session
from src.models.jogador import Jogador, db
from src.models.pelada import Pelada, MembroPelada
from src.models.partida import Partida, ConfirmacaoPresenca, EstatisticaPartida, Voto
from src.utils.rankings import calcular_destaques_partida
from datetime import datetime, time, timedelta
from sqlalchemy import func

partidas_bp = Blueprint('partidas', __name__)

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

# ==================== ROTAS DE PARTIDAS ====================

@partidas_bp.route("/peladas/<int:pelada_id>/partidas", methods=["GET"])
def listar_partidas(pelada_id):
    """Listar partidas da pelada"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        if not is_membro_pelada(jogador.id, pelada_id):
            return jsonify({"error": "Acesso negado"}), 403
        
        partidas = Partida.query.filter_by(
            id_pelada=pelada_id
        ).order_by(Partida.data_partida.desc()).all()
        
        resultado = []
        for partida in partidas:
            partida_dict = partida.to_dict()
            
            # Verificar confirmação do usuário
            confirmacao = ConfirmacaoPresenca.query.filter_by(
                id_partida=partida.id,
                id_jogador=jogador.id
            ).first()
            
            partida_dict["minha_confirmacao"] = {
                "confirmado": confirmacao.confirmado if confirmacao else None,
                "data_confirmacao": confirmacao.data_confirmacao.isoformat() if confirmacao and confirmacao.data_confirmacao else None
            }
            
            resultado.append(partida_dict)
        
        return jsonify({"partidas": resultado}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@partidas_bp.route("/peladas/<int:pelada_id>/partidas", methods=["POST"])
def criar_partida(pelada_id):
    """Criar nova partida (apenas admins)"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        if not is_admin_pelada(jogador.id, pelada_id):
            return jsonify({"error": "Apenas admins podem criar partidas"}), 403
        
        data = request.get_json()
        
        # Validar dados obrigatórios
        data_partida_str = data.get('data_partida')
        horario_inicio_str = data.get('horario_inicio')
        horario_fim_str = data.get('horario_fim')
        
        if not all([data_partida_str, horario_inicio_str, horario_fim_str]):
            return jsonify({"error": "Data, horário de início e fim são obrigatórios"}), 400
        
        # Converter strings para objetos datetime/time
        try:
            data_partida = datetime.strptime(data_partida_str, '%Y-%m-%d').date()
            horario_inicio = datetime.strptime(horario_inicio_str, '%H:%M').time()
            horario_fim = datetime.strptime(horario_fim_str, '%H:%M').time()
        except ValueError:
            return jsonify({"error": "Formato de data/hora inválido"}), 400
        
        # Criar partida
        partida = Partida(
            id_pelada=pelada_id,
            data_partida=datetime.combine(data_partida, time.min),
            horario_inicio=horario_inicio,
            horario_fim=horario_fim,
            local=data.get('local', ''),
            observacoes=data.get('observacoes', ''),
            id_criador=jogador.id
        )
        
        db.session.add(partida)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Partida criada com sucesso",
            "partida": partida.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@partidas_bp.route("/partidas/<int:partida_id>", methods=["GET"])
def obter_partida(partida_id):
    """Obter detalhes de uma partida"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        partida = Partida.query.get(partida_id)
        if not partida:
            return jsonify({"error": "Partida não encontrada"}), 404
        
        if not is_membro_pelada(jogador.id, partida.id_pelada):
            return jsonify({"error": "Acesso negado"}), 403
        
        partida_dict = partida.to_dict()
        
        # Adicionar informações extras
        partida_dict["is_admin"] = is_admin_pelada(jogador.id, partida.id_pelada)
        
        # Lista de confirmações
        confirmacoes = ConfirmacaoPresenca.query.filter_by(
            id_partida=partida_id
        ).all()
        
        partida_dict["confirmacoes"] = [conf.to_dict() for conf in confirmacoes]
        
        # Minha confirmação
        minha_confirmacao = ConfirmacaoPresenca.query.filter_by(
            id_partida=partida_id,
            id_jogador=jogador.id
        ).first()
        
        partida_dict["minha_confirmacao"] = {
            "confirmado": minha_confirmacao.confirmado if minha_confirmacao else None
        }
        
        # Se finalizada, incluir estatísticas e destaques
        if partida.finalizada:
            estatisticas = EstatisticaPartida.query.filter_by(
                id_partida=partida_id
            ).all()
            
            partida_dict["estatisticas"] = [est.to_dict() for est in estatisticas]
            partida_dict["destaques"] = calcular_destaques_partida(partida_id)
        
        # Se votação aberta, verificar se já votou
        if partida.votacao_aberta and not partida.votacao_encerrada:
            meu_voto = Voto.query.filter_by(
                id_partida=partida_id,
                id_jogador_votante=jogador.id
            ).first()
            
            partida_dict["ja_votei"] = meu_voto is not None
            
            # Lista de quem já votou (apenas para admins)
            if is_admin_pelada(jogador.id, partida.id_pelada):
                votos = Voto.query.filter_by(id_partida=partida_id).all()
                partida_dict["votantes"] = [v.votante.nome for v in votos]
        
        return jsonify({"partida": partida_dict}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== CONFIRMAÇÃO DE PRESENÇA ====================

@partidas_bp.route("/partidas/<int:partida_id>/confirmar", methods=["POST"])
def confirmar_presenca(partida_id):
    """Confirmar presença na partida"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        partida = Partida.query.get(partida_id)
        if not partida:
            return jsonify({"error": "Partida não encontrada"}), 404
        
        if not is_membro_pelada(jogador.id, partida.id_pelada):
            return jsonify({"error": "Acesso negado"}), 403
        
        data = request.get_json()
        confirmado = data.get('confirmado', False)
        
        # Verificar se já existe confirmação
        confirmacao = ConfirmacaoPresenca.query.filter_by(
            id_partida=partida_id,
            id_jogador=jogador.id
        ).first()
        
        if confirmacao:
            # Atualizar confirmação existente
            confirmacao.confirmado = confirmado
            confirmacao.data_confirmacao = datetime.utcnow()
        else:
            # Criar nova confirmação
            confirmacao = ConfirmacaoPresenca(
                id_partida=partida_id,
                id_jogador=jogador.id,
                confirmado=confirmado
            )
            db.session.add(confirmacao)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Presença {'confirmada' if confirmado else 'não confirmada'}"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@partidas_bp.route("/partidas/<int:partida_id>/confirmar/<int:jogador_id>", methods=["POST"])
def admin_confirmar_presenca(partida_id, jogador_id):
    """Admin confirmar presença de outro jogador"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        partida = Partida.query.get(partida_id)
        if not partida:
            return jsonify({"error": "Partida não encontrada"}), 404
        
        if not is_admin_pelada(jogador.id, partida.id_pelada):
            return jsonify({"error": "Apenas admins podem confirmar presença de outros"}), 403
        
        data = request.get_json()
        confirmado = data.get('confirmado', False)
        
        # Verificar se o jogador é membro da pelada
        if not is_membro_pelada(jogador_id, partida.id_pelada):
            return jsonify({"error": "Jogador não é membro da pelada"}), 400
        
        # Verificar se já existe confirmação
        confirmacao = ConfirmacaoPresenca.query.filter_by(
            id_partida=partida_id,
            id_jogador=jogador_id
        ).first()
        
        if confirmacao:
            confirmacao.confirmado = confirmado
            confirmacao.data_confirmacao = datetime.utcnow()
        else:
            confirmacao = ConfirmacaoPresenca(
                id_partida=partida_id,
                id_jogador=jogador_id,
                confirmado=confirmado
            )
            db.session.add(confirmacao)
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Presença atualizada com sucesso"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ==================== ESTATÍSTICAS ====================

@partidas_bp.route("/partidas/<int:partida_id>/estatisticas", methods=["POST"])
def adicionar_estatisticas(partida_id):
    """Adicionar estatísticas da partida (apenas admins)"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        partida = Partida.query.get(partida_id)
        if not partida:
            return jsonify({"error": "Partida não encontrada"}), 404
        
        if not is_admin_pelada(jogador.id, partida.id_pelada):
            return jsonify({"error": "Apenas admins podem adicionar estatísticas"}), 403
        
        if partida.finalizada:
            return jsonify({"error": "Partida já finalizada"}), 400
        
        data = request.get_json()
        estatisticas_jogadores = data.get('estatisticas', [])
        
        if not estatisticas_jogadores:
            return jsonify({"error": "Nenhuma estatística fornecida"}), 400
        
        # Processar estatísticas de cada jogador
        for est_data in estatisticas_jogadores:
            id_jogador = est_data.get('id_jogador')
            
            if not id_jogador:
                continue
            
            # Verificar se jogador confirmou presença
            confirmacao = ConfirmacaoPresenca.query.filter_by(
                id_partida=partida_id,
                id_jogador=id_jogador,
                confirmado=True
            ).first()
            
            if not confirmacao:
                continue
            
            # Verificar se já existe estatística
            estatistica = EstatisticaPartida.query.filter_by(
                id_partida=partida_id,
                id_jogador=id_jogador
            ).first()
            
            if not estatistica:
                estatistica = EstatisticaPartida(
                    id_partida=partida_id,
                    id_jogador=id_jogador
                )
                db.session.add(estatistica)
            
            # Atualizar estatísticas
            estatistica.gols = est_data.get('gols', 0)
            estatistica.assistencias = est_data.get('assistencias', 0)
            estatistica.defesas = est_data.get('defesas', 0)
            estatistica.gols_sofridos = est_data.get('gols_sofridos', 0)
            estatistica.desarmes = est_data.get('desarmes', 0)
            
            # Calcular pontos das estatísticas
            estatistica.pontos_estatisticas = estatistica.calcular_pontos_estatisticas()
            estatistica.pontos_total = estatistica.calcular_pontos_total()
        
        # Marcar partida como finalizada e abrir votação
        partida.finalizada = True
        partida.votacao_aberta = True
        partida.status = 'finalizada'
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Estatísticas adicionadas e votação iniciada"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ==================== VOTAÇÃO ====================

@partidas_bp.route("/partidas/<int:partida_id>/votar", methods=["POST"])
def votar(partida_id):
    """Votar MVP e Bola Murcha"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        partida = Partida.query.get(partida_id)
        if not partida:
            return jsonify({"error": "Partida não encontrada"}), 404
        
        if not partida.votacao_aberta or partida.votacao_encerrada:
            return jsonify({"error": "Votação não está aberta"}), 400
        
        # Verificar se confirmou presença
        confirmacao = ConfirmacaoPresenca.query.filter_by(
            id_partida=partida_id,
            id_jogador=jogador.id,
            confirmado=True
        ).first()
        
        if not confirmacao:
            return jsonify({"error": "Apenas quem confirmou presença pode votar"}), 403
        
        data = request.get_json()
        id_mvp = data.get('id_mvp')
        id_bola_murcha = data.get('id_bola_murcha')
        
        if not id_mvp or not id_bola_murcha:
            return jsonify({"error": "MVP e Bola Murcha são obrigatórios"}), 400
        
        if id_mvp == id_bola_murcha:
            return jsonify({"error": "MVP e Bola Murcha devem ser jogadores diferentes"}), 400
        
        # Verificar se já votou
        voto_existente = Voto.query.filter_by(
            id_partida=partida_id,
            id_jogador_votante=jogador.id
        ).first()
        
        if voto_existente:
            return jsonify({"error": "Você já votou nesta partida"}), 400
        
        # Criar voto
        voto = Voto(
            id_partida=partida_id,
            id_jogador_votante=jogador.id,
            id_jogador_mvp=id_mvp,
            id_jogador_bola_murcha=id_bola_murcha
        )
        
        db.session.add(voto)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Voto registrado com sucesso"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@partidas_bp.route("/partidas/<int:partida_id>/encerrar-votacao", methods=["POST"])
def encerrar_votacao(partida_id):
    """Encerrar votação e calcular resultados (apenas admins)"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        partida = Partida.query.get(partida_id)
        if not partida:
            return jsonify({"error": "Partida não encontrada"}), 404
        
        if not is_admin_pelada(jogador.id, partida.id_pelada):
            return jsonify({"error": "Apenas admins podem encerrar votação"}), 403
        
        if not partida.votacao_aberta or partida.votacao_encerrada:
            return jsonify({"error": "Votação não está aberta"}), 400
        
        # Contar votos
        votos_mvp = db.session.query(
            Voto.id_jogador_mvp,
            func.count(Voto.id).label('total_votos')
        ).filter_by(id_partida=partida_id).group_by(Voto.id_jogador_mvp).all()
        
        votos_bola_murcha = db.session.query(
            Voto.id_jogador_bola_murcha,
            func.count(Voto.id).label('total_votos')
        ).filter_by(id_partida=partida_id).group_by(Voto.id_jogador_bola_murcha).all()
        
        # Aplicar pontos de votação
        for voto_mvp in votos_mvp:
            estatistica = EstatisticaPartida.query.filter_by(
                id_partida=partida_id,
                id_jogador=voto_mvp.id_jogador_mvp
            ).first()
            
            if estatistica:
                estatistica.pontos_votacao += voto_mvp.total_votos * 3  # +3 por voto MVP
                estatistica.pontos_total = estatistica.calcular_pontos_total()
        
        for voto_bola_murcha in votos_bola_murcha:
            estatistica = EstatisticaPartida.query.filter_by(
                id_partida=partida_id,
                id_jogador=voto_bola_murcha.id_jogador_bola_murcha
            ).first()
            
            if estatistica:
                estatistica.pontos_votacao -= voto_bola_murcha.total_votos * 3  # -3 por voto Bola Murcha
                estatistica.pontos_total = estatistica.calcular_pontos_total()
        
        # Penalizar quem não votou (-5 pontos)
        confirmados = ConfirmacaoPresenca.query.filter_by(
            id_partida=partida_id,
            confirmado=True
        ).all()
        
        votantes = db.session.query(Voto.id_jogador_votante).filter_by(
            id_partida=partida_id
        ).distinct().all()
        
        ids_votantes = [v.id_jogador_votante for v in votantes]
        
        for confirmacao in confirmados:
            if confirmacao.id_jogador not in ids_votantes:
                # Jogador não votou, aplicar penalidade
                estatistica = EstatisticaPartida.query.filter_by(
                    id_partida=partida_id,
                    id_jogador=confirmacao.id_jogador
                ).first()
                
                if estatistica:
                    estatistica.pontos_votacao -= 5  # -5 por não votar
                    estatistica.pontos_total = estatistica.calcular_pontos_total()
        
        # Encerrar votação
        partida.votacao_encerrada = True
        
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Votação encerrada e pontuações calculadas"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

