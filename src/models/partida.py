from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Partida(db.Model):
    __tablename__ = 'partidas'
    
    id = db.Column(db.Integer, primary_key=True)
    id_pelada = db.Column(db.Integer, db.ForeignKey('peladas.id'), nullable=False)
    data_partida = db.Column(db.DateTime, nullable=False)
    horario_inicio = db.Column(db.Time, nullable=False)
    horario_fim = db.Column(db.Time, nullable=False)
    local = db.Column(db.String(200))
    observacoes = db.Column(db.Text)
    status = db.Column(db.String(20), default='agendada')  # 'agendada', 'em_andamento', 'finalizada', 'cancelada'
    finalizada = db.Column(db.Boolean, default=False)
    votacao_aberta = db.Column(db.Boolean, default=False)
    votacao_encerrada = db.Column(db.Boolean, default=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    id_criador = db.Column(db.Integer, db.ForeignKey('jogadores.id'), nullable=False)
    
    # Relacionamentos
    criador = db.relationship('Jogador', backref='partidas_criadas')
    confirmacoes = db.relationship('ConfirmacaoPresenca', backref='partida', lazy=True, cascade='all, delete-orphan')
    estatisticas = db.relationship('EstatisticaPartida', backref='partida', lazy=True, cascade='all, delete-orphan')
    votos = db.relationship('Voto', backref='partida', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_pelada': self.id_pelada,
            'data_partida': self.data_partida.isoformat() if self.data_partida else None,
            'horario_inicio': self.horario_inicio.strftime('%H:%M') if self.horario_inicio else None,
            'horario_fim': self.horario_fim.strftime('%H:%M') if self.horario_fim else None,
            'local': self.local,
            'observacoes': self.observacoes,
            'status': self.status,
            'finalizada': self.finalizada,
            'votacao_aberta': self.votacao_aberta,
            'votacao_encerrada': self.votacao_encerrada,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'total_confirmados': len([c for c in self.confirmacoes if c.confirmado]),
            'total_nao_confirmados': len([c for c in self.confirmacoes if not c.confirmado]),
            'total_pendentes': len([m for m in self.pelada.membros if not any(c.id_jogador == m.id_jogador for c in self.confirmacoes)])
        }

class ConfirmacaoPresenca(db.Model):
    __tablename__ = 'confirmacoes_presenca'
    
    id = db.Column(db.Integer, primary_key=True)
    id_partida = db.Column(db.Integer, db.ForeignKey('partidas.id'), nullable=False)
    id_jogador = db.Column(db.Integer, db.ForeignKey('jogadores.id'), nullable=False)
    confirmado = db.Column(db.Boolean, nullable=False)
    data_confirmacao = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    jogador = db.relationship('Jogador', backref='confirmacoes_presenca')
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_partida': self.id_partida,
            'id_jogador': self.id_jogador,
            'confirmado': self.confirmado,
            'data_confirmacao': self.data_confirmacao.isoformat() if self.data_confirmacao else None,
            'jogador': self.jogador.to_dict() if self.jogador else None
        }

class EstatisticaPartida(db.Model):
    __tablename__ = 'estatisticas_partida'
    
    id = db.Column(db.Integer, primary_key=True)
    id_partida = db.Column(db.Integer, db.ForeignKey('partidas.id'), nullable=False)
    id_jogador = db.Column(db.Integer, db.ForeignKey('jogadores.id'), nullable=False)
    gols = db.Column(db.Integer, default=0)
    assistencias = db.Column(db.Integer, default=0)
    defesas = db.Column(db.Integer, default=0)  # Para goleiros
    gols_sofridos = db.Column(db.Integer, default=0)  # Para goleiros
    desarmes = db.Column(db.Integer, default=0)
    pontos_estatisticas = db.Column(db.Integer, default=0)  # Pontos das estatísticas
    pontos_votacao = db.Column(db.Integer, default=0)  # Pontos da votação (MVP/Bola Murcha)
    pontos_total = db.Column(db.Integer, default=0)  # Total de pontos
    
    # Relacionamentos
    jogador = db.relationship('Jogador', backref='estatisticas_partidas')
    
    def calcular_pontos_estatisticas(self):
        """Calcula pontos baseado nas estatísticas"""
        pontos = 0
        pontos += self.gols * 8  # 8 pontos por gol
        pontos += self.assistencias * 5  # 5 pontos por assistência
        pontos += self.defesas * 2  # 2 pontos por defesa
        pontos -= self.gols_sofridos * 1  # -1 ponto por gol sofrido
        pontos += self.desarmes * 1  # 1 ponto por desarme
        return pontos
    
    def calcular_pontos_total(self):
        """Calcula pontos totais (estatísticas + votação)"""
        return self.pontos_estatisticas + self.pontos_votacao
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_partida': self.id_partida,
            'id_jogador': self.id_jogador,
            'gols': self.gols,
            'assistencias': self.assistencias,
            'defesas': self.defesas,
            'gols_sofridos': self.gols_sofridos,
            'desarmes': self.desarmes,
            'pontos_estatisticas': self.pontos_estatisticas,
            'pontos_votacao': self.pontos_votacao,
            'pontos_total': self.pontos_total,
            'jogador': self.jogador.to_dict() if self.jogador else None
        }

class Voto(db.Model):
    __tablename__ = 'votos'
    
    id = db.Column(db.Integer, primary_key=True)
    id_partida = db.Column(db.Integer, db.ForeignKey('partidas.id'), nullable=False)
    id_jogador_votante = db.Column(db.Integer, db.ForeignKey('jogadores.id'), nullable=False)
    id_jogador_mvp = db.Column(db.Integer, db.ForeignKey('jogadores.id'))
    id_jogador_bola_murcha = db.Column(db.Integer, db.ForeignKey('jogadores.id'))
    data_voto = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    votante = db.relationship('Jogador', foreign_keys=[id_jogador_votante], backref='votos_dados')
    jogador_mvp = db.relationship('Jogador', foreign_keys=[id_jogador_mvp], backref='votos_mvp_recebidos')
    jogador_bola_murcha = db.relationship('Jogador', foreign_keys=[id_jogador_bola_murcha], backref='votos_bola_murcha_recebidos')
    
    def to_dict(self):
        return {
            'id': self.id,
            'id_partida': self.id_partida,
            'id_jogador_votante': self.id_jogador_votante,
            'id_jogador_mvp': self.id_jogador_mvp,
            'id_jogador_bola_murcha': self.id_jogador_bola_murcha,
            'data_voto': self.data_voto.isoformat() if self.data_voto else None
        }

