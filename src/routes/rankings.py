"""
Rotas para rankings
"""

from flask import Blueprint, request, jsonify, session
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import logging
from ..database.init_db import get_db_connection

logger = logging.getLogger(__name__)

rankings_bp = Blueprint('rankings', __name__)

@rankings_bp.route('/rankings/geral', methods=['GET'])
def get_ranking_geral():
    """Ranking geral do aplicativo"""
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Top 10 jogadores por média de pontos
        cursor.execute('''
            SELECT j.id, j.nome, j.posicao, j.foto_url, j.pontos_totais, j.partidas_jogadas,
                   j.media_pontos, j.gols_totais, j.assistencias_totais, j.defesas_totais,
                   j.desarmes_totais, j.mvp_count, j.bola_murcha_count,
                   p.nome as pelada_principal
            FROM jogadores j
            LEFT JOIN (
                SELECT mp.jogador_id, p.nome,
                       ROW_NUMBER() OVER (PARTITION BY mp.jogador_id ORDER BY mp.joined_at ASC) as rn
                FROM membros_pelada mp
                JOIN peladas p ON mp.pelada_id = p.id
                WHERE mp.status = 'ativo'
            ) p ON j.id = p.jogador_id AND p.rn = 1
            WHERE j.partidas_jogadas > 0
            ORDER BY j.media_pontos DESC, j.pontos_totais DESC
            LIMIT 10
        ''')
        
        top_10 = cursor.fetchall()
        
        # Posição do usuário atual
        cursor.execute('''
            SELECT COUNT(*) + 1 as posicao
            FROM jogadores 
            WHERE media_pontos > (
                SELECT media_pontos FROM jogadores WHERE id = %s
            ) OR (
                media_pontos = (SELECT media_pontos FROM jogadores WHERE id = %s)
                AND pontos_totais > (SELECT pontos_totais FROM jogadores WHERE id = %s)
            )
        ''', (jogador_id, jogador_id, jogador_id))
        
        posicao_usuario = cursor.fetchone()['posicao']
        
        # Dados do usuário atual
        cursor.execute('''
            SELECT j.id, j.nome, j.posicao, j.foto_url, j.pontos_totais, j.partidas_jogadas,
                   j.media_pontos, j.gols_totais, j.assistencias_totais, j.defesas_totais,
                   j.desarmes_totais, j.mvp_count, j.bola_murcha_count,
                   p.nome as pelada_principal
            FROM jogadores j
            LEFT JOIN (
                SELECT mp.jogador_id, p.nome,
                       ROW_NUMBER() OVER (PARTITION BY mp.jogador_id ORDER BY mp.joined_at ASC) as rn
                FROM membros_pelada mp
                JOIN peladas p ON mp.pelada_id = p.id
                WHERE mp.status = 'ativo'
            ) p ON j.id = p.jogador_id AND p.rn = 1
            WHERE j.id = %s
        ''', (jogador_id,))
        
        usuario_atual = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'ranking': {
                'top_10': [dict(jogador) for jogador in top_10],
                'usuario_atual': dict(usuario_atual) if usuario_atual else None,
                'posicao_usuario': posicao_usuario
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar ranking geral: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@rankings_bp.route('/peladas/<int:pelada_id>/rankings/geral', methods=['GET'])
def get_ranking_pelada_geral(pelada_id):
    """Ranking geral da pelada"""
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
        
        # Ranking da pelada (baseado em estatísticas das partidas desta pelada)
        cursor.execute('''
            SELECT j.id, j.nome, j.posicao, j.foto_url,
                   COALESCE(SUM(ep.pontos_total), 0) as pontos_pelada,
                   COALESCE(SUM(ep.gols), 0) as gols_pelada,
                   COALESCE(SUM(ep.assistencias), 0) as assistencias_pelada,
                   COALESCE(SUM(ep.defesas), 0) as defesas_pelada,
                   COALESCE(SUM(ep.desarmes), 0) as desarmes_pelada,
                   COUNT(DISTINCT p.id) as partidas_pelada,
                   CASE 
                       WHEN COUNT(DISTINCT p.id) > 0 THEN 
                           ROUND(COALESCE(SUM(ep.pontos_total), 0)::decimal / COUNT(DISTINCT p.id), 2)
                       ELSE 0 
                   END as media_pontos_pelada,
                   COALESCE(SUM(CASE WHEN ep.votos_mvp > 0 THEN 1 ELSE 0 END), 0) as mvp_count_pelada,
                   COALESCE(SUM(CASE WHEN ep.votos_bola_murcha > 0 THEN 1 ELSE 0 END), 0) as bola_murcha_count_pelada
            FROM membros_pelada mp
            JOIN jogadores j ON mp.jogador_id = j.id
            LEFT JOIN partidas p ON mp.pelada_id = p.pelada_id AND p.status = 'finalizada'
            LEFT JOIN estatisticas_partida ep ON p.id = ep.partida_id AND j.id = ep.jogador_id
            WHERE mp.pelada_id = %s AND mp.status = 'ativo'
            GROUP BY j.id, j.nome, j.posicao, j.foto_url
            ORDER BY pontos_pelada DESC, media_pontos_pelada DESC
        ''', (pelada_id,))
        
        ranking = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'ranking': [dict(jogador) for jogador in ranking]
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar ranking da pelada: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@rankings_bp.route('/peladas/<int:pelada_id>/rankings/ano/<int:ano>', methods=['GET'])
def get_ranking_pelada_ano(pelada_id, ano):
    """Ranking da pelada por ano"""
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
        
        # Ranking do ano específico
        cursor.execute('''
            SELECT j.id, j.nome, j.posicao, j.foto_url,
                   COALESCE(SUM(ep.pontos_total), 0) as pontos_ano,
                   COALESCE(SUM(ep.gols), 0) as gols_ano,
                   COALESCE(SUM(ep.assistencias), 0) as assistencias_ano,
                   COALESCE(SUM(ep.defesas), 0) as defesas_ano,
                   COALESCE(SUM(ep.desarmes), 0) as desarmes_ano,
                   COUNT(DISTINCT p.id) as partidas_ano,
                   CASE 
                       WHEN COUNT(DISTINCT p.id) > 0 THEN 
                           ROUND(COALESCE(SUM(ep.pontos_total), 0)::decimal / COUNT(DISTINCT p.id), 2)
                       ELSE 0 
                   END as media_pontos_ano
            FROM membros_pelada mp
            JOIN jogadores j ON mp.jogador_id = j.id
            LEFT JOIN partidas p ON mp.pelada_id = p.pelada_id 
                AND p.status = 'finalizada' 
                AND EXTRACT(YEAR FROM p.data_partida) = %s
            LEFT JOIN estatisticas_partida ep ON p.id = ep.partida_id AND j.id = ep.jogador_id
            WHERE mp.pelada_id = %s AND mp.status = 'ativo'
            GROUP BY j.id, j.nome, j.posicao, j.foto_url
            ORDER BY pontos_ano DESC, media_pontos_ano DESC
        ''', (ano, pelada_id))
        
        ranking = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'ranking': [dict(jogador) for jogador in ranking],
            'ano': ano
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar ranking do ano: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@rankings_bp.route('/peladas/<int:pelada_id>/rankings/mes', methods=['GET'])
def get_ranking_pelada_mes(pelada_id):
    """Ranking da pelada do último mês"""
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
        
        # Data de 30 dias atrás
        data_limite = datetime.now() - timedelta(days=30)
        
        # Ranking do último mês
        cursor.execute('''
            SELECT j.id, j.nome, j.posicao, j.foto_url,
                   COALESCE(SUM(ep.pontos_total), 0) as pontos_mes,
                   COALESCE(SUM(ep.gols), 0) as gols_mes,
                   COALESCE(SUM(ep.assistencias), 0) as assistencias_mes,
                   COALESCE(SUM(ep.defesas), 0) as defesas_mes,
                   COALESCE(SUM(ep.desarmes), 0) as desarmes_mes,
                   COUNT(DISTINCT p.id) as partidas_mes,
                   CASE 
                       WHEN COUNT(DISTINCT p.id) > 0 THEN 
                           ROUND(COALESCE(SUM(ep.pontos_total), 0)::decimal / COUNT(DISTINCT p.id), 2)
                       ELSE 0 
                   END as media_pontos_mes
            FROM membros_pelada mp
            JOIN jogadores j ON mp.jogador_id = j.id
            LEFT JOIN partidas p ON mp.pelada_id = p.pelada_id 
                AND p.status = 'finalizada' 
                AND p.data_partida >= %s
            LEFT JOIN estatisticas_partida ep ON p.id = ep.partida_id AND j.id = ep.jogador_id
            WHERE mp.pelada_id = %s AND mp.status = 'ativo'
            GROUP BY j.id, j.nome, j.posicao, j.foto_url
            ORDER BY pontos_mes DESC, media_pontos_mes DESC
        ''', (data_limite.date(), pelada_id))
        
        ranking = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'ranking': [dict(jogador) for jogador in ranking],
            'periodo': 'Últimos 30 dias'
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar ranking do mês: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@rankings_bp.route('/peladas/<int:pelada_id>/destaques', methods=['GET'])
def get_destaques_pelada(pelada_id):
    """Buscar destaques da pelada (Rei, Artilheiro, etc.)"""
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
        
        # Buscar destaques
        cursor.execute('''
            WITH stats_pelada AS (
                SELECT j.id, j.nome, j.foto_url,
                       COALESCE(SUM(ep.pontos_total), 0) as pontos_total,
                       COALESCE(SUM(ep.gols), 0) as gols_total,
                       COALESCE(SUM(ep.assistencias), 0) as assistencias_total,
                       COALESCE(SUM(ep.defesas), 0) as defesas_total,
                       COALESCE(SUM(ep.desarmes), 0) as desarmes_total,
                       COUNT(DISTINCT p.id) as partidas_total
                FROM membros_pelada mp
                JOIN jogadores j ON mp.jogador_id = j.id
                LEFT JOIN partidas p ON mp.pelada_id = p.pelada_id AND p.status = 'finalizada'
                LEFT JOIN estatisticas_partida ep ON p.id = ep.partida_id AND j.id = ep.jogador_id
                WHERE mp.pelada_id = %s AND mp.status = 'ativo'
                GROUP BY j.id, j.nome, j.foto_url
                HAVING COUNT(DISTINCT p.id) > 0
            )
            SELECT 
                (SELECT json_build_object('id', id, 'nome', nome, 'foto_url', foto_url, 'pontos', pontos_total)
                 FROM stats_pelada ORDER BY pontos_total DESC LIMIT 1) as rei,
                (SELECT json_build_object('id', id, 'nome', nome, 'foto_url', foto_url, 'gols', gols_total)
                 FROM stats_pelada ORDER BY gols_total DESC LIMIT 1) as artilheiro,
                (SELECT json_build_object('id', id, 'nome', nome, 'foto_url', foto_url, 'assistencias', assistencias_total)
                 FROM stats_pelada ORDER BY assistencias_total DESC LIMIT 1) as garcom,
                (SELECT json_build_object('id', id, 'nome', nome, 'foto_url', foto_url, 'desarmes', desarmes_total)
                 FROM stats_pelada ORDER BY desarmes_total DESC LIMIT 1) as xerife,
                (SELECT json_build_object('id', id, 'nome', nome, 'foto_url', foto_url, 'defesas', defesas_total)
                 FROM stats_pelada ORDER BY defesas_total DESC LIMIT 1) as paredao
        ''', (pelada_id,))
        
        destaques = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'destaques': dict(destaques) if destaques else {}
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar destaques: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

