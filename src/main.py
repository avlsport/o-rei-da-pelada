import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.jogador import db
from src.models.pelada import Pelada, MembroPelada, SolicitacaoEntrada, ConfirmacaoPresenca, PagamentoPartida
from src.models.partida import Partida, EstatisticaPartida, Voto
from src.routes.auth import auth_bp
from src.routes.peladas import peladas_bp
from src.routes.partidas import partidas_bp
from src.routes.financeiro import financeiro_bp
from src.routes.rankings import rankings_bp
from src.routes.dashboard import dashboard_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuração de produção
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# Configurações de sessão para produção
app.config['SESSION_COOKIE_SECURE'] = False  # Permite HTTP
app.config['SESSION_COOKIE_HTTPONLY'] = False  # Permite JavaScript acessar
app.config['SESSION_COOKIE_SAMESITE'] = None  # Permite CORS
app.config['SESSION_COOKIE_DOMAIN'] = None  # Permite qualquer domínio
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 horas

# Habilitar CORS para todas as rotas com configurações específicas
CORS(app, 
     supports_credentials=True, 
     origins=['*'],
     allow_headers=['Content-Type', 'Authorization'],
     methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])

# Registrar blueprints
app.register_blueprint(auth_bp, url_prefix='/api')
app.register_blueprint(peladas_bp, url_prefix='/api')
app.register_blueprint(partidas_bp, url_prefix='/api')
app.register_blueprint(financeiro_bp, url_prefix='/api')
app.register_blueprint(rankings_bp, url_prefix='/api')
app.register_blueprint(dashboard_bp, url_prefix='/api')

# Configuração do banco de dados - PostgreSQL para produção, SQLite para desenvolvimento
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Produção - PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # Desenvolvimento - SQLite
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), 'uploads')

# Criar pasta de uploads se não existir
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

# Importar todos os modelos para criar as tabelas
with app.app_context():
    db.create_all()

# Rota de teste para verificar se API está funcionando
@app.route('/api/test', methods=['GET'])
def test_api():
    return {"message": "API funcionando", "status": "ok"}, 200

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
    debug = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug)

