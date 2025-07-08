from flask import Blueprint, request, jsonify, session
from src.models.jogador import Jogador, db
from src.models.pelada import MembroPelada
from src.utils.rankings import calcular_ranking_geral_aplicativo, calcular_ranking_pelada

rankings_bp = Blueprint('rankings', __name__)

def require_auth():
    """Verifica se o usuário está autenticado"""
    jogador_id = session.get("jogador_id")
    if not jogador_id:
        return None
    return Jogador.query.get(jogador_id)

def is_membro_pelada(jogador_id, pelada_id):
    """Verifica se o jogador é membro da pelada"""
    membro = MembroPelada.query.filter_by(
        id_jogador=jogador_id, 
        id_pelada=pelada_id,
        ativo=True
    ).first()
    return membro is not None

# ==================== RANKING GERAL DO APLICATIVO ====================

@rankings_bp.route("/ranking/geral", methods=["GET"])
def ranking_geral_aplicativo():
    """Obter ranking geral do aplicativo"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        # Calcular ranking incluindo posição do jogador logado
        ranking = calcular_ranking_geral_aplicativo(
            limit=10, 
            jogador_especifico_id=jogador.id
        )
        
        return jsonify(ranking), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==================== RANKINGS DE PELADAS ====================

@rankings_bp.route("/peladas/<int:pelada_id>/ranking", methods=["GET"])
def ranking_pelada(pelada_id):
    """Obter ranking de uma pelada específica"""
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

@rankings_bp.route("/peladas/<int:pelada_id>/ranking/anos", methods=["GET"])
def anos_disponiveis(pelada_id):
    """Obter anos disponíveis para ranking da pelada"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        if not is_membro_pelada(jogador.id, pelada_id):
            return jsonify({"error": "Acesso negado"}), 403
        
        # Buscar anos com partidas finalizadas
        from src.models.partida import Partida
        from sqlalchemy import extract, distinct
        
        anos = db.session.query(
            distinct(extract('year', Partida.data_partida)).label('ano')
        ).filter_by(
            id_pelada=pelada_id,
            finalizada=True
        ).order_by('ano').all()
        
        anos_lista = [int(ano.ano) for ano in anos]
        
        return jsonify({"anos": anos_lista}), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

