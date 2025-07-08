from flask import Blueprint, request, jsonify, session
from src.models.jogador import Jogador, db
from src.models.pelada import Pelada, MembroPelada, MovimentacaoFinanceira
from datetime import datetime
from sqlalchemy import func

financeiro_bp = Blueprint('financeiro', __name__)

def require_auth():
    """Verifica se o usuário está autenticado"""
    jogador_id = session.get("jogador_id")
    if not jogador_id:
        return None
    return Jogador.query.get(jogador_id)

def is_admin_pelada(jogador_id, pelada_id):
    """Verifica se o jogador é admin da pelada"""
    membro = MembroPelada.query.filter_by(
        id_jogador=jogador_id, 
        id_pelada=pelada_id, 
        papel='admin'
    ).first()
    return membro is not None

def is_membro_pelada(jogador_id, pelada_id):
    """Verifica se o jogador é membro da pelada"""
    membro = MembroPelada.query.filter_by(
        id_jogador=jogador_id, 
        id_pelada=pelada_id,
        ativo=True
    ).first()
    return membro is not None

# ==================== ROTAS FINANCEIRAS ====================

@financeiro_bp.route("/peladas/<int:pelada_id>/financeiro", methods=["GET"])
def obter_financeiro(pelada_id):
    """Obter movimentações financeiras da pelada"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        if not is_membro_pelada(jogador.id, pelada_id):
            return jsonify({"error": "Acesso negado"}), 403
        
        # Buscar movimentações
        movimentacoes = MovimentacaoFinanceira.query.filter_by(
            id_pelada=pelada_id
        ).order_by(MovimentacaoFinanceira.data_movimentacao.desc()).all()
        
        # Calcular totais
        total_entradas = db.session.query(
            func.sum(MovimentacaoFinanceira.valor)
        ).filter_by(
            id_pelada=pelada_id,
            tipo='entrada'
        ).scalar() or 0
        
        total_saidas = db.session.query(
            func.sum(MovimentacaoFinanceira.valor)
        ).filter_by(
            id_pelada=pelada_id,
            tipo='saida'
        ).scalar() or 0
        
        saldo_atual = total_entradas - total_saidas
        
        resultado = {
            "movimentacoes": [mov.to_dict() for mov in movimentacoes],
            "resumo": {
                "total_entradas": float(total_entradas),
                "total_saidas": float(total_saidas),
                "saldo_atual": float(saldo_atual)
            },
            "is_admin": is_admin_pelada(jogador.id, pelada_id)
        }
        
        return jsonify(resultado), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@financeiro_bp.route("/peladas/<int:pelada_id>/financeiro", methods=["POST"])
def adicionar_movimentacao(pelada_id):
    """Adicionar movimentação financeira (apenas admins)"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        if not is_admin_pelada(jogador.id, pelada_id):
            return jsonify({"error": "Apenas admins podem adicionar movimentações"}), 403
        
        data = request.get_json()
        
        tipo = data.get('tipo')  # 'entrada' ou 'saida'
        descricao = data.get('descricao')
        valor = data.get('valor')
        
        # Validações
        if not tipo or tipo not in ['entrada', 'saida']:
            return jsonify({"error": "Tipo deve ser 'entrada' ou 'saida'"}), 400
        
        if not descricao or not descricao.strip():
            return jsonify({"error": "Descrição é obrigatória"}), 400
        
        if not valor or valor <= 0:
            return jsonify({"error": "Valor deve ser maior que zero"}), 400
        
        # Criar movimentação
        movimentacao = MovimentacaoFinanceira(
            id_pelada=pelada_id,
            tipo=tipo,
            descricao=descricao.strip(),
            valor=float(valor),
            id_admin=jogador.id
        )
        
        db.session.add(movimentacao)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Movimentação adicionada com sucesso",
            "movimentacao": movimentacao.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@financeiro_bp.route("/peladas/<int:pelada_id>/financeiro/<int:movimentacao_id>", methods=["DELETE"])
