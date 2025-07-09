from flask import Blueprint, request, jsonify, session
from src.models.user import db, User, Pelada, MembroPelada, EstatisticaJogadorPartida, Partida
from sqlalchemy import func, extract
from datetime import datetime, timedelta

ranking_bp = Blueprint('ranking', __name__)

@ranking_bp.route('/geral', methods=['GET'])
def get_ranking_geral():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        # Calcular estatísticas gerais de todos os usuários
        ranking_query = db.session.query(
            User.id,
            User.nome,
            User.posicao,
            func.count(EstatisticaJogadorPartida.partida_id).label('total_partidas'),
            func.sum(EstatisticaJogadorPartida.gols).label('total_gols'),
            func.sum(EstatisticaJogadorPartida.assistencias).label('total_assistencias'),
            func.sum(EstatisticaJogadorPartida.defesas).label('total_defesas'),
            func.sum(EstatisticaJogadorPartida.gols_sofridos).label('total_gols_sofridos'),
            func.sum(EstatisticaJogadorPartida.desarmes).label('total_desarmes'),
            func.avg(EstatisticaJogadorPartida.pontuacao_total).label('media_pontos')
        ).join(
            EstatisticaJogadorPartida, User.id == EstatisticaJogadorPartida.usuario_id
        ).join(
            Partida, EstatisticaJogadorPartida.partida_id == Partida.id
        ).filter(
            Partida.status == 'concluida'
        ).group_by(
            User.id
        ).having(
            func.count(EstatisticaJogadorPartida.partida_id) > 0
        ).order_by(
            func.avg(EstatisticaJogadorPartida.pontuacao_total).desc()
        ).all()
        
        ranking = []
        user_position = None
        
        for i, row in enumerate(ranking_query):
            # Buscar uma pelada principal do usuário (primeira que encontrar)
            membro = MembroPelada.query.filter_by(usuario_id=row.id).first()
            pelada_nome = None
            if membro:
                pelada = Pelada.query.get(membro.pelada_id)
                pelada_nome = pelada.nome if pelada else 'Sem pelada'
            
            jogador = {
                'posicao': i + 1,
                'usuario_id': row.id,
                'nome': row.nome,
                'posicao_campo': row.posicao,
                'pelada': pelada_nome,
                'total_partidas': row.total_partidas or 0,
                'total_gols': row.total_gols or 0,
                'total_assistencias': row.total_assistencias or 0,
                'total_defesas': row.total_defesas or 0,
                'total_gols_sofridos': row.total_gols_sofridos or 0,
                'total_desarmes': row.total_desarmes or 0,
                'media_pontos': round(float(row.media_pontos or 0), 2)
            }
            
            ranking.append(jogador)
            
            # Verificar se é o usuário logado
            if row.id == session['user_id']:
                user_position = jogador
        
        # Se o usuário não estiver no top 10, adicionar sua posição
        top_10 = ranking[:10]
        if user_position and user_position['posicao'] > 10:
            top_10.append(user_position)
        
        return jsonify({'ranking': top_10}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ranking_bp.route('/pelada/<pelada_id>', methods=['GET'])
def get_ranking_pelada(pelada_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        # Verificar se o usuário é membro da pelada
        membro = MembroPelada.query.filter_by(usuario_id=session['user_id'], pelada_id=pelada_id).first()
        if not membro:
            return jsonify({'error': 'Acesso negado'}), 403
        
        tipo = request.args.get('tipo', 'geral')  # geral, ano, mes
        ano = request.args.get('ano', datetime.now().year)
        
        # Base query
        query = db.session.query(
            User.id,
            User.nome,
            User.posicao,
            func.count(EstatisticaJogadorPartida.partida_id).label('total_partidas'),
            func.sum(EstatisticaJogadorPartida.gols).label('total_gols'),
            func.sum(EstatisticaJogadorPartida.assistencias).label('total_assistencias'),
            func.sum(EstatisticaJogadorPartida.defesas).label('total_defesas'),
            func.sum(EstatisticaJogadorPartida.gols_sofridos).label('total_gols_sofridos'),
            func.sum(EstatisticaJogadorPartida.desarmes).label('total_desarmes'),
            func.avg(EstatisticaJogadorPartida.pontuacao_total).label('media_pontos')
        ).join(
            EstatisticaJogadorPartida, User.id == EstatisticaJogadorPartida.usuario_id
        ).join(
            Partida, EstatisticaJogadorPartida.partida_id == Partida.id
        ).filter(
            Partida.pelada_id == pelada_id,
            Partida.status == 'concluida'
        )
        
        # Filtros por período
        if tipo == 'ano':
            query = query.filter(extract('year', Partida.data_partida) == ano)
        elif tipo == 'mes':
            # Último mês
            um_mes_atras = datetime.now() - timedelta(days=30)
            query = query.filter(Partida.data_partida >= um_mes_atras.date())
        
        ranking_query = query.group_by(
            User.id
        ).having(
            func.count(EstatisticaJogadorPartida.partida_id) > 0
        ).order_by(
            func.avg(EstatisticaJogadorPartida.pontuacao_total).desc()
        ).all()
        
        ranking = []
        for i, row in enumerate(ranking_query):
            jogador = {
                'posicao': i + 1,
                'usuario_id': row.id,
                'nome': row.nome,
                'posicao_campo': row.posicao,
                'total_partidas': row.total_partidas or 0,
                'total_gols': row.total_gols or 0,
                'total_assistencias': row.total_assistencias or 0,
                'total_defesas': row.total_defesas or 0,
                'total_gols_sofridos': row.total_gols_sofridos or 0,
                'total_desarmes': row.total_desarmes or 0,
                'media_pontos': round(float(row.media_pontos or 0), 2)
            }
            ranking.append(jogador)
        
        return jsonify({'ranking': ranking}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ranking_bp.route('/pelada/<pelada_id>/anos', methods=['GET'])
def get_anos_pelada(pelada_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        # Verificar se o usuário é membro da pelada
        membro = MembroPelada.query.filter_by(usuario_id=session['user_id'], pelada_id=pelada_id).first()
        if not membro:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Buscar anos com partidas
        anos = db.session.query(
            extract('year', Partida.data_partida).label('ano')
        ).filter(
            Partida.pelada_id == pelada_id,
            Partida.status == 'concluida'
        ).distinct().order_by('ano').all()
        
        anos_list = [int(ano.ano) for ano in anos]
        
        return jsonify({'anos': anos_list}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@ranking_bp.route('/user/<user_id>/stats', methods=['GET'])
def get_user_stats(user_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({'error': 'Usuário não encontrado'}), 404
        
        # Calcular estatísticas gerais do usuário
        stats_query = db.session.query(
            func.count(EstatisticaJogadorPartida.partida_id).label('total_partidas'),
            func.sum(EstatisticaJogadorPartida.gols).label('total_gols'),
            func.sum(EstatisticaJogadorPartida.assistencias).label('total_assistencias'),
            func.sum(EstatisticaJogadorPartida.defesas).label('total_defesas'),
            func.sum(EstatisticaJogadorPartida.gols_sofridos).label('total_gols_sofridos'),
            func.sum(EstatisticaJogadorPartida.desarmes).label('total_desarmes'),
            func.avg(EstatisticaJogadorPartida.pontuacao_total).label('media_pontos')
        ).join(
            Partida, EstatisticaJogadorPartida.partida_id == Partida.id
        ).filter(
            EstatisticaJogadorPartida.usuario_id == user_id,
            Partida.status == 'concluida'
        ).first()
        
        stats = {
            'usuario': user.to_dict(),
            'total_partidas': stats_query.total_partidas or 0,
            'total_gols': stats_query.total_gols or 0,
            'total_assistencias': stats_query.total_assistencias or 0,
            'total_defesas': stats_query.total_defesas or 0,
            'total_gols_sofridos': stats_query.total_gols_sofridos or 0,
            'total_desarmes': stats_query.total_desarmes or 0,
            'media_pontos': round(float(stats_query.media_pontos or 0), 2)
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

