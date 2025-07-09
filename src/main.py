import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify, request, session
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from datetime import datetime
import uuid

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))
app.config['SECRET_KEY'] = 'asdf#FGSgvasgf$5$WGT'

# Configurar CORS para permitir requisições do frontend
CORS(app, supports_credentials=True)

# Configuração do banco de dados - usa PostgreSQL no Railway, SQLite localmente
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar SQLAlchemy
db = SQLAlchemy(app)

# Modelos do banco de dados
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    position = db.Column(db.String(50), nullable=False)
    photo_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Estatísticas
    goals = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    matches_played = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    mvp_count = db.Column(db.Integer, default=0)
    worst_player_count = db.Column(db.Integer, default=0)

class Pelada(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    location = db.Column(db.String(200), nullable=False)
    monthly_fee = db.Column(db.Float, default=0.0)
    max_players = db.Column(db.Integer, default=20)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class PeladaMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pelada_id = db.Column(db.Integer, db.ForeignKey('pelada.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pelada_id = db.Column(db.Integer, db.ForeignKey('pelada.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    team_a_score = db.Column(db.Integer, default=0)
    team_b_score = db.Column(db.Integer, default=0)
    mvp_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    worst_player_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Criar diretório de uploads se não existir
upload_dir = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(upload_dir, exist_ok=True)

# Criar diretório de database se não existir
database_dir = os.path.join(os.path.dirname(__file__), 'database')
os.makedirs(database_dir, exist_ok=True)

with app.app_context():
    db.create_all()

# Rotas da API
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        if request.content_type and 'multipart/form-data' in request.content_type:
            data = request.form.to_dict()
        else:
            data = request.get_json()
        
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email já cadastrado'}), 400
        
        password_hash = generate_password_hash(data['password'])
        
        user = User(
            name=data['name'],
            email=data['email'],
            password_hash=password_hash,
            position=data['position']
        )
        
        # Handle file upload if present
        if 'photo' in request.files:
            file = request.files['photo']
            if file and file.filename:
                filename = secure_filename(f"{uuid.uuid4()}_{file.filename}")
                file.save(os.path.join(upload_dir, filename))
                user.photo_url = f"/uploads/{filename}"
        
        db.session.add(user)
        db.session.commit()
        
        session['user_id'] = user.id
        
        return jsonify({
            'message': 'Usuário criado com sucesso',
            'user': {
                'id': user.id,
                'name': user.name,
                'email': user.email,
                'position': user.position,
                'photo_url': user.photo_url
            }
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user = User.query.filter_by(email=data['email']).first()
        
        if user and check_password_hash(user.password_hash, data['password']):
            session['user_id'] = user.id
            return jsonify({
                'message': 'Login realizado com sucesso',
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'position': user.position,
                    'photo_url': user.photo_url
                }
            }), 200
        else:
            return jsonify({'error': 'Credenciais inválidas'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/auth/check-auth', methods=['GET'])
def check_auth():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        if user:
            return jsonify({
                'authenticated': True,
                'user': {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'position': user.position,
                    'photo_url': user.photo_url
                }
            }), 200
    return jsonify({'authenticated': False}), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'message': 'Logout realizado com sucesso'}), 200

@app.route('/api/peladas', methods=['GET'])
def get_peladas():
    peladas = Pelada.query.all()
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'location': p.location,
        'monthly_fee': p.monthly_fee,
        'max_players': p.max_players,
        'admin_id': p.admin_id,
        'created_at': p.created_at.isoformat()
    } for p in peladas]), 200

@app.route('/api/peladas', methods=['POST'])
def create_pelada():
    try:
        data = request.get_json()
        pelada = Pelada(
            name=data['name'],
            description=data.get('description', ''),
            location=data['location'],
            monthly_fee=data.get('monthly_fee', 0.0),
            max_players=data.get('max_players', 20),
            admin_id=session['user_id']
        )
        
        db.session.add(pelada)
        db.session.commit()
        
        # Adicionar o criador como membro
        member = PeladaMember(
            pelada_id=pelada.id,
            user_id=session['user_id']
        )
        db.session.add(member)
        db.session.commit()
        
        return jsonify({
            'message': 'Pelada criada com sucesso',
            'pelada': {
                'id': pelada.id,
                'name': pelada.name,
                'description': pelada.description,
                'location': pelada.location,
                'monthly_fee': pelada.monthly_fee,
                'max_players': pelada.max_players
            }
        }), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/peladas/my', methods=['GET'])
def get_my_peladas():
    if 'user_id' not in session:
        return jsonify({'error': 'Não autenticado'}), 401
    
    user_peladas = db.session.query(Pelada).join(PeladaMember).filter(
        PeladaMember.user_id == session['user_id'],
        PeladaMember.is_active == True
    ).all()
    
    return jsonify([{
        'id': p.id,
        'name': p.name,
        'description': p.description,
        'location': p.location,
        'monthly_fee': p.monthly_fee,
        'max_players': p.max_players,
        'admin_id': p.admin_id,
        'created_at': p.created_at.isoformat()
    } for p in user_peladas]), 200

@app.route('/api/ranking/global', methods=['GET'])
def get_global_ranking():
    users = User.query.order_by(
        (User.goals * 3 + User.assists * 2 + User.mvp_count * 5).desc()
    ).limit(10).all()
    
    return jsonify([{
        'id': u.id,
        'name': u.name,
        'position': u.position,
        'photo_url': u.photo_url,
        'goals': u.goals,
        'assists': u.assists,
        'matches_played': u.matches_played,
        'wins': u.wins,
        'mvp_count': u.mvp_count,
        'score': u.goals * 3 + u.assists * 2 + u.mvp_count * 5
    } for u in users]), 200

@app.route('/api/users/<int:user_id>/stats', methods=['GET'])
def get_user_stats(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        'id': user.id,
        'name': user.name,
        'position': user.position,
        'photo_url': user.photo_url,
        'goals': user.goals,
        'assists': user.assists,
        'matches_played': user.matches_played,
        'wins': user.wins,
        'mvp_count': user.mvp_count,
        'worst_player_count': user.worst_player_count,
        'win_rate': (user.wins / user.matches_played * 100) if user.matches_played > 0 else 0
    }), 200

# Rota para servir arquivos de upload
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(os.path.join(app.static_folder, 'uploads'), filename)

# Rota para servir o frontend React
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
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=True)

