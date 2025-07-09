from flask import Blueprint, request, jsonify, session
from database.connection_manager import get_db_manager

user_bp = Blueprint('user', __name__)

@user_bp.route('/api/user', methods=['GET'])
def get_user():
    """Retorna dados do usuário logado"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Usuário não logado'}), 401
        
        db_manager = get_db_manager()
        
        user = db_manager.execute_query(
            'SELECT id, nome, email, posicao, foto_url FROM jogadores WHERE id = ? AND ativo = 1',
            (session['user_id'],),
            fetch_one=True
        )
        
        if not user:
            session.clear()
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'nome': user['nome'],
                'email': user['email'],
                'posicao': user['posicao'],
                'foto_url': user['foto_url']
            }
        })
        
    except Exception as e:
        print(f"Erro ao buscar usuário: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@user_bp.route('/api/user/historico', methods=['GET'])
def get_historico():
    """Retorna histórico de partidas do usuário"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Usuário não logado'}), 401
        
        db_manager = get_db_manager()
        user_id = session['user_id']
        
        # Buscar histórico de partidas
        historico = db_manager.execute_query("""
            SELECT p.data_partida, p.hora_partida, p.local, pel.nome as pelada_nome,
                   pe.gols, pe.assistencias, pe.defesas, pe.gols_sofridos, pe.pontos,
                   pe.mvp, pe.bola_murcha
            FROM partida_estatisticas pe
            JOIN partidas p ON pe.partida_id = p.id
            JOIN peladas pel ON p.pelada_id = pel.id
            WHERE pe.jogador_id = ? AND p.finalizada = 1
            ORDER BY p.data_partida DESC, p.hora_partida DESC
            LIMIT 50
        """, (user_id,), fetch_all=True)
        
        historico_list = []
        for partida in historico:
            historico_list.append({
                'data_partida': partida['data_partida'],
                'hora_partida': partida['hora_partida'],
                'local': partida['local'],
                'pelada_nome': partida['pelada_nome'],
                'gols': partida['gols'],
                'assistencias': partida['assistencias'],
                'defesas': partida['defesas'],
                'gols_sofridos': partida['gols_sofridos'],
                'pontos': partida['pontos'],
                'mvp': bool(partida['mvp']),
                'bola_murcha': bool(partida['bola_murcha'])
            })
        
        return jsonify({
            'success': True,
            'historico': historico_list
        })
        
    except Exception as e:
        print(f"Erro ao buscar histórico: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@user_bp.route('/api/user/estatisticas', methods=['GET'])
def get_estatisticas():
    """Retorna estatísticas gerais do usuário"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Usuário não logado'}), 401
        
        db_manager = get_db_manager()
        user_id = session['user_id']
        
        # Buscar estatísticas gerais
        stats = db_manager.execute_query("""
            SELECT 
                COUNT(DISTINCT pe.partida_id) as total_partidas,
                COALESCE(SUM(pe.gols), 0) as total_gols,
                COALESCE(SUM(pe.assistencias), 0) as total_assistencias,
                COALESCE(SUM(pe.defesas), 0) as total_defesas,
                COALESCE(SUM(pe.gols_sofridos), 0) as total_gols_sofridos,
                COALESCE(SUM(pe.pontos), 0) as total_pontos,
                COALESCE(SUM(CASE WHEN pe.mvp = 1 THEN 1 ELSE 0 END), 0) as total_mvp,
                COALESCE(SUM(CASE WHEN pe.bola_murcha = 1 THEN 1 ELSE 0 END), 0) as total_bola_murcha
            FROM partida_estatisticas pe
            JOIN partidas p ON pe.partida_id = p.id
            WHERE pe.jogador_id = ? AND p.finalizada = 1
        """, (user_id,), fetch_one=True)
        
        # Calcular médias
        media_gols = 0
        media_pontos = 0
        if stats['total_partidas'] > 0:
            media_gols = round(stats['total_gols'] / stats['total_partidas'], 2)
            media_pontos = round(stats['total_pontos'] / stats['total_partidas'], 2)
        
        # Buscar número de peladas
        total_peladas = db_manager.execute_query("""
            SELECT COUNT(DISTINCT pelada_id) as total
            FROM pelada_membros 
            WHERE jogador_id = ? AND ativo = 1
        """, (user_id,), fetch_one=True)
        
        return jsonify({
            'success': True,
            'estatisticas': {
                'total_partidas': stats['total_partidas'],
                'total_peladas': total_peladas['total'],
                'total_gols': stats['total_gols'],
                'total_assistencias': stats['total_assistencias'],
                'total_defesas': stats['total_defesas'],
                'total_gols_sofridos': stats['total_gols_sofridos'],
                'total_pontos': stats['total_pontos'],
                'total_mvp': stats['total_mvp'],
                'total_bola_murcha': stats['total_bola_murcha'],
                'media_gols': media_gols,
                'media_pontos': media_pontos
            }
        })
        
    except Exception as e:
        print(f"Erro ao buscar estatísticas: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@user_bp.route('/api/me', methods=['GET'])
def get_current_user():
    """Retorna dados do usuário logado"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        user_id = session['user_id']
        db_manager = get_db_manager()
        
        user = db_manager.execute_query(
            'SELECT id, nome, email, posicao, foto_url FROM jogadores WHERE id = ? AND ativo = 1',
            (user_id,),
            fetch_one=True
        )
        
        if not user:
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
        
        return jsonify({
            'id': user['id'],
            'nome': user['nome'],
            'email': user['email'],
            'posicao': user['posicao'],
            'foto_url': user['foto_url']
        })
        
    except Exception as e:
        print(f"Erro ao buscar usuário: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500
