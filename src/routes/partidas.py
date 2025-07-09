from flask import Blueprint, request, jsonify, session
from database.connection_manager import get_db_manager

partidas_bp = Blueprint('partidas', __name__)

def verificar_membro_pelada(pelada_id, user_id):
    """Verifica se o usuário é membro da pelada"""
    db_manager = get_db_manager()
    membro = db_manager.execute_query(
        "SELECT id FROM pelada_membros WHERE pelada_id = ? AND jogador_id = ? AND ativo = 1",
        (pelada_id, user_id),
        fetch_one=True
    )
    return membro is not None

@partidas_bp.route('/api/peladas/<int:pelada_id>/partidas', methods=['GET'])
def get_partidas(pelada_id):
    """Retorna partidas da pelada"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Acesso negado'}), 401
        
        user_id = session['user_id']
        
        if not verificar_membro_pelada(pelada_id, user_id):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        db_manager = get_db_manager()
        
        # Buscar partidas
        partidas = db_manager.execute_query("""
            SELECT p.id, p.data_partida, p.hora_partida, p.local, p.descricao, 
                   p.status, p.finalizada,
                   COUNT(DISTINCT pc.jogador_id) as confirmados
            FROM partidas p
            LEFT JOIN partida_confirmacoes pc ON p.id = pc.partida_id AND pc.confirmado = 1
            WHERE p.pelada_id = ?
            GROUP BY p.id, p.data_partida, p.hora_partida, p.local, p.descricao, p.status, p.finalizada
            ORDER BY p.data_partida DESC, p.hora_partida DESC
        """, (pelada_id,), fetch_all=True)
        
        partidas_list = []
        for partida in partidas:
            partidas_list.append({
                'id': partida['id'],
                'data_partida': partida['data_partida'],
                'hora_partida': partida['hora_partida'],
                'local': partida['local'],
                'descricao': partida['descricao'],
                'status': partida['status'],
                'finalizada': bool(partida['finalizada']),
                'confirmados': partida['confirmados']
            })
        
        return jsonify({
            'success': True,
            'partidas': partidas_list
        })
        
    except Exception as e:
        print(f"Erro ao buscar partidas: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@partidas_bp.route('/api/peladas/<int:pelada_id>/partidas', methods=['POST'])
def criar_partida(pelada_id):
    """Cria uma nova partida"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Acesso negado'}), 401
        
        user_id = session['user_id']
        
        if not verificar_membro_pelada(pelada_id, user_id):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        data = request.get_json()
        data_partida = data.get('data_partida')
        hora_partida = data.get('hora_partida')
        local = data.get('local')
        descricao = data.get('descricao', '')
        
        # Validações
        if not data_partida or not data_partida.strip():
            return jsonify({'success': False, 'message': 'Data é obrigatória'}), 400
        
        if not hora_partida or not hora_partida.strip():
            return jsonify({'success': False, 'message': 'Hora é obrigatória'}), 400
            
        if not local or not local.strip():
            return jsonify({'success': False, 'message': 'Local é obrigatório'}), 400
        
        db_manager = get_db_manager()
        
        # Criar partida
        partida_id = db_manager.execute_query("""
            INSERT INTO partidas (pelada_id, data_partida, hora_partida, local, descricao, status, finalizada, criador_id)
            VALUES (?, ?, ?, ?, ?, 'agendada', 0, ?)
        """, (pelada_id, data_partida.strip(), hora_partida.strip(), local.strip(), descricao.strip(), user_id))
        
        return jsonify({
            'success': True,
            'message': 'Partida criada com sucesso!',
            'partida_id': partida_id
        })
        
    except Exception as e:
        print(f"Erro ao criar partida: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@partidas_bp.route('/api/peladas/<int:pelada_id>/partidas/<int:partida_id>/confirmar', methods=['POST'])
def confirmar_partida(pelada_id, partida_id):
    """Confirma presença na partida"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Acesso negado'}), 401
        
        user_id = session['user_id']
        
        if not verificar_membro_pelada(pelada_id, user_id):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        db_manager = get_db_manager()
        
        # Verificar se a partida existe
        partida = db_manager.execute_query(
            "SELECT id FROM partidas WHERE id = ? AND pelada_id = ?",
            (partida_id, pelada_id),
            fetch_one=True
        )
        
        if not partida:
            return jsonify({'success': False, 'message': 'Partida não encontrada'}), 404
        
        # Inserir ou atualizar confirmação
        db_manager.execute_query("""
            INSERT OR REPLACE INTO partida_confirmacoes (partida_id, jogador_id, confirmado)
            VALUES (?, ?, 1)
        """, (partida_id, user_id))
        
        return jsonify({
            'success': True,
            'message': 'Presença confirmada!'
        })
        
    except Exception as e:
        print(f"Erro ao confirmar partida: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@partidas_bp.route('/api/peladas/<int:pelada_id>/partidas/<int:partida_id>/desconfirmar', methods=['POST'])
def desconfirmar_partida(pelada_id, partida_id):
    """Remove confirmação da partida"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Acesso negado'}), 401
        
        user_id = session['user_id']
        
        if not verificar_membro_pelada(pelada_id, user_id):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        db_manager = get_db_manager()
        
        # Remover confirmação
        db_manager.execute_query("""
            DELETE FROM partida_confirmacoes 
            WHERE partida_id = ? AND jogador_id = ?
        """, (partida_id, user_id))
        
        return jsonify({
            'success': True,
            'message': 'Confirmação removida!'
        })
        
    except Exception as e:
        print(f"Erro ao desconfirmar partida: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500
