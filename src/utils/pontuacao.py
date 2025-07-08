# Sistema de pontuação da pelada

# Pontuações por estatística
PONTOS_GOL = 8
PONTOS_ASSISTENCIA = 5
PONTOS_DEFESA = 2
PONTOS_DESARME = 1  # NOVO
PONTOS_GOL_SOFRIDO = -1
PONTOS_VOTO_MVP = 3
PONTOS_VOTO_BOLA_MURCHA = -3

def calcular_pontuacao_jogador(estatistica, votos_mvp=0, votos_bola_murcha=0):
    """
    Calcula a pontuação total de um jogador baseado nas estatísticas e votos
    """
    pontuacao = 0
    
    # Pontos por estatísticas
    pontuacao += estatistica.gols * PONTOS_GOL
    pontuacao += estatistica.assistencias * PONTOS_ASSISTENCIA
    pontuacao += estatistica.defesas * PONTOS_DEFESA
    pontuacao += estatistica.desarmes * PONTOS_DESARME  # NOVO
    pontuacao += estatistica.gols_sofridos * PONTOS_GOL_SOFRIDO
    
    # Pontos por votos
    pontuacao += votos_mvp * PONTOS_VOTO_MVP
    pontuacao += votos_bola_murcha * PONTOS_VOTO_BOLA_MURCHA
    
    return pontuacao

def calcular_pontuacao_partida(partida_id, db):
    """
    Calcula e atualiza as pontuações de todos os jogadores de uma partida
    Retorna um resumo com rankings da partida
    """
    from src.models.partida import EstatisticaPartida, Voto
    from src.models.jogador import Jogador
    
    # Obter todas as estatísticas da partida
    estatisticas = EstatisticaPartida.query.filter_by(id_partida=partida_id).all()
    
    # Obter todos os votos da partida
    votos = Voto.query.filter_by(id_partida=partida_id).all()
    
    # Contar votos por jogador
    votos_por_jogador = {}
    for voto in votos:
        jogador_id = voto.id_jogador_votado
        if jogador_id not in votos_por_jogador:
            votos_por_jogador[jogador_id] = {'MVP': 0, 'BOLA_MURCHA': 0}
        votos_por_jogador[jogador_id][voto.tipo_voto] += 1
    
    # Calcular pontuação para cada jogador
    jogadores_pontuacao = []
    
    for estatistica in estatisticas:
        jogador_id = estatistica.id_jogador
        votos_jogador = votos_por_jogador.get(jogador_id, {'MVP': 0, 'BOLA_MURCHA': 0})
        
        # Calcular pontuação total
        pontuacao = calcular_pontuacao_jogador(
            estatistica,
            votos_jogador['MVP'],
            votos_jogador['BOLA_MURCHA']
        )
        
        # Atualizar no banco
        estatistica.pontuacao_calculada = pontuacao
        
        # Obter dados do jogador
        jogador = Jogador.query.get(jogador_id)
        
        jogadores_pontuacao.append({
            'jogador': jogador.to_dict() if jogador else None,
            'estatistica': estatistica.to_dict(),
            'votos_mvp': votos_jogador['MVP'],
            'votos_bola_murcha': votos_jogador['BOLA_MURCHA'],
            'pontuacao_total': pontuacao
        })
    
    db.session.commit()
    
    # Gerar rankings da partida
    rankings = gerar_rankings_partida(jogadores_pontuacao)
    
    return {
        'jogadores': jogadores_pontuacao,
        'rankings': rankings
    }

def gerar_rankings_partida(jogadores_pontuacao):
    """
    Gera os rankings de uma partida específica
    """
    # Ordenar por pontuação (maior para menor)
    por_pontuacao = sorted(jogadores_pontuacao, key=lambda x: x['pontuacao_total'], reverse=True)
    
    # Artilheiro (mais gols)
    artilheiro = max(jogadores_pontuacao, key=lambda x: x['estatistica']['gols'], default=None)
    
    # Garçom/Assistências (mais assistências)
    garcom = max(jogadores_pontuacao, key=lambda x: x['estatistica']['assistencias'], default=None)
    
    # Paredão (mais defesas)
    paredao = max(jogadores_pontuacao, key=lambda x: x['estatistica']['defesas'], default=None)
    
    # Xerifão (mais desarmes) - NOVO
    xerifao = max(jogadores_pontuacao, key=lambda x: x['estatistica']['desarmes'], default=None)
    
    # MVP (mais votos MVP)
    mvp = max(jogadores_pontuacao, key=lambda x: x['votos_mvp'], default=None)
    
    # Bola Murcha (mais votos Bola Murcha)
    bola_murcha = max(jogadores_pontuacao, key=lambda x: x['votos_bola_murcha'], default=None)
    
    return {
        'melhor_jogador': por_pontuacao[0] if por_pontuacao else None,
        'pior_jogador': por_pontuacao[-1] if por_pontuacao else None,
        'artilheiro': artilheiro,
        'garcom': garcom,
        'paredao': paredao,
        'xerifao': xerifao,  # NOVO
        'mvp': mvp,
        'bola_murcha': bola_murcha,
        'ranking_completo': por_pontuacao
    }

