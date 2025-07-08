"""
Modelo para Peladas
"""

class Pelada:
    def __init__(self, id=None, nome=None, local=None, descricao=None, foto_url=None, 
                 criador_id=None, created_at=None):
        self.id = id
        self.nome = nome
        self.local = local
        self.descricao = descricao
        self.foto_url = foto_url
        self.criador_id = criador_id
        self.created_at = created_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'local': self.local,
            'descricao': self.descricao,
            'foto_url': self.foto_url,
            'criador_id': self.criador_id,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class MembroPelada:
    def __init__(self, id=None, pelada_id=None, jogador_id=None, is_admin=False, 
                 status='ativo', joined_at=None):
        self.id = id
        self.pelada_id = pelada_id
        self.jogador_id = jogador_id
        self.is_admin = is_admin
        self.status = status  # 'ativo', 'pendente', 'removido'
        self.joined_at = joined_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'pelada_id': self.pelada_id,
            'jogador_id': self.jogador_id,
            'is_admin': self.is_admin,
            'status': self.status,
            'joined_at': self.joined_at.isoformat() if self.joined_at else None
        }

class SolicitacaoEntrada:
    def __init__(self, id=None, pelada_id=None, jogador_id=None, status='pendente',
                 mensagem=None, created_at=None, respondido_por=None, respondido_at=None):
        self.id = id
        self.pelada_id = pelada_id
        self.jogador_id = jogador_id
        self.status = status  # 'pendente', 'aprovada', 'rejeitada'
        self.mensagem = mensagem
        self.created_at = created_at
        self.respondido_por = respondido_por
        self.respondido_at = respondido_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'pelada_id': self.pelada_id,
            'jogador_id': self.jogador_id,
            'status': self.status,
            'mensagem': self.mensagem,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'respondido_por': self.respondido_por,
            'respondido_at': self.respondido_at.isoformat() if self.respondido_at else None
        }

