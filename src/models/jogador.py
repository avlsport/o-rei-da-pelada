from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class Jogador(db.Model):
    __tablename__ = 'jogadores'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    posicao = db.Column(db.String(50))
    foto_url = db.Column(db.String(255))
    pontos_totais = db.Column(db.Integer, default=0)
    media_pontos = db.Column(db.Float, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def set_senha(self, senha):
        """Define a senha do jogador"""
        self.senha_hash = generate_password_hash(senha)
    
    def check_senha(self, senha):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, senha)
    
    def to_dict(self):
        """Converte o jogador para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'posicao': self.posicao,
            'foto_url': self.foto_url,
            'pontos_totais': self.pontos_totais,
            'media_pontos': self.media_pontos,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

