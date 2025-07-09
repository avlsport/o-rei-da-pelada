from flask import Blueprint, request, jsonify, session
from src.models.user import db, User
from werkzeug.utils import secure_filename
import os
import uuid

auth_bp = Blueprint('auth', __name__)

UPLOAD_FOLDER = 'src/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        
        # Validação dos dados
        if not data or not all(k in data for k in ('nome', 'email', 'senha', 'posicao')):
            return jsonify({'error': 'Dados incompletos'}), 400
        
        # Verificar se o email já existe
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já cadastrado'}), 400
        
        # Criar novo usuário
        user = User(
            nome=data['nome'],
            email=data['email'],
            posicao=data['posicao']
        )
        user.set_password(data['senha'])
        
        db.session.add(user)
        db.session.commit()
        
        # Fazer login automático
        session['user_id'] = user.id
        
        return jsonify({
            'message': 'Usuário cadastrado com sucesso',
            'user': user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ('email', 'senha')):
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if user and user.check_password(data['senha']):
            session['user_id'] = user.id
            return jsonify({
                'message': 'Login realizado com sucesso',
                'user': user.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Email ou senha inválidos'}), 401
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@auth_bp.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logout realizado com sucesso'}), 200

@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    user = User.query.get(session['user_id'])
    if not user:
        return jsonify({'error': 'Usuário não encontrado'}), 404
    
    return jsonify({'user': user.to_dict()}), 200

@auth_bp.route('/upload-photo', methods=['POST'])
def upload_photo():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    if 'file' not in request.files:
        return jsonify({'error': 'Nenhum arquivo enviado'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'Nenhum arquivo selecionado'}), 400
    
    if file and allowed_file(file.filename):
        # Criar diretório se não existir
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Gerar nome único para o arquivo
        filename = str(uuid.uuid4()) + '.' + file.filename.rsplit('.', 1)[1].lower()
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Atualizar usuário com a URL da foto
        user = User.query.get(session['user_id'])
        user.foto_perfil_url = f'/uploads/{filename}'
        db.session.commit()
        
        return jsonify({
            'message': 'Foto enviada com sucesso',
            'foto_url': user.foto_perfil_url
        }), 200
    
    return jsonify({'error': 'Tipo de arquivo não permitido'}), 400

