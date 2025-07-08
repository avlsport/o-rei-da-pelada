import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configuração básica
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'asdf#FGSgvasgf$5$WGT')

# CORS
CORS(app, supports_credentials=True, origins=['*'])

# Rota de teste
@app.route('/api/test', methods=['GET'])
def test_api():
    return {
        "message": "API funcionando", 
        "status": "ok", 
        "python_version": sys.version,
        "environment": os.environ.get('RAILWAY_ENVIRONMENT', 'local')
    }, 200

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
    app.run(host='0.0.0.0', port=port, debug=False)

