from flask import Blueprint, request, jsonify, session
from database.connection_manager import get_db_manager

busca_peladas_bp = Blueprint('busca_peladas', __name__)

@busca_peladas_bp.route('/api/buscar-peladas', methods=['GET'])
def buscar_peladas():
    """Busca peladas públicas disponíveis"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Usuário não logado'}), 401
        
        db_manager = get_db_manager()
        user_id = session['user_id']
        
        # Buscar peladas que o usuário NÃO participa
        peladas = db_manager.execute_query("""
            SELECT p.id, p.nome, p.descricao, p.local, p.foto_url,
                   j.nome as criador_nome,
                   COUNT(pm.jogador_id) as total_membros
            FROM peladas p
            JOIN jogadores j ON p.criador_id = j.id
            LEFT JOIN pelada_membros pm ON p.id = pm.pelada_id AND pm.ativo = 1
            WHERE p.ativa = 1 
            AND p.id NOT IN (
                SELECT pelada_id FROM pelada_membros 
                WHERE jogador_id = ? AND ativo = 1
            )
            GROUP BY p.id, p.nome, p.descricao, p.local, p.foto_url, j.nome
            ORDER BY p.data_criacao DESC
        """, (user_id,), fetch_all=True)
        
        peladas_list = []
        for pelada in peladas:
            peladas_list.append({
                'id': pelada['id'],
                'nome': pelada['nome'],
                'descricao': pelada['descricao'],
                'local': pelada['local'],
                'foto_url': pelada['foto_url'],
                'criador_nome': pelada['criador_nome'],
                'total_membros': pelada['total_membros']
            })
        
        return jsonify({
            'success': True,
            'peladas': peladas_list
        })
        
    except Exception as e:
        print(f"Erro ao buscar peladas: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@busca_peladas_bp.route('/api/entrar-pelada/<int:pelada_id>', methods=['POST'])
def entrar_pelada(pelada_id):
    """Permite que o usuário entre em uma pelada"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Usuário não logado'}), 401
        
        db_manager = get_db_manager()
        user_id = session['user_id']
        
        # Verificar se a pelada existe e está ativa
        pelada = db_manager.execute_query(
            "SELECT id, nome FROM peladas WHERE id = ? AND ativa = 1",
            (pelada_id,),
            fetch_one=True
        )
        
        if not pelada:
            return jsonify({'success': False, 'message': 'Pelada não encontrada'}), 404
        
        # Verificar se o usuário já é membro
        membro_existente = db_manager.execute_query(
            "SELECT id FROM pelada_membros WHERE pelada_id = ? AND jogador_id = ? AND ativo = 1",
            (pelada_id, user_id),
            fetch_one=True
        )
        
        if membro_existente:
            return jsonify({'success': False, 'message': 'Você já participa desta pelada'}), 400
        
        # Adicionar usuário à pelada
        db_manager.execute_query(
            "INSERT INTO pelada_membros (pelada_id, jogador_id, ativo) VALUES (?, ?, 1)",
            (pelada_id, user_id)
        )
        
        return jsonify({
            'success': True,
            'message': f'Você entrou na pelada "{pelada["nome"]}" com sucesso!'
        })
        
    except Exception as e:
        print(f"Erro ao entrar na pelada: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500
