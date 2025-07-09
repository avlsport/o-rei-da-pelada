from flask import Blueprint, jsonify, request, session
from datetime import datetime, timedelta, date, time
from sqlalchemy import func, extract
from src.models.user import User, Pelada, PeladaMember, Match, MatchParticipant, MatchStats, Vote, db

matches_bp = Blueprint('matches', __name__)

def require_auth():
    if 'user_id' not in session:
        return None
    return User.query.get(session['user_id'])

def require_pelada_member(pelada_id, user_id):
    """Verificar se o usuário é membro aprovado da pelada"""
    return PeladaMember.query.filter_by(user_id=user_id, pelada_id=pelada_id, is_approved=True).first()

def require_pelada_admin(pelada_id, user_id):
    """Verificar se o usuário é admin da pelada"""
    return PeladaMember.query.filter_by(user_id=user_id, pelada_id=pelada_id, is_admin=True).first()

@matches_bp.route('/peladas/<int:pelada_id>/matches', methods=['GET'])
def get_matches(pelada_id):
    """Obter todas as partidas de uma pelada"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    # Verificar se é membro da pelada
    if not require_pelada_member(pelada_id, user.id):
        return jsonify({'error': 'Acesso negado'}), 403
    
    matches = Match.query.filter_by(pelada_id=pelada_id).order_by(Match.date.desc(), Match.start_time.desc()).all()
    
    result = []
    for match in matches:
        match_dict = match.to_dict()
        
        # Adicionar contagem de participantes
        confirmed_count = MatchParticipant.query.filter_by(match_id=match.id, confirmed=True).count()
        not_confirmed_count = MatchParticipant.query.filter_by(match_id=match.id, confirmed=False).count()
        undecided_count = MatchParticipant.query.filter_by(match_id=match.id, confirmed=None).count()
        
        match_dict['confirmed_count'] = confirmed_count
        match_dict['not_confirmed_count'] = not_confirmed_count
        match_dict['undecided_count'] = undecided_count
        
        # Verificar se o usuário confirmou presença
        user_participation = MatchParticipant.query.filter_by(match_id=match.id, user_id=user.id).first()
        match_dict['user_confirmed'] = user_participation.confirmed if user_participation else None
        
        result.append(match_dict)
    
    return jsonify(result), 200

@matches_bp.route('/peladas/<int:pelada_id>/matches', methods=['POST'])
def create_match(pelada_id):
    """Criar nova partida (apenas para admins)"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    # Verificar se é admin da pelada
    if not require_pelada_admin(pelada_id, user.id):
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        data = request.json
        
        # Validação dos campos obrigatórios
        required_fields = ['date', 'start_time', 'end_time']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'Campo {field} é obrigatório'}), 400
        
        # Converter strings para objetos date e time
        match_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        start_time = datetime.strptime(data['start_time'], '%H:%M').time()
        end_time = datetime.strptime(data['end_time'], '%H:%M').time()
        
        # Criar partida
        match = Match(
            pelada_id=pelada_id,
            date=match_date,
            start_time=start_time,
            end_time=end_time
        )
        
        db.session.add(match)
        db.session.flush()  # Para obter o ID da partida
        
        # Adicionar todos os membros da pelada como participantes
        members = PeladaMember.query.filter_by(pelada_id=pelada_id, is_approved=True).all()
        for member in members:
            participant = MatchParticipant(
                match_id=match.id,
                user_id=member.user_id,
                confirmed=None  # Ainda não decidiu
            )
            db.session.add(participant)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Partida criada com sucesso',
            'match': match.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@matches_bp.route('/matches/<int:match_id>/participants', methods=['GET'])
