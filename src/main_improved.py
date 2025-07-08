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

# Importar gerenciador de banco
try:
    from .database.connection_manager import db_manager, get_db_connection, is_database_available, init_database
    from psycopg2.extras import RealDictCursor
    import psycopg2
    
    # Tentar inicializar banco se disponível
    if db_manager.is_database_available():
        try:
            init_database()
            logger.info("✅ Sistema de banco inicializado com sucesso")
        except Exception as e:
            logger.error(f"❌ Erro ao inicializar tabelas: {e}")
    
    DATABASE_SYSTEM_AVAILABLE = True
    
except Exception as e:
    logger.error(f"❌ Erro ao importar sistema de banco: {e}")
    DATABASE_SYSTEM_AVAILABLE = False
    
    # Funções fallback
    def is_database_available():
        return False
    
    def get_db_connection():
        raise Exception("Sistema de banco não disponível")

# ROTAS DE AUTENTICAÇÃO
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        # Verificar se banco está disponível
        if not is_database_available():
            return jsonify({
                'success': False, 
                'message': 'Serviço temporariamente indisponível. O banco de dados está sendo configurado. Tente novamente em alguns minutos.',
                'code': 'DATABASE_UNAVAILABLE'
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
        if "não disponível" in str(e):
            return jsonify({
                'success': False, 
                'message': 'Serviço temporariamente indisponível. Tente novamente em alguns minutos.',
                'code': 'DATABASE_UNAVAILABLE'
            }), 503
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        # Verificar se banco está disponível
        if not is_database_available():
            return jsonify({
                'success': False, 
                'message': 'Serviço temporariamente indisponível. O banco de dados está sendo configurado. Tente novamente em alguns minutos.',
                'code': 'DATABASE_UNAVAILABLE'
            }), 503
        
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
        if "não disponível" in str(e):
            return jsonify({
                'success': False, 
                'message': 'Serviço temporariamente indisponível. Tente novamente em alguns minutos.',
                'code': 'DATABASE_UNAVAILABLE'
            }), 503
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logout realizado com sucesso'})

@app.route('/api/auth/me', methods=['GET'])
def get_current_user():
    try:
        if not is_database_available():
            return jsonify({'success': False, 'message': 'Serviço temporariamente indisponível'}), 503
        
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        conn = get_db_connection()
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
        "database_available": is_database_available(),
        "database_url_exists": bool(os.environ.get('DATABASE_URL')),
        "database_system_available": DATABASE_SYSTEM_AVAILABLE
    }, 200

# Rota de saúde
@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        database_status = 'not_configured'
        if DATABASE_SYSTEM_AVAILABLE:
            if is_database_available():
                database_status = 'connected'
            elif os.environ.get('DATABASE_URL'):
                database_status = 'configured_but_unavailable'
        
        return jsonify({
            'status': 'healthy',
            'database': database_status,
            'database_available': is_database_available(),
            'database_system_available': DATABASE_SYSTEM_AVAILABLE,
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
        'available': is_database_available(),
        'system_available': DATABASE_SYSTEM_AVAILABLE,
        'url_configured': bool(os.environ.get('DATABASE_URL')),
        'message': 'Banco disponível' if is_database_available() else 'Banco não disponível - aguarde configuração'
    })

# Rota para forçar reconexão
@app.route('/api/database/reconnect', methods=['POST'])
def database_reconnect():
    try:
        if DATABASE_SYSTEM_AVAILABLE:
            db_manager._test_connection()
            if db_manager.is_available:
                init_database()
                return jsonify({'success': True, 'message': 'Reconexão bem-sucedida'})
            else:
                return jsonify({'success': False, 'message': 'Falha na reconexão'})
        else:
            return jsonify({'success': False, 'message': 'Sistema de banco não disponível'})
    except Exception as e:
        logger.error(f"Erro na reconexão: {e}")
        return jsonify({'success': False, 'message': str(e)})

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
    logger.info(f"📊 Sistema de banco: {'Disponível' if DATABASE_SYSTEM_AVAILABLE else 'Não disponível'}")
    logger.info(f"📊 Banco conectado: {'Sim' if is_database_available() else 'Não'}")
    app.run(host='0.0.0.0', port=port, debug=False)

