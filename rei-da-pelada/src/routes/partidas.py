from flask import Blueprint, request, jsonify, session
from src.models.user import db, User, Pelada, MembroPelada, Partida, PresencaPartida, EstatisticaJogadorPartida, AvaliacaoPartida
from datetime import datetime, date, time
from sqlalchemy import func

partidas_bp = Blueprint('partidas', __name__)

@partidas_bp.route('/create', methods=['POST'])
def create_partida():
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ('pelada_id', 'data_partida', 'hora_inicio')):
            return jsonify({'error': 'Dados incompletos'}), 400
        
        pelada_id = data['pelada_id']
        
        # Verificar se o usuário é admin da pelada
        membro = MembroPelada.query.filter_by(usuario_id=session['user_id'], pelada_id=pelada_id).first()
        if not membro or not membro.is_admin:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Converter strings para objetos date e time
        data_partida = datetime.strptime(data['data_partida'], '%Y-%m-%d').date()
        hora_inicio = datetime.strptime(data['hora_inicio'], '%H:%M').time()
        hora_fim = None
        if data.get('hora_fim'):
            hora_fim = datetime.strptime(data['hora_fim'], '%H:%M').time()
        
        # Criar nova partida
        partida = Partida(
            pelada_id=pelada_id,
            data_partida=data_partida,
            hora_inicio=hora_inicio,
            hora_fim=hora_fim
        )
        
        db.session.add(partida)
        db.session.flush()
        
        # Criar presenças pendentes para todos os membros da pelada
        membros = MembroPelada.query.filter_by(pelada_id=pelada_id).all()
        for membro in membros:
            presenca = PresencaPartida(
                partida_id=partida.id,
                usuario_id=membro.usuario_id
            )
            db.session.add(presenca)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Partida criada com sucesso',
            'partida': partida.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@partidas_bp.route('/pelada/<pelada_id>', methods=['GET'])
