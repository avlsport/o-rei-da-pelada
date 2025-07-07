from src.models.jogador import db
from datetime import datetime

class Voto(db.Model):
    __tablename__ = 'votos'
    
    id = db.Column(db.Integer, primary_key=True)
    id_partida = db.Column(db.Integer, db.ForeignKey('partidas.id'), nullable=False)
    id_jogador_votante = db.Column(db.Integer, db.ForeignKey('jogadores.id'), nullable=False)
    id_jogador_votado = db.Column(db.Integer, db.ForeignKey('jogadores.id'), nullable=False)
    tipo_voto = db.Column(db.String(20), nullable=False)  # 'MVP' ou 'BOLA_MURCHA'
    data_voto = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relacionamentos
    # Removendo backrefs duplicados aqui, eles serão definidos no modelo Jogador
    
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


