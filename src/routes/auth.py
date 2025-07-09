from flask import Blueprint, request, jsonify, session
from src.models.jogador import Jogador, db
from werkzeug.utils import secure_filename
import os
import uuid

auth_bp = Blueprint('auth', __name__)

def upload_file(file, upload_folder):
    """Faz upload de arquivo e retorna a URL"""
    if file and file.filename:
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(upload_folder, unique_filename)
        file.save(filepath)
        return f"/uploads/{unique_filename}"
    return None

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    try:
        # Verificar se é multipart/form-data ou JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            data = request.form.to_dict()
            foto = request.files.get('foto')
        else:
            data = request.get_json()
            foto = None
        
        nome = data.get('nome')
        email = data.get('email')
        senha = data.get('senha')
        posicao = data.get('posicao')
        
        if not all([nome, email, senha]):
            return jsonify({'success': False, 'error': 'Nome, email e senha são obrigatórios'}), 400
        
        # Verificar se email já existe
        if Jogador.query.filter_by(email=email).first():
            return jsonify({'success': False, 'error': 'Email já cadastrado'}), 400
        
        # Criar novo jogador
        novo_jogador = Jogador(
            nome=nome,
            email=email,
            posicao=posicao
        )
        novo_jogador.set_senha(senha)
        
        # Upload da foto se fornecida
        if foto:
            upload_folder = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
            os.makedirs(upload_folder, exist_ok=True)
            foto_url = upload_file(foto, upload_folder)
            novo_jogador.foto_url = foto_url
        
        db.session.add(novo_jogador)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Cadastro realizado com sucesso!',
            'user': novo_jogador.to_dict()
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        senha = data.get('senha')
        
        if not email or not senha:
            return jsonify({'success': False, 'error': 'Email e senha são obrigatórios'}), 400
        
        jogador = Jogador.query.filter_by(email=email).first()
        
        if not jogador or not jogador.check_senha(senha):
            return jsonify({'success': False, 'error': 'Email ou senha inválidos'}), 401
        
        # Criar sessão
        session.clear()
        session['user_id'] = jogador.id
        session['user_nome'] = jogador.nome
        session.permanent = True
        
        return jsonify({
            'success': True,
            'message': 'Login realizado com sucesso!',
            'user': jogador.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500

@auth_bp.route('/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logout realizado com sucesso'})

@auth_bp.route('/auth/me', methods=['GET'])
def get_current_user():
    try:
        user_id = session.get('user_id')
        if not user_id:
            return jsonify({'success': False, 'error': 'Não autenticado'}), 401
        
        jogador = Jogador.query.get(user_id)
        
        if not jogador:
            session.clear()
            return jsonify({'success': False, 'error': 'Usuário não encontrado'}), 404
        
        return jsonify({
            'success': True,
            'user': jogador.to_dict()
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': 'Erro interno do servidor'}), 500