def get_partidas_pelada(pelada_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        # Verificar se o usuário é membro da pelada
        membro = MembroPelada.query.filter_by(usuario_id=session['user_id'], pelada_id=pelada_id).first()
        if not membro:
            return jsonify({'error': 'Acesso negado'}), 403
        
        partidas = Partida.query.filter_by(pelada_id=pelada_id).order_by(Partida.data_partida.desc()).all()
        
        partidas_list = []
        for partida in partidas:
            partida_dict = partida.to_dict()
            
            # Contar presenças confirmadas
            confirmados = PresencaPartida.query.filter_by(partida_id=partida.id, confirmacao='confirmado').count()
            nao_confirmados = PresencaPartida.query.filter_by(partida_id=partida.id, confirmacao='nao_confirmado').count()
            pendentes = PresencaPartida.query.filter_by(partida_id=partida.id, confirmacao='pendente').count()
            
            partida_dict['confirmados'] = confirmados
            partida_dict['nao_confirmados'] = nao_confirmados
            partida_dict['pendentes'] = pendentes
            
            partidas_list.append(partida_dict)
        
        return jsonify({'partidas': partidas_list}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@partidas_bp.route('/<partida_id>', methods=['GET'])
def get_partida_details(partida_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        partida = Partida.query.get(partida_id)
        if not partida:
            return jsonify({'error': 'Partida não encontrada'}), 404
        
        # Verificar se o usuário é membro da pelada
        membro = MembroPelada.query.filter_by(usuario_id=session['user_id'], pelada_id=partida.pelada_id).first()
        if not membro:
            return jsonify({'error': 'Acesso negado'}), 403
        
        partida_dict = partida.to_dict()
        partida_dict['is_admin'] = membro.is_admin
        
        # Buscar presenças
        presencas = PresencaPartida.query.filter_by(partida_id=partida_id).all()
        presencas_list = []
        
        for presenca in presencas:
            usuario = User.query.get(presenca.usuario_id)
            if usuario:
                presenca_dict = presenca.to_dict()
                presenca_dict['usuario'] = usuario.to_dict()
                presencas_list.append(presenca_dict)
        
        partida_dict['presencas'] = presencas_list
        
        # Se a partida estiver finalizada, buscar estatísticas
        if partida.status in ['finalizada', 'avaliacao', 'concluida']:
            estatisticas = EstatisticaJogadorPartida.query.filter_by(partida_id=partida_id).all()
            estatisticas_list = []
            
            for estatistica in estatisticas:
                usuario = User.query.get(estatistica.usuario_id)
                if usuario:
                    estatistica_dict = estatistica.to_dict()
                    estatistica_dict['usuario'] = usuario.to_dict()
                    estatisticas_list.append(estatistica_dict)
            
            partida_dict['estatisticas'] = estatisticas_list
        
        return jsonify({'partida': partida_dict}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@partidas_bp.route('/<partida_id>/confirm-presence', methods=['POST'])
def confirm_presence(partida_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        data = request.get_json()
        confirmacao = data.get('confirmacao', 'confirmado')  # confirmado, nao_confirmado
        
        presenca = PresencaPartida.query.filter_by(partida_id=partida_id, usuario_id=session['user_id']).first()
        if not presenca:
            return jsonify({'error': 'Presença não encontrada'}), 404
        
        presenca.confirmacao = confirmacao
        presenca.data_confirmacao = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Presença confirmada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@partidas_bp.route('/<partida_id>/update-presence', methods=['POST'])
def update_presence(partida_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ('usuario_id', 'confirmacao')):
            return jsonify({'error': 'Dados incompletos'}), 400
        
        partida = Partida.query.get(partida_id)
        if not partida:
            return jsonify({'error': 'Partida não encontrada'}), 404
        
        # Verificar se o usuário é admin da pelada
        membro = MembroPelada.query.filter_by(usuario_id=session['user_id'], pelada_id=partida.pelada_id).first()
        if not membro or not membro.is_admin:
            return jsonify({'error': 'Acesso negado'}), 403
        
        presenca = PresencaPartida.query.filter_by(partida_id=partida_id, usuario_id=data['usuario_id']).first()
        if not presenca:
            return jsonify({'error': 'Presença não encontrada'}), 404
        
        presenca.confirmacao = data['confirmacao']
        presenca.data_confirmacao = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'message': 'Presença atualizada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@partidas_bp.route('/<partida_id>/add-statistics', methods=['POST'])
def add_statistics(partida_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        data = request.get_json()
        
        if not data or 'estatisticas' not in data:
            return jsonify({'error': 'Dados incompletos'}), 400
        
        partida = Partida.query.get(partida_id)
        if not partida:
            return jsonify({'error': 'Partida não encontrada'}), 404
        
        # Verificar se o usuário é admin da pelada
        membro = MembroPelada.query.filter_by(usuario_id=session['user_id'], pelada_id=partida.pelada_id).first()
        if not membro or not membro.is_admin:
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Adicionar/atualizar estatísticas
        for stat_data in data['estatisticas']:
            estatistica = EstatisticaJogadorPartida.query.filter_by(
                partida_id=partida_id,
                usuario_id=stat_data['usuario_id']
            ).first()
            
            if not estatistica:
                estatistica = EstatisticaJogadorPartida(
                    partida_id=partida_id,
                    usuario_id=stat_data['usuario_id']
                )
                db.session.add(estatistica)
            
            estatistica.gols = stat_data.get('gols', 0)
            estatistica.assistencias = stat_data.get('assistencias', 0)
            estatistica.defesas = stat_data.get('defesas', 0)
            estatistica.gols_sofridos = stat_data.get('gols_sofridos', 0)
            estatistica.desarmes = stat_data.get('desarmes', 0)
            
            # Calcular pontuação básica (sem votos ainda)
            estatistica.calcular_pontuacao()
        
        # Atualizar status da partida
        partida.status = 'avaliacao'
        
        db.session.commit()
        
        return jsonify({'message': 'Estatísticas adicionadas com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@partidas_bp.route('/<partida_id>/vote', methods=['POST'])
def vote_partida(partida_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        data = request.get_json()
        
        if not data or not all(k in data for k in ('mvp_id', 'bola_murcha_id')):
            return jsonify({'error': 'Dados incompletos'}), 400
        
        partida = Partida.query.get(partida_id)
        if not partida:
            return jsonify({'error': 'Partida não encontrada'}), 404
        
        if partida.status != 'avaliacao':
            return jsonify({'error': 'Partida não está em período de avaliação'}), 400
        
        # Verificar se o usuário confirmou presença
        presenca = PresencaPartida.query.filter_by(
            partida_id=partida_id,
            usuario_id=session['user_id'],
            confirmacao='confirmado'
        ).first()
        
        if not presenca:
            return jsonify({'error': 'Apenas jogadores que confirmaram presença podem votar'}), 403
        
        # Verificar se já votou
        voto_existente = AvaliacaoPartida.query.filter_by(
            partida_id=partida_id,
            avaliador_id=session['user_id']
        ).first()
        
        if voto_existente:
            return jsonify({'error': 'Você já votou nesta partida'}), 400
        
        # Adicionar votos
        voto_mvp = AvaliacaoPartida(
            partida_id=partida_id,
            avaliador_id=session['user_id'],
            avaliado_id=data['mvp_id'],
            tipo_avaliacao='mvp'
        )
        
        voto_bola_murcha = AvaliacaoPartida(
            partida_id=partida_id,
            avaliador_id=session['user_id'],
            avaliado_id=data['bola_murcha_id'],
            tipo_avaliacao='bola_murcha'
        )
        
        db.session.add(voto_mvp)
        db.session.add(voto_bola_murcha)
        db.session.commit()
        
        return jsonify({'message': 'Voto registrado com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@partidas_bp.route('/<partida_id>/finalize', methods=['POST'])
def finalize_partida(partida_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        partida = Partida.query.get(partida_id)
        if not partida:
            return jsonify({'error': 'Partida não encontrada'}), 404
        
        # Verificar se o usuário é admin da pelada
        membro = MembroPelada.query.filter_by(usuario_id=session['user_id'], pelada_id=partida.pelada_id).first()
        if not membro or not membro.is_admin:
            return jsonify({'error': 'Acesso negado'}), 403
        
        if partida.status != 'avaliacao':
            return jsonify({'error': 'Partida não está em período de avaliação'}), 400
        
        # Calcular votos e atualizar pontuações
        estatisticas = EstatisticaJogadorPartida.query.filter_by(partida_id=partida_id).all()
        
        for estatistica in estatisticas:
            # Contar votos MVP
            votos_mvp = AvaliacaoPartida.query.filter_by(
                partida_id=partida_id,
                avaliado_id=estatistica.usuario_id,
                tipo_avaliacao='mvp'
            ).count()
            
            # Contar votos Bola Murcha
            votos_bola_murcha = AvaliacaoPartida.query.filter_by(
                partida_id=partida_id,
                avaliado_id=estatistica.usuario_id,
                tipo_avaliacao='bola_murcha'
            ).count()
            
            # Verificar se o jogador votou
            votou = AvaliacaoPartida.query.filter_by(
                partida_id=partida_id,
                avaliador_id=estatistica.usuario_id
            ).first() is not None
            
            # Recalcular pontuação com votos
            estatistica.calcular_pontuacao(votos_mvp, votos_bola_murcha, not votou)
        
        # Determinar MVP e Bola Murcha
        mvp_stat = max(estatisticas, key=lambda x: x.pontuacao_total)
        bola_murcha_stat = min(estatisticas, key=lambda x: x.pontuacao_total)
        
        partida.mvp_id = mvp_stat.usuario_id
        partida.bola_murcha_id = bola_murcha_stat.usuario_id
        partida.status = 'concluida'
        
        db.session.commit()
        
        return jsonify({'message': 'Partida finalizada com sucesso'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@partidas_bp.route('/<partida_id>/ranking', methods=['GET'])
def get_partida_ranking(partida_id):
    if 'user_id' not in session:
        return jsonify({'error': 'Usuário não autenticado'}), 401
    
    try:
        partida = Partida.query.get(partida_id)
        if not partida:
            return jsonify({'error': 'Partida não encontrada'}), 404
        
        # Verificar se o usuário é membro da pelada
        membro = MembroPelada.query.filter_by(usuario_id=session['user_id'], pelada_id=partida.pelada_id).first()
        if not membro:
            return jsonify({'error': 'Acesso negado'}), 403
        
        if partida.status != 'concluida':
            return jsonify({'error': 'Partida ainda não foi finalizada'}), 400
        
        # Buscar estatísticas ordenadas por pontuação
        estatisticas = EstatisticaJogadorPartida.query.filter_by(partida_id=partida_id).order_by(
            EstatisticaJogadorPartida.pontuacao_total.desc()
        ).all()
        
        ranking = []
        artilheiro = None
        garcom = None
        xerife = None
        paredao = None
        
        max_gols = 0
        max_assistencias = 0
        max_desarmes = 0
        max_pontos_goleiro = 0
        
        for i, estatistica in enumerate(estatisticas):
            usuario = User.query.get(estatistica.usuario_id)
            if usuario:
                estatistica_dict = estatistica.to_dict()
                estatistica_dict['usuario'] = usuario.to_dict()
                estatistica_dict['posicao'] = i + 1
                ranking.append(estatistica_dict)
                
                # Determinar destaques
                if estatistica.gols > max_gols:
                    max_gols = estatistica.gols
                    artilheiro = estatistica_dict
                
                if estatistica.assistencias > max_assistencias:
                    max_assistencias = estatistica.assistencias
                    garcom = estatistica_dict
                
                if estatistica.desarmes > max_desarmes:
                    max_desarmes = estatistica.desarmes
                    xerife = estatistica_dict
                
                if usuario.posicao == 'Goleiro' and estatistica.pontuacao_total > max_pontos_goleiro:
                    max_pontos_goleiro = estatistica.pontuacao_total
                    paredao = estatistica_dict
        
        # MVP e Bola Murcha
        mvp = ranking[0] if ranking else None
        bola_murcha = ranking[-1] if ranking else None
        
        return jsonify({
            'ranking': ranking,
            'destaques': {
                'artilheiro': artilheiro,
                'garcom': garcom,
                'xerife': xerife,
                'paredao': paredao,
                'mvp': mvp,
                'bola_murcha': bola_murcha
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

