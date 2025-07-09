from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

db = SQLAlchemy()

class User(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    senha_hash = db.Column(db.String(255), nullable=False)
    posicao = db.Column(db.String(20), nullable=False)  # Goleiro, Zagueiro, Meio Campo, Atacante
    foto_perfil_url = db.Column(db.String(255))
    data_cadastro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    peladas_admin = db.relationship('Pelada', backref='admin', lazy=True, foreign_keys='Pelada.admin_id')
    membros_pelada = db.relationship('MembroPelada', backref='usuario', lazy=True)
    presencas = db.relationship('PresencaPartida', backref='usuario', lazy=True)
    estatisticas = db.relationship('EstatisticaJogadorPartida', backref='usuario', lazy=True)
    avaliacoes_feitas = db.relationship('AvaliacaoPartida', backref='avaliador', lazy=True, foreign_keys='AvaliacaoPartida.avaliador_id')
    avaliacoes_recebidas = db.relationship('AvaliacaoPartida', backref='avaliado', lazy=True, foreign_keys='AvaliacaoPartida.avaliado_id')
    movimentos_financeiros = db.relationship('Financeiro', backref='registrado_por_usuario', lazy=True)
    solicitacoes = db.relationship('SolicitacaoPelada', backref='usuario', lazy=True)

    def __repr__(self):
        return f'<User {self.nome}>'

    def set_password(self, password):
        self.senha_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.senha_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'posicao': self.posicao,
            'foto_perfil_url': self.foto_perfil_url,
            'data_cadastro': self.data_cadastro.isoformat() if self.data_cadastro else None
        }

class Pelada(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nome = db.Column(db.String(100), unique=True, nullable=False)
    local = db.Column(db.String(200), nullable=False)
    descricao = db.Column(db.Text)
    foto_pelada_url = db.Column(db.String(255))
    admin_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    membros = db.relationship('MembroPelada', backref='pelada', lazy=True)
    partidas = db.relationship('Partida', backref='pelada', lazy=True)
    movimentos_financeiros = db.relationship('Financeiro', backref='pelada', lazy=True)
    mensalistas = db.relationship('Mensalista', backref='pelada', lazy=True)
    solicitacoes = db.relationship('SolicitacaoPelada', backref='pelada', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'local': self.local,
            'descricao': self.descricao,
            'foto_pelada_url': self.foto_pelada_url,
            'admin_id': self.admin_id,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }

class MembroPelada(db.Model):
    usuario_id = db.Column(db.String(36), db.ForeignKey('user.id'), primary_key=True)
    pelada_id = db.Column(db.String(36), db.ForeignKey('pelada.id'), primary_key=True)
    is_admin = db.Column(db.Boolean, default=False)
    data_entrada = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'usuario_id': self.usuario_id,
            'pelada_id': self.pelada_id,
            'is_admin': self.is_admin,
            'data_entrada': self.data_entrada.isoformat() if self.data_entrada else None
        }

class Partida(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pelada_id = db.Column(db.String(36), db.ForeignKey('pelada.id'), nullable=False)
    data_partida = db.Column(db.Date, nullable=False)
    hora_inicio = db.Column(db.Time, nullable=False)
    hora_fim = db.Column(db.Time)
    status = db.Column(db.String(20), default='agendada')  # agendada, em_andamento, finalizada, avaliacao, concluida
    mvp_id = db.Column(db.String(36), db.ForeignKey('user.id'))
    bola_murcha_id = db.Column(db.String(36), db.ForeignKey('user.id'))
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    presencas = db.relationship('PresencaPartida', backref='partida', lazy=True)
    estatisticas = db.relationship('EstatisticaJogadorPartida', backref='partida', lazy=True)
    avaliacoes = db.relationship('AvaliacaoPartida', backref='partida', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'pelada_id': self.pelada_id,
            'data_partida': self.data_partida.isoformat() if self.data_partida else None,
            'hora_inicio': self.hora_inicio.isoformat() if self.hora_inicio else None,
            'hora_fim': self.hora_fim.isoformat() if self.hora_fim else None,
            'status': self.status,
            'mvp_id': self.mvp_id,
            'bola_murcha_id': self.bola_murcha_id,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None
        }

class PresencaPartida(db.Model):
    partida_id = db.Column(db.String(36), db.ForeignKey('partida.id'), primary_key=True)
    usuario_id = db.Column(db.String(36), db.ForeignKey('user.id'), primary_key=True)
    confirmacao = db.Column(db.String(20), default='pendente')  # pendente, confirmado, nao_confirmado
    data_confirmacao = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'partida_id': self.partida_id,
            'usuario_id': self.usuario_id,
            'confirmacao': self.confirmacao,
            'data_confirmacao': self.data_confirmacao.isoformat() if self.data_confirmacao else None
        }

