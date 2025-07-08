import os
import sys
import logging

# Configurar logging primeiro
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Adicionar diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify, send_from_directory, request, session
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import uuid
from datetime import datetime, timedelta

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuração básica
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

# Configurações de sessão otimizadas para produção
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SESSION_COOKIE_DOMAIN'] = None
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=7)

# CORS
CORS(app, supports_credentials=True, origins=['*'])

# Criar pasta de uploads
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Função para upload de arquivos
def upload_file(file, folder='uploads'):
    if file and file.filename:
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        return f"/uploads/{unique_filename}"
    return None

# Variável global para controlar status do banco
DATABASE_AVAILABLE = False
db_connection_func = None

# Tentar importar e configurar banco
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
    from urllib.parse import urlparse
    
    def get_db_connection():
        """Conecta ao banco PostgreSQL"""
        database_url = os.environ.get('DATABASE_URL')
        if not database_url:
            raise Exception("DATABASE_URL não encontrada nas variáveis de ambiente")
        
        # Corrigir URL para SQLAlchemy 2.0+ se necessário
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
            connect_timeout=30,
            application_name='o-rei-da-pelada'
        )
        return conn
    
    def init_database():
        """Inicializa o banco de dados com todas as tabelas"""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        logger.info("🔄 Criando tabelas do banco de dados...")
        
        # Tabela de jogadores
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
                partidas_jogadas INTEGER DEFAULT 0,
                media_pontos DECIMAL(5,2) DEFAULT 0.0,
                mvp_count INTEGER DEFAULT 0,
                bola_murcha_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Outras tabelas...
        tables = [
            '''CREATE TABLE IF NOT EXISTS peladas (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                local VARCHAR(200) NOT NULL,
                descricao TEXT,
                foto_url VARCHAR(255),
                criador_id INTEGER REFERENCES jogadores(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''',
            '''CREATE TABLE IF NOT EXISTS membros_pelada (
                id SERIAL PRIMARY KEY,
                pelada_id INTEGER REFERENCES peladas(id) ON DELETE CASCADE,
                jogador_id INTEGER REFERENCES jogadores(id) ON DELETE CASCADE,
                is_admin BOOLEAN DEFAULT FALSE,
                status VARCHAR(20) DEFAULT 'ativo',
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(pelada_id, jogador_id)
            )'''
        ]
        
        for table_sql in tables:
            cursor.execute(table_sql)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("✅ Banco de dados inicializado com sucesso")
    
    # Tentar inicializar banco se DATABASE_URL estiver disponível
    if os.environ.get('DATABASE_URL'):
        try:
            logger.info("🔄 Testando conexão com banco de dados...")
            test_conn = get_db_connection()
            test_conn.close()
            
            logger.info("🔄 Inicializando banco de dados...")
            init_database()
            
            DATABASE_AVAILABLE = True
            db_connection_func = get_db_connection
            logger.info("✅ Banco de dados configurado e disponível")
            
        except Exception as e:
            logger.error(f"❌ Erro ao configurar banco: {e}")
            DATABASE_AVAILABLE = False
    else:
        logger.warning("⚠️ DATABASE_URL não encontrada")
        DATABASE_AVAILABLE = False

except ImportError as e:
    logger.error(f"❌ Erro ao importar psycopg2: {e}")
    DATABASE_AVAILABLE = False
except Exception as e:
    logger.error(f"❌ Erro geral na configuração do banco: {e}")
    DATABASE_AVAILABLE = False

# Importar blueprints com tratamento de erro
try:
    if DATABASE_AVAILABLE:
        from .routes.peladas import peladas_bp
        from .routes.partidas import partidas_bp
        from .routes.rankings import rankings_bp
        from .routes.financeiro import financeiro_bp
        
        # Registrar blueprints
        app.register_blueprint(peladas_bp, url_prefix='/api')
        app.register_blueprint(partidas_bp, url_prefix='/api')
        app.register_blueprint(rankings_bp, url_prefix='/api')
        app.register_blueprint(financeiro_bp, url_prefix='/api')
        
        logger.info("✅ Blueprints registrados com sucesso")
    else:
        logger.warning("⚠️ Blueprints não registrados - banco não disponível")
        
