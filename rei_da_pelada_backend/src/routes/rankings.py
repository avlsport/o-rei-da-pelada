from flask import Blueprint, jsonify, request, session
from datetime import datetime, timedelta
from sqlalchemy import func, extract, and_
from src.models.user import User, Pelada, PeladaMember, Match, MatchParticipant, MatchStats, db

rankings_bp = Blueprint('rankings', __name__)

def require_auth():
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])

def require_pelada_member(pelada_id, user_id):
    """Verificar se o usuário é membro aprovado da pelada"""
    return PeladaMember.query.filter_by(user_id=user_id, pelada_id=pelada_id, is_approved=True).first()

@rankings_bp.route('/ranking/global', methods=['GET'])
def get_global_ranking():
    """Ranking geral de todos os jogadores do aplicativo"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    # Calcular estatísticas globais de cada usuário
    global_stats = db.session.query(
        User.id,
        User.name,
        User.position,
        User.photo_url,
        func.count(MatchStats.id).label('total_matches'),
        func.sum(MatchStats.goals).label('total_goals'),
        func.sum(MatchStats.assists).label('total_assists'),
        func.sum(MatchStats.saves).label('total_saves'),
        func.sum(MatchStats.goals_conceded).label('total_goals_conceded'),
        func.sum(MatchStats.tackles).label('total_tackles'),
        func.sum(MatchStats.total_points).label('total_points'),
        func.avg(MatchStats.total_points).label('avg_points')
    ).join(MatchStats).join(Match).filter(
        Match.voting_closed == True
    ).group_by(User.id).having(
        func.count(MatchStats.id) > 0
    ).order_by(func.avg(MatchStats.total_points).desc()).all()
    
    ranking = []
    user_position = None
    
    for i, stats in enumerate(global_stats, 1):
        player_data = {
            'position': i,
            'user_id': stats.id,
            'user_name': stats.name,
            'user_position': stats.position,
            'user_photo_url': stats.photo_url,
            'total_matches': stats.total_matches or 0,
            'total_goals': stats.total_goals or 0,
            'total_assists': stats.total_assists or 0,
            'total_saves': stats.total_saves or 0,
            'total_goals_conceded': stats.total_goals_conceded or 0,
            'total_tackles': stats.total_tackles or 0,
            'total_points': stats.total_points or 0,
            'avg_points': round(float(stats.avg_points), 2) if stats.avg_points else 0
        }
        
        ranking.append(player_data)
        
        # Guardar posição do usuário logado
        if stats.id == user.id:
            user_position = player_data
    
    # Retornar top 10 + posição do usuário se não estiver no top 10
    result = {
        'top_10': ranking[:10],
        'user_position': user_position if user_position and user_position['position'] > 10 else None
    }
    
    return jsonify(result), 200

@rankings_bp.route('/peladas/<int:pelada_id>/ranking', methods=['GET'])
def get_pelada_ranking(pelada_id):
    """Ranking geral de uma pelada específica"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    # Verificar se é membro da pelada
    if not require_pelada_member(pelada_id, user.id):
        return jsonify({'error': 'Acesso negado'}), 403
    
    ranking_type = request.args.get('type', 'general')  # general, yearly, monthly
    year = request.args.get('year', datetime.now().year, type=int)
    
    # Base query
    query = db.session.query(
        User.id,
        User.name,
        User.position,
        User.photo_url,
        func.count(MatchStats.id).label('total_matches'),
        func.sum(MatchStats.goals).label('total_goals'),
        func.sum(MatchStats.assists).label('total_assists'),
        func.sum(MatchStats.saves).label('total_saves'),
        func.sum(MatchStats.goals_conceded).label('total_goals_conceded'),
        func.sum(MatchStats.tackles).label('total_tackles'),
        func.sum(MatchStats.total_points).label('total_points'),
        func.avg(MatchStats.total_points).label('avg_points')
    ).join(MatchStats).join(Match).filter(
        and_(
            Match.pelada_id == pelada_id,
            Match.voting_closed == True
        )
    )
    
    # Filtros por período
    if ranking_type == 'yearly':
        query = query.filter(extract('year', Match.date) == year)
    elif ranking_type == 'monthly':
        # Último mês
        last_month = datetime.now() - timedelta(days=30)
        query = query.filter(Match.date >= last_month.date())
    
    stats = query.group_by(User.id).having(
        func.count(MatchStats.id) > 0
    ).order_by(func.avg(MatchStats.total_points).desc()).all()
    
    ranking = []
    for i, stat in enumerate(stats, 1):
        ranking.append({
            'position': i,
            'user_id': stat.id,
            'user_name': stat.name,
            'user_position': stat.position,
            'user_photo_url': stat.photo_url,
            'total_matches': stat.total_matches or 0,
            'total_goals': stat.total_goals or 0,
            'total_assists': stat.total_assists or 0,
            'total_saves': stat.total_saves or 0,
            'total_goals_conceded': stat.total_goals_conceded or 0,
            'total_tackles': stat.total_tackles or 0,
            'total_points': stat.total_points or 0,
            'avg_points': round(float(stat.avg_points), 2) if stat.avg_points else 0
        })
    
    return jsonify(ranking), 200