def excluir_movimentacao(pelada_id, movimentacao_id):
    """Excluir movimentação financeira (apenas admins)"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        if not is_admin_pelada(jogador.id, pelada_id):
            return jsonify({"error": "Apenas admins podem excluir movimentações"}), 403
        
        movimentacao = MovimentacaoFinanceira.query.filter_by(
            id=movimentacao_id,
            id_pelada=pelada_id
        ).first()
        
        if not movimentacao:
            return jsonify({"error": "Movimentação não encontrada"}), 404
        
        db.session.delete(movimentacao)
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": "Movimentação excluída com sucesso"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# ==================== MENSALIDADES ====================

@financeiro_bp.route("/peladas/<int:pelada_id>/mensalidades", methods=["GET"])
def obter_mensalidades(pelada_id):
    """Obter status das mensalidades dos membros"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        if not is_membro_pelada(jogador.id, pelada_id):
            return jsonify({"error": "Acesso negado"}), 403
        
        # Buscar membros ativos
        membros = MembroPelada.query.filter_by(
            id_pelada=pelada_id,
            ativo=True
        ).all()
        
        resultado = []
        for membro in membros:
            resultado.append({
                "id_membro": membro.id,
                "jogador": membro.jogador.to_dict(),
                "mensalidade_paga": membro.mensalidade_paga,
                "data_entrada": membro.data_entrada.isoformat() if membro.data_entrada else None
            })
        
        # Estatísticas
        total_membros = len(membros)
        membros_pagos = len([m for m in membros if m.mensalidade_paga])
        membros_pendentes = total_membros - membros_pagos
        
        return jsonify({
            "membros": resultado,
            "estatisticas": {
                "total_membros": total_membros,
                "membros_pagos": membros_pagos,
                "membros_pendentes": membros_pendentes,
                "percentual_pagos": round((membros_pagos / total_membros * 100) if total_membros > 0 else 0, 1)
            },
            "is_admin": is_admin_pelada(jogador.id, pelada_id)
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@financeiro_bp.route("/peladas/<int:pelada_id>/mensalidades/<int:membro_id>", methods=["PUT"])
def atualizar_mensalidade(pelada_id, membro_id):
    """Atualizar status da mensalidade (apenas admins)"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        if not is_admin_pelada(jogador.id, pelada_id):
            return jsonify({"error": "Apenas admins podem atualizar mensalidades"}), 403
        
        data = request.get_json()
        mensalidade_paga = data.get('mensalidade_paga', False)
        
        membro = MembroPelada.query.filter_by(
            id=membro_id,
            id_pelada=pelada_id
        ).first()
        
        if not membro:
            return jsonify({"error": "Membro não encontrado"}), 404
        
        membro.mensalidade_paga = mensalidade_paga
        db.session.commit()
        
        return jsonify({
            "success": True,
            "message": f"Mensalidade {'marcada como paga' if mensalidade_paga else 'marcada como pendente'}"
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@financeiro_bp.route("/peladas/<int:pelada_id>/mensalidades/marcar-todas", methods=["POST"])
def marcar_todas_mensalidades(pelada_id):
    """Marcar todas as mensalidades como pagas ou pendentes (apenas admins)"""
    try:
        jogador = require_auth()
        if not jogador:
            return jsonify({"error": "Não autenticado"}), 401
        
        if not is_admin_pelada(jogador.id, pelada_id):
            return jsonify({"error": "Apenas admins podem atualizar mensalidades"}), 403
        
        data = request.get_json()
        mensalidade_paga = data.get('mensalidade_paga', False)
        
        # Atualizar todos os membros ativos
        membros = MembroPelada.query.filter_by(
            id_pelada=pelada_id,
            ativo=True
        ).all()
        
        for membro in membros:
            membro.mensalidade_paga = mensalidade_paga
        
        db.session.commit()
        
        status = "pagas" if mensalidade_paga else "pendentes"
        
        return jsonify({
            "success": True,
            "message": f"Todas as mensalidades foram marcadas como {status}",
            "total_atualizados": len(membros)
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

