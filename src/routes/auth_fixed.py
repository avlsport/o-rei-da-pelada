from flask import Blueprint, request, jsonify, session
import hashlib
import os
from werkzeug.utils import secure_filename
from models.jogador import Jogador
from  import db

auth_bp = Blueprint('auth', __name__)

def allowed_file(filename):
    """Verifica se o arquivo é permitido"""
    if not filename:
        return True  # Foto é opcional
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    try:
        # Obter dados do formulário
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()
        posicao = request.form.get('posicao', '').strip()
        
        # Validações básicas
        if not all([nome, email, senha, posicao]):
            return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios'}), 400
        
        # Verificar se email já existe
        try:
            existing_user = Jogador.query.filter_by(email=email).first()
            if existing_user:
                return jsonify({'success': False, 'message': 'Email já cadastrado'}), 400
        except Exception as e:
            print(f"Erro ao verificar email existente: {e}")
            # Se der erro na consulta, continua (pode ser primeira execução)
        
        # Processar foto (opcional)
        foto_url = None
        if 'foto' in request.files:
            file = request.files['foto']
            if file and file.filename and allowed_file(file.filename):
                try:
                    filename = secure_filename(file.filename)
                    # Criar nome único
                    import time
                    timestamp = str(int(time.time()))
                    filename = f"{timestamp}_{filename}"
                    
                    # Salvar arquivo
                    upload_folder = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads')
                    os.makedirs(upload_folder, exist_ok=True)
                    file_path = os.path.join(upload_folder, filename)
                    file.save(file_path)
                    foto_url = f'/static/uploads/{filename}'
                except Exception as e:
                    print(f"Erro ao salvar foto: {e}")
                    # Continua sem foto se der erro
        
        # Hash da senha
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        
        # Criar novo jogador
        try:
            novo_jogador = Jogador(
                nome=nome,
                email=email,
                senha_hash=senha_hash,
                posicao=posicao,
                foto_url=foto_url
            )
            
            # Tentar salvar no banco
            db.session.add(novo_jogador)
            db.session.commit()
            
            return jsonify({'success': True, 'message': 'Cadastro realizado com sucesso!'})
            
        except Exception as e:
            print(f"Erro ao salvar no banco: {e}")
            db.session.rollback()
            
            # Se der erro, pode ser que a tabela não existe - vamos criar
            try:
                db.create_all()
                db.session.add(novo_jogador)
                db.session.commit()
                return jsonify({'success': True, 'message': 'Cadastro realizado com sucesso!'})
            except Exception as e2:
                print(f"Erro ao criar tabelas e salvar: {e2}")
                db.session.rollback()
                return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500
        
    except Exception as e:
        print(f"Erro geral no cadastro: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email', '').strip()
        senha = data.get('senha', '').strip()
        
        if not email or not senha:
            return jsonify({'success': False, 'message': 'Email e senha são obrigatórios'}), 400
        
        # Hash da senha
        senha_hash = hashlib.sha256(senha.encode()).hexdigest()
        
        # Buscar jogador
        try:
            jogador = Jogador.query.filter_by(email=email, senha_hash=senha_hash).first()
            
            if jogador:
                # Salvar na sessão
                session['user_id'] = jogador.id
                session['user_name'] = jogador.nome
                
                return jsonify({
                    'success': True, 
                    'message': 'Login realizado com sucesso!',
                    'user': {
                        'id': jogador.id,
                        'nome': jogador.nome,
                        'email': jogador.email,
                        'posicao': jogador.posicao,
                        'foto_url': jogador.foto_url
                    }
                })
            else:
                return jsonify({'success': False, 'message': 'Email ou senha incorretos'}), 401
                
        except Exception as e:
            print(f"Erro ao buscar jogador: {e}")
            return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500
        
    except Exception as e:
        print(f"Erro geral no login: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@auth_bp.route('/api/auth/logout', methods=['POST'])
def logout():
    try:
        session.clear()
        return jsonify({'success': True, 'message': 'Logout realizado com sucesso!'})
    except Exception as e:
        print(f"Erro no logout: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

