from flask import Blueprint, request, jsonify, session
import hashlib
import os
import sqlite3
from werkzeug.utils import secure_filename

auth_bp = Blueprint('auth', __name__)

def get_db_connection():
    """Conecta ao banco SQLite"""
    db_path = os.path.join(os.path.dirname(__file__), '..', 'database', 'app.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def init_database():
    """Inicializa o banco de dados"""
    conn = get_db_connection()
    try:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS jogadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha_hash TEXT NOT NULL,
                posicao TEXT NOT NULL,
                foto_url TEXT,
                pontos_totais INTEGER DEFAULT 0,
                jogos_totais INTEGER DEFAULT 0,
                vitorias INTEGER DEFAULT 0,
                derrotas INTEGER DEFAULT 0,
                gols INTEGER DEFAULT 0,
                assistencias INTEGER DEFAULT 0,
                mvp_count INTEGER DEFAULT 0,
                bola_murcha_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
    except Exception as e:
        print(f"Erro ao criar tabela: {e}")
    finally:
        conn.close()

def allowed_file(filename):
    """Verifica se o arquivo é permitido"""
    if not filename:
        return True  # Foto é opcional
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@auth_bp.route('/api/auth/register', methods=['POST'])
def register():
    try:
        # Inicializar banco se necessário
        init_database()
        
        # Obter dados do formulário
        nome = request.form.get('nome', '').strip()
        email = request.form.get('email', '').strip()
        senha = request.form.get('senha', '').strip()
        posicao = request.form.get('posicao', '').strip()
        
        # Validações básicas
        if not all([nome, email, senha, posicao]):
            return jsonify({'success': False, 'message': 'Todos os campos são obrigatórios'}), 400
        
        # Verificar se email já existe
        conn = get_db_connection()
        try:
            existing_user = conn.execute('SELECT id FROM jogadores WHERE email = ?', (email,)).fetchone()
            if existing_user:
                conn.close()
                return jsonify({'success': False, 'message': 'Email já cadastrado'}), 400
        except Exception as e:
            print(f"Erro ao verificar email existente: {e}")
        
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
        
        # Inserir no banco
        try:
            conn.execute('''
                INSERT INTO jogadores (nome, email, senha_hash, posicao, foto_url)
                VALUES (?, ?, ?, ?, ?)
            ''', (nome, email, senha_hash, posicao, foto_url))
            conn.commit()
            conn.close()
            
            return jsonify({'success': True, 'message': 'Cadastro realizado com sucesso!'})
            
        except Exception as e:
            print(f"Erro ao salvar no banco: {e}")
            conn.close()
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
        conn = get_db_connection()
        try:
            jogador = conn.execute('''
                SELECT id, nome, email, posicao, foto_url 
                FROM jogadores 
                WHERE email = ? AND senha_hash = ?
            ''', (email, senha_hash)).fetchone()
            
            conn.close()
            
            if jogador:
                # Salvar na sessão
                session['user_id'] = jogador['id']
                session['user_name'] = jogador['nome']
                
                return jsonify({
                    'success': True, 
                    'message': 'Login realizado com sucesso!',
                    'user': {
                        'id': jogador['id'],
                        'nome': jogador['nome'],
                        'email': jogador['email'],
                        'posicao': jogador['posicao'],
                        'foto_url': jogador['foto_url']
                    }
                })
            else:
                return jsonify({'success': False, 'message': 'Email ou senha incorretos'}), 401
                
        except Exception as e:
            print(f"Erro ao buscar jogador: {e}")
            conn.close()
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

