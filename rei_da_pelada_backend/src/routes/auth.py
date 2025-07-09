from flask import Blueprint, jsonify, request, session
from werkzeug.utils import secure_filename
import os
import uuid
from src.models.user import User, db

auth_bp = Blueprint('auth', __name__)

UPLOAD_FOLDER = 'src/static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth_bp.route('/register', methods=['POST'])
def register():
    try:
        data = request.form
        
        # Validação dos campos obrigatórios
        required_fields = ['name', 'email', 'password', 'confirm_password', 'position']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Verificar se as senhas coincidem
        if data['password'] != data['confirm_password']:
            return jsonify({'error': 'Senhas não coincidem'}), 400
        
        # Verificar se o email já existe
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já cadastrado'}), 400
        
        # Validar posição
        valid_positions = ['Goleiro', 'Zagueiro', 'Meio Campo', 'Atacante']
        if data['position'] not in valid_positions:
            return jsonify({'error': 'Posição inválida'}), 400
        
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
        
        # Criar usuário
        user = User(
            name=data['name'],
            email=data['email'],
            position=data['position'],
            photo_url=photo_url
        )
        user.set_password(data['password'])
        
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
        data = request.json
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email e senha são obrigatórios'}), 400
        
        user = User.query.filter_by(email=data['email']).first()
        
        if not user or not user.check_password(data['password']):
            return jsonify({'error': 'Email ou senha inválidos'}), 401
        
        session['user_id'] = user.id
        
        return jsonify({
            'message': 'Login realizado com sucesso',
            'user': user.to_dict()
        }), 200
        
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
    
    return jsonify(user.to_dict()), 200

@auth_bp.route('/check-auth', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return jsonify({'authenticated': True, 'user': user.to_dict()}), 200
    
    return jsonify({'authenticated': False}), 200

