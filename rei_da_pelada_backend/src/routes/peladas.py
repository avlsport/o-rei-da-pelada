from flask import Blueprint, jsonify, request, session
from werkzeug.utils import secure_filename
import os
import uuid
from src.models.user import User, Pelada, PeladaMember, db

peladas_bp = Blueprint('peladas', __name__)

UPLOAD_FOLDER = 'src/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def require_auth():
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])

@peladas_bp.route('/peladas', methods=['GET'])
def get_all_peladas():
    """Buscar todas as peladas (para a aba Buscar Peladas)"""
    search = request.args.get('search', '')
    
    query = Pelada.query
    if search:
        query = query.filter(Pelada.name.contains(search))
    
    peladas = query.all()
    
    result = []
    for pelada in peladas:
        pelada_dict = pelada.to_dict()
        pelada_dict['creator_name'] = pelada.creator.name
        pelada_dict['members_count'] = len([m for m in pelada.members if m.is_approved])
        result.append(pelada_dict)
    
    return jsonify(result), 200

@peladas_bp.route('/peladas/my', methods=['GET'])
def get_my_peladas():
    """Buscar peladas do usuário logado (para a aba Minhas Peladas)"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    # Peladas onde o usuário é membro aprovado
    memberships = PeladaMember.query.filter_by(user_id=user.id, is_approved=True).all()
    
    result = []
    for membership in memberships:
        pelada_dict = membership.pelada.to_dict()
        pelada_dict['is_admin'] = membership.is_admin
        pelada_dict['creator_name'] = membership.pelada.creator.name
        pelada_dict['members_count'] = len([m for m in membership.pelada.members if m.is_approved])
        result.append(pelada_dict)
    
    return jsonify(result), 200

@peladas_bp.route('/peladas', methods=['POST'])
def create_pelada():
    """Criar nova pelada"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        data = request.form
        
        # Validação dos campos obrigatórios
        required_fields = ['name', 'location']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Processar upload da foto
        photo_url = None
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename != '' and allowed_file(file.filename):
                # Criar diretório se não existir
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                
                # Gerar nome único para o arquivo
                filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.save(file_path)
                photo_url = f'/uploads/{filename}'
        
        # Criar pelada
        pelada = Pelada(
            name=data['name'],
            location=data['location'],
            description=data.get('description', ''),
            photo_url=photo_url,
            creator_id=user.id
        )
        
        db.session.add(pelada)
        db.session.flush()  # Para obter o ID da pelada
        
        # Adicionar o criador como membro admin aprovado
        membership = PeladaMember(
            user_id=user.id,
            pelada_id=pelada.id,
            is_admin=True,
            is_approved=True
        )
        
        db.session.add(membership)
        db.session.commit()
        
        return jsonify({
            'message': 'Pelada criada com sucesso',
            'pelada': pelada.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@peladas_bp.route('/peladas/<int:pelada_id>', methods=['GET'])
def get_pelada(pelada_id):
    """Obter detalhes de uma pelada específica"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    pelada = Pelada.query.get_or_404(pelada_id)
    
    # Verificar se o usuário é membro da pelada
    membership = PeladaMember.query.filter_by(user_id=user.id, pelada_id=pelada_id).first()
    if not membership or not membership.is_approved:
        return jsonify({'error': 'Acesso negado'}), 403
    
    pelada_dict = pelada.to_dict()
    pelada_dict['is_admin'] = membership.is_admin
    pelada_dict['creator_name'] = pelada.creator.name
    
    # Adicionar membros
    members = []
    for member in pelada.members:
        if member.is_approved:
            member_dict = member.to_dict()
            member_dict['user_name'] = member.user.name
            member_dict['user_position'] = member.user.position
            member_dict['user_photo_url'] = member.user.photo_url
            members.append(member_dict)
    
    pelada_dict['members'] = members
    
    return jsonify(pelada_dict), 200

@peladas_bp.route('/peladas/<int:pelada_id>/join', methods=['POST'])
def join_pelada():
    """Solicitar entrada em uma pelada"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    pelada_id = request.json.get('pelada_id')
    if not pelada_id:
        return jsonify({'error': 'ID da pelada é obrigatório'}), 400
    
    pelada = Pelada.query.get_or_404(pelada_id)
    
    # Verificar se já é membro
    existing_membership = PeladaMember.query.filter_by(user_id=user.id, pelada_id=pelada_id).first()
    if existing_membership:
        if existing_membership.is_approved:
            return jsonify({'error': 'Você já é membro desta pelada'}), 400
        else:
            return jsonify({'error': 'Sua solicitação já foi enviada'}), 400
    
    # Criar solicitação de entrada
    membership = PeladaMember(
        user_id=user.id,
        pelada_id=pelada_id,
        is_admin=False,
        is_approved=False
    )
    
    db.session.add(membership)
    db.session.commit()
    
    return jsonify({'message': 'Solicitação enviada com sucesso'}), 201

@peladas_bp.route('/peladas/<int:pelada_id>/requests', methods=['GET'])
def get_join_requests(pelada_id):
    """Obter solicitações de entrada (apenas para admins)"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    # Verificar se é admin da pelada
    membership = PeladaMember.query.filter_by(user_id=user.id, pelada_id=pelada_id, is_admin=True).first()
    if not membership:
        return jsonify({'error': 'Acesso negado'}), 403
    
    requests = PeladaMember.query.filter_by(pelada_id=pelada_id, is_approved=False).all()
    
    result = []
    for req in requests:
        req_dict = req.to_dict()
        req_dict['user_name'] = req.user.name
        req_dict['user_position'] = req.user.position
        req_dict['user_photo_url'] = req.user.photo_url
        result.append(req_dict)
    
    return jsonify(result), 200

@peladas_bp.route('/peladas/<int:pelada_id>/requests/<int:request_id>/approve', methods=['POST'])
def approve_request(pelada_id, request_id):
    """Aprovar solicitação de entrada (apenas para admins)"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    # Verificar se é admin da pelada
    admin_membership = PeladaMember.query.filter_by(user_id=user.id, pelada_id=pelada_id, is_admin=True).first()
    if not admin_membership:
        return jsonify({'error': 'Acesso negado'}), 403
    
    # Encontrar a solicitação
    request_membership = PeladaMember.query.get_or_404(request_id)
    if request_membership.pelada_id != pelada_id:
        return jsonify({'error': 'Solicitação não encontrada'}), 404
    
    request_membership.is_approved = True
    db.session.commit()
    
    return jsonify({'message': 'Solicitação aprovada com sucesso'}), 200

@peladas_bp.route('/peladas/<int:pelada_id>/requests/<int:request_id>/reject', methods=['DELETE'])
def reject_request(pelada_id, request_id):
    """Rejeitar solicitação de entrada (apenas para admins)"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    # Verificar se é admin da pelada
    admin_membership = PeladaMember.query.filter_by(user_id=user.id, pelada_id=pelada_id, is_admin=True).first()
    if not admin_membership:
        return jsonify({'error': 'Acesso negado'}), 403
    
    # Encontrar a solicitação
    request_membership = PeladaMember.query.get_or_404(request_id)
    if request_membership.pelada_id != pelada_id:
        return jsonify({'error': 'Solicitação não encontrada'}), 404
    
    db.session.delete(request_membership)
    db.session.commit()
    
    return jsonify({'message': 'Solicitação rejeitada com sucesso'}), 200

