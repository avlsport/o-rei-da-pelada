from src.models.jogador import db
from datetime import datetime

class Pelada(db.Model):
    __tablename__ = 'peladas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False)
    descricao = db.Column(db.Text)
    local = db.Column(db.String(200), nullable=False)
    foto_url = db.Column(db.String(500))  # Foto da pelada
    id_criador = db.Column(db.Integer, db.ForeignKey('jogadores.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    ativa = db.Column(db.Boolean, default=True)
    
    # CAMPOS FINANCEIROS
    valor_por_partida = db.Column(db.Float, default=0.0)  # Valor que cada jogador paga por partida
    controle_financeiro = db.Column(db.Boolean, default=False)  # Se a pelada tem controle financeiro
    
    # Relacionamentos
    criador = db.relationship('Jogador', backref='peladas_criadas', lazy=True)
    membros = db.relationship('MembroPelada', backref='pelada', lazy=True, cascade='all, delete-orphan')
    solicitacoes = db.relationship('SolicitacaoEntrada', backref='pelada', lazy=True, cascade='all, delete-orphan')
    partidas = db.relationship('Partida', backref='pelada', lazy=True, cascade='all, delete-orphan')
    pagamentos = db.relationship('PagamentoPartida', backref='pelada', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'nome': self.nome,
            'descricao': self.descricao,
            'local': self.local,
            'foto_url': self.foto_url,
            'id_criador': self.id_criador,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'ativa': self.ativa,
            'valor_por_partida': self.valor_por_partida,
            'controle_financeiro': self.controle_financeiro
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
    confirmado = db.Column(db.Boolean, default=False)  # True = confirmado, False = não confirmado
    data_confirmacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    jogador = db.relationship('Jogador', backref='confirmacoes_presenca', lazy=True)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'id_partida': self.id_partida,
            'id_jogador': self.id_jogador,
            'confirmado': self.confirmado,
            'data_confirmacao': self.data_confirmacao.isoformat() if self.data_confirmacao else None
        }
    
    def __repr__(self):
        return f'<ConfirmacaoPresenca {self.id_jogador} - Partida {self.id_partida}>'


class PagamentoPartida(db.Model):
    __tablename__ = 'pagamentos_partida'
    
    id = db.Column(db.Integer, primary_key=True)
    id_pelada = db.Column(db.Integer, db.ForeignKey('peladas.id'), nullable=False)
    id_partida = db.Column(db.Integer, db.ForeignKey('partidas.id'), nullable=False)
    id_jogador = db.Column(db.Integer, db.ForeignKey('jogadores.id'), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    pago = db.Column(db.Boolean, default=False)
    data_pagamento = db.Column(db.DateTime)
    observacoes = db.Column(db.Text)
    
    # Relacionamentos
    jogador = db.relationship('Jogador', backref='pagamentos_partida', lazy=True)
    partida = db.relationship('Partida', backref='pagamentos', lazy=True)
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'id_pelada': self.id_pelada,
            'id_partida': self.id_partida,
            'id_jogador': self.id_jogador,
            'valor': self.valor,
            'pago': self.pago,
            'data_pagamento': self.data_pagamento.isoformat() if self.data_pagamento else None,
            'observacoes': self.observacoes
        }
    
    def __repr__(self):
        return f'<PagamentoPartida {self.id_jogador} - Partida {self.id_partida}>'

