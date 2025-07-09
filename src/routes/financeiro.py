from flask import Blueprint, request, jsonify, session
from database.connection_manager import get_db_manager

financeiro_bp = Blueprint('financeiro', __name__)

def verificar_membro_pelada(pelada_id, user_id):
    """Verifica se o usuário é membro da pelada"""
    db_manager = get_db_manager()
    membro = db_manager.execute_query(
        "SELECT id FROM pelada_membros WHERE pelada_id = ? AND jogador_id = ? AND ativo = 1",
        (pelada_id, user_id),
        fetch_one=True
    )
    return membro is not None

@financeiro_bp.route('/api/peladas/<int:pelada_id>/financeiro', methods=['GET'])
def get_financeiro(pelada_id):
    """Retorna dados financeiros da pelada"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Acesso negado'}), 401
        
        user_id = session['user_id']
        
        if not verificar_membro_pelada(pelada_id, user_id):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        db_manager = get_db_manager()
        
        # Buscar transações
        transacoes = db_manager.execute_query("""
            SELECT t.id, t.tipo, t.descricao, t.valor, t.categoria, t.data_transacao,
                   j.nome as criado_por_nome
            FROM transacoes_financeiras t
            JOIN jogadores j ON t.criado_por = j.id
            WHERE t.pelada_id = ?
            ORDER BY t.data_transacao DESC, t.data_criacao DESC
        """, (pelada_id,), fetch_all=True)
        
        # Calcular totais
        total_receitas = 0
        total_despesas = 0
        
        transacoes_list = []
        for transacao in transacoes:
            valor = float(transacao['valor'])
            if transacao['tipo'] == 'receita':
                total_receitas += valor
            else:
                total_despesas += valor
            
            transacoes_list.append({
                'id': transacao['id'],
                'tipo': transacao['tipo'],
                'descricao': transacao['descricao'],
                'valor': valor,
                'categoria': transacao['categoria'],
                'data_transacao': transacao['data_transacao'],
                'criado_por_nome': transacao['criado_por_nome']
            })
        
        saldo = total_receitas - total_despesas
        
        return jsonify({
            'success': True,
            'transacoes': transacoes_list,
            'resumo': {
                'total_receitas': total_receitas,
                'total_despesas': total_despesas,
                'saldo': saldo
            }
        })
        
    except Exception as e:
        print(f"Erro ao buscar financeiro: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@financeiro_bp.route('/api/peladas/<int:pelada_id>/financeiro', methods=['POST'])
def adicionar_transacao(pelada_id):
    """Adiciona nova transação financeira"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Acesso negado'}), 401
        
        user_id = session['user_id']
        
        if not verificar_membro_pelada(pelada_id, user_id):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        data = request.get_json()
        tipo = data.get('tipo')
        descricao = data.get('descricao')
        valor = data.get('valor')
        categoria = data.get('categoria')
        data_transacao = data.get('data_transacao')
        
        # Validações
        if not all([tipo, descricao, valor, data_transacao]):
            return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios'}), 400
        
        if tipo not in ['receita', 'despesa']:
            return jsonify({'success': False, 'message': 'Tipo deve ser receita ou despesa'}), 400
        
        try:
            valor = float(valor)
            if valor <= 0:
                return jsonify({'success': False, 'message': 'Valor deve ser positivo'}), 400
        except ValueError:
            return jsonify({'success': False, 'message': 'Valor inválido'}), 400
        
        db_manager = get_db_manager()
        
        # Inserir transação
        transacao_id = db_manager.execute_query("""
            INSERT INTO transacoes_financeiras 
            (pelada_id, tipo, descricao, valor, categoria, data_transacao, criado_por)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (pelada_id, tipo, descricao, valor, categoria, data_transacao, user_id))
        
        return jsonify({
            'success': True,
            'message': 'Transação adicionada com sucesso!',
            'transacao_id': transacao_id
        })
        
    except Exception as e:
        print(f"Erro ao adicionar transação: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@financeiro_bp.route('/api/peladas/<int:pelada_id>/financeiro/<int:transacao_id>', methods=['DELETE'])
def remover_transacao(pelada_id, transacao_id):
    """Remove uma transação financeira"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Acesso negado'}), 401
        
        user_id = session['user_id']
        
        if not verificar_membro_pelada(pelada_id, user_id):
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        db_manager = get_db_manager()
        
        # Verificar se a transação existe e pertence à pelada
        transacao = db_manager.execute_query(
            "SELECT id, criado_por FROM transacoes_financeiras WHERE id = ? AND pelada_id = ?",
            (transacao_id, pelada_id),
            fetch_one=True
        )
        
        if not transacao:
            return jsonify({'success': False, 'message': 'Transação não encontrada'}), 404
        
        # Verificar se o usuário pode remover (criador da transação)
        if transacao['criado_por'] != user_id:
            return jsonify({'success': False, 'message': 'Você só pode remover suas próprias transações'}), 403
        
        # Remover transação
        db_manager.execute_query(
            "DELETE FROM transacoes_financeiras WHERE id = ?",
            (transacao_id,)
        )
        
        return jsonify({
            'success': True,
            'message': 'Transação removida com sucesso!'
        })
        
    except Exception as e:
        print(f"Erro ao remover transação: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500
