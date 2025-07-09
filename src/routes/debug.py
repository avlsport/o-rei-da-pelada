from flask import Blueprint, jsonify, session
import sqlite3
import os

debug_bp = Blueprint('debug', __name__)

def get_db_path():
    """Retorna o caminho do banco de dados"""
    return os.path.join(os.path.dirname(__file__), '..', 'database', 'app.db')

@debug_bp.route('/api/debug/session', methods=['GET'])
def debug_session():
    """Debug da sessão atual"""
    try:
        user_id = session.get('user_id')
        
        return jsonify({
            'success': True,
            'session_data': {
                'user_id': user_id,
                'user_name': session.get('user_name'),
                'user_email': session.get('user_email'),
                'all_session_keys': list(session.keys())
            },
            'session_exists': user_id is not None
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@debug_bp.route('/api/debug/pelada/<int:pelada_id>/membership', methods=['GET'])
def debug_membership(pelada_id):
    """Debug da associação do usuário à pelada"""
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'message': 'Usuário não autenticado'}), 401
        
        db_path = get_db_path()
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        
        try:
            # Verificar se usuário é membro da pelada
            cursor = conn.execute('''
                SELECT pm.*, p.nome as pelada_nome, j.nome as jogador_nome
                FROM pelada_membros pm
                LEFT JOIN peladas p ON pm.pelada_id = p.id
                LEFT JOIN jogadores j ON pm.jogador_id = j.id
                WHERE pm.pelada_id = ? AND pm.jogador_id = ?
            ''', (pelada_id, user_id))
            
            membership = cursor.fetchone()
            
            # Buscar todas as associações do usuário
            cursor = conn.execute('''
                SELECT pm.*, p.nome as pelada_nome
                FROM pelada_membros pm
                LEFT JOIN peladas p ON pm.pelada_id = p.id
                WHERE pm.jogador_id = ?
            ''', (user_id,))
            
            all_memberships = cursor.fetchall()
            
            # Buscar dados da pelada
            cursor = conn.execute('''
                SELECT * FROM peladas WHERE id = ?
            ''', (pelada_id,))
            
            pelada_data = cursor.fetchone()
            
            conn.close()
            
            return jsonify({
                'success': True,
                'user_id': user_id,
                'pelada_id': pelada_id,
                'membership': dict(membership) if membership else None,
                'all_memberships': [dict(m) for m in all_memberships],
                'pelada_data': dict(pelada_data) if pelada_data else None,
                'is_member': membership is not None,
                'is_active_member': membership and membership['ativo'] == 1 if membership else False
            })
            
        except Exception as e:
            conn.close()
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

