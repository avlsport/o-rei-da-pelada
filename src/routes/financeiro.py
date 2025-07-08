"""
Rotas para controle financeiro
"""

from flask import Blueprint, request, jsonify, session
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, date
import logging
from ..database.init_db import get_db_connection

logger = logging.getLogger(__name__)

financeiro_bp = Blueprint('financeiro', __name__)

@financeiro_bp.route('/peladas/<int:pelada_id>/financeiro', methods=['GET'])
def get_financeiro(pelada_id):
    """Buscar dados financeiros da pelada"""
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Verificar se é membro da pelada
        cursor.execute('''
            SELECT 1 FROM membros_pelada 
            WHERE pelada_id = %s AND jogador_id = %s AND status = 'ativo'
        ''', (pelada_id, jogador_id))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        # Buscar transações
        cursor.execute('''
            SELECT tf.*, j.nome as responsavel_nome
            FROM transacoes_financeiras tf
            LEFT JOIN jogadores j ON tf.responsavel_id = j.id
            WHERE tf.pelada_id = %s
            ORDER BY tf.data_transacao DESC, tf.created_at DESC
        ''', (pelada_id,))
        
        transacoes = cursor.fetchall()
        
        # Calcular totais
        cursor.execute('''
            SELECT 
                COALESCE(SUM(CASE WHEN tipo = 'entrada' THEN valor ELSE 0 END), 0) as total_entradas,
                COALESCE(SUM(CASE WHEN tipo = 'saida' THEN valor ELSE 0 END), 0) as total_saidas
            FROM transacoes_financeiras 
            WHERE pelada_id = %s
        ''', (pelada_id,))
        
        totais = cursor.fetchone()
        saldo_atual = totais['total_entradas'] - totais['total_saidas']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'financeiro': {
                'transacoes': [dict(transacao) for transacao in transacoes],
                'total_entradas': float(totais['total_entradas']),
                'total_saidas': float(totais['total_saidas']),
                'saldo_atual': float(saldo_atual)
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar financeiro: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@financeiro_bp.route('/peladas/<int:pelada_id>/financeiro/transacoes', methods=['POST'])
def add_transacao(pelada_id):
    """Adicionar transação financeira (apenas admins)"""
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        data = request.get_json()
        tipo = data.get('tipo')  # 'entrada' ou 'saida'
        descricao = data.get('descricao')
        valor = data.get('valor')
        data_transacao = data.get('data_transacao')
        categoria = data.get('categoria', 'outros')
        
        if not all([tipo, descricao, valor, data_transacao]):
            return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios'}), 400
        
        if tipo not in ['entrada', 'saida']:
            return jsonify({'success': False, 'message': 'Tipo deve ser entrada ou saida'}), 400
        
        try:
            valor = float(valor)
            if valor <= 0:
                return jsonify({'success': False, 'message': 'Valor deve ser positivo'}), 400
        except ValueError:
            return jsonify({'success': False, 'message': 'Valor inválido'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar se é admin da pelada
            cursor.execute('''
                SELECT is_admin FROM membros_pelada 
                WHERE pelada_id = %s AND jogador_id = %s
            ''', (pelada_id, jogador_id))
            
            membro = cursor.fetchone()
            if not membro or not membro[0]:
                return jsonify({'success': False, 'message': 'Apenas admins podem adicionar transações'}), 403
            
            # Adicionar transação
            cursor.execute('''
                INSERT INTO transacoes_financeiras 
                (pelada_id, tipo, descricao, valor, data_transacao, responsavel_id, categoria)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            ''', (pelada_id, tipo, descricao, valor, data_transacao, jogador_id, categoria))
            
            transacao_id = cursor.fetchone()[0]
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': 'Transação adicionada com sucesso!',
                'transacao_id': transacao_id
            })
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"❌ Erro ao adicionar transação: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@financeiro_bp.route('/peladas/<int:pelada_id>/financeiro/transacoes/<int:transacao_id>', methods=['PUT'])
def update_transacao(pelada_id, transacao_id):
    """Atualizar transação financeira (apenas admins)"""
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        data = request.get_json()
        tipo = data.get('tipo')
        descricao = data.get('descricao')
        valor = data.get('valor')
        data_transacao = data.get('data_transacao')
        categoria = data.get('categoria', 'outros')
        
        if not all([tipo, descricao, valor, data_transacao]):
            return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios'}), 400
        
        if tipo not in ['entrada', 'saida']:
            return jsonify({'success': False, 'message': 'Tipo deve ser entrada ou saida'}), 400
        
        try:
            valor = float(valor)
            if valor <= 0:
                return jsonify({'success': False, 'message': 'Valor deve ser positivo'}), 400
        except ValueError:
            return jsonify({'success': False, 'message': 'Valor inválido'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar se é admin da pelada
            cursor.execute('''
                SELECT is_admin FROM membros_pelada 
                WHERE pelada_id = %s AND jogador_id = %s
            ''', (pelada_id, jogador_id))
            
            membro = cursor.fetchone()
            if not membro or not membro[0]:
                return jsonify({'success': False, 'message': 'Apenas admins podem editar transações'}), 403
            
            # Verificar se transação existe
            cursor.execute('''
                SELECT id FROM transacoes_financeiras 
                WHERE id = %s AND pelada_id = %s
            ''', (transacao_id, pelada_id))
            
            if not cursor.fetchone():
                return jsonify({'success': False, 'message': 'Transação não encontrada'}), 404
            
            # Atualizar transação
            cursor.execute('''
                UPDATE transacoes_financeiras 
                SET tipo = %s, descricao = %s, valor = %s, data_transacao = %s, categoria = %s
                WHERE id = %s AND pelada_id = %s
            ''', (tipo, descricao, valor, data_transacao, categoria, transacao_id, pelada_id))
            
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': 'Transação atualizada com sucesso!'
            })
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar transação: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@financeiro_bp.route('/peladas/<int:pelada_id>/financeiro/transacoes/<int:transacao_id>', methods=['DELETE'])
def delete_transacao(pelada_id, transacao_id):
    """Excluir transação financeira (apenas admins)"""
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar se é admin da pelada
            cursor.execute('''
                SELECT is_admin FROM membros_pelada 
                WHERE pelada_id = %s AND jogador_id = %s
            ''', (pelada_id, jogador_id))
            
            membro = cursor.fetchone()
            if not membro or not membro[0]:
                return jsonify({'success': False, 'message': 'Apenas admins podem excluir transações'}), 403
            
            # Verificar se transação existe
            cursor.execute('''
                SELECT id FROM transacoes_financeiras 
                WHERE id = %s AND pelada_id = %s
            ''', (transacao_id, pelada_id))
            
            if not cursor.fetchone():
                return jsonify({'success': False, 'message': 'Transação não encontrada'}), 404
            
            # Excluir transação
            cursor.execute('''
                DELETE FROM transacoes_financeiras 
                WHERE id = %s AND pelada_id = %s
            ''', (transacao_id, pelada_id))
            
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': 'Transação excluída com sucesso!'
            })
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"❌ Erro ao excluir transação: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@financeiro_bp.route('/peladas/<int:pelada_id>/mensalidades', methods=['GET'])
def get_mensalidades(pelada_id):
    """Buscar mensalidades da pelada"""
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Verificar se é membro da pelada
        cursor.execute('''
            SELECT 1 FROM membros_pelada 
            WHERE pelada_id = %s AND jogador_id = %s AND status = 'ativo'
        ''', (pelada_id, jogador_id))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        # Buscar mensalidades do mês atual
        mes_atual = datetime.now().month
        ano_atual = datetime.now().year
        
        cursor.execute('''
            SELECT m.*, j.nome as jogador_nome, j.foto_url
            FROM mensalidades m
            JOIN jogadores j ON m.jogador_id = j.id
            WHERE m.pelada_id = %s AND m.mes = %s AND m.ano = %s
            ORDER BY j.nome
        ''', (pelada_id, mes_atual, ano_atual))
        
        mensalidades = cursor.fetchall()
        
        # Se não há mensalidades para o mês atual, criar para todos os membros
        if not mensalidades:
            cursor.execute('''
                SELECT mp.jogador_id, j.nome
                FROM membros_pelada mp
                JOIN jogadores j ON mp.jogador_id = j.id
                WHERE mp.pelada_id = %s AND mp.status = 'ativo'
            ''', (pelada_id,))
            
            membros = cursor.fetchall()
            
            # Criar mensalidades para o mês atual (valor padrão: 50.00)
            for membro in membros:
                cursor.execute('''
                    INSERT INTO mensalidades (pelada_id, jogador_id, mes, ano, valor)
                    VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT (pelada_id, jogador_id, mes, ano) DO NOTHING
                ''', (pelada_id, membro['jogador_id'], mes_atual, ano_atual, 50.00))
            
            conn.commit()
            
            # Buscar novamente
            cursor.execute('''
                SELECT m.*, j.nome as jogador_nome, j.foto_url
                FROM mensalidades m
                JOIN jogadores j ON m.jogador_id = j.id
                WHERE m.pelada_id = %s AND m.mes = %s AND m.ano = %s
                ORDER BY j.nome
            ''', (pelada_id, mes_atual, ano_atual))
            
            mensalidades = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'mensalidades': [dict(mensalidade) for mensalidade in mensalidades],
            'mes': mes_atual,
            'ano': ano_atual
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar mensalidades: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@financeiro_bp.route('/peladas/<int:pelada_id>/mensalidades/<int:mensalidade_id>/pagar', methods=['PUT'])
def marcar_pagamento(pelada_id, mensalidade_id):
    """Marcar mensalidade como paga/não paga (apenas admins)"""
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        data = request.get_json()
        pago = data.get('pago', False)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar se é admin da pelada
            cursor.execute('''
                SELECT is_admin FROM membros_pelada 
                WHERE pelada_id = %s AND jogador_id = %s
            ''', (pelada_id, jogador_id))
            
            membro = cursor.fetchone()
            if not membro or not membro[0]:
                return jsonify({'success': False, 'message': 'Apenas admins podem marcar pagamentos'}), 403
            
            # Verificar se mensalidade existe
            cursor.execute('''
                SELECT id FROM mensalidades 
                WHERE id = %s AND pelada_id = %s
            ''', (mensalidade_id, pelada_id))
            
            if not cursor.fetchone():
                return jsonify({'success': False, 'message': 'Mensalidade não encontrada'}), 404
            
            # Atualizar pagamento
            data_pagamento = date.today() if pago else None
            
            cursor.execute('''
                UPDATE mensalidades 
                SET pago = %s, data_pagamento = %s
                WHERE id = %s AND pelada_id = %s
            ''', (pago, data_pagamento, mensalidade_id, pelada_id))
            
            conn.commit()
            
            status = 'marcada como paga' if pago else 'marcada como não paga'
            
            return jsonify({
                'success': True,
                'message': f'Mensalidade {status} com sucesso!'
            })
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"❌ Erro ao marcar pagamento: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@financeiro_bp.route('/peladas/<int:pelada_id>/mensalidades/valor', methods=['PUT'])
def atualizar_valor_mensalidade(pelada_id):
    """Atualizar valor da mensalidade (apenas admins)"""
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        data = request.get_json()
        novo_valor = data.get('valor')
        mes = data.get('mes', datetime.now().month)
        ano = data.get('ano', datetime.now().year)
        
        if not novo_valor:
            return jsonify({'success': False, 'message': 'Valor é obrigatório'}), 400
        
        try:
            novo_valor = float(novo_valor)
            if novo_valor <= 0:
                return jsonify({'success': False, 'message': 'Valor deve ser positivo'}), 400
        except ValueError:
            return jsonify({'success': False, 'message': 'Valor inválido'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar se é admin da pelada
            cursor.execute('''
                SELECT is_admin FROM membros_pelada 
                WHERE pelada_id = %s AND jogador_id = %s
            ''', (pelada_id, jogador_id))
            
            membro = cursor.fetchone()
            if not membro or not membro[0]:
                return jsonify({'success': False, 'message': 'Apenas admins podem alterar valores'}), 403
            
            # Atualizar valor para todas as mensalidades do mês/ano
            cursor.execute('''
                UPDATE mensalidades 
                SET valor = %s
                WHERE pelada_id = %s AND mes = %s AND ano = %s
            ''', (novo_valor, pelada_id, mes, ano))
            
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': 'Valor da mensalidade atualizado com sucesso!'
            })
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"❌ Erro ao atualizar valor: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