def get_match_participants(match_id):
    """Obter participantes de uma partida"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    match = Match.query.get_or_404(match_id)
    
    # Verificar se é membro da pelada
    if not require_pelada_member(match.pelada_id, user.id):
        return jsonify({'error': 'Acesso negado'}), 403
    
    participants = MatchParticipant.query.filter_by(match_id=match_id).all()
    
    confirmed = []
    not_confirmed = []
    undecided = []
    
    for participant in participants:
        participant_dict = {
            'id': participant.id,
            'user_id': participant.user_id,
            'user_name': participant.user.name,
            'user_position': participant.user.position,
            'user_photo_url': participant.user.photo_url,
            'confirmed': participant.confirmed,
            'confirmed_at': participant.confirmed_at.isoformat() if participant.confirmed_at else None
        }
        
        if participant.confirmed is True:
            confirmed.append(participant_dict)
        elif participant.confirmed is False:
            not_confirmed.append(participant_dict)
        else:
            undecided.append(participant_dict)
    
    return jsonify({
        'confirmed': confirmed,
        'not_confirmed': not_confirmed,
        'undecided': undecided
    }), 200

@matches_bp.route('/matches/<int:match_id>/confirm', methods=['POST'])
def confirm_participation(match_id):
    """Confirmar/desconfirmar participação em uma partida"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    match = Match.query.get_or_404(match_id)
    
    # Verificar se é membro da pelada
    if not require_pelada_member(match.pelada_id, user.id):
        return jsonify({'error': 'Acesso negado'}), 403
    
    data = request.json
    confirmed = data.get('confirmed')  # True, False ou None
    
    participant = MatchParticipant.query.filter_by(match_id=match_id, user_id=user.id).first()
    if not participant:
        return jsonify({'error': 'Participante não encontrado'}), 404
    
    participant.confirmed = confirmed
    participant.confirmed_at = datetime.utcnow() if confirmed is not None else None
    
    db.session.commit()
    
    return jsonify({'message': 'Participação atualizada com sucesso'}), 200

