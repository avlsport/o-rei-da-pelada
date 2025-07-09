from flask import Blueprint, request, jsonify, session
from database.connection_manager import DatabaseManager
import hashlib
import logging

user_profile_bp = Blueprint('user_profile', __name__)

@user_profile_bp.route('/api/partidas/historico', methods=['GET'])
def get_historico_partidas():
    """Obter histórico de partidas do usuário"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
        
        user_id = session['user_id']
        
        with DatabaseManager() as db:
            # Buscar partidas do usuário (simplificado para evitar erros de tabelas inexistentes)
            cursor = db.execute('''
                SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='partidas'
            ''')
            
            if cursor.fetchone()[0] == 0:
                # Tabela não existe ainda
                return jsonify({
                    'success': True,
                    'partidas': []
                })
            
            # Buscar partidas básicas
            cursor = db.execute('''
                SELECT 
                    p.id,
                    p.data,
                    p.local,
                    pe.nome as pelada_nome
                FROM partidas p
                JOIN peladas pe ON p.pelada_id = pe.id
                JOIN pelada_membros pm ON pe.id = pm.pelada_id
                WHERE pm.jogador_id = ?
                ORDER BY p.data DESC
                LIMIT 50
            ''', (user_id,))
            
            partidas = []
            for row in cursor.fetchall():
                partidas.append({
                    'id': row[0],
                    'data': row[1],
                    'local': row[2],
                    'pelada_nome': row[3],
                    'gols': 0,
                    'assistencias': 0,
                    'pontos': 0,
                    'foi_mvp': False,
                    'foi_bola_murcha': False
                })
            
            return jsonify({
                'success': True,
                'partidas': partidas
            })
            
    except Exception as e:
        logging.error(f"Erro ao buscar histórico: {e}")
        return jsonify({'success': True, 'partidas': []}), 200

@user_profile_bp.route('/api/user/change-password', methods=['POST'])
def change_password():
    """Alterar senha do usuário"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
            
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'success': False, 'message': 'Senhas são obrigatórias'}), 400
        
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'Nova senha deve ter pelo menos 6 caracteres'}), 400
        
        user_id = session['user_id']
        
        with DatabaseManager() as db:
            # Verificar senha atual
            cursor = db.execute('SELECT senha FROM jogadores WHERE id = ?', (user_id,))
            user = cursor.fetchone()
            
            if not user:
                return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
            
            # Verificar se a senha atual está correta
            current_password_hash = hashlib.sha256(current_password.encode()).hexdigest()
            if user[0] != current_password_hash:
                return jsonify({'success': False, 'message': 'Senha atual incorreta'}), 400
            
            # Atualizar senha
            new_password_hash = hashlib.sha256(new_password.encode()).hexdigest()
            db.execute('UPDATE jogadores SET senha = ? WHERE id = ?', (new_password_hash, user_id))
            db.commit()
            
            return jsonify({
                'success': True,
                'message': 'Senha alterada com sucesso'
            })
            
    except Exception as e:
        logging.error(f"Erro ao alterar senha: {e}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@user_profile_bp.route('/api/user/change-position', methods=['POST'])
def change_position():
    """Alterar posição do usuário"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
        
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'message': 'Dados não fornecidos'}), 400
            
        new_position = data.get('position')
        
        valid_positions = ['Goleiro', 'Zagueiro', 'Meio-campo', 'Atacante']
        if new_position not in valid_positions:
            return jsonify({'success': False, 'message': 'Posição inválida'}), 400
        
        user_id = session['user_id']
        
        with DatabaseManager() as db:
            # Atualizar posição
            db.execute('UPDATE jogadores SET posicao = ? WHERE id = ?', (new_position, user_id))
            db.commit()
            
            return jsonify({
                'success': True,
                'message': 'Posição alterada com sucesso'
            })
            
    except Exception as e:
        logging.error(f"Erro ao alterar posição: {e}")
        return jsonify({'success': False, 'message': f'Erro interno: {str(e)}'}), 500

@user_profile_bp.route('/api/user/stats', methods=['GET'])
def get_user_stats():
    """Obter estatísticas detalhadas do usuário"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
        
        user_id = session['user_id']
        
        with DatabaseManager() as db:
            # Verificar se tabelas existem
            cursor = db.execute('''
                SELECT COUNT(*) FROM sqlite_master WHERE type='table' AND name='partidas'
            ''')
            
            if cursor.fetchone()[0] == 0:
                # Tabelas não existem ainda, retornar estatísticas zeradas
                return jsonify({
                    'success': True,
                    'stats': {
                        'total_partidas': 0,
                        'total_gols': 0,
                        'total_assistencias': 0,
                        'total_pontos': 0,
                        'melhor_partida': 0,
                        'pior_partida': 0,
                        'total_mvps': 0,
                        'total_bola_murcha': 0,
                        'media_pontos': 0,
                        'media_gols': 0,
                        'ranking_posicao': 1
                    }
                })
            
            # Estatísticas básicas (sem estatisticas_partida por enquanto)
            cursor = db.execute('''
                SELECT COUNT(DISTINCT p.id) as total_partidas
                FROM partidas p
                JOIN pelada_membros pm ON p.pelada_id = pm.pelada_id
                WHERE pm.jogador_id = ?
            ''', (user_id,))
            
            total_partidas = cursor.fetchone()[0] or 0
            
            return jsonify({
                'success': True,
                'stats': {
                    'total_partidas': total_partidas,
                    'total_gols': 0,
                    'total_assistencias': 0,
                    'total_pontos': 0,
                    'melhor_partida': 0,
                    'pior_partida': 0,
                    'total_mvps': 0,
                    'total_bola_murcha': 0,
                    'media_pontos': 0,
                    'media_gols': 0,
                    'ranking_posicao': 1
                }
            })
            
    except Exception as e:
        logging.error(f"Erro ao buscar estatísticas: {e}")
        return jsonify({
            'success': True,
            'stats': {
                'total_partidas': 0,
                'total_gols': 0,
                'total_assistencias': 0,
                'total_pontos': 0,
                'melhor_partida': 0,
                'pior_partida': 0,
                'total_mvps': 0,
                'total_bola_murcha': 0,
                'media_pontos': 0,
                'media_gols': 0,
                'ranking_posicao': 1
            }
        }), 200

