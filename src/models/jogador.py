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
    posicao = db.Column(db.String(50), nullable=False)
    foto_url = db.Column(db.String(255))
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    # partidas_criadas é definido no modelo Partida com backref='criador'
    estatisticas = db.relationship('EstatisticaPartida', backref='estatisticas_jogador', lazy=True)
    votos_dados = db.relationship('Voto', foreign_keys='Voto.id_jogador_votante', backref='votante_jogador', lazy=True)
    votos_recebidos = db.relationship('Voto', foreign_keys='Voto.id_jogador_votado', backref='votado_jogador', lazy=True)
    
    def set_senha(self, senha):
        """Define a senha do jogador com hash"""
        self.senha_hash = generate_password_hash(senha)
    
    def check_senha(self, senha):
        """Verifica se a senha está correta"""
        return check_password_hash(self.senha_hash, senha)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'posicao': self.posicao,
            'foto_url': self.foto_url,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None,
            'ativo': self.ativo
        }
    
    def __repr__(self):
        return f'<Jogador {self.nome}>'