class EstatisticaJogadorPartida(db.Model):
    partida_id = db.Column(db.String(36), db.ForeignKey('partida.id'), primary_key=True)
    usuario_id = db.Column(db.String(36), db.ForeignKey('user.id'), primary_key=True)
    gols = db.Column(db.Integer, default=0)
    assistencias = db.Column(db.Integer, default=0)
    defesas = db.Column(db.Integer, default=0)
    gols_sofridos = db.Column(db.Integer, default=0)
    desarmes = db.Column(db.Integer, default=0)
    pontuacao_total = db.Column(db.Integer, default=0)

    def calcular_pontuacao(self, votos_mvp=0, votos_bola_murcha=0, nao_votou=False):
        pontos = 0
        pontos += self.gols * 8
        pontos += self.assistencias * 5
        pontos += self.defesas * 2
        pontos -= self.gols_sofridos * 1
        pontos += self.desarmes * 1
        pontos += votos_mvp * 3
        pontos -= votos_bola_murcha * 3
        if nao_votou:
            pontos -= 5
        self.pontuacao_total = pontos
        return pontos

    def to_dict(self):
        return {
            'partida_id': self.partida_id,
            'usuario_id': self.usuario_id,
            'gols': self.gols,
            'assistencias': self.assistencias,
            'defesas': self.defesas,
            'gols_sofridos': self.gols_sofridos,
            'desarmes': self.desarmes,
            'pontuacao_total': self.pontuacao_total
        }

class AvaliacaoPartida(db.Model):
    partida_id = db.Column(db.String(36), db.ForeignKey('partida.id'), primary_key=True)
    avaliador_id = db.Column(db.String(36), db.ForeignKey('user.id'), primary_key=True)
    avaliado_id = db.Column(db.String(36), db.ForeignKey('user.id'), primary_key=True)
    tipo_avaliacao = db.Column(db.String(20), nullable=False)  # mvp, bola_murcha
    data_avaliacao = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'partida_id': self.partida_id,
            'avaliador_id': self.avaliador_id,
            'avaliado_id': self.avaliado_id,
            'tipo_avaliacao': self.tipo_avaliacao,
            'data_avaliacao': self.data_avaliacao.isoformat() if self.data_avaliacao else None
        }

class Financeiro(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pelada_id = db.Column(db.String(36), db.ForeignKey('pelada.id'), nullable=False)
    tipo_movimento = db.Column(db.String(20), nullable=False)  # entrada, saida
    descricao = db.Column(db.Text, nullable=False)
    valor = db.Column(db.Numeric(10, 2), nullable=False)
    data_movimento = db.Column(db.DateTime, default=datetime.utcnow)
    registrado_por = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'pelada_id': self.pelada_id,
            'tipo_movimento': self.tipo_movimento,
            'descricao': self.descricao,
            'valor': float(self.valor),
            'data_movimento': self.data_movimento.isoformat() if self.data_movimento else None,
            'registrado_por': self.registrado_por
        }

class Mensalista(db.Model):
    pelada_id = db.Column(db.String(36), db.ForeignKey('pelada.id'), primary_key=True)
    usuario_id = db.Column(db.String(36), db.ForeignKey('user.id'), primary_key=True)
    status_pagamento = db.Column(db.String(20), default='pendente')  # pago, pendente
    data_ultimo_pagamento = db.Column(db.Date)

    def to_dict(self):
        return {
            'pelada_id': self.pelada_id,
            'usuario_id': self.usuario_id,
            'status_pagamento': self.status_pagamento,
            'data_ultimo_pagamento': self.data_ultimo_pagamento.isoformat() if self.data_ultimo_pagamento else None
        }

class SolicitacaoPelada(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    pelada_id = db.Column(db.String(36), db.ForeignKey('pelada.id'), nullable=False)
    status = db.Column(db.String(20), default='pendente')  # pendente, aprovada, rejeitada
    data_solicitacao = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'usuario_id': self.usuario_id,
            'pelada_id': self.pelada_id,
            'status': self.status,
            'data_solicitacao': self.data_solicitacao.isoformat() if self.data_solicitacao else None
        }

