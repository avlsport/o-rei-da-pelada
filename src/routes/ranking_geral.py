from flask import Blueprint, request, jsonify, session
from database.connection_manager import get_db_manager

ranking_geral_bp = Blueprint('ranking_geral', __name__)

@ranking_geral_bp.route('/api/ranking-geral', methods=['GET'])
def get_ranking_geral():
    """Retorna ranking geral de todos os jogadores"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Acesso negado'}), 401
        
        db_manager = get_db_manager()
        
        # Buscar estatísticas gerais dos jogadores
        rankings = db_manager.execute_query("""
            SELECT j.id, j.nome, j.posicao, j.foto_url,
                   COUNT(DISTINCT pe.partida_id) as partidas_jogadas,
                   COALESCE(SUM(pe.gols), 0) as total_gols,
                   COALESCE(SUM(pe.assistencias), 0) as total_assistencias,
                   COALESCE(SUM(pe.defesas), 0) as total_defesas,
                   COALESCE(SUM(pe.gols_sofridos), 0) as total_gols_sofridos,
                   COALESCE(SUM(pe.pontos), 0) as total_pontos,
                   COALESCE(SUM(CASE WHEN pe.mvp = 1 THEN 1 ELSE 0 END), 0) as total_mvp,
                   COALESCE(SUM(CASE WHEN pe.bola_murcha = 1 THEN 1 ELSE 0 END), 0) as total_bola_murcha,
                   COUNT(DISTINCT pm.pelada_id) as peladas_participando
            FROM jogadores j
            LEFT JOIN partida_estatisticas pe ON j.id = pe.jogador_id
            LEFT JOIN pelada_membros pm ON j.id = pm.jogador_id AND pm.ativo = 1
            WHERE j.ativo = 1
            GROUP BY j.id, j.nome, j.posicao, j.foto_url
            HAVING partidas_jogadas > 0 OR peladas_participando > 0
            ORDER BY total_pontos DESC, total_gols DESC, j.nome
        """, fetch_all=True)
        
        rankings_list = []
        posicao = 1
        for ranking in rankings:
            media_pontos = 0
            if ranking['partidas_jogadas'] > 0:
                media_pontos = round(ranking['total_pontos'] / ranking['partidas_jogadas'], 2)
            
            rankings_list.append({
                'posicao': posicao,
                'id': ranking['id'],
                'nome': ranking['nome'],
                'posicao_campo': ranking['posicao'],
                'foto_url': ranking['foto_url'],
                'partidas_jogadas': ranking['partidas_jogadas'],
                'total_gols': ranking['total_gols'],
                'total_assistencias': ranking['total_assistencias'],
                'total_defesas': ranking['total_defesas'],
                'total_gols_sofridos': ranking['total_gols_sofridos'],
                'total_pontos': ranking['total_pontos'],
                'media_pontos': media_pontos,
                'total_mvp': ranking['total_mvp'],
                'total_bola_murcha': ranking['total_bola_murcha'],
                'peladas_participando': ranking['peladas_participando']
            })
            posicao += 1
        
        return jsonify({
            'success': True,
            'rankings': rankings_list
        })
        
    except Exception as e:
        print(f"Erro ao buscar ranking geral: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500
