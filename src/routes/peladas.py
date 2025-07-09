from flask import Blueprint, request, jsonify, session
from src.models.user import db, User, Pelada, MembroPelada, SolicitacaoPelada
from sqlalchemy import or_
import uuid

peladas_bp = Blueprint('peladas', __name__)

@peladas_bp.route('/create', methods=['POST'])
def create_pelada():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ('nome', 'local', 'descricao')):
            return jsonify({'error': 'Dados incompletos'}), 400
        
        # Verificar se já existe uma pelada com esse nome
        if Pelada.query.filter_by(nome=data['nome']).first():
            return jsonify({'error': 'Já existe uma pelada com esse nome'}), 400
        
        # Criar nova pelada
        pelada = Pelada(
            nome=data['nome'],
            local=data['local'],
            descricao=data['descricao'],
            admin_id=session['user_id'],
            foto_pelada_url=data.get('foto_pelada_url')
        )
        
        db.session.add(pelada)
        db.session.flush()  # Para obter o ID da pelada
        
        # Adicionar o criador como membro admin
        membro = MembroPelada(
            usuario_id=session['user_id'],
            pelada_id=pelada.id,
            is_admin=True
        )
        
        db.session.add(membro)
        db.session.commit()
        
        return jsonify({
            'message': 'Pelada criada com sucesso',
            'pelada': pelada.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@peladas_bp.route('/my-peladas', methods=['GET'])
def get_my_peladas():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        # Buscar peladas onde o usuário é membro
        membros = MembroPelada.query.filter_by(usuario_id=session['user_id']).all()
        peladas = []
        
        for membro in membros:
            pelada = Pelada.query.get(membro.pelada_id)
            if pelada:
                pelada_dict = pelada.to_dict()
                pelada_dict['is_admin'] = membro.is_admin
                peladas.append(pelada_dict)
        
        return jsonify({'peladas': peladas}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@peladas_bp.route('/search', methods=['GET'])
def search_peladas():
    try:
        nome = request.args.get('nome', '')
        
        if nome:
            peladas = Pelada.query.filter(Pelada.nome.ilike(f'%{nome}%')).all()
        else:
            peladas = Pelada.query.all()
        
        peladas_list = []
        for pelada in peladas:
            pelada_dict = pelada.to_dict()
            # Adicionar informações do admin
            admin = User.query.get(pelada.admin_id)
            pelada_dict['admin_nome'] = admin.nome if admin else 'Desconhecido'
            # Contar membros
            pelada_dict['total_membros'] = MembroPelada.query.filter_by(pelada_id=pelada.id).count()
            peladas_list.append(pelada_dict)
        
        return jsonify({'peladas': peladas_list}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@peladas_bp.route('/request-join', methods=['POST'])
def request_join_pelada():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        data = request.get_json()
        
        if not data or 'pelada_id' not in data:
            return jsonify({'error': 'ID da pelada é obrigatório'}), 400
        
        pelada_id = data['pelada_id']
        user_id = session['user_id']
        
        # Verificar se a pelada existe
        pelada = Pelada.query.get(pelada_id)
        if not pelada:
            return jsonify({'error': 'Pelada não encontrada'}), 404
        
        # Verificar se já é membro
        if MembroPelada.query.filter_by(usuario_id=user_id, pelada_id=pelada_id).first():
            return jsonify({'error': 'Você já é membro desta pelada'}), 400
        
        # Verificar se já tem solicitação pendente
        if SolicitacaoPelada.query.filter_by(usuario_id=user_id, pelada_id=pelada_id, status='pendente').first():
            return jsonify({'error': 'Você já tem uma solicitação pendente para esta pelada'}), 400
        
        # Criar solicitação
        solicitacao = SolicitacaoPelada(
            usuario_id=user_id,
            pelada_id=pelada_id
        )
        
        db.session.add(solicitacao)
        db.session.commit()
        
        return jsonify({'message': 'Solicitação enviada com sucesso'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@peladas_bp.route('/<pelada_id>/requests', methods=['GET'])
def get_pelada_requests(pelada_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        # Verificar se o usuário é admin da pelada
        membro = MembroPelada.query.filter_by(usuario_id=session['user_id'], pelada_id=pelada_id).first()
        if not membro or not membro.is_admin:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Buscar solicitações pendentes
        solicitacoes = SolicitacaoPelada.query.filter_by(pelada_id=pelada_id, status='pendente').all()
        
        solicitacoes_list = []
        for solicitacao in solicitacoes:
            usuario = User.query.get(solicitacao.usuario_id)
            if usuario:
                solicitacao_dict = solicitacao.to_dict()
                solicitacao_dict['usuario'] = usuario.to_dict()
                solicitacoes_list.append(solicitacao_dict)
        
        return jsonify({'solicitacoes': solicitacoes_list}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@peladas_bp.route('/request/<request_id>/approve', methods=['POST'])
def approve_request(request_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        solicitacao = SolicitacaoPelada.query.get(request_id)
        if not solicitacao:
            return jsonify({'error': 'Solicitação não encontrada'}), 404
        
        # Verificar se o usuário é admin da pelada
        membro = MembroPelada.query.filter_by(usuario_id=session['user_id'], pelada_id=solicitacao.pelada_id).first()
        if not membro or not membro.is_admin:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Aprovar solicitação
        solicitacao.status = 'aprovada'
        
        # Adicionar como membro
        novo_membro = MembroPelada(
            usuario_id=solicitacao.usuario_id,
            pelada_id=solicitacao.pelada_id,
            is_admin=False
        )
        
        db.session.add(novo_membro)
        db.session.commit()
        
        return jsonify({'message': 'Solicitação aprovada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@peladas_bp.route('/request/<request_id>/reject', methods=['POST'])
def reject_request(request_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        solicitacao = SolicitacaoPelada.query.get(request_id)
        if not solicitacao:
            return jsonify({'error': 'Solicitação não encontrada'}), 404
        
        # Verificar se o usuário é admin da pelada
        membro = MembroPelada.query.filter_by(usuario_id=session['user_id'], pelada_id=solicitacao.pelada_id).first()
        if not membro or not membro.is_admin:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Rejeitar solicitação
        solicitacao.status = 'rejeitada'
        db.session.commit()
        
        return jsonify({'message': 'Solicitação rejeitada'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@peladas_bp.route('/<pelada_id>', methods=['GET'])
def get_pelada_details(pelada_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        pelada = Pelada.query.get(pelada_id)
        if not pelada:
            return jsonify({'error': 'Pelada não encontrada'}), 404
        
        # Verificar se o usuário é membro
        membro = MembroPelada.query.filter_by(usuario_id=session['user_id'], pelada_id=pelada_id).first()
        if not membro:
            return jsonify({'error': 'Acesso negado'}), 403
        
        pelada_dict = pelada.to_dict()
        pelada_dict['is_admin'] = membro.is_admin
        
        # Adicionar lista de membros
        membros = MembroPelada.query.filter_by(pelada_id=pelada_id).all()
        membros_list = []
        for m in membros:
            usuario = User.query.get(m.usuario_id)
            if usuario:
                membro_dict = m.to_dict()
                membro_dict['usuario'] = usuario.to_dict()
                membros_list.append(membro_dict)
        
        pelada_dict['membros'] = membros_list
        
        return jsonify({'pelada': pelada_dict}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