def obter_rankings_pelada(pelada_id, db):
    """
    Calcula os rankings gerais de uma pelada (soma de todas as partidas)
    """
    from src.models.partida import Partida, EstatisticaPartida, Voto
    from src.models.jogador import Jogador
    from src.models.pelada import MembroPelada
    
    # Obter todas as partidas finalizadas da pelada
    partidas = Partida.query.filter_by(id_pelada=pelada_id, finalizada=True).all()
    partidas_ids = [p.id for p in partidas]
    
    if not partidas_ids:
        return {
            'total_partidas': 0,
            'rankings': {},
            'jogadores': []
        }
    
    # Obter todas as estatísticas das partidas da pelada
    estatisticas = EstatisticaPartida.query.filter(
        EstatisticaPartida.id_partida.in_(partidas_ids)
    ).all()
    
    # Obter todos os votos das partidas da pelada
    votos = Voto.query.filter(Voto.id_partida.in_(partidas_ids)).all()
    
    # Agrupar estatísticas por jogador
    stats_por_jogador = {}
    for estatistica in estatisticas:
        jogador_id = estatistica.id_jogador
        if jogador_id not in stats_por_jogador:
            stats_por_jogador[jogador_id] = {
                'gols': 0,
                'assistencias': 0,
                'defesas': 0,
                'desarmes': 0,  # NOVO
                'gols_sofridos': 0,
                'pontuacao_total': 0,
                'partidas_jogadas': 0
            }
        
        stats_por_jogador[jogador_id]['gols'] += estatistica.gols
        stats_por_jogador[jogador_id]['assistencias'] += estatistica.assistencias
        stats_por_jogador[jogador_id]['defesas'] += estatistica.defesas
        stats_por_jogador[jogador_id]['desarmes'] += estatistica.desarmes  # NOVO
        stats_por_jogador[jogador_id]['gols_sofridos'] += estatistica.gols_sofridos
        stats_por_jogador[jogador_id]['pontuacao_total'] += estatistica.pontuacao_calculada
        stats_por_jogador[jogador_id]['partidas_jogadas'] += 1
    
    # Contar votos por jogador
    votos_por_jogador = {}
    for voto in votos:
        jogador_id = voto.id_jogador_votado
        if jogador_id not in votos_por_jogador:
            votos_por_jogador[jogador_id] = {'MVP': 0, 'BOLA_MURCHA': 0}
        votos_por_jogador[jogador_id][voto.tipo_voto] += 1
    
    # Obter dados dos jogadores
    jogadores_ids = list(stats_por_jogador.keys())
    jogadores = {j.id: j.to_dict() for j in Jogador.query.filter(Jogador.id.in_(jogadores_ids)).all()}
    
    # Montar dados completos dos jogadores
    jogadores_completos = []
    for jogador_id, stats in stats_por_jogador.items():
        jogador_data = jogadores.get(jogador_id)
        if jogador_data:
            votos_jogador = votos_por_jogador.get(jogador_id, {'MVP': 0, 'BOLA_MURCHA': 0})
            
            jogadores_completos.append({
                'jogador': jogador_data,
                'estatisticas': stats,
                'votos_mvp': votos_jogador['MVP'],
                'votos_bola_murcha': votos_jogador['BOLA_MURCHA'],
                'media_pontos': round(stats['pontuacao_total'] / stats['partidas_jogadas'], 1) if stats['partidas_jogadas'] > 0 else 0
            })
    
    # Gerar rankings
    rankings = {
        'artilheiro': sorted(jogadores_completos, key=lambda x: x['estatisticas']['gols'], reverse=True)[:10],
        'garcom': sorted(jogadores_completos, key=lambda x: x['estatisticas']['assistencias'], reverse=True)[:10],
        'paredao': sorted(jogadores_completos, key=lambda x: x['estatisticas']['defesas'], reverse=True)[:10],
        'xerifao': sorted(jogadores_completos, key=lambda x: x['estatisticas']['desarmes'], reverse=True)[:10],  # NOVO
        'pontuacao': sorted(jogadores_completos, key=lambda x: x['estatisticas']['pontuacao_total'], reverse=True)[:10],
        'media_pontos': sorted(jogadores_completos, key=lambda x: x['media_pontos'], reverse=True)[:10],
        'mvp': sorted(jogadores_completos, key=lambda x: x['votos_mvp'], reverse=True)[:10],
        'bola_murcha': sorted(jogadores_completos, key=lambda x: x['votos_bola_murcha'], reverse=True)[:10]
    }
    
    return {
        'total_partidas': len(partidas),
        'rankings': rankings,
        'jogadores': jogadores_completos
    }

