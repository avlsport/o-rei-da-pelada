from datetime import datetime, timedelta
from sqlalchemy import func, extract
from src.models.partida import EstatisticaPartida, Partida
from src.models.pelada import Pelada, MembroPelada
from src.models.jogador import Jogador, db

def calcular_ranking_geral_aplicativo(limit=10, jogador_especifico_id=None):
    """
    Calcula o ranking geral do aplicativo baseado na média de pontos por partida
    """
    # Subquery para calcular estatísticas por jogador
    stats = db.session.query(
        EstatisticaPartida.id_jogador,
        func.sum(EstatisticaPartida.pontos_total).label('total_pontos'),
        func.count(EstatisticaPartida.id).label('total_partidas'),
        (func.sum(EstatisticaPartida.pontos_total) / func.count(EstatisticaPartida.id)).label('media_pontos')
    ).join(
        Partida, EstatisticaPartida.id_partida == Partida.id
    ).filter(
        Partida.finalizada == True
    ).group_by(
        EstatisticaPartida.id_jogador
    ).having(
        func.count(EstatisticaPartida.id) >= 3  # Mínimo 3 partidas para aparecer no ranking
    ).subquery()
    
    # Query principal com informações do jogador
    ranking_query = db.session.query(
        stats.c.id_jogador,
        Jogador.nome,
        Jogador.posicao,
        Jogador.foto_url,
        stats.c.total_pontos,
        stats.c.total_partidas,
        stats.c.media_pontos
    ).join(
        Jogador, stats.c.id_jogador == Jogador.id
    ).order_by(
        stats.c.media_pontos.desc()
    )
    
    # Buscar top 10
    top_10 = ranking_query.limit(limit).all()
    
    resultado = {
        'top_10': [],
        'jogador_especifico': None
    }
    
    # Processar top 10
    for i, jogador in enumerate(top_10, 1):
        jogador_data = {
            'posicao': i,
            'id_jogador': jogador.id_jogador,
            'nome': jogador.nome,
            'posicao_campo': jogador.posicao,
            'foto_url': jogador.foto_url,
            'total_pontos': int(jogador.total_pontos),
            'total_partidas': jogador.total_partidas,
            'media_pontos': round(float(jogador.media_pontos), 2),
            'pelada_principal': obter_pelada_principal(jogador.id_jogador)
        }
        resultado['top_10'].append(jogador_data)
    
    # Se jogador específico não está no top 10, buscar sua posição
    if jogador_especifico_id:
        jogador_no_top = any(j['id_jogador'] == jogador_especifico_id for j in resultado['top_10'])
        
        if not jogador_no_top:
            # Buscar posição do jogador específico
            todos_jogadores = ranking_query.all()
            for i, jogador in enumerate(todos_jogadores, 1):
                if jogador.id_jogador == jogador_especifico_id:
                    resultado['jogador_especifico'] = {
                        'posicao': i,
                        'id_jogador': jogador.id_jogador,
                        'nome': jogador.nome,
                        'posicao_campo': jogador.posicao,
                        'foto_url': jogador.foto_url,
                        'total_pontos': int(jogador.total_pontos),
                        'total_partidas': jogador.total_partidas,
                        'media_pontos': round(float(jogador.media_pontos), 2),
                        'pelada_principal': obter_pelada_principal(jogador.id_jogador)
                    }
                    break
    
    return resultado

def calcular_ranking_pelada(id_pelada, tipo='geral', ano=None):
    """
    Calcula ranking de uma pelada específica
    tipo: 'geral', 'ano', 'ultimo_mes'
    """
    query = db.session.query(
        EstatisticaPartida.id_jogador,
        func.sum(EstatisticaPartida.gols).label('total_gols'),
        func.sum(EstatisticaPartida.assistencias).label('total_assistencias'),
        func.sum(EstatisticaPartida.defesas).label('total_defesas'),
        func.sum(EstatisticaPartida.gols_sofridos).label('total_gols_sofridos'),
        func.sum(EstatisticaPartida.desarmes).label('total_desarmes'),
        func.sum(EstatisticaPartida.pontos_total).label('total_pontos'),
        func.count(EstatisticaPartida.id).label('total_partidas'),
        (func.sum(EstatisticaPartida.pontos_total) / func.count(EstatisticaPartida.id)).label('media_pontos')
    ).join(
        Partida, EstatisticaPartida.id_partida == Partida.id
    ).filter(
        Partida.id_pelada == id_pelada,
        Partida.finalizada == True
    )
    
    # Filtros por período
    if tipo == 'ano' and ano:
        query = query.filter(extract('year', Partida.data_partida) == ano)
    elif tipo == 'ultimo_mes':
        um_mes_atras = datetime.now() - timedelta(days=30)
        query = query.filter(Partida.data_partida >= um_mes_atras)
    
    stats = query.group_by(EstatisticaPartida.id_jogador).subquery()
    
    # Query com informações do jogador
    ranking = db.session.query(
        stats.c.id_jogador,
        Jogador.nome,
        Jogador.posicao,
        Jogador.foto_url,
        stats.c.total_gols,
        stats.c.total_assistencias,
        stats.c.total_defesas,
        stats.c.total_gols_sofridos,
        stats.c.total_desarmes,
        stats.c.total_pontos,
        stats.c.total_partidas,
        stats.c.media_pontos
    ).join(
        Jogador, stats.c.id_jogador == Jogador.id
    ).order_by(
        stats.c.media_pontos.desc()
    ).all()
    
    resultado = []
    for i, jogador in enumerate(ranking, 1):
        resultado.append({
            'posicao': i,
            'id_jogador': jogador.id_jogador,
            'nome': jogador.nome,
            'posicao_campo': jogador.posicao,
            'foto_url': jogador.foto_url,
            'total_gols': jogador.total_gols,
            'total_assistencias': jogador.total_assistencias,
            'total_defesas': jogador.total_defesas,
            'total_gols_sofridos': jogador.total_gols_sofridos,
            'total_desarmes': jogador.total_desarmes,
            'total_pontos': int(jogador.total_pontos),
            'total_partidas': jogador.total_partidas,
            'media_pontos': round(float(jogador.media_pontos), 2)
        })
    
    return resultado

