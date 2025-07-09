from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    position = db.Column(db.String(20), nullable=False)  # Goleiro, Zagueiro, Meio Campo, Atacante
    photo_url = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    peladas_created = db.relationship('Pelada', backref='creator', lazy=True, foreign_keys='Pelada.creator_id')
    pelada_memberships = db.relationship('PeladaMember', backref='user', lazy=True)
    match_participations = db.relationship('MatchParticipant', backref='user', lazy=True)
    match_stats = db.relationship('MatchStats', backref='user', lazy=True)
    votes_given = db.relationship('Vote', backref='voter', lazy=True, foreign_keys='Vote.voter_id')
    votes_received = db.relationship('Vote', backref='voted_user', lazy=True, foreign_keys='Vote.voted_user_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'position': self.position,
            'photo_url': self.photo_url,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Pelada(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    photo_url = db.Column(db.String(255), nullable=True)
    creator_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    members = db.relationship('PeladaMember', backref='pelada', lazy=True, cascade='all, delete-orphan')
    matches = db.relationship('Match', backref='pelada', lazy=True, cascade='all, delete-orphan')
    financial_records = db.relationship('FinancialRecord', backref='pelada', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Pelada {self.name}>'

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'location': self.location,
            'description': self.description,
            'photo_url': self.photo_url,
            'creator_id': self.creator_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class PeladaMember(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    pelada_id = db.Column(db.Integer, db.ForeignKey('pelada.id'), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)
    is_approved = db.Column(db.Boolean, default=False)
    monthly_payment_status = db.Column(db.Boolean, default=False)
    joined_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'pelada_id': self.pelada_id,
            'is_admin': self.is_admin,
            'is_approved': self.is_approved,
            'monthly_payment_status': self.monthly_payment_status,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None
        }

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pelada_id = db.Column(db.Integer, db.ForeignKey('pelada.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    is_completed = db.Column(db.Boolean, default=False)
    voting_deadline = db.Column(db.DateTime, nullable=True)
    voting_closed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    participants = db.relationship('MatchParticipant', backref='match', lazy=True, cascade='all, delete-orphan')
    stats = db.relationship('MatchStats', backref='match', lazy=True, cascade='all, delete-orphan')
    votes = db.relationship('Vote', backref='match', lazy=True, cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'pelada_id': self.pelada_id,
            'date': self.date.isoformat() if self.date else None,
            'start_time': self.start_time.isoformat() if self.start_time else None,
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'is_completed': self.is_completed,
            'voting_deadline': self.voting_deadline.isoformat() if self.voting_deadline else None,
            'voting_closed': self.voting_closed,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class MatchParticipant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    confirmed = db.Column(db.Boolean, nullable=True)  # True=confirmado, False=não vai, None=não decidiu
    confirmed_at = db.Column(db.DateTime, nullable=True)

    def to_dict(self):
        return {
            'id': self.id,
            'match_id': self.match_id,
            'user_id': self.user_id,
            'confirmed': self.confirmed,
            'confirmed_at': self.confirmed_at.isoformat() if self.confirmed_at else None
        }

class MatchStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    goals = db.Column(db.Integer, default=0)
    assists = db.Column(db.Integer, default=0)
    saves = db.Column(db.Integer, default=0)  # Para goleiros
    goals_conceded = db.Column(db.Integer, default=0)  # Para goleiros
    tackles = db.Column(db.Integer, default=0)  # Desarmes
    total_points = db.Column(db.Integer, default=0)

    def calculate_points(self, mvp_votes=0, worst_votes=0, voted=True):
        """Calcula os pontos baseado nas estatísticas e votações"""
        points = 0
        points += self.goals * 8  # 8 pontos por gol
        points += self.assists * 5  # 5 pontos por assistência
        points += self.saves * 2  # 2 pontos por defesa
        points -= self.goals_conceded * 1  # -1 ponto por gol sofrido
        points += self.tackles * 1  # 1 ponto por desarme
        points += mvp_votes * 3  # 3 pontos por voto de MVP
        points -= worst_votes * 3  # -3 pontos por voto de pior jogador
        if not voted:
            points -= 5  # -5 pontos por não votar
        
        self.total_points = points
        return points

    def to_dict(self):
        return {
            'id': self.id,
            'match_id': self.match_id,
            'user_id': self.user_id,
            'goals': self.goals,
            'assists': self.assists,
            'saves': self.saves,
            'goals_conceded': self.goals_conceded,
            'tackles': self.tackles,
            'total_points': self.total_points
        }

class Vote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match.id'), nullable=False)
    voter_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    voted_user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)  # 'mvp' ou 'worst'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'match_id': self.match_id,
            'voter_id': self.voter_id,
            'voted_user_id': self.voted_user_id,
            'vote_type': self.vote_type,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class FinancialRecord(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pelada_id = db.Column(db.Integer, db.ForeignKey('pelada.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'income' ou 'expense'
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'pelada_id': self.pelada_id,
            'description': self.description,
            'amount': self.amount,
            'type': self.type,
            'date': self.date.isoformat() if self.date else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

