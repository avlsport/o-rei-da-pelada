from flask import Blueprint, request, jsonify, session
from src.models.partida import Partida, EstatisticaPartida, Voto, db
from src.models.pelada import Pelada, MembroPelada, ConfirmacaoPresenca
from src.models.jogador import Jogador
from src.utils.pontuacao import calcular_pontuacao_partida, obter_rankings_pelada
from datetime import datetime

partidas_bp = Blueprint('partidas', __name__)

def require_auth():
    """Verifica se o usuário está autenticado"""
    jogador_id = session.get('jogador_id')
    if not jogador_id:
        return None
    return Jogador.query.get(jogador_id)

def is_admin_pelada(jogador_id, pelada_id):
    """Verifica se o jogador é admin da pelada"""
    membro = MembroPelada.query.filter_by(id_jogador=jogador_id, id_pelada=pelada_id).first()
    return membro and membro.papel == 'admin'

def is_membro_pelada(jogador_id, pelada_id):
    """Verifica se o jogador é membro da pelada"""
    membro = MembroPelada.query.filter_by(id_jogador=jogador_id, id_pelada=pelada_id).first()
    return membro is not None

@partidas_bp.route('/peladas/<int:pelada_id>/partidas', methods=['POST'])
def criar_partida(pelada_id):
    """Endpoint para criar uma nova partida dentro de uma pelada"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({'error': 'Não autenticado'}), 401
        
        # Verificar se é admin da pelada
        if not is_admin_pelada(jogador.id, pelada_id):
            return jsonify({'error': 'Apenas admins podem criar partidas'}), 403
        
        data = request.get_json()
        
        if not data or not data.get('data') or not data.get('local'):
            return jsonify({'error': 'Data e local são obrigatórios'}), 400
        
        # Criar nova partida
        partida = Partida(
            data=datetime.fromisoformat(data['data']).date(),
            local=data['local'],
            id_criador=jogador.id,
            id_pelada=pelada_id
        )
        
        db.session.add(partida)
        db.session.flush()  # Para obter o ID da partida
        
        # Criar confirmações de presença para todos os membros da pelada
        membros = MembroPelada.query.filter_by(id_pelada=pelada_id).all()
        
        for membro in membros:
            confirmacao = ConfirmacaoPresenca(
                id_partida=partida.id,
                id_jogador=membro.id_jogador,
                status='pendente'
            )
            db.session.add(confirmacao)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Partida criada com sucesso',
            'partida': partida.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@partidas_bp.route('/peladas/<int:pelada_id>/partidas', methods=['GET'])
def listar_partidas(pelada_id):
    """Endpoint para listar partidas de uma pelada"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({'error': 'Não autenticado'}), 401
        
        # Verificar se é membro da pelada
        if not is_membro_pelada(jogador.id, pelada_id):
            return jsonify({'error': 'Acesso negado'}), 403
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        
        partidas = Partida.query.filter_by(id_pelada=pelada_id).order_by(Partida.data.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return jsonify({
            'partidas': [partida.to_dict() for partida in partidas.items],
            'total': partidas.total,
            'pages': partidas.pages,
            'current_page': page
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@partidas_bp.route('/partidas/<int:partida_id>', methods=['GET'])
def obter_partida(partida_id):
    """Endpoint para obter detalhes de uma partida"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({'error': 'Não autenticado'}), 401
        
        partida = Partida.query.get(partida_id)
        
        if not partida:
            return jsonify({'error': 'Partida não encontrada'}), 404
        
        # Verificar se é membro da pelada
        if not is_membro_pelada(jogador.id, partida.id_pelada):
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Obter confirmações de presença
        confirmacoes = ConfirmacaoPresenca.query.filter_by(id_partida=partida_id).all()
        
        # Obter dados dos jogadores
        jogadores_ids = [c.id_jogador for c in confirmacoes]
        jogadores = {j.id: j.to_dict() for j in Jogador.query.filter(Jogador.id.in_(jogadores_ids)).all()}
        
        # Adicionar status de confirmação aos jogadores
        for confirmacao in confirmacoes:
            if confirmacao.id_jogador in jogadores:
                jogadores[confirmacao.id_jogador]['status_presenca'] = confirmacao.status
                jogadores[confirmacao.id_jogador]['data_confirmacao'] = confirmacao.data_confirmacao.isoformat() if confirmacao.data_confirmacao else None
        
        # Obter estatísticas da partida (se finalizada)
        estatisticas = []
        votos = []
        if partida.finalizada:
            estatisticas = EstatisticaPartida.query.filter_by(id_partida=partida_id).all()
            votos = Voto.query.filter_by(id_partida=partida_id).all()
        
        return jsonify({
            'partida': partida.to_dict(),
            'confirmacoes': list(jogadores.values()),
            'estatisticas': [e.to_dict() for e in estatisticas],
            'votos': [v.to_dict() for v in votos],
            'papel_usuario': 'admin' if is_admin_pelada(jogador.id, partida.id_pelada) else 'membro'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@partidas_bp.route('/partidas/<int:partida_id>/confirmar_presenca', methods=['POST'])
def confirmar_presenca(partida_id):
    """Endpoint para confirmar presença em uma partida"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({'error': 'Não autenticado'}), 401
        
        partida = Partida.query.get(partida_id)
        
        if not partida:
            return jsonify({'error': 'Partida não encontrada'}), 404
        
        # Verificar se é membro da pelada
        if not is_membro_pelada(jogador.id, partida.id_pelada):
            return jsonify({'error': 'Acesso negado'}), 403
        
        data = request.get_json()
        status = data.get('status')  # 'confirmado' ou 'recusado'
        
        if status not in ['confirmado', 'recusado']:
            return jsonify({'error': 'Status inválido'}), 400
        
        # Buscar confirmação existente
        confirmacao = ConfirmacaoPresenca.query.filter_by(
            id_partida=partida_id,
            id_jogador=jogador.id
        ).first()
        
        if not confirmacao:
            return jsonify({'error': 'Confirmação não encontrada'}), 404
        
        # Atualizar status
        confirmacao.status = status
        confirmacao.data_confirmacao = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'message': f'Presença {status} com sucesso',
            'confirmacao': confirmacao.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@partidas_bp.route('/partidas/<int:partida_id>/registrar_estatisticas', methods=['POST'])
def registrar_estatisticas(partida_id):
    """Endpoint para registrar estatísticas da partida"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({'error': 'Não autenticado'}), 401
        
        partida = Partida.query.get(partida_id)
        
        if not partida:
            return jsonify({'error': 'Partida não encontrada'}), 404
        
        # Verificar se é admin da pelada
        if not is_admin_pelada(jogador.id, partida.id_pelada):
            return jsonify({'error': 'Apenas admins podem registrar estatísticas'}), 403
        
        data = request.get_json()
        estatisticas_data = data.get('estatisticas', {})
        
        # Obter jogadores que confirmaram presença
        confirmacoes = ConfirmacaoPresenca.query.filter_by(
            id_partida=partida_id,
            status='confirmado'
        ).all()
        
        jogadores_confirmados = [c.id_jogador for c in confirmacoes]
        
        # Registrar estatísticas apenas para jogadores confirmados
        for jogador_id_str, stats in estatisticas_data.items():
            jogador_id = int(jogador_id_str)
            
            if jogador_id not in jogadores_confirmados:
                continue
            
            # Buscar ou criar estatística
            estatistica = EstatisticaPartida.query.filter_by(
                id_partida=partida_id,
                id_jogador=jogador_id
            ).first()
            
            if not estatistica:
                estatistica = EstatisticaPartida(
                    id_partida=partida_id,
                    id_jogador=jogador_id
                )
                db.session.add(estatistica)
            
            # Atualizar estatísticas
            estatistica.gols = stats.get('gols', 0)
            estatistica.assistencias = stats.get('assistencias', 0)
            estatistica.defesas = stats.get('defesas', 0)
            estatistica.gols_sofridos = stats.get('gols_sofridos', 0)
        
        db.session.commit()
        
        return jsonify({
            'message': 'Estatísticas registradas com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@partidas_bp.route('/partidas/<int:partida_id>/votar', methods=['POST'])
def votar(partida_id):
    """Endpoint para votar em MVP/Bola Murcha"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({'error': 'Não autenticado'}), 401
        
        partida = Partida.query.get(partida_id)
        
        if not partida:
            return jsonify({'error': 'Partida não encontrada'}), 404
        
        # Verificar se confirmou presença na partida
        confirmacao = ConfirmacaoPresenca.query.filter_by(
            id_partida=partida_id,
            id_jogador=jogador.id,
            status='confirmado'
        ).first()
        
        if not confirmacao:
            return jsonify({'error': 'Apenas jogadores que confirmaram presença podem votar'}), 403
        
        data = request.get_json()
        tipo_voto = data.get('tipo_voto')  # 'MVP' ou 'BOLA_MURCHA'
        id_jogador_votado = data.get('id_jogador_votado')
        
        if tipo_voto not in ['MVP', 'BOLA_MURCHA']:
            return jsonify({'error': 'Tipo de voto inválido'}), 400
        
        if not id_jogador_votado:
            return jsonify({'error': 'Jogador votado é obrigatório'}), 400
        
        # Verificar se já votou neste tipo
        voto_existente = Voto.query.filter_by(
            id_partida=partida_id,
            id_jogador_votante=jogador.id,
            tipo_voto=tipo_voto
        ).first()
        
        if voto_existente:
            # Atualizar voto existente
            voto_existente.id_jogador_votado = id_jogador_votado
            voto_existente.data_voto = datetime.utcnow()
        else:
            # Criar novo voto
            voto = Voto(
                id_partida=partida_id,
                id_jogador_votante=jogador.id,
                id_jogador_votado=id_jogador_votado,
                tipo_voto=tipo_voto
            )
            db.session.add(voto)
        
        db.session.commit()
        
        return jsonify({
            'message': f'Voto {tipo_voto} registrado com sucesso'
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@partidas_bp.route('/partidas/<int:partida_id>/finalizar', methods=['POST'])
def finalizar_partida(partida_id):
    """Endpoint para finalizar uma partida e calcular pontuações"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({'error': 'Não autenticado'}), 401
        
        partida = Partida.query.get(partida_id)
        
        if not partida:
            return jsonify({'error': 'Partida não encontrada'}), 404
        
        # Verificar se é admin da pelada
        if not is_admin_pelada(jogador.id, partida.id_pelada):
            return jsonify({'error': 'Apenas admins podem finalizar partidas'}), 403
        
        if partida.finalizada:
            return jsonify({'error': 'Partida já foi finalizada'}), 400
        
        # Calcular pontuações
        resumo = calcular_pontuacao_partida(partida_id, db)
        
        # Marcar partida como finalizada
        partida.finalizada = True
        db.session.commit()
        
        return jsonify({
            'message': 'Partida finalizada com sucesso',
            'resumo': resumo
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@partidas_bp.route('/partidas/<int:partida_id>/rankings', methods=['GET'])
def obter_rankings_partida(partida_id):
    """Endpoint para obter rankings de uma partida específica"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({'error': 'Não autenticado'}), 401
        
        partida = Partida.query.get(partida_id)
        
        if not partida:
            return jsonify({'error': 'Partida não encontrada'}), 404
        
        # Verificar se é membro da pelada
        if not is_membro_pelada(jogador.id, partida.id_pelada):
            return jsonify({'error': 'Acesso negado'}), 403
        
        if not partida.finalizada:
            return jsonify({'error': 'Partida ainda não foi finalizada'}), 400
        
        # Calcular rankings da partida
        resumo = calcular_pontuacao_partida(partida_id, db)
        
        return jsonify({'rankings': resumo}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@partidas_bp.route('/peladas/<int:pelada_id>/historico', methods=['GET'])
def obter_historico_pelada(pelada_id):
    """Endpoint para obter histórico geral da pelada"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({'error': 'Não autenticado'}), 401
        
        # Verificar se é membro da pelada
        if not is_membro_pelada(jogador.id, pelada_id):
            return jsonify({'error': 'Acesso negado'}), 403
        
        # Obter rankings gerais da pelada
        rankings = obter_rankings_pelada(pelada_id, db)
        
        return jsonify(rankings), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

