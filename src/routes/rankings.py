from flask import Blueprint, request, jsonify, session
from database.connection_manager import get_db_manager

rankings_bp = Blueprint('rankings', __name__)

def verificar_membro_pelada(pelada_id, user_id):
    """Verifica se o usuário é membro da pelada"""
    db_manager = get_db_manager()
    membro = db_manager.execute_query(
        "SELECT id FROM pelada_membros WHERE pelada_id = ? AND jogador_id = ? AND ativo = 1",
        (pelada_id, user_id),
        fetch_one=True
    )
    return membro is not None

@rankings_bp.route('/api/peladas/<int:pelada_id>/rankings', methods=['GET'])
def get_rankings(pelada_id):
    """Retorna rankings da pelada"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Acesso negado'}), 401
        
        user_id = session['user_id']
        
        if not verificar_membro_pelada(pelada_id, user_id):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        db_manager = get_db_manager()
        
        # Buscar estatísticas dos jogadores
        rankings = db_manager.execute_query("""
            SELECT j.id, j.nome, j.posicao, j.foto_url,
                   COUNT(DISTINCT pe.partida_id) as partidas_jogadas,
                   COALESCE(SUM(pe.gols), 0) as total_gols,
                   COALESCE(SUM(pe.assistencias), 0) as total_assistencias,
                   COALESCE(SUM(pe.defesas), 0) as total_defesas,
                   COALESCE(SUM(pe.gols_sofridos), 0) as total_gols_sofridos,
                   COALESCE(SUM(pe.pontos), 0) as total_pontos,
                   COALESCE(SUM(CASE WHEN pe.mvp = 1 THEN 1 ELSE 0 END), 0) as total_mvp,
                   COALESCE(SUM(CASE WHEN pe.bola_murcha = 1 THEN 1 ELSE 0 END), 0) as total_bola_murcha
            FROM pelada_membros pm
            JOIN jogadores j ON pm.jogador_id = j.id
            LEFT JOIN partida_estatisticas pe ON j.id = pe.jogador_id 
                AND pe.partida_id IN (SELECT id FROM partidas WHERE pelada_id = ?)
            WHERE pm.pelada_id = ? AND pm.ativo = 1
            GROUP BY j.id, j.nome, j.posicao, j.foto_url
            ORDER BY total_pontos DESC, total_gols DESC, j.nome
        """, (pelada_id, pelada_id), fetch_all=True)
        
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
                'total_bola_murcha': ranking['total_bola_murcha']
            })
            posicao += 1
        
        return jsonify({
            'success': True,
            'rankings': rankings_list
        })
        
    except Exception as e:
        print(f"Erro ao buscar rankings: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500
