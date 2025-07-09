import os
import sys
# DON'T CHANGE THIS - Add the src directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import logging
from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS

# Configurar logging
logging.basicConfig(level=logging.INFO)

def create_app():
    app = Flask(__name__, static_folder='static')
    
    # Configurações
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Inicializar CORS
    CORS(app, supports_credentials=True)
    
    # Inicializar banco de dados
    from database.connection_manager import init_database
    init_database()
    
    # Registrar blueprints
    from routes.auth_ultra_simple import auth_bp
    from routes.rankings import rankings_bp
    from routes.ranking_geral import ranking_geral_bp
    from routes.peladas import peladas_bp
    from routes.partidas import partidas_bp
    from routes.financeiro import financeiro_bp
    from routes.busca_peladas import busca_peladas_bp
    from routes.jogadores import jogadores_bp
    from routes.user import user_bp
    from routes.debug import debug_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(rankings_bp)
    app.register_blueprint(ranking_geral_bp)
    app.register_blueprint(peladas_bp)
    app.register_blueprint(partidas_bp)
    app.register_blueprint(financeiro_bp)
    app.register_blueprint(busca_peladas_bp)
    app.register_blueprint(jogadores_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(debug_bp)
    
    # Rota para servir arquivos estáticos
    @app.route('/')
    def index():
        return send_from_directory(app.static_folder, 'index.html')
    
    @app.route('/dashboard.html')
    def dashboard():
        return send_from_directory(app.static_folder, 'dashboard.html')
    
    @app.route('/pelada.html')
    def pelada():
        return send_from_directory(app.static_folder, 'pelada.html')
    
    # Health check
    @app.route('/api/health')
    def health_check():
        try:
            # Testar se consegue criar conexão SQLite
            from .database.connection_manager import get_db_manager
            db_manager = get_db_manager()
            result = db_manager.execute_query('SELECT 1 as test', fetch_one=True)
            
            return jsonify({
                'status': 'healthy',
                'database': 'connected',
                'database_available': True,
                'database_type': 'SQLite'
            })
        except Exception as e:
            return jsonify({
                'status': 'unhealthy',
                'database': 'disconnected',
                'database_available': False,
                'error': str(e)
            }), 500
    
    return app

# Criar aplicação
app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
