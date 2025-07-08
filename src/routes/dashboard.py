from flask import Blueprint, jsonify, session
from src.models.jogador import Jogador, db
from src.models.pelada import Pelada
from src.models.partida import Partida
from sqlalchemy import func

dashboard_bp = Blueprint('dashboard', __name__)

def require_auth():
    """Verifica se o usuário está autenticado"""
    jogador_id = session.get("jogador_id")
    if not jogador_id:
        return None
    return Jogador.query.get(jogador_id)

@dashboard_bp.route("/dashboard/stats", methods=["GET"])
def obter_estatisticas_gerais():
    """Obter estatísticas gerais do aplicativo"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        # Total de peladas ativas
        total_peladas = Pelada.query.filter_by(ativa=True).count()
        
        # Total de partidas finalizadas
        total_partidas = Partida.query.filter_by(finalizada=True).count()
        
        # Total de jogadores únicos
        total_jogadores = Jogador.query.count()
        
        return jsonify({
            "totalPeladas": total_peladas,
            "totalPartidas": total_partidas,
            "totalJogadores": total_jogadores
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

