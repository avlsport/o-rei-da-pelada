from flask import Blueprint, request, jsonify, session
from src.models.jogador import db, Jogador
from src.models.pelada import Pelada, PagamentoPartida
from src.models.partida import Partida
from datetime import datetime
from sqlalchemy import func

financeiro_bp = Blueprint('financeiro', __name__)

@financeiro_bp.route('/peladas/<int:pelada_id>/financeiro', methods=['GET'])
def get_financeiro_pelada(pelada_id):
    """Buscar dados financeiros da pelada"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Não autenticado'}), 401
        
        # Verificar se o usuário é membro da pelada
        pelada = Pelada.query.get_or_404(pelada_id)
        
        # Buscar resumo financeiro
        total_esperado = db.session.query(func.sum(PagamentoPartida.valor)).filter_by(id_pelada=pelada_id).scalar() or 0
        total_arrecadado = db.session.query(func.sum(PagamentoPartida.valor)).filter_by(id_pelada=pelada_id, pago=True).scalar() or 0
        pagamentos_em_dia = db.session.query(func.count(PagamentoPartida.id)).filter_by(id_pelada=pelada_id, pago=True).scalar() or 0
        inadimplentes = db.session.query(func.count(PagamentoPartida.id)).filter_by(id_pelada=pelada_id, pago=False).scalar() or 0
        
        # Buscar todos os pagamentos
        pagamentos = db.session.query(
            PagamentoPartida,
            Jogador.nome.label('jogador_nome'),
            Partida.data_partida
        ).join(
            Jogador, PagamentoPartida.id_jogador == Jogador.id
        ).join(
            Partida, PagamentoPartida.id_partida == Partida.id
        ).filter(
            PagamentoPartida.id_pelada == pelada_id
        ).order_by(Partida.data_partida.desc()).all()
        
        pagamentos_list = []
        for pagamento, jogador_nome, data_partida in pagamentos:
            pagamento_dict = pagamento.to_dict()
            pagamento_dict['jogador_nome'] = jogador_nome
            pagamento_dict['data_partida'] = data_partida.isoformat() if data_partida else None
            pagamentos_list.append(pagamento_dict)
        
        return jsonify({
            'resumo': {
                'total_esperado': total_esperado,
                'total_arrecadado': total_arrecadado,
                'pagamentos_em_dia': pagamentos_em_dia,
                'inadimplentes': inadimplentes
            },
            'pagamentos': pagamentos_list
        })
        
    except Exception as e:
        print(f"Erro ao buscar financeiro: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

@financeiro_bp.route('/pagamentos/<int:pagamento_id>', methods=['PUT'])
def atualizar_pagamento(pagamento_id):
    """Atualizar status de pagamento"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Não autenticado'}), 401
        
        data = request.get_json()
        pago = data.get('pago', False)
        
        pagamento = PagamentoPartida.query.get_or_404(pagamento_id)
        
        # Verificar se o usuário é o criador da pelada
        pelada = Pelada.query.get(pagamento.id_pelada)
        if pelada.id_criador != session['user_id']:
            return jsonify({'error': 'Sem permissão'}), 403
        
        pagamento.pago = pago
        if pago:
            pagamento.data_pagamento = datetime.utcnow()
        else:
            pagamento.data_pagamento = None
        
        db.session.commit()
        
        return jsonify({'message': 'Pagamento atualizado com sucesso'})
        
    except Exception as e:
        print(f"Erro ao atualizar pagamento: {e}")
        db.session.rollback()
        return jsonify({'error': 'Erro interno do servidor'}), 500

@financeiro_bp.route('/peladas/<int:pelada_id>/relatorio-financeiro', methods=['GET'])
def relatorio_financeiro(pelada_id):
    """Gerar relatório financeiro detalhado"""
    try:
        if 'user_id' not in session:
            return jsonify({'error': 'Não autenticado'}), 401
        
        # Verificar se o usuário é o criador da pelada
        pelada = Pelada.query.get_or_404(pelada_id)
        if pelada.id_criador != session['user_id']:
            return jsonify({'error': 'Sem permissão'}), 403
        
        # Relatório por jogador
        relatorio_jogadores = db.session.query(
            Jogador.nome,
            func.count(PagamentoPartida.id).label('total_partidas'),
            func.sum(PagamentoPartida.valor).label('total_devido'),
            func.sum(func.case([(PagamentoPartida.pago == True, PagamentoPartida.valor)], else_=0)).label('total_pago'),
            func.count(func.case([(PagamentoPartida.pago == True, 1)])).label('partidas_pagas'),
            func.count(func.case([(PagamentoPartida.pago == False, 1)])).label('partidas_pendentes')
        ).join(
            PagamentoPartida, Jogador.id == PagamentoPartida.id_jogador
        ).filter(
            PagamentoPartida.id_pelada == pelada_id
        ).group_by(
            Jogador.id, Jogador.nome
        ).all()
        
        # Relatório por partida
        relatorio_partidas = db.session.query(
            Partida.id,
            Partida.data_partida,
            func.count(PagamentoPartida.id).label('total_jogadores'),
            func.sum(PagamentoPartida.valor).label('total_esperado'),
            func.sum(func.case([(PagamentoPartida.pago == True, PagamentoPartida.valor)], else_=0)).label('total_arrecadado'),
            func.count(func.case([(PagamentoPartida.pago == True, 1)])).label('pagamentos_confirmados')
        ).join(
            PagamentoPartida, Partida.id == PagamentoPartida.id_partida
        ).filter(
            PagamentoPartida.id_pelada == pelada_id
        ).group_by(
            Partida.id, Partida.data_partida
        ).order_by(
            Partida.data_partida.desc()
        ).all()
        
        return jsonify({
            'relatorio_jogadores': [
                {
                    'nome': r.nome,
                    'total_partidas': r.total_partidas,
                    'total_devido': float(r.total_devido or 0),
                    'total_pago': float(r.total_pago or 0),
                    'partidas_pagas': r.partidas_pagas,
                    'partidas_pendentes': r.partidas_pendentes,
                    'percentual_pagamento': round((r.partidas_pagas / r.total_partidas * 100) if r.total_partidas > 0 else 0, 1)
                }
                for r in relatorio_jogadores
            ],
            'relatorio_partidas': [
                {
                    'id_partida': r.id,
                    'data_partida': r.data_partida.isoformat() if r.data_partida else None,
                    'total_jogadores': r.total_jogadores,
                    'total_esperado': float(r.total_esperado or 0),
                    'total_arrecadado': float(r.total_arrecadado or 0),
                    'pagamentos_confirmados': r.pagamentos_confirmados,
                    'percentual_arrecadacao': round((r.total_arrecadado / r.total_esperado * 100) if r.total_esperado > 0 else 0, 1)
                }
                for r in relatorio_partidas
            ]
        })
        
    except Exception as e:
        print(f"Erro ao gerar relatório: {e}")
        return jsonify({'error': 'Erro interno do servidor'}), 500

