"""
Modelo para Partidas
"""

class Partida:
    def __init__(self, id=None, pelada_id=None, data_partida=None, horario_inicio=None,
                 horario_fim=None, local=None, status='agendada', created_at=None,
                 criado_por=None):
        self.id = id
        self.pelada_id = pelada_id
        self.data_partida = data_partida
        self.horario_inicio = horario_inicio
        self.horario_fim = horario_fim
        self.local = local
        self.status = status  # 'agendada', 'em_andamento', 'finalizada', 'cancelada'
        self.created_at = created_at
        self.criado_por = criado_por
    
    def to_dict(self):
        return {
            'id': self.id,
            'pelada_id': self.pelada_id,
            'data_partida': self.data_partida.isoformat() if self.data_partida else None,
            'horario_inicio': str(self.horario_inicio) if self.horario_inicio else None,
            'horario_fim': str(self.horario_fim) if self.horario_fim else None,
            'local': self.local,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'criado_por': self.criado_por
        }

class ConfirmacaoPartida:
    def __init__(self, id=None, partida_id=None, jogador_id=None, confirmado=None,
                 created_at=None, updated_at=None):
        self.id = id
        self.partida_id = partida_id
        self.jogador_id = jogador_id
        self.confirmado = confirmado  # True, False, None (não decidiu)
        self.created_at = created_at
        self.updated_at = updated_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'partida_id': self.partida_id,
            'jogador_id': self.jogador_id,
            'confirmado': self.confirmado,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class EstatisticaPartida:
    def __init__(self, id=None, partida_id=None, jogador_id=None, gols=0, assistencias=0,
                 defesas=0, gols_sofridos=0, desarmes=0, pontos_estatisticas=0,
                 votos_mvp=0, votos_bola_murcha=0, pontos_votacao=0, pontos_total=0,
                 created_at=None):
        self.id = id
        self.partida_id = partida_id
        self.jogador_id = jogador_id
        self.gols = gols
        self.assistencias = assistencias
        self.defesas = defesas
        self.gols_sofridos = gols_sofridos
        self.desarmes = desarmes
        self.pontos_estatisticas = pontos_estatisticas
        self.votos_mvp = votos_mvp
        self.votos_bola_murcha = votos_bola_murcha
        self.pontos_votacao = pontos_votacao
        self.pontos_total = pontos_total
        self.created_at = created_at
    
    def calcular_pontos_estatisticas(self):
        """Calcula pontos baseado nas estatísticas"""
        pontos = 0
        pontos += self.gols * 8  # 8 pontos por gol
        pontos += self.assistencias * 5  # 5 pontos por assistência
        pontos += self.defesas * 2  # 2 pontos por defesa
        pontos -= self.gols_sofridos * 1  # -1 ponto por gol sofrido
        pontos += self.desarmes * 1  # 1 ponto por desarme
        self.pontos_estatisticas = pontos
        return pontos
    
    def calcular_pontos_votacao(self):
        """Calcula pontos baseado nas votações"""
        pontos = 0
        pontos += self.votos_mvp * 3  # 3 pontos por voto MVP
        pontos -= self.votos_bola_murcha * 3  # -3 pontos por voto bola murcha
        self.pontos_votacao = pontos
        return pontos
    
    def calcular_pontos_total(self):
        """Calcula pontuação total"""
        self.calcular_pontos_estatisticas()
        self.calcular_pontos_votacao()
        self.pontos_total = self.pontos_estatisticas + self.pontos_votacao
        return self.pontos_total
    
    def to_dict(self):
        return {
            'id': self.id,
            'partida_id': self.partida_id,
            'jogador_id': self.jogador_id,
            'gols': self.gols,
            'assistencias': self.assistencias,
            'defesas': self.defesas,
            'gols_sofridos': self.gols_sofridos,
            'desarmes': self.desarmes,
            'pontos_estatisticas': self.pontos_estatisticas,
            'votos_mvp': self.votos_mvp,
            'votos_bola_murcha': self.votos_bola_murcha,
            'pontos_votacao': self.pontos_votacao,
            'pontos_total': self.pontos_total,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class VotacaoPartida:
    def __init__(self, id=None, partida_id=None, votante_id=None, mvp_id=None,
                 bola_murcha_id=None, created_at=None):
        self.id = id
        self.partida_id = partida_id
        self.votante_id = votante_id
        self.mvp_id = mvp_id
        self.bola_murcha_id = bola_murcha_id
        self.created_at = created_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'partida_id': self.partida_id,
            'votante_id': self.votante_id,
            'mvp_id': self.mvp_id,
            'bola_murcha_id': self.bola_murcha_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

