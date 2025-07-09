import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from src.models.user import db
from src.routes.user import user_bp
from src.routes.auth import auth_bp
from src.routes.peladas import peladas_bp
from src.routes.partidas import partidas_bp
from src.routes.ranking import ranking_bp
from src.routes.financeiro import financeiro_bp

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Habilitar CORS para todas as rotas
CORS(app)

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(auth_bp, url_prefix='/api/auth')
app.register_blueprint(peladas_bp, url_prefix='/api/peladas')
app.register_blueprint(partidas_bp, url_prefix='/api/partidas')
app.register_blueprint(ranking_bp, url_prefix='/api/ranking')
app.register_blueprint(financeiro_bp, url_prefix='/api/financeiro')

# Configuração do banco de dados
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Railway PostgreSQL
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    # SQLite local para desenvolvimento
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Criar diretório de uploads
uploads_dir = os.path.join(app.static_folder, 'uploads')
os.makedirs(uploads_dir, exist_ok=True)

with app.app_context():
    db.create_all()

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    uploads_dir = os.path.join(app.static_folder, 'uploads')
    return send_from_directory(uploads_dir, filename)

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
    app.run(host='0.0.0.0', port=port, debug=False)

