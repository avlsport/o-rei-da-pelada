"""
Modelo para Financeiro
"""

class TransacaoFinanceira:
    def __init__(self, id=None, pelada_id=None, tipo=None, descricao=None, valor=0.0,
                 data_transacao=None, responsavel_id=None, categoria=None, created_at=None):
        self.id = id
        self.pelada_id = pelada_id
        self.tipo = tipo  # 'entrada', 'saida'
        self.descricao = descricao
        self.valor = valor
        self.data_transacao = data_transacao
        self.responsavel_id = responsavel_id
        self.categoria = categoria  # 'mensalidade', 'equipamento', 'arbitragem', 'outros'
        self.created_at = created_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'pelada_id': self.pelada_id,
            'tipo': self.tipo,
            'descricao': self.descricao,
            'valor': float(self.valor),
            'data_transacao': self.data_transacao.isoformat() if self.data_transacao else None,
            'responsavel_id': self.responsavel_id,
            'categoria': self.categoria,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

class Mensalidade:
    def __init__(self, id=None, pelada_id=None, jogador_id=None, mes=None, ano=None,
                 valor=0.0, pago=False, data_pagamento=None, observacoes=None, created_at=None):
        self.id = id
        self.pelada_id = pelada_id
        self.jogador_id = jogador_id
        self.mes = mes
        self.ano = ano
        self.valor = valor
        self.pago = pago
        self.data_pagamento = data_pagamento
        self.observacoes = observacoes
        self.created_at = created_at
    
    def to_dict(self):
        return {
            'id': self.id,
            'pelada_id': self.pelada_id,
            'jogador_id': self.jogador_id,
            'mes': self.mes,
            'ano': self.ano,
            'valor': float(self.valor),
            'pago': self.pago,
            'data_pagamento': self.data_pagamento.isoformat() if self.data_pagamento else None,
            'observacoes': self.observacoes,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

