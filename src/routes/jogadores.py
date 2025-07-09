from flask import Blueprint, request, jsonify, session
from database.connection_manager import get_db_manager

jogadores_bp = Blueprint('jogadores', __name__)

def verificar_membro_pelada(pelada_id, user_id):
    """Verifica se o usuário é membro da pelada"""
    db_manager = get_db_manager()
    membro = db_manager.execute_query(
        "SELECT id FROM pelada_membros WHERE pelada_id = ? AND jogador_id = ? AND ativo = 1",
        (pelada_id, user_id),
        fetch_one=True
    )
    return membro is not None

@jogadores_bp.route('/api/peladas/<int:pelada_id>/jogadores', methods=['GET'])
def get_jogadores(pelada_id):
    """Retorna jogadores da pelada"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Acesso negado'}), 401
        
        user_id = session['user_id']
        
        if not verificar_membro_pelada(pelada_id, user_id):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        db_manager = get_db_manager()
        
        # Buscar jogadores da pelada
        jogadores = db_manager.execute_query("""
            SELECT j.id, j.nome, j.email, j.posicao, j.foto_url, pm.data_entrada,
                   COUNT(DISTINCT pe.partida_id) as partidas_jogadas,
                   COALESCE(SUM(pe.gols), 0) as total_gols,
                   COALESCE(SUM(pe.pontos), 0) as total_pontos
            FROM pelada_membros pm
            JOIN jogadores j ON pm.jogador_id = j.id
            LEFT JOIN partida_estatisticas pe ON j.id = pe.jogador_id 
                AND pe.partida_id IN (SELECT id FROM partidas WHERE pelada_id = ?)
            WHERE pm.pelada_id = ? AND pm.ativo = 1
            GROUP BY j.id, j.nome, j.email, j.posicao, j.foto_url, pm.data_entrada
            ORDER BY j.nome
        """, (pelada_id, pelada_id), fetch_all=True)
        
        jogadores_list = []
        for jogador in jogadores:
            jogadores_list.append({
                'id': jogador['id'],
                'nome': jogador['nome'],
                'email': jogador['email'],
                'posicao': jogador['posicao'],
                'foto_url': jogador['foto_url'],
                'data_entrada': jogador['data_entrada'],
                'partidas_jogadas': jogador['partidas_jogadas'],
                'total_gols': jogador['total_gols'],
                'total_pontos': jogador['total_pontos']
            })
        
        return jsonify({
            'success': True,
            'jogadores': jogadores_list
        })
        
    except Exception as e:
        print(f"Erro ao buscar jogadores: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@jogadores_bp.route('/api/peladas/<int:pelada_id>/jogadores', methods=['POST'])
def adicionar_jogador(pelada_id):
    """Adiciona jogador à pelada"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Acesso negado'}), 401
        
        user_id = session['user_id']
        
        if not verificar_membro_pelada(pelada_id, user_id):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        data = request.get_json()
        email_jogador = data.get('email')
        
        if not email_jogador:
            return jsonify({'success': False, 'message': 'Email é obrigatório'}), 400
        
        db_manager = get_db_manager()
        
        # Verificar se o jogador existe
        jogador = db_manager.execute_query(
            "SELECT id, nome FROM jogadores WHERE email = ? AND ativo = 1",
            (email_jogador,),
            fetch_one=True
        )
        
        if not jogador:
            return jsonify({'success': False, 'message': 'Jogador não encontrado'}), 404
        
        # Verificar se já é membro
        membro_existente = db_manager.execute_query(
            "SELECT id FROM pelada_membros WHERE pelada_id = ? AND jogador_id = ? AND ativo = 1",
            (pelada_id, jogador['id']),
            fetch_one=True
        )
        
        if membro_existente:
            return jsonify({'success': False, 'message': 'Jogador já é membro desta pelada'}), 400
        
        # Adicionar jogador à pelada
        db_manager.execute_query(
            "INSERT INTO pelada_membros (pelada_id, jogador_id, ativo) VALUES (?, ?, 1)",
            (pelada_id, jogador['id'])
        )
        
        return jsonify({
            'success': True,
            'message': f'{jogador["nome"]} foi adicionado à pelada!'
        })
        
    except Exception as e:
        print(f"Erro ao adicionar jogador: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@jogadores_bp.route('/api/peladas/<int:pelada_id>/jogadores/<int:jogador_id>', methods=['DELETE'])
def remover_jogador(pelada_id, jogador_id):
    """Remove jogador da pelada"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Acesso negado'}), 401
        
        user_id = session['user_id']
        
        if not verificar_membro_pelada(pelada_id, user_id):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        # Não permitir remover a si mesmo
        if user_id == jogador_id:
            return jsonify({'success': False, 'message': 'Você não pode se remover da pelada'}), 400
        
        db_manager = get_db_manager()
        
        # Verificar se é o criador da pelada
        pelada = db_manager.execute_query(
            "SELECT criador_id FROM peladas WHERE id = ?",
            (pelada_id,),
            fetch_one=True
        )
        
        if not pelada or pelada['criador_id'] != user_id:
            return jsonify({'success': False, 'message': 'Apenas o criador pode remover jogadores'}), 403
        
        # Remover jogador
        db_manager.execute_query(
            "UPDATE pelada_membros SET ativo = 0 WHERE pelada_id = ? AND jogador_id = ?",
            (pelada_id, jogador_id)
        )
        
        return jsonify({
            'success': True,
            'message': 'Jogador removido da pelada!'
        })
        
    except Exception as e:
        print(f"Erro ao remover jogador: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@jogadores_bp.route('/api/jogadores/buscar', methods=['GET'])
def buscar_jogadores():
    """Busca jogadores por email ou nome"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Acesso negado'}), 401
        
        termo = request.args.get('q', '').strip()
        
        if len(termo) < 3:
            return jsonify({'success': False, 'message': 'Digite pelo menos 3 caracteres'}), 400
        
        db_manager = get_db_manager()
        
        # Buscar jogadores
        jogadores = db_manager.execute_query("""
            SELECT id, nome, email, posicao, foto_url
            FROM jogadores 
            WHERE (nome LIKE ? OR email LIKE ?) AND ativo = 1
            ORDER BY nome
            LIMIT 10
        """, (f'%{termo}%', f'%{termo}%'), fetch_all=True)
        
        jogadores_list = []
        for jogador in jogadores:
            jogadores_list.append({
                'id': jogador['id'],
                'nome': jogador['nome'],
                'email': jogador['email'],
                'posicao': jogador['posicao'],
                'foto_url': jogador['foto_url']
            })
        
        return jsonify({
            'success': True,
            'jogadores': jogadores_list
        })
        
    except Exception as e:
        print(f"Erro ao buscar jogadores: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500
