from flask import Blueprint, request, jsonify, session
from src.models.user import db, User, Pelada, MembroPelada, Financeiro, Mensalista
from datetime import datetime, date

financeiro_bp = Blueprint('financeiro', __name__)

@financeiro_bp.route('/pelada/<pelada_id>/movimentos', methods=['GET'])
def get_movimentos_financeiros(pelada_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        # Verificar se o usuário é membro da pelada
        membro = MembroPelada.query.filter_by(usuario_id=session['user_id'], pelada_id=pelada_id).first()
        if not membro:
            return jsonify({'error': 'Acesso negado'}), 403
        
        movimentos = Financeiro.query.filter_by(pelada_id=pelada_id).order_by(
            Financeiro.data_movimento.desc()
        ).all()
        
        movimentos_list = []
        total_entradas = 0
        total_saidas = 0
        
        for movimento in movimentos:
            registrado_por = User.query.get(movimento.registrado_por)
            movimento_dict = movimento.to_dict()
            movimento_dict['registrado_por_nome'] = registrado_por.nome if registrado_por else 'Desconhecido'
            
            movimentos_list.append(movimento_dict)
            
            if movimento.tipo_movimento == 'entrada':
                total_entradas += float(movimento.valor)
            else:
                total_saidas += float(movimento.valor)
        
        saldo = total_entradas - total_saidas
        
        return jsonify({
            'movimentos': movimentos_list,
            'resumo': {
                'total_entradas': total_entradas,
                'total_saidas': total_saidas,
                'saldo': saldo
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@financeiro_bp.route('/pelada/<pelada_id>/movimento', methods=['POST'])
def add_movimento_financeiro(pelada_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        # Verificar se o usuário é admin da pelada
        membro = MembroPelada.query.filter_by(usuario_id=session['user_id'], pelada_id=pelada_id).first()
        if not membro or not membro.is_admin:
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        
        if not data or not all(k in data for k in ('tipo_movimento', 'descricao', 'valor')):
            return jsonify({'error': 'Dados incompletos'}), 400
        
        if data['tipo_movimento'] not in ['entrada', 'saida']:
            return jsonify({'error': 'Tipo de movimento inválido'}), 400
        
        movimento = Financeiro(
            pelada_id=pelada_id,
            tipo_movimento=data['tipo_movimento'],
            descricao=data['descricao'],
            valor=float(data['valor']),
            registrado_por=session['user_id']
        )
        
        db.session.add(movimento)
        db.session.commit()
        
        return jsonify({
            'message': 'Movimento financeiro adicionado com sucesso',
            'movimento': movimento.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@financeiro_bp.route('/movimento/<movimento_id>', methods=['DELETE'])
def delete_movimento_financeiro(movimento_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        movimento = Financeiro.query.get(movimento_id)
        if not movimento:
            return jsonify({'error': 'Movimento não encontrado'}), 404
        
        # Verificar se o usuário é admin da pelada
        membro = MembroPelada.query.filter_by(usuario_id=session['user_id'], pelada_id=movimento.pelada_id).first()
        if not membro or not membro.is_admin:
            return jsonify({'error': 'Acesso negado'}), 403
        
        db.session.delete(movimento)
        db.session.commit()
        
        return jsonify({'message': 'Movimento financeiro removido com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@financeiro_bp.route('/pelada/<pelada_id>/mensalistas', methods=['GET'])
def get_mensalistas(pelada_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        # Verificar se o usuário é membro da pelada
        membro = MembroPelada.query.filter_by(usuario_id=session['user_id'], pelada_id=pelada_id).first()
        if not membro:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Buscar todos os membros da pelada
        membros = MembroPelada.query.filter_by(pelada_id=pelada_id).all()
        
        mensalistas_list = []
        for membro_pelada in membros:
            usuario = User.query.get(membro_pelada.usuario_id)
            if usuario:
                # Buscar informações de mensalista
                mensalista = Mensalista.query.filter_by(
                    pelada_id=pelada_id,
                    usuario_id=usuario.id
                ).first()
                
                if not mensalista:
                    # Criar registro de mensalista se não existir
                    mensalista = Mensalista(
                        pelada_id=pelada_id,
                        usuario_id=usuario.id
                    )
                    db.session.add(mensalista)
                
                mensalista_dict = mensalista.to_dict()
                mensalista_dict['usuario'] = usuario.to_dict()
                mensalistas_list.append(mensalista_dict)
        
        db.session.commit()
        
        return jsonify({'mensalistas': mensalistas_list}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@financeiro_bp.route('/pelada/<pelada_id>/mensalista/<usuario_id>/pagamento', methods=['POST'])
def update_pagamento_mensalista(pelada_id, usuario_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        # Verificar se o usuário é admin da pelada
        membro = MembroPelada.query.filter_by(usuario_id=session['user_id'], pelada_id=pelada_id).first()
        if not membro or not membro.is_admin:
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        
        if not data or 'status_pagamento' not in data:
            return jsonify({'error': 'Status de pagamento é obrigatório'}), 400
        
        if data['status_pagamento'] not in ['pago', 'pendente']:
            return jsonify({'error': 'Status de pagamento inválido'}), 400
        
        mensalista = Mensalista.query.filter_by(pelada_id=pelada_id, usuario_id=usuario_id).first()
        
        if not mensalista:
            # Criar registro se não existir
            mensalista = Mensalista(
                pelada_id=pelada_id,
                usuario_id=usuario_id
            )
            db.session.add(mensalista)
        
        mensalista.status_pagamento = data['status_pagamento']
        
        if data['status_pagamento'] == 'pago':
            mensalista.data_ultimo_pagamento = date.today()
        
        db.session.commit()
        
        return jsonify({
            'message': 'Status de pagamento atualizado com sucesso',
            'mensalista': mensalista.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

