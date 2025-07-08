from src.models.jogador import db
from datetime import datetime

class Partida(db.Model):
    __tablename__ = 'partidas'
    
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.Date, nullable=False)
    horario_inicio = db.Column(db.Time, nullable=False)  # NOVO CAMPO
    horario_fim = db.Column(db.Time, nullable=False)     # NOVO CAMPO
    local = db.Column(db.String(200), nullable=False)
    id_criador = db.Column(db.Integer, db.ForeignKey('jogadores.id'), nullable=False)
    id_pelada = db.Column(db.Integer, db.ForeignKey('peladas.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    finalizada = db.Column(db.Boolean, default=False)
    
    # Relacionamentos
    # criador é definido no modelo Jogador com backref=\'partidas_criadas\'
    estatisticas = db.relationship('EstatisticaPartida', backref='partida', lazy=True, cascade='all, delete-orphan')
    votos = db.relationship('Voto', backref='partida', lazy=True, cascade='all, delete-orphan')
    confirmacoes = db.relationship('ConfirmacaoPresenca', backref='partida', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'data': self.data.isoformat() if self.data else None,
            'horario_inicio': self.horario_inicio.strftime('%H:%M') if self.horario_inicio else None,  # NOVO CAMPO
            'horario_fim': self.horario_fim.strftime('%H:%M') if self.horario_fim else None,           # NOVO CAMPO
            'local': self.local,
            'id_criador': self.id_criador,
            'id_pelada': self.id_pelada,
            'data_criacao': self.data_criacao.isoformat() if self.data_criacao else None,
            'finalizada': self.finalizada
        }
    
    def __repr__(self):
        return f'<Partida {self.id} - {self.local}>'


class EstatisticaPartida(db.Model):
    __tablename__ = 'estatisticas_partida'
    
    id = db.Column(db.Integer, primary_key=True)
    id_partida = db.Column(db.Integer, db.ForeignKey('partidas.id'), nullable=False)
    id_jogador = db.Column(db.Integer, db.ForeignKey('jogadores.id'), nullable=False)
    gols = db.Column(db.Integer, default=0)
    assistencias = db.Column(db.Integer, default=0)
    defesas = db.Column(db.Integer, default=0)
    gols_sofridos = db.Column(db.Integer, default=0)
    desarmes = db.Column(db.Integer, default=0)  # NOVO CAMPO
    pontuacao_calculada = db.Column(db.Integer, default=0)
    
    # Relacionamentos
    # jogador é definido no modelo Jogador com backref=\'estatisticas_partida\'
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'id_partida': self.id_partida,
            'id_jogador': self.id_jogador,
            'gols': self.gols,
            'assistencias': self.assistencias,
            'defesas': self.defesas,
            'gols_sofridos': self.gols_sofridos,
            'desarmes': self.desarmes,  # NOVO CAMPO
            'pontuacao_calculada': self.pontuacao_calculada
        }
    
    def __repr__(self):
        return f'<EstatisticaPartida {self.id_jogador} - Partida {self.id_partida}>'


class Voto(db.Model):
    __tablename__ = 'votos'
    
    id = db.Column(db.Integer, primary_key=True)
    id_partida = db.Column(db.Integer, db.ForeignKey('partidas.id'), nullable=False)
    id_jogador_votante = db.Column(db.Integer, db.ForeignKey('jogadores.id'), nullable=False)
    id_jogador_votado = db.Column(db.Integer, db.ForeignKey('jogadores.id'), nullable=False)
    tipo_voto = db.Column(db.String(20), nullable=False)  # 'MVP' ou 'BOLA_MURCHA'
    data_voto = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    # votante e votado são definidos no modelo Jogador com backrefs específicos
    
    def to_dict(self):
        """Converte o objeto para dicionário"""
        return {
            'id': self.id,
            'id_partida': self.id_partida,
            'id_jogador_votante': self.id_jogador_votante,
            'id_jogador_votado': self.id_jogador_votado,
            'tipo_voto': self.tipo_voto,
            'data_voto': self.data_voto.isoformat() if self.data_voto else None
        }
    
    def __repr__(self):
        return f'<Voto {self.tipo_voto} - Partida {self.id_partida}>'