@matches_bp.route('/matches/<int:match_id>/admin-confirm', methods=['POST'])
def admin_confirm_participation(match_id):
    """Admin confirmar/desconfirmar participação de qualquer jogador"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    match = Match.query.get_or_404(match_id)
    
    # Verificar se é admin da pelada
    if not require_pelada_admin(match.pelada_id, user.id):
        return jsonify({'error': 'Acesso negado'}), 403
    
    data = request.json
    user_id = data.get('user_id')
    confirmed = data.get('confirmed')  # True, False ou None
    
    participant = MatchParticipant.query.filter_by(match_id=match_id, user_id=user_id).first()
    if not participant:
        return jsonify({'error': 'Participante não encontrado'}), 404
    
    participant.confirmed = confirmed
    participant.confirmed_at = datetime.utcnow() if confirmed is not None else None
    
    db.session.commit()
    
    return jsonify({'message': 'Participação atualizada com sucesso'}), 200

@matches_bp.route('/matches/<int:match_id>/stats', methods=['POST'])
def add_match_stats(match_id):
    """Adicionar estatísticas da partida (apenas para admins)"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    match = Match.query.get_or_404(match_id)
    
    # Verificar se é admin da pelada
    if not require_pelada_admin(match.pelada_id, user.id):
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        data = request.json
        stats_list = data.get('stats', [])
        
        # Limpar estatísticas existentes
        MatchStats.query.filter_by(match_id=match_id).delete()
        
        # Adicionar novas estatísticas
        for stat_data in stats_list:
            stats = MatchStats(
                match_id=match_id,
                user_id=stat_data['user_id'],
                goals=stat_data.get('goals', 0),
                assists=stat_data.get('assists', 0),
                saves=stat_data.get('saves', 0),
                goals_conceded=stat_data.get('goals_conceded', 0),
                tackles=stat_data.get('tackles', 0)
            )
            db.session.add(stats)
        
        # Marcar partida como completa e definir prazo de votação
        match.is_completed = True
        match.voting_deadline = datetime.utcnow() + timedelta(hours=6)
        
        db.session.commit()
        
        return jsonify({'message': 'Estatísticas adicionadas com sucesso'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@matches_bp.route('/matches/<int:match_id>/vote', methods=['POST'])
def vote_match(match_id):
    """Votar no MVP e pior jogador da partida"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    match = Match.query.get_or_404(match_id)
    
    # Verificar se é membro da pelada e confirmou presença
    participant = MatchParticipant.query.filter_by(match_id=match_id, user_id=user.id, confirmed=True).first()
    if not participant:
        return jsonify({'error': 'Apenas participantes confirmados podem votar'}), 403
    
    # Verificar se a votação ainda está aberta
    if match.voting_closed or (match.voting_deadline and datetime.utcnow() > match.voting_deadline):
        return jsonify({'error': 'Votação encerrada'}), 400
    
    data = request.json
    mvp_user_id = data.get('mvp_user_id')
    worst_user_id = data.get('worst_user_id')
    
    if not mvp_user_id or not worst_user_id:
        return jsonify({'error': 'MVP e pior jogador são obrigatórios'}), 400
    
    if mvp_user_id == worst_user_id:
        return jsonify({'error': 'MVP e pior jogador não podem ser a mesma pessoa'}), 400
    
    try:
        # Remover votos anteriores do usuário
        Vote.query.filter_by(match_id=match_id, voter_id=user.id).delete()
        
        # Adicionar novos votos
        mvp_vote = Vote(
            match_id=match_id,
            voter_id=user.id,
            voted_user_id=mvp_user_id,
            vote_type='mvp'
        )
        
        worst_vote = Vote(
            match_id=match_id,
            voter_id=user.id,
            voted_user_id=worst_user_id,
            vote_type='worst'
        )
        
        db.session.add(mvp_vote)
        db.session.add(worst_vote)
        db.session.commit()
        
        return jsonify({'message': 'Voto registrado com sucesso'}), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@matches_bp.route('/matches/<int:match_id>/close-voting', methods=['POST'])
def close_voting(match_id):
    """Encerrar votação (apenas para admins)"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    match = Match.query.get_or_404(match_id)
    
    # Verificar se é admin da pelada
    if not require_pelada_admin(match.pelada_id, user.id):
        return jsonify({'error': 'Acesso negado'}), 403
    
    try:
        # Calcular pontuações finais
        participants = MatchParticipant.query.filter_by(match_id=match_id, confirmed=True).all()
        
        for participant in participants:
            stats = MatchStats.query.filter_by(match_id=match_id, user_id=participant.user_id).first()
            if stats:
                # Contar votos
                mvp_votes = Vote.query.filter_by(match_id=match_id, voted_user_id=participant.user_id, vote_type='mvp').count()
                worst_votes = Vote.query.filter_by(match_id=match_id, voted_user_id=participant.user_id, vote_type='worst').count()
                
                # Verificar se o usuário votou
                user_voted = Vote.query.filter_by(match_id=match_id, voter_id=participant.user_id).first() is not None
                
                # Calcular pontos
                stats.calculate_points(mvp_votes, worst_votes, user_voted)
        
        match.voting_closed = True
        db.session.commit()
        
        return jsonify({'message': 'Votação encerrada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@matches_bp.route('/matches/<int:match_id>/ranking', methods=['GET'])
def get_match_ranking(match_id):
    """Obter ranking da partida"""
    user = require_auth()
    if not user:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    match = Match.query.get_or_404(match_id)
    
    # Verificar se é membro da pelada
    if not require_pelada_member(match.pelada_id, user.id):
        return jsonify({'error': 'Acesso negado'}), 403
    
    # Obter estatísticas ordenadas por pontos
    stats = db.session.query(MatchStats, User).join(User).filter(
        MatchStats.match_id == match_id
    ).order_by(MatchStats.total_points.desc()).all()
    
    ranking = []
    for stat, user_obj in stats:
        ranking.append({
            'user_id': user_obj.id,
            'user_name': user_obj.name,
            'user_position': user_obj.position,
            'user_photo_url': user_obj.photo_url,
            'goals': stat.goals,
            'assists': stat.assists,
            'saves': stat.saves,
            'goals_conceded': stat.goals_conceded,
            'tackles': stat.tackles,
            'total_points': stat.total_points
        })
    
    # Calcular títulos especiais
    titles = {}
    if ranking:
        # Artilheiro (mais gols)
        max_goals = max([r['goals'] for r in ranking])
        titles['artilheiro'] = [r for r in ranking if r['goals'] == max_goals][0] if max_goals > 0 else None
        
        # Garçom (mais assistências)
        max_assists = max([r['assists'] for r in ranking])
        titles['garcom'] = [r for r in ranking if r['assists'] == max_assists][0] if max_assists > 0 else None
        
        # Xerife (mais desarmes)
        max_tackles = max([r['tackles'] for r in ranking])
        titles['xerife'] = [r for r in ranking if r['tackles'] == max_tackles][0] if max_tackles > 0 else None
        
        # Paredão (goleiro com mais pontos)
        goalkeepers = [r for r in ranking if r['user_position'] == 'Goleiro']
        titles['paredao'] = goalkeepers[0] if goalkeepers else None
        
        # MVP (mais pontos)
        titles['mvp'] = ranking[0] if ranking else None
        
        # Bola Murcha (menos pontos)
        titles['bola_murcha'] = ranking[-1] if ranking else None
    
    return jsonify({
        'ranking': ranking,
        'titles': titles,
        'podium': ranking[:3] if len(ranking) >= 3 else ranking
    }), 200