def calcular_destaques_partida(id_partida):
    """
    Calcula os destaques de uma partida específica
    """
    estatisticas = db.session.query(EstatisticaPartida).join(
        Jogador, EstatisticaPartida.id_jogador == Jogador.id
    ).filter(
        EstatisticaPartida.id_partida == id_partida
    ).all()
    
    if not estatisticas:
        return None
    
    # Calcular destaques
    artilheiro = max(estatisticas, key=lambda x: x.gols)
    garcom = max(estatisticas, key=lambda x: x.assistencias)
    xerife = max(estatisticas, key=lambda x: x.desarmes)
    paredao = max([e for e in estatisticas if e.defesas > 0], key=lambda x: x.pontos_total, default=None)
    mvp = max(estatisticas, key=lambda x: x.pontos_total)
    bola_murcha = min(estatisticas, key=lambda x: x.pontos_total)
    
    # Top 3
    top_3 = sorted(estatisticas, key=lambda x: x.pontos_total, reverse=True)[:3]
    
    # Time da rodada (melhor de cada posição)
    goleiro = max([e for e in estatisticas if e.jogador.posicao == 'Goleiro'], 
                  key=lambda x: x.pontos_total, default=None)
    zagueiros = sorted([e for e in estatisticas if e.jogador.posicao == 'Zagueiro'], 
                       key=lambda x: x.pontos_total, reverse=True)[:2]
    meio_campos = sorted([e for e in estatisticas if e.jogador.posicao == 'Meio-campo'], 
                         key=lambda x: x.pontos_total, reverse=True)[:2]
    atacantes = sorted([e for e in estatisticas if e.jogador.posicao == 'Atacante'], 
                       key=lambda x: x.pontos_total, reverse=True)[:1]
    
    return {
        'artilheiro': {
            'jogador': artilheiro.jogador.to_dict(),
            'gols': artilheiro.gols
        } if artilheiro.gols > 0 else None,
        'garcom': {
            'jogador': garcom.jogador.to_dict(),
            'assistencias': garcom.assistencias
        } if garcom.assistencias > 0 else None,
        'xerife': {
            'jogador': xerife.jogador.to_dict(),
            'desarmes': xerife.desarmes
        } if xerife.desarmes > 0 else None,
        'paredao': {
            'jogador': paredao.jogador.to_dict(),
            'defesas': paredao.defesas,
            'pontos': paredao.pontos_total
        } if paredao else None,
        'mvp': {
            'jogador': mvp.jogador.to_dict(),
            'pontos': mvp.pontos_total
        },
        'bola_murcha': {
            'jogador': bola_murcha.jogador.to_dict(),
            'pontos': bola_murcha.pontos_total
        },
        'top_3': [
            {
                'jogador': e.jogador.to_dict(),
                'pontos': e.pontos_total,
                'posicao': i + 1
            } for i, e in enumerate(top_3)
        ],
        'time_da_rodada': {
            'goleiro': goleiro.jogador.to_dict() if goleiro else None,
            'zagueiros': [z.jogador.to_dict() for z in zagueiros],
            'meio_campos': [m.jogador.to_dict() for m in meio_campos],
            'atacantes': [a.jogador.to_dict() for a in atacantes]
        }
    }

def obter_pelada_principal(id_jogador):
    """
    Obtém a pelada principal do jogador (onde ele mais joga)
    """
    pelada = db.session.query(
        Pelada.nome
    ).join(
        MembroPelada, Pelada.id == MembroPelada.id_pelada
    ).join(
        Partida, Pelada.id == Partida.id_pelada
    ).join(
        EstatisticaPartida, Partida.id == EstatisticaPartida.id_partida
    ).filter(
        MembroPelada.id_jogador == id_jogador,
        EstatisticaPartida.id_jogador == id_jogador,
        Partida.finalizada == True
    ).group_by(
        Pelada.id, Pelada.nome
    ).order_by(
        func.count(EstatisticaPartida.id).desc()
    ).first()
    
    return pelada.nome if pelada else "Sem pelada"

