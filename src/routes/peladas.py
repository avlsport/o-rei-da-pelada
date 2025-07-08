"""
Rotas para gerenciamento de peladas
"""

from flask import Blueprint, request, jsonify, session
from werkzeug.utils import secure_filename
import psycopg2
from psycopg2.extras import RealDictCursor
import os
import uuid
from datetime import datetime
import logging
from ..database.init_db import get_db_connection

logger = logging.getLogger(__name__)

peladas_bp = Blueprint('peladas', __name__)

def upload_file(file, folder='uploads'):
    """Upload de arquivo"""
    if file and file.filename:
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4()}_{filename}"
        upload_folder = os.path.join('src', 'uploads')
        os.makedirs(upload_folder, exist_ok=True)
        filepath = os.path.join(upload_folder, unique_filename)
        file.save(filepath)
        return f"/uploads/{unique_filename}"
    return None

@peladas_bp.route('/peladas', methods=['GET'])
def get_peladas():
    """Buscar peladas do usuário"""
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Buscar peladas onde o usuário é membro
        cursor.execute('''
            SELECT p.*, j.nome as criador_nome, mp.is_admin, mp.status
            FROM peladas p
            JOIN jogadores j ON p.criador_id = j.id
            JOIN membros_pelada mp ON p.id = mp.pelada_id
            WHERE mp.jogador_id = %s AND mp.status = 'ativo'
            ORDER BY p.created_at DESC
        ''', (jogador_id,))
        
        peladas = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'peladas': [dict(pelada) for pelada in peladas]
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar peladas: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@peladas_bp.route('/peladas', methods=['POST'])
def create_pelada():
    """Criar nova pelada"""
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        logger.debug("=== CRIANDO PELADA ===")
        
        # Verificar se é multipart/form-data ou JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            data = request.form.to_dict()
            foto = request.files.get('foto')
        else:
            data = request.get_json()
            foto = None
        
        nome = data.get('nome')
        local = data.get('local')
        descricao = data.get('descricao', '')
        
        if not nome or not local:
            return jsonify({'success': False, 'message': 'Nome e local são obrigatórios'}), 400
        
        # Upload da foto se fornecida
        foto_url = None
        if foto:
            foto_url = upload_file(foto)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Criar pelada
            cursor.execute('''
                INSERT INTO peladas (nome, local, descricao, foto_url, criador_id)
                VALUES (%s, %s, %s, %s, %s) RETURNING id
            ''', (nome, local, descricao, foto_url, jogador_id))
            
            pelada_id = cursor.fetchone()[0]
            
            # Adicionar criador como admin
            cursor.execute('''
                INSERT INTO membros_pelada (pelada_id, jogador_id, is_admin, status)
                VALUES (%s, %s, %s, %s)
            ''', (pelada_id, jogador_id, True, 'ativo'))
            
            conn.commit()
            
            logger.info(f"✅ Pelada criada com ID: {pelada_id}")
            
            return jsonify({
                'success': True,
                'message': 'Pelada criada com sucesso!',
                'pelada_id': pelada_id
            })
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"❌ Erro ao criar pelada: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@peladas_bp.route('/peladas/search', methods=['GET'])
def search_peladas():
    """Buscar peladas por nome"""
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        nome = request.args.get('nome', '').strip()
        if not nome:
            return jsonify({'success': False, 'message': 'Nome é obrigatório'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Buscar peladas que não são do usuário
        cursor.execute('''
            SELECT p.*, j.nome as criador_nome,
                   CASE WHEN mp.jogador_id IS NOT NULL THEN TRUE ELSE FALSE END as ja_membro,
                   CASE WHEN se.id IS NOT NULL THEN se.status ELSE NULL END as status_solicitacao
            FROM peladas p
            JOIN jogadores j ON p.criador_id = j.id
            LEFT JOIN membros_pelada mp ON p.id = mp.pelada_id AND mp.jogador_id = %s
            LEFT JOIN solicitacoes_entrada se ON p.id = se.pelada_id AND se.jogador_id = %s
            WHERE LOWER(p.nome) LIKE LOWER(%s) AND mp.jogador_id IS NULL
            ORDER BY p.created_at DESC
            LIMIT 20
        ''', (jogador_id, jogador_id, f'%{nome}%'))
        
        peladas = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'peladas': [dict(pelada) for pelada in peladas]
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar peladas: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@peladas_bp.route('/peladas/<int:pelada_id>/solicitar', methods=['POST'])
def solicitar_entrada(pelada_id):
    """Solicitar entrada em uma pelada"""
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        data = request.get_json()
        mensagem = data.get('mensagem', '')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar se já é membro
            cursor.execute('''
                SELECT 1 FROM membros_pelada 
                WHERE pelada_id = %s AND jogador_id = %s
            ''', (pelada_id, jogador_id))
            
            if cursor.fetchone():
                return jsonify({'success': False, 'message': 'Você já é membro desta pelada'}), 400
            
            # Verificar se já tem solicitação pendente
            cursor.execute('''
                SELECT status FROM solicitacoes_entrada 
                WHERE pelada_id = %s AND jogador_id = %s
            ''', (pelada_id, jogador_id))
            
            solicitacao = cursor.fetchone()
            if solicitacao:
                if solicitacao[0] == 'pendente':
                    return jsonify({'success': False, 'message': 'Você já tem uma solicitação pendente'}), 400
                elif solicitacao[0] == 'rejeitada':
                    # Atualizar solicitação rejeitada
                    cursor.execute('''
                        UPDATE solicitacoes_entrada 
                        SET status = 'pendente', mensagem = %s, created_at = CURRENT_TIMESTAMP,
                            respondido_por = NULL, respondido_at = NULL
                        WHERE pelada_id = %s AND jogador_id = %s
                    ''', (mensagem, pelada_id, jogador_id))
                else:
                    return jsonify({'success': False, 'message': 'Solicitação já processada'}), 400
            else:
                # Criar nova solicitação
                cursor.execute('''
                    INSERT INTO solicitacoes_entrada (pelada_id, jogador_id, mensagem)
                    VALUES (%s, %s, %s)
                ''', (pelada_id, jogador_id, mensagem))
            
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': 'Solicitação enviada com sucesso!'
            })
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"❌ Erro ao solicitar entrada: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@peladas_bp.route('/peladas/<int:pelada_id>/solicitacoes', methods=['GET'])
def get_solicitacoes(pelada_id):
    """Buscar solicitações de entrada (apenas admins)"""
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Verificar se é admin da pelada
        cursor.execute('''
            SELECT is_admin FROM membros_pelada 
            WHERE pelada_id = %s AND jogador_id = %s
        ''', (pelada_id, jogador_id))
        
        membro = cursor.fetchone()
        if not membro or not membro['is_admin']:
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        # Buscar solicitações pendentes
        cursor.execute('''
            SELECT se.*, j.nome as jogador_nome, j.posicao, j.foto_url
            FROM solicitacoes_entrada se
            JOIN jogadores j ON se.jogador_id = j.id
            WHERE se.pelada_id = %s AND se.status = 'pendente'
            ORDER BY se.created_at ASC
        ''', (pelada_id,))
        
        solicitacoes = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'solicitacoes': [dict(solicitacao) for solicitacao in solicitacoes]
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar solicitações: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@peladas_bp.route('/peladas/<int:pelada_id>/solicitacoes/<int:solicitacao_id>', methods=['PUT'])
def responder_solicitacao(pelada_id, solicitacao_id):
    """Responder solicitação de entrada (apenas admins)"""
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        data = request.get_json()
        acao = data.get('acao')  # 'aprovar' ou 'rejeitar'
        
        if acao not in ['aprovar', 'rejeitar']:
            return jsonify({'success': False, 'message': 'Ação inválida'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar se é admin da pelada
            cursor.execute('''
                SELECT is_admin FROM membros_pelada 
                WHERE pelada_id = %s AND jogador_id = %s
            ''', (pelada_id, jogador_id))
            
            membro = cursor.fetchone()
            if not membro or not membro[0]:
                return jsonify({'success': False, 'message': 'Acesso negado'}), 403
            
            # Buscar solicitação
            cursor.execute('''
                SELECT jogador_id FROM solicitacoes_entrada 
                WHERE id = %s AND pelada_id = %s AND status = 'pendente'
            ''', (solicitacao_id, pelada_id))
            
            solicitacao = cursor.fetchone()
            if not solicitacao:
                return jsonify({'success': False, 'message': 'Solicitação não encontrada'}), 404
            
            solicitante_id = solicitacao[0]
            
            if acao == 'aprovar':
                # Aprovar solicitação
                cursor.execute('''
                    UPDATE solicitacoes_entrada 
                    SET status = 'aprovada', respondido_por = %s, respondido_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                ''', (jogador_id, solicitacao_id))
                
                # Adicionar como membro
                cursor.execute('''
                    INSERT INTO membros_pelada (pelada_id, jogador_id, is_admin, status)
                    VALUES (%s, %s, %s, %s)
                    ON CONFLICT (pelada_id, jogador_id) DO NOTHING
                ''', (pelada_id, solicitante_id, False, 'ativo'))
                
                message = 'Solicitação aprovada com sucesso!'
            else:
                # Rejeitar solicitação
                cursor.execute('''
                    UPDATE solicitacoes_entrada 
                    SET status = 'rejeitada', respondido_por = %s, respondido_at = CURRENT_TIMESTAMP
                    WHERE id = %s
                ''', (jogador_id, solicitacao_id))
                
                message = 'Solicitação rejeitada'
            
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': message
            })
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"❌ Erro ao responder solicitação: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@peladas_bp.route('/peladas/<int:pelada_id>/membros', methods=['GET'])
def get_membros(pelada_id):
    """Buscar membros da pelada"""
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Verificar se é membro da pelada
        cursor.execute('''
            SELECT 1 FROM membros_pelada 
            WHERE pelada_id = %s AND jogador_id = %s AND status = 'ativo'
        ''', (pelada_id, jogador_id))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        # Buscar membros
        cursor.execute('''
            SELECT j.id, j.nome, j.posicao, j.foto_url, j.pontos_totais, j.media_pontos,
                   mp.is_admin, mp.joined_at
            FROM membros_pelada mp
            JOIN jogadores j ON mp.jogador_id = j.id
            WHERE mp.pelada_id = %s AND mp.status = 'ativo'
            ORDER BY mp.is_admin DESC, mp.joined_at ASC
        ''', (pelada_id,))
        
        membros = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'membros': [dict(membro) for membro in membros]
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar membros: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