except Exception as e:
    logger.error(f"❌ Erro ao importar blueprints: {e}")

# ROTAS DE AUTENTICAÇÃO
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        if not DATABASE_AVAILABLE:
            return jsonify({
                'success': False, 
                'message': 'Serviço temporariamente indisponível. O banco de dados está sendo configurado. Tente novamente em alguns minutos.'
            }), 503
        
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
        conn = db_connection_func()
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
        if not DATABASE_AVAILABLE:
            return jsonify({
                'success': False, 
                'message': 'Serviço temporariamente indisponível. O banco de dados está sendo configurado. Tente novamente em alguns minutos.'
            }), 503
        
        logger.debug("=== INÍCIO DO LOGIN ===")
        
        data = request.get_json()
        email = data.get('email')
        senha = data.get('senha')
        
        logger.debug(f"Tentativa de login para: {email}")
        
        if not email or not senha:
            return jsonify({'success': False, 'message': 'Email e senha são obrigatórios'}), 400
        
        conn = db_connection_func()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('''
            SELECT id, nome, email, senha_hash, posicao, foto_url, pontos_totais, media_pontos
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
                'pontos_totais': jogador['pontos_totais'],
                'media_pontos': float(jogador['media_pontos']) if jogador['media_pontos'] else 0.0
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
        if not DATABASE_AVAILABLE:
            return jsonify({'success': False, 'message': 'Serviço temporariamente indisponível'}), 503
        
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        conn = db_connection_func()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute('''
            SELECT id, nome, email, posicao, foto_url, pontos_totais, media_pontos
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
            'user': {
                'id': jogador['id'],
                'nome': jogador['nome'],
                'email': jogador['email'],
                'posicao': jogador['posicao'],
                'foto_url': jogador['foto_url'],
                'pontos_totais': jogador['pontos_totais'],
                'media_pontos': float(jogador['media_pontos']) if jogador['media_pontos'] else 0.0
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar usuário: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

# Rota de teste
@app.route('/api/test', methods=['GET'])
def test_api():
    return {
        "message": "API funcionando", 
        "status": "ok", 
        "python_version": sys.version,
        "environment": os.environ.get('RAILWAY_ENVIRONMENT', 'local'),
        "session_id": session.get('jogador_id', 'Não logado'),
        "database_available": DATABASE_AVAILABLE,
        "database_url_exists": bool(os.environ.get('DATABASE_URL'))
    }, 200

# Rota de saúde
@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        database_status = 'not_configured'
        if DATABASE_AVAILABLE:
            try:
                conn = db_connection_func()
                cursor = conn.cursor()
                cursor.execute('SELECT 1')
                cursor.close()
                conn.close()
                database_status = 'connected'
            except Exception as db_error:
                logger.error(f"Erro na conexão do banco: {db_error}")
                database_status = 'disconnected'
        elif os.environ.get('DATABASE_URL'):
            database_status = 'configured_but_unavailable'
        
        return jsonify({
            'status': 'healthy',
            'database': database_status,
            'database_available': DATABASE_AVAILABLE,
            'timestamp': datetime.now().isoformat(),
            'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'local')
        })
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 500

# Rota para status do banco
@app.route('/api/database/status', methods=['GET'])
def database_status():
    return jsonify({
        'available': DATABASE_AVAILABLE,
        'url_configured': bool(os.environ.get('DATABASE_URL')),
        'message': 'Banco disponível' if DATABASE_AVAILABLE else 'Banco não disponível - aguarde configuração'
    })

# Servir arquivos de upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Servir arquivos estáticos
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            return "index.html not found", 404

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Iniciando servidor na porta {port}")
    logger.info(f"📊 Status do banco: {'Disponível' if DATABASE_AVAILABLE else 'Não disponível'}")
    app.run(host='0.0.0.0', port=port, debug=False)

