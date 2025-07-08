from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Pelada(db.Model):
    __tablename__ = 'peladas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    local = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    foto_url = db.Column(db.String(255))
    id_criador = db.Column(db.Integer, db.ForeignKey('jogadores.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ativa = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    criador = db.relationship('Jogador', backref='peladas_criadas')
    membros = db.relationship('MembroPelada', backref='pelada', lazy=True, cascade='all, delete-orphan')
    partidas = db.relationship('Partida', backref='pelada', lazy=True, cascade='all, delete-orphan')
    solicitacoes = db.relationship('SolicitacaoEntrada', backref='pelada', lazy=True, cascade='all, delete-orphan')
    financeiro = db.relationship('MovimentacaoFinanceira', backref='pelada', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'local': self.local,
            'descricao': self.descricao,
            'foto_url': self.foto_url,
            'id_criador': self.id_criador,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'ativa': self.ativa,
            'total_membros': len(self.membros),
            'total_partidas': len([p for p in self.partidas if p.finalizada])
        }

class MembroPelada(db.Model):
    __tablename__ = 'membros_pelada'
    
    id = db.Column(db.Integer, primary_key=True)
    id_pelada = db.Column(db.Integer, db.ForeignKey('peladas.id'), nullable=False)
    id_jogador = db.Column(db.Integer, db.ForeignKey('jogadores.id'), nullable=False)
    papel = db.Column(db.String(20), default='membro')  # 'admin' ou 'membro'
    data_entrada = db.Column(db.DateTime, default=datetime.utcnow)
    mensalidade_paga = db.Column(db.Boolean, default=False)
    ativo = db.Column(db.Boolean, default=True)
    
    # Relacionamentos
    jogador = db.relationship('Jogador', backref='membros_peladas')
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_pelada': self.id_pelada,
            'id_jogador': self.id_jogador,
            'papel': self.papel,
            'data_entrada': self.data_entrada.isoformat() if self.data_entrada else None,
            'mensalidade_paga': self.mensalidade_paga,
            'ativo': self.ativo,
            'jogador': self.jogador.to_dict() if self.jogador else None
        }

class SolicitacaoEntrada(db.Model):
    __tablename__ = 'solicitacoes_entrada'
    
    id = db.Column(db.Integer, primary_key=True)
    id_pelada = db.Column(db.Integer, db.ForeignKey('peladas.id'), nullable=False)
    id_jogador = db.Column(db.Integer, db.ForeignKey('jogadores.id'), nullable=False)
    mensagem = db.Column(db.Text)
    status = db.Column(db.String(20), default='pendente')  # 'pendente', 'aprovada', 'rejeitada'
    data_solicitacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_resposta = db.Column(db.DateTime)
    id_admin_resposta = db.Column(db.Integer, db.ForeignKey('jogadores.id'))
    
    # Relacionamentos
    jogador = db.relationship('Jogador', foreign_keys=[id_jogador], backref='solicitacoes_enviadas')
    admin_resposta = db.relationship('Jogador', foreign_keys=[id_admin_resposta], backref='solicitacoes_respondidas')
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_pelada': self.id_pelada,
            'id_jogador': self.id_jogador,
            'mensagem': self.mensagem,
            'status': self.status,
            'data_solicitacao': self.data_solicitacao.isoformat() if self.data_solicitacao else None,
            'data_resposta': self.data_resposta.isoformat() if self.data_resposta else None,
            'jogador': self.jogador.to_dict() if self.jogador else None
        }

class MovimentacaoFinanceira(db.Model):
    __tablename__ = 'movimentacoes_financeiras'
    
    id = db.Column(db.Integer, primary_key=True)
    id_pelada = db.Column(db.Integer, db.ForeignKey('peladas.id'), nullable=False)
    tipo = db.Column(db.String(20), nullable=False)  # 'entrada' ou 'saida'
    descricao = db.Column(db.String(200), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    data_movimentacao = db.Column(db.DateTime, default=datetime.utcnow)
    id_admin = db.Column(db.Integer, db.ForeignKey('jogadores.id'), nullable=False)
    
    # Relacionamentos
    admin = db.relationship('Jogador', backref='movimentacoes_criadas')
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_pelada': self.id_pelada,
            'tipo': self.tipo,
            'descricao': self.descricao,
            'valor': self.valor,
            'data_movimentacao': self.data_movimentacao.isoformat() if self.data_movimentacao else None,
            'admin': self.admin.nome if self.admin else None
        }

