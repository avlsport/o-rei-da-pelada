from flask import Flask, request, jsonify, session, send_from_directory
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import uuid
from datetime import datetime, timedelta
import time
from urllib.parse import urlparse
import logging

# Configurar logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='../static', static_url_path='')

# Configurações
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

# Configurações de sessão otimizadas para produção
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_DOMAIN'] = None
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# CORS otimizado
CORS(app, 
     origins=['*'],
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
     supports_credentials=True)

# Criar pasta de uploads
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Configuração do banco PostgreSQL
def get_db_connection():
    """Conecta ao banco PostgreSQL com retry"""
    max_retries = 5
    for attempt in range(max_retries):
        try:
            database_url = os.environ.get('DATABASE_URL')
            if not database_url:
                raise Exception("DATABASE_URL não encontrada")
            
            # Corrigir URL para SQLAlchemy 2.0+
            if database_url.startswith('postgres://'):
                database_url = database_url.replace('postgres://', 'postgresql://', 1)
            
            # Parse da URL
            parsed = urlparse(database_url)
            
            conn = psycopg2.connect(
                host=parsed.hostname,
                database=parsed.path[1:],
                user=parsed.username,
                password=parsed.password,
                port=parsed.port,
                sslmode='require',
                connect_timeout=60
            )
            logger.info(f"✅ Conexão com banco estabelecida (tentativa {attempt + 1})")
            return conn
        except Exception as e:
            logger.error(f"❌ Erro na conexão (tentativa {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Backoff exponencial
            else:
                raise

def init_database():
    """Inicializa o banco de dados com todas as tabelas"""
    max_retries = 5
    for attempt in range(max_retries):
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Criar tabelas
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS jogadores (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL,
                    email VARCHAR(100) UNIQUE NOT NULL,
                    senha_hash VARCHAR(255) NOT NULL,
                    posicao VARCHAR(50),
                    foto_url VARCHAR(255),
                    pontos_totais INTEGER DEFAULT 0,
                    gols_totais INTEGER DEFAULT 0,
                    assistencias_totais INTEGER DEFAULT 0,
                    defesas_totais INTEGER DEFAULT 0,
                    desarmes_totais INTEGER DEFAULT 0,
                    mvp_count INTEGER DEFAULT 0,
                    bola_murcha_count INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS peladas (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL,
                    local VARCHAR(200) NOT NULL,
                    descricao TEXT,
                    foto_url VARCHAR(255),
                    criador_id INTEGER REFERENCES jogadores(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS membros_pelada (
                    id SERIAL PRIMARY KEY,
                    pelada_id INTEGER REFERENCES peladas(id) ON DELETE CASCADE,
                    jogador_id INTEGER REFERENCES jogadores(id) ON DELETE CASCADE,
                    is_admin BOOLEAN DEFAULT FALSE,
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(pelada_id, jogador_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS partidas (
                    id SERIAL PRIMARY KEY,
                    pelada_id INTEGER REFERENCES peladas(id) ON DELETE CASCADE,
                    data_partida DATE NOT NULL,
                    horario_inicio TIME,
                    horario_fim TIME,
                    local VARCHAR(200),
                    status VARCHAR(20) DEFAULT 'agendada',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS confirmacoes_partida (
                    id SERIAL PRIMARY KEY,
                    partida_id INTEGER REFERENCES partidas(id) ON DELETE CASCADE,
                    jogador_id INTEGER REFERENCES jogadores(id) ON DELETE CASCADE,
                    confirmado BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(partida_id, jogador_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS estatisticas_partida (
                    id SERIAL PRIMARY KEY,
                    partida_id INTEGER REFERENCES partidas(id) ON DELETE CASCADE,
                    jogador_id INTEGER REFERENCES jogadores(id) ON DELETE CASCADE,
                    gols INTEGER DEFAULT 0,
                    assistencias INTEGER DEFAULT 0,
                    defesas INTEGER DEFAULT 0,
                    desarmes INTEGER DEFAULT 0,
                    mvp BOOLEAN DEFAULT FALSE,
                    bola_murcha BOOLEAN DEFAULT FALSE,
                    pontos_partida INTEGER DEFAULT 0,
                    UNIQUE(partida_id, jogador_id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS financeiro (
                    id SERIAL PRIMARY KEY,
                    pelada_id INTEGER REFERENCES peladas(id) ON DELETE CASCADE,
                    tipo VARCHAR(20) NOT NULL,
                    descricao VARCHAR(200) NOT NULL,
                    valor DECIMAL(10,2) NOT NULL,
                    data_transacao DATE NOT NULL,
                    responsavel_id INTEGER REFERENCES jogadores(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS mensalidades (
                    id SERIAL PRIMARY KEY,
                    pelada_id INTEGER REFERENCES peladas(id) ON DELETE CASCADE,
                    jogador_id INTEGER REFERENCES jogadores(id) ON DELETE CASCADE,
                    mes INTEGER NOT NULL,
                    ano INTEGER NOT NULL,
                    valor DECIMAL(10,2) NOT NULL,
                    pago BOOLEAN DEFAULT FALSE,
                    data_pagamento DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(pelada_id, jogador_id, mes, ano)
                )
            ''')
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info(f"✅ Tabelas criadas com sucesso (tentativa {attempt + 1})")
            return
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabelas (tentativa {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise

# Inicializar banco na inicialização
try:
    init_database()
except Exception as e:
    logger.error(f"❌ Falha crítica na inicialização do banco: {e}")

# Função para upload de arquivos
def upload_file(file, folder='uploads'):
    if file and file.filename:
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        return f"/static/uploads/{unique_filename}"
    return None

# ROTAS DE AUTENTICAÇÃO
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        logger.debug("=== INÍCIO DO CADASTRO ===")
        
        # Verificar se é multipart/form-data ou JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            data = request.form.to_dict()
            foto = request.files.get('foto')
        else:
            data = request.get_json()
            foto = None
        
        logger.debug(f"Dados recebidos: {data}")
        
        nome = data.get('nome')
        email = data.get('email')
        senha = data.get('senha')
        posicao = data.get('posicao')
        
        if not all([nome, email, senha]):
            return jsonify({'success': False, 'message': 'Nome, email e senha são obrigatórios'}), 400
        
        # Upload da foto se fornecida
        foto_url = None
        if foto:
            foto_url = upload_file(foto)
            logger.debug(f"Foto salva em: {foto_url}")
        
        # Hash da senha
        senha_hash = generate_password_hash(senha)
        
        # Inserir no banco
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO jogadores (nome, email, senha_hash, posicao, foto_url)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            ''', (nome, email, senha_hash, posicao, foto_url))
            
            jogador_id = cursor.fetchone()[0]
            conn.commit()
            
            logger.info(f"✅ Jogador cadastrado com ID: {jogador_id}")
            
            return jsonify({
                'success': True,
                'message': 'Cadastro realizado com sucesso!',
                'jogador_id': jogador_id
            })
            
        except psycopg2.IntegrityError:
            conn.rollback()
            return jsonify({'success': False, 'message': 'Email já cadastrado'}), 400
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"❌ Erro no cadastro: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        logger.debug("=== INÍCIO DO LOGIN ===")
        
        data = request.get_json()
        email = data.get('email')
        senha = data.get('senha')
        
        logger.debug(f"Tentativa de login para: {email}")
        
        if not email or not senha:
            return jsonify({'success': False, 'message': 'Email e senha são obrigatórios'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('''
            SELECT id, nome, email, senha_hash, posicao, foto_url, pontos_totais
            FROM jogadores WHERE email = %s
        ''', (email,))
        
        jogador = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not jogador or not check_password_hash(jogador['senha_hash'], senha):
            logger.debug("❌ Credenciais inválidas")
            return jsonify({'success': False, 'message': 'Email ou senha inválidos'}), 401
        
        # Criar sessão
        session.clear()
        session['jogador_id'] = jogador['id']
        session['jogador_nome'] = jogador['nome']
        session.modified = True
        session.permanent = True
        
        logger.info(f"✅ Login bem-sucedido para: {jogador['nome']} (ID: {jogador['id']})")
        
        return jsonify({
            'success': True,
            'message': 'Login realizado com sucesso!',
            'user': {
                'id': jogador['id'],
                'nome': jogador['nome'],
                'email': jogador['email'],
                'posicao': jogador['posicao'],
                'foto_url': jogador['foto_url'],
                'pontos_totais': jogador['pontos_totais']
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Erro no login: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logout realizado com sucesso'})

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('''
            SELECT id, nome, email, posicao, foto_url, pontos_totais
            FROM jogadores WHERE id = %s
        ''', (jogador_id,))
        
        jogador = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not jogador:
            session.clear()
            return jsonify({'success': False, 'message': 'Usuário não encontrado'}), 404
        
        return jsonify({
            'success': True,
            'user': dict(jogador)
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar usuário: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

# ROTAS DE PELADAS
@app.route('/api/peladas', methods=['GET'])
def get_peladas():
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Buscar peladas do jogador
        cursor.execute('''
            SELECT p.*, j.nome as criador_nome, mp.is_admin
            FROM peladas p
            JOIN jogadores j ON p.criador_id = j.id
            JOIN membros_pelada mp ON p.id = mp.pelada_id
            WHERE mp.jogador_id = %s
            ORDER BY p.created_at DESC
        ''', (jogador_id,))
        
        peladas = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'peladas': [dict(pelada) for pelada in peladas]
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar peladas: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@app.route('/api/peladas', methods=['POST'])
def create_pelada():
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        logger.debug("=== CRIANDO PELADA ===")
        
        # Verificar se é multipart/form-data ou JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            data = request.form.to_dict()
            foto = request.files.get('foto')
        else:
            data = request.get_json()
            foto = None
        
        nome = data.get('nome')
        local = data.get('local')
        descricao = data.get('descricao', '')
        
        if not nome or not local:
            return jsonify({'success': False, 'message': 'Nome e local são obrigatórios'}), 400
        
        # Upload da foto se fornecida
        foto_url = None
        if foto:
            foto_url = upload_file(foto)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Criar pelada
            cursor.execute('''
                INSERT INTO peladas (nome, local, descricao, foto_url, criador_id)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            ''', (nome, local, descricao, foto_url, jogador_id))
            
            pelada_id = cursor.fetchone()[0]
            
            # Adicionar criador como admin
            cursor.execute('''
                INSERT INTO membros_pelada (pelada_id, jogador_id, is_admin)
                VALUES (%s, %s, %s)
            ''', (pelada_id, jogador_id, True))
            
            conn.commit()
            
            logger.info(f"✅ Pelada criada com ID: {pelada_id}")
            
            return jsonify({
                'success': True,
                'message': 'Pelada criada com sucesso!',
                'pelada_id': pelada_id
            })
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"❌ Erro ao criar pelada: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

# ROTAS DE RANKINGS
@app.route('/api/rankings/geral', methods=['GET'])
def get_ranking_geral():
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Ranking geral (top 10)
        cursor.execute('''
            SELECT id, nome, pontos_totais, gols_totais, assistencias_totais, 
                   defesas_totais, desarmes_totais, mvp_count, bola_murcha_count,
                   foto_url
            FROM jogadores 
            WHERE pontos_totais > 0
            ORDER BY pontos_totais DESC, gols_totais DESC
            LIMIT 10
        ''')
        
        top_10 = cursor.fetchall()
        
        # Posição do usuário atual
        cursor.execute('''
            SELECT COUNT(*) + 1 as posicao
            FROM jogadores 
            WHERE pontos_totais > (
                SELECT pontos_totais FROM jogadores WHERE id = %s
            )
        ''', (jogador_id,))
        
        posicao_usuario = cursor.fetchone()['posicao']
        
        # Dados do usuário atual
        cursor.execute('''
            SELECT id, nome, pontos_totais, gols_totais, assistencias_totais,
                   defesas_totais, desarmes_totais, mvp_count, bola_murcha_count,
                   foto_url
            FROM jogadores WHERE id = %s
        ''', (jogador_id,))
        
        usuario_atual = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'ranking': {
                'top_10': [dict(jogador) for jogador in top_10],
                'usuario_atual': dict(usuario_atual) if usuario_atual else None,
                'posicao_usuario': posicao_usuario
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar ranking geral: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

# ROTAS DE PARTIDAS
@app.route('/api/peladas/<int:pelada_id>/partidas', methods=['GET'])
def get_partidas_pelada(pelada_id):
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Verificar se é membro da pelada
        cursor.execute('''
            SELECT 1 FROM membros_pelada 
            WHERE pelada_id = %s AND jogador_id = %s
        ''', (pelada_id, jogador_id))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        # Buscar partidas
        cursor.execute('''
            SELECT * FROM partidas 
            WHERE pelada_id = %s 
            ORDER BY data_partida DESC, horario_inicio DESC
        ''', (pelada_id,))
        
        partidas = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'partidas': [dict(partida) for partida in partidas]
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar partidas: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

# ROTAS DE FINANCEIRO
@app.route('/api/peladas/<int:pelada_id>/financeiro', methods=['GET'])
def get_financeiro_pelada(pelada_id):
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Verificar se é membro da pelada
        cursor.execute('''
            SELECT 1 FROM membros_pelada 
            WHERE pelada_id = %s AND jogador_id = %s
        ''', (pelada_id, jogador_id))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        # Buscar transações financeiras
        cursor.execute('''
            SELECT f.*, j.nome as responsavel_nome
            FROM financeiro f
            LEFT JOIN jogadores j ON f.responsavel_id = j.id
            WHERE f.pelada_id = %s
            ORDER BY f.data_transacao DESC, f.created_at DESC
        ''', (pelada_id,))
        
        transacoes = cursor.fetchall()
        
        # Calcular saldo
        cursor.execute('''
            SELECT 
                COALESCE(SUM(CASE WHEN tipo = 'entrada' THEN valor ELSE 0 END), 0) as total_entradas,
                COALESCE(SUM(CASE WHEN tipo = 'saida' THEN valor ELSE 0 END), 0) as total_saidas
            FROM financeiro WHERE pelada_id = %s
        ''', (pelada_id,))
        
        saldo_info = cursor.fetchone()
        saldo_atual = saldo_info['total_entradas'] - saldo_info['total_saidas']
        
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'financeiro': {
                'transacoes': [dict(transacao) for transacao in transacoes],
                'saldo_atual': float(saldo_atual),
                'total_entradas': float(saldo_info['total_entradas']),
                'total_saidas': float(saldo_info['total_saidas'])
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar financeiro: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

# ROTAS DE TESTE E SAÚDE
@app.route('/api/test', methods=['GET'])
def test_api():
    return jsonify({
        'status': 'API funcionando',
        'timestamp': datetime.now().isoformat(),
        'session_id': session.get('jogador_id', 'Não logado'),
        'python_version': os.sys.version
    })

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        # Testar conexão com banco
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT 1')
        cursor.close()
        conn.close()
        
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Servir arquivos estáticos
@app.route('/static/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Rota catch-all para React Router
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_react_app(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)

