from src.models.jogador import db
from datetime import datetime

class Pelada(db.Model):
    __tablename__ = 'peladas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    foto_url = db.Column(db.String(500))  # NOVO CAMPO para foto da pelada
    id_criador = db.Column(db.Integer, db.ForeignKey('jogadores.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ativa = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    criador = db.relationship('Jogador', backref='peladas_criadas', lazy=True)
    membros = db.relationship('MembroPelada', backref='pelada', lazy=True, cascade='all, delete-orphan')
    solicitacoes = db.relationship('SolicitacaoEntrada', backref='pelada', lazy=True, cascade='all, delete-orphan')
    partidas = db.relationship('Partida', backref='pelada', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'foto_url': self.foto_url,  # NOVO CAMPO
            'id_criador': self.id_criador,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'ativa': self.ativa
        }
    
    def __repr__(self):
        return f'<Pelada {self.nome}>'


class MembroPelada(db.Model):
    __tablename__ = 'membros_pelada'
    
    id = db.Column(db.Integer, primary_key=True)
    id_pelada = db.Column(db.Integer, db.ForeignKey('peladas.id'), nullable=False)
    id_jogador = db.Column(db.Integer, db.ForeignKey('jogadores.id'), nullable=False)
    data_entrada = db.Column(db.DateTime, default=datetime.utcnow)
    papel = db.Column(db.String(20), default='membro')  # 'admin' ou 'membro'
    
    # Relacionamentos
    jogador = db.relationship('Jogador', backref='membros_pelada', lazy=True)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'id_pelada': self.id_pelada,
            'id_jogador': self.id_jogador,
            'data_entrada': self.data_entrada.isoformat() if self.data_entrada else None,
            'papel': self.papel
        }
    
    def __repr__(self):
        return f'<MembroPelada {self.id_jogador} - Pelada {self.id_pelada}>'


class SolicitacaoEntrada(db.Model):
    __tablename__ = 'solicitacoes_entrada'
    
    id = db.Column(db.Integer, primary_key=True)
    id_pelada = db.Column(db.Integer, db.ForeignKey('peladas.id'), nullable=False)
    id_jogador = db.Column(db.Integer, db.ForeignKey('jogadores.id'), nullable=False)
    data_solicitacao = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pendente')  # 'pendente', 'aprovada', 'rejeitada'
    
    # Relacionamentos
    jogador = db.relationship('Jogador', backref='solicitacoes_entrada', lazy=True)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'id_pelada': self.id_pelada,
            'id_jogador': self.id_jogador,
            'data_solicitacao': self.data_solicitacao.isoformat() if self.data_solicitacao else None,
            'status': self.status
        }
    
    def __repr__(self):
        return f'<SolicitacaoEntrada {self.id_jogador} - Pelada {self.id_pelada}>'


class ConfirmacaoPresenca(db.Model):
    __tablename__ = 'confirmacoes_presenca'
    
    id = db.Column(db.Integer, primary_key=True)
    id_partida = db.Column(db.Integer, db.ForeignKey('partidas.id'), nullable=False)
    id_jogador = db.Column(db.Integer, db.ForeignKey('jogadores.id'), nullable=False)
    status = db.Column(db.String(20), default='pendente')  # 'confirmado', 'recusado', 'pendente'
    data_confirmacao = db.Column(db.DateTime)
    
    # Relacionamentos
    jogador = db.relationship('Jogador', backref='confirmacoes_presenca', lazy=True)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'id_partida': self.id_partida,
            'id_jogador': self.id_jogador,
            'status': self.status,
            'data_confirmacao': self.data_confirmacao.isoformat() if self.data_confirmacao else None
        }
    
    def __repr__(self):
        return f'<ConfirmacaoPresenca {self.id_jogador} - Partida {self.id_partida}>'

