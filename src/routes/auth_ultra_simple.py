from flask import Blueprint, request, jsonify, session
import hashlib
import os
from werkzeug.utils import secure_filename
from database.connection_manager import get_db_manager

auth_bp = Blueprint('auth', __name__)

def hash_password(password):
    """Hash da senha usando SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

@auth_bp.route('/api/cadastro', methods=['POST'])
def cadastro():
    try:
        db_manager = get_db_manager()
        
        # Dados do formulário
        nome = request.form.get('nome')
        email = request.form.get('email')
        senha = request.form.get('senha')
        posicao = request.form.get('posicao')
        
        # Validações básicas
        if not all([nome, email, senha, posicao]):
            return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios'}), 400
        
        # Verificar se email já existe
        existing_user = db_manager.execute_query(
            'SELECT id FROM jogadores WHERE email = ?', 
            (email,), 
            fetch_one=True
        )
        
        if existing_user:
            return jsonify({'success': False, 'message': 'Email já cadastrado'}), 400
        
        # Hash da senha
        senha_hash = hash_password(senha)
        
        # Upload da foto (opcional)
        foto_url = None
        if 'foto' in request.files:
            foto = request.files['foto']
            if foto and foto.filename:
                filename = secure_filename(foto.filename)
                # Criar diretório de uploads se não existir
                upload_dir = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                
                # Salvar arquivo
                file_path = os.path.join(upload_dir, filename)
                foto.save(file_path)
                foto_url = f'/static/uploads/{filename}'
        
        # Inserir usuário
        user_id = db_manager.execute_query(
            """INSERT INTO jogadores (nome, email, senha_hash, posicao, foto_url, ativo, data_cadastro) 
               VALUES (?, ?, ?, ?, ?, 1, CURRENT_TIMESTAMP)""",
            (nome, email, senha_hash, posicao, foto_url)
        )
        
        return jsonify({
            'success': True, 
            'message': 'Cadastro realizado com sucesso!',
            'user_id': user_id
        })
        
    except Exception as e:
        print(f"Erro no cadastro: {e}")
        return jsonify({'success': False, 'message': f'Erro interno do servidor: {str(e)}'}), 500

@auth_bp.route('/api/login', methods=['POST'])
def login():
    try:
        db_manager = get_db_manager()
        
        data = request.get_json()
        email = data.get('email')
        senha = data.get('senha')
        
        if not email or not senha:
            return jsonify({'success': False, 'message': 'Email e senha são obrigatórios'}), 400
        
        # Hash da senha
        senha_hash = hash_password(senha)
        
        # Buscar usuário
        user = db_manager.execute_query(
            'SELECT id, nome, email, posicao, foto_url FROM jogadores WHERE email = ? AND senha_hash = ? AND ativo = 1',
            (email, senha_hash),
            fetch_one=True
        )
        
        if not user:
            return jsonify({'success': False, 'message': 'Email ou senha incorretos'}), 401
        
        # Criar sessão
        session['user_id'] = user['id']
        session['user_name'] = user['nome']
        session['user_email'] = user['email']
        session['user_posicao'] = user['posicao']
        session['user_foto'] = user['foto_url']
        
        return jsonify({
            'success': True,
            'message': 'Login realizado com sucesso!',
            'user': {
                'id': user['id'],
                'nome': user['nome'],
                'email': user['email'],
                'posicao': user['posicao'],
                'foto_url': user['foto_url']
            }
        })
        
    except Exception as e:
        print(f"Erro no login: {e}")
        return jsonify({'success': False, 'message': f'Erro interno do servidor: {str(e)}'}), 500

@auth_bp.route('/api/logout', methods=['POST'])
def logout():
    try:
        session.clear()
        return jsonify({'success': True, 'message': 'Logout realizado com sucesso!'})
    except Exception as e:
        print(f"Erro no logout: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/api/user', methods=['GET'])
def get_user():
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Usuário não logado'}), 401
        
        db_manager = get_db_manager()
        
        user = db_manager.execute_query(
            'SELECT id, nome, email, posicao, foto_url FROM jogadores WHERE id = ? AND ativo = 1',
            (session['user_id'],),
            fetch_one=True
        )
        
        if not user:
            session.clear()
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
        
        return jsonify({
            'success': True,
            'user': {
                'id': user['id'],
                'nome': user['nome'],
                'email': user['email'],
                'posicao': user['posicao'],
                'foto_url': user['foto_url']
            }
        })
        
    except Exception as e:
        print(f"Erro ao buscar usuário: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500