@rankings_bp.route('/users/<int:user_id>/stats', methods=['GET'])
def get_user_stats(user_id):
    """Obter estatísticas detalhadas de um usuário"""
    current_user = require_auth()
    if not current_user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    user = User.query.get_or_404(user_id)
    
    # Estatísticas gerais
    general_stats = db.session.query(
        func.count(MatchStats.id).label('total_matches'),
        func.sum(MatchStats.goals).label('total_goals'),
        func.sum(MatchStats.assists).label('total_assists'),
        func.sum(MatchStats.saves).label('total_saves'),
        func.sum(MatchStats.goals_conceded).label('total_goals_conceded'),
        func.sum(MatchStats.tackles).label('total_tackles'),
        func.sum(MatchStats.total_points).label('total_points'),
        func.avg(MatchStats.total_points).label('avg_points')
    ).join(Match).filter(
        and_(
            MatchStats.user_id == user_id,
            Match.voting_closed == True
        )
    ).first()
    
    # Estatísticas por pelada
    pelada_stats = db.session.query(
        Pelada.id,
        Pelada.name,
        func.count(MatchStats.id).label('matches'),
        func.sum(MatchStats.goals).label('goals'),
        func.sum(MatchStats.assists).label('assists'),
        func.sum(MatchStats.saves).label('saves'),
        func.sum(MatchStats.goals_conceded).label('goals_conceded'),
        func.sum(MatchStats.tackles).label('tackles'),
        func.avg(MatchStats.total_points).label('avg_points')
    ).join(Match).join(MatchStats).filter(
        and_(
            MatchStats.user_id == user_id,
            Match.voting_closed == True
        )
    ).group_by(Pelada.id).all()
    
    result = {
        'user': user.to_dict(),
        'general_stats': {
            'total_matches': general_stats.total_matches or 0,
            'total_goals': general_stats.total_goals or 0,
            'total_assists': general_stats.total_assists or 0,
            'total_saves': general_stats.total_saves or 0,
            'total_goals_conceded': general_stats.total_goals_conceded or 0,
            'total_tackles': general_stats.total_tackles or 0,
            'total_points': general_stats.total_points or 0,
            'avg_points': round(float(general_stats.avg_points), 2) if general_stats.avg_points else 0
        },
        'pelada_stats': []
    }
    
    for stats in pelada_stats:
        result['pelada_stats'].append({
            'pelada_id': stats.id,
            'pelada_name': stats.name,
            'matches': stats.matches or 0,
            'goals': stats.goals or 0,
            'assists': stats.assists or 0,
            'saves': stats.saves or 0,
            'goals_conceded': stats.goals_conceded or 0,
            'tackles': stats.tackles or 0,
            'avg_points': round(float(stats.avg_points), 2) if stats.avg_points else 0
        })
    
    return jsonify(result), 200

@rankings_bp.route('/peladas/<int:pelada_id>/years', methods=['GET'])
def get_pelada_years(pelada_id):
    """Obter anos disponíveis para ranking de uma pelada"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    # Verificar se é membro da pelada
    if not require_pelada_member(pelada_id, user.id):
        return jsonify({'error': 'Acesso negado'}), 403
    
    years = db.session.query(
        extract('year', Match.date).label('year')
    ).filter(
        and_(
            Match.pelada_id == pelada_id,
            Match.voting_closed == True
        )
    ).distinct().order_by('year').all()
    
    return jsonify([int(year.year) for year in years]), 200

