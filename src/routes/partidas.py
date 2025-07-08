"""
Rotas para gerenciamento de partidas
"""

from flask import Blueprint, request, jsonify, session
import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import logging
from ..database.init_db import get_db_connection

logger = logging.getLogger(__name__)

partidas_bp = Blueprint('partidas', __name__)

@partidas_bp.route('/peladas/<int:pelada_id>/partidas', methods=['GET'])
def get_partidas(pelada_id):
    """Buscar partidas da pelada"""
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
        
        # Buscar partidas
        cursor.execute('''
            SELECT p.*, j.nome as criador_nome,
                   COUNT(cp.id) as total_confirmacoes,
                   COUNT(CASE WHEN cp.confirmado = true THEN 1 END) as confirmados,
                   COUNT(CASE WHEN cp.confirmado = false THEN 1 END) as nao_confirmados,
                   COUNT(CASE WHEN cp.confirmado IS NULL THEN 1 END) as pendentes
            FROM partidas p
            JOIN jogadores j ON p.criado_por = j.id
            LEFT JOIN confirmacoes_partida cp ON p.id = cp.partida_id
            WHERE p.pelada_id = %s
            GROUP BY p.id, j.nome
            ORDER BY p.data_partida DESC, p.horario_inicio DESC
        ''', (pelada_id,))
        
        partidas = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'partidas': [dict(partida) for partida in partidas]
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar partidas: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@partidas_bp.route('/peladas/<int:pelada_id>/partidas', methods=['POST'])
def create_partida(pelada_id):
    """Criar nova partida (apenas admins)"""
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        data = request.get_json()
        data_partida = data.get('data_partida')
        horario_inicio = data.get('horario_inicio')
        horario_fim = data.get('horario_fim')
        local = data.get('local', '')
        
        if not data_partida or not horario_inicio:
            return jsonify({'success': False, 'message': 'Data e horário de início são obrigatórios'}), 400
        
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
                return jsonify({'success': False, 'message': 'Apenas admins podem criar partidas'}), 403
            
            # Criar partida
            cursor.execute('''
                INSERT INTO partidas (pelada_id, data_partida, horario_inicio, horario_fim, local, criado_por)
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
            ''', (pelada_id, data_partida, horario_inicio, horario_fim, local, jogador_id))
            
            partida_id = cursor.fetchone()[0]
            
            # Criar confirmações para todos os membros ativos
            cursor.execute('''
                INSERT INTO confirmacoes_partida (partida_id, jogador_id, confirmado)
                SELECT %s, mp.jogador_id, NULL
                FROM membros_pelada mp
                WHERE mp.pelada_id = %s AND mp.status = 'ativo'
            ''', (partida_id, pelada_id))
            
            conn.commit()
            
            logger.info(f"✅ Partida criada com ID: {partida_id}")
            
            return jsonify({
                'success': True,
                'message': 'Partida criada com sucesso!',
                'partida_id': partida_id
            })
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"❌ Erro ao criar partida: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@partidas_bp.route('/partidas/<int:partida_id>/confirmar', methods=['PUT'])
def confirmar_presenca(partida_id):
    """Confirmar presença na partida"""
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        data = request.get_json()
        confirmado = data.get('confirmado')  # True, False ou None
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar se o jogador pode confirmar presença
            cursor.execute('''
                SELECT cp.id FROM confirmacoes_partida cp
                JOIN partidas p ON cp.partida_id = p.id
                JOIN membros_pelada mp ON p.pelada_id = mp.pelada_id AND cp.jogador_id = mp.jogador_id
                WHERE cp.partida_id = %s AND cp.jogador_id = %s AND mp.status = 'ativo'
            ''', (partida_id, jogador_id))
            
            if not cursor.fetchone():
                return jsonify({'success': False, 'message': 'Você não pode confirmar presença nesta partida'}), 403
            
            # Atualizar confirmação
            cursor.execute('''
                UPDATE confirmacoes_partida 
                SET confirmado = %s, updated_at = CURRENT_TIMESTAMP
                WHERE partida_id = %s AND jogador_id = %s
            ''', (confirmado, partida_id, jogador_id))
            
            conn.commit()
            
            status_msg = 'confirmada' if confirmado else 'recusada' if confirmado is False else 'removida'
            
            return jsonify({
                'success': True,
                'message': f'Presença {status_msg} com sucesso!'
            })
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"❌ Erro ao confirmar presença: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@partidas_bp.route('/partidas/<int:partida_id>/confirmacoes', methods=['GET'])
def get_confirmacoes(partida_id):
    """Buscar confirmações da partida"""
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Verificar se é membro da pelada
        cursor.execute('''
            SELECT 1 FROM confirmacoes_partida cp
            JOIN partidas p ON cp.partida_id = p.id
            JOIN membros_pelada mp ON p.pelada_id = mp.pelada_id AND cp.jogador_id = mp.jogador_id
            WHERE cp.partida_id = %s AND cp.jogador_id = %s AND mp.status = 'ativo'
        ''', (partida_id, jogador_id))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        # Buscar confirmações
        cursor.execute('''
            SELECT cp.*, j.nome, j.posicao, j.foto_url
            FROM confirmacoes_partida cp
            JOIN jogadores j ON cp.jogador_id = j.id
            WHERE cp.partida_id = %s
            ORDER BY 
                CASE 
                    WHEN cp.confirmado = true THEN 1
                    WHEN cp.confirmado = false THEN 3
                    ELSE 2
                END,
                j.nome
        ''', (partida_id,))
        
        confirmacoes = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'confirmacoes': [dict(confirmacao) for confirmacao in confirmacoes]
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar confirmações: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@partidas_bp.route('/partidas/<int:partida_id>/estatisticas', methods=['POST'])
def adicionar_estatisticas(partida_id):
    """Adicionar estatísticas da partida (apenas admins)"""
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        data = request.get_json()
        estatisticas = data.get('estatisticas', [])  # Lista de estatísticas por jogador
        
        if not estatisticas:
            return jsonify({'success': False, 'message': 'Estatísticas são obrigatórias'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar se é admin da pelada
            cursor.execute('''
                SELECT mp.is_admin FROM membros_pelada mp
                JOIN partidas p ON mp.pelada_id = p.pelada_id
                WHERE p.id = %s AND mp.jogador_id = %s
            ''', (partida_id, jogador_id))
            
            membro = cursor.fetchone()
            if not membro or not membro[0]:
                return jsonify({'success': False, 'message': 'Apenas admins podem adicionar estatísticas'}), 403
            
            # Verificar se partida existe e não foi finalizada
            cursor.execute('''
                SELECT status FROM partidas WHERE id = %s
            ''', (partida_id,))
            
            partida = cursor.fetchone()
            if not partida:
                return jsonify({'success': False, 'message': 'Partida não encontrada'}), 404
            
            if partida[0] == 'finalizada':
                return jsonify({'success': False, 'message': 'Partida já foi finalizada'}), 400
            
            # Adicionar estatísticas
            for stat in estatisticas:
                jogador_stat_id = stat.get('jogador_id')
                gols = stat.get('gols', 0)
                assistencias = stat.get('assistencias', 0)
                defesas = stat.get('defesas', 0)
                gols_sofridos = stat.get('gols_sofridos', 0)
                desarmes = stat.get('desarmes', 0)
                
                # Calcular pontos das estatísticas
                pontos_estatisticas = (gols * 8) + (assistencias * 5) + (defesas * 2) - (gols_sofridos * 1) + (desarmes * 1)
                
                # Inserir ou atualizar estatísticas
                cursor.execute('''
                    INSERT INTO estatisticas_partida 
                    (partida_id, jogador_id, gols, assistencias, defesas, gols_sofridos, desarmes, pontos_estatisticas)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (partida_id, jogador_id) 
                    DO UPDATE SET 
                        gols = EXCLUDED.gols,
                        assistencias = EXCLUDED.assistencias,
                        defesas = EXCLUDED.defesas,
                        gols_sofridos = EXCLUDED.gols_sofridos,
                        desarmes = EXCLUDED.desarmes,
                        pontos_estatisticas = EXCLUDED.pontos_estatisticas
                ''', (partida_id, jogador_stat_id, gols, assistencias, defesas, gols_sofridos, desarmes, pontos_estatisticas))
            
            # Atualizar status da partida para permitir votação
            cursor.execute('''
                UPDATE partidas SET status = 'em_votacao' WHERE id = %s
            ''', (partida_id,))
            
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': 'Estatísticas adicionadas com sucesso! Votação iniciada.'
            })
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"❌ Erro ao adicionar estatísticas: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@partidas_bp.route('/partidas/<int:partida_id>/votar', methods=['POST'])
def votar_partida(partida_id):
    """Votar MVP e Bola Murcha da partida"""
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        data = request.get_json()
        mvp_id = data.get('mvp_id')
        bola_murcha_id = data.get('bola_murcha_id')
        
        if not mvp_id or not bola_murcha_id:
            return jsonify({'success': False, 'message': 'MVP e Bola Murcha são obrigatórios'}), 400
        
        if mvp_id == bola_murcha_id:
            return jsonify({'success': False, 'message': 'MVP e Bola Murcha devem ser jogadores diferentes'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar se pode votar (confirmou presença)
            cursor.execute('''
                SELECT cp.confirmado FROM confirmacoes_partida cp
                JOIN partidas p ON cp.partida_id = p.id
                WHERE cp.partida_id = %s AND cp.jogador_id = %s AND cp.confirmado = true
            ''', (partida_id, jogador_id))
            
            if not cursor.fetchone():
                return jsonify({'success': False, 'message': 'Apenas quem confirmou presença pode votar'}), 403
            
            # Verificar se partida está em votação
            cursor.execute('''
                SELECT status FROM partidas WHERE id = %s
            ''', (partida_id,))
            
            partida = cursor.fetchone()
            if not partida or partida[0] != 'em_votacao':
                return jsonify({'success': False, 'message': 'Votação não está disponível'}), 400
            
            # Inserir ou atualizar voto
            cursor.execute('''
                INSERT INTO votacoes_partida (partida_id, votante_id, mvp_id, bola_murcha_id)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (partida_id, votante_id)
                DO UPDATE SET 
                    mvp_id = EXCLUDED.mvp_id,
                    bola_murcha_id = EXCLUDED.bola_murcha_id
            ''', (partida_id, jogador_id, mvp_id, bola_murcha_id))
            
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': 'Voto registrado com sucesso!'
            })
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"❌ Erro ao votar: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@partidas_bp.route('/partidas/<int:partida_id>/finalizar', methods=['POST'])
def finalizar_partida(partida_id):
    """Finalizar partida e calcular resultados (apenas admins)"""
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # Verificar se é admin da pelada
            cursor.execute('''
                SELECT mp.is_admin FROM membros_pelada mp
                JOIN partidas p ON mp.pelada_id = p.pelada_id
                WHERE p.id = %s AND mp.jogador_id = %s
            ''', (partida_id, jogador_id))
            
            membro = cursor.fetchone()
            if not membro or not membro[0]:
                return jsonify({'success': False, 'message': 'Apenas admins podem finalizar partidas'}), 403
            
            # Contar votos
            cursor.execute('''
                SELECT mvp_id, COUNT(*) as votos
                FROM votacoes_partida 
                WHERE partida_id = %s 
                GROUP BY mvp_id
                ORDER BY votos DESC
            ''', (partida_id,))
            votos_mvp = cursor.fetchall()
            
            cursor.execute('''
                SELECT bola_murcha_id, COUNT(*) as votos
                FROM votacoes_partida 
                WHERE partida_id = %s 
                GROUP BY bola_murcha_id
                ORDER BY votos DESC
            ''', (partida_id,))
            votos_bola_murcha = cursor.fetchall()
            
            # Atualizar estatísticas com votos
            for mvp_id, votos in votos_mvp:
                cursor.execute('''
                    UPDATE estatisticas_partida 
                    SET votos_mvp = %s
                    WHERE partida_id = %s AND jogador_id = %s
                ''', (votos, partida_id, mvp_id))
            
            for bola_murcha_id, votos in votos_bola_murcha:
                cursor.execute('''
                    UPDATE estatisticas_partida 
                    SET votos_bola_murcha = %s
                    WHERE partida_id = %s AND jogador_id = %s
                ''', (votos, partida_id, bola_murcha_id))
            
            # Calcular pontos finais
            cursor.execute('''
                UPDATE estatisticas_partida 
                SET pontos_votacao = (votos_mvp * 3) - (votos_bola_murcha * 3),
                    pontos_total = pontos_estatisticas + ((votos_mvp * 3) - (votos_bola_murcha * 3))
                WHERE partida_id = %s
            ''', (partida_id,))
            
            # Penalizar quem não votou (-5 pontos)
            cursor.execute('''
                UPDATE estatisticas_partida 
                SET pontos_total = pontos_total - 5
                WHERE partida_id = %s AND jogador_id NOT IN (
                    SELECT votante_id FROM votacoes_partida WHERE partida_id = %s
                ) AND jogador_id IN (
                    SELECT jogador_id FROM confirmacoes_partida 
                    WHERE partida_id = %s AND confirmado = true
                )
            ''', (partida_id, partida_id, partida_id))
            
            # Atualizar totais dos jogadores
            cursor.execute('''
                UPDATE jogadores 
                SET pontos_totais = pontos_totais + ep.pontos_total,
                    gols_totais = gols_totais + ep.gols,
                    assistencias_totais = assistencias_totais + ep.assistencias,
                    defesas_totais = defesas_totais + ep.defesas,
                    desarmes_totais = desarmes_totais + ep.desarmes,
                    partidas_jogadas = partidas_jogadas + 1,
                    mvp_count = mvp_count + CASE WHEN ep.votos_mvp > 0 THEN 1 ELSE 0 END,
                    bola_murcha_count = bola_murcha_count + CASE WHEN ep.votos_bola_murcha > 0 THEN 1 ELSE 0 END
                FROM estatisticas_partida ep
                WHERE jogadores.id = ep.jogador_id AND ep.partida_id = %s
            ''', (partida_id,))
            
            # Atualizar média de pontos
            cursor.execute('''
                UPDATE jogadores 
                SET media_pontos = CASE 
                    WHEN partidas_jogadas > 0 THEN ROUND(pontos_totais::decimal / partidas_jogadas, 2)
                    ELSE 0 
                END
                WHERE id IN (
                    SELECT jogador_id FROM estatisticas_partida WHERE partida_id = %s
                )
            ''', (partida_id,))
            
            # Finalizar partida
            cursor.execute('''
                UPDATE partidas SET status = 'finalizada' WHERE id = %s
            ''', (partida_id,))
            
            conn.commit()
            
            return jsonify({
                'success': True,
                'message': 'Partida finalizada com sucesso!'
            })
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"❌ Erro ao finalizar partida: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@partidas_bp.route('/partidas/<int:partida_id>/ranking', methods=['GET'])
def get_ranking_partida(partida_id):
    """Buscar ranking da partida"""
    try:
        jogador_id = session.get('jogador_id')
        if not jogador_id:
            return jsonify({'success': False, 'message': 'Não autenticado'}), 401
        
        conn = get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Verificar acesso
        cursor.execute('''
            SELECT 1 FROM confirmacoes_partida cp
            JOIN partidas p ON cp.partida_id = p.id
            JOIN membros_pelada mp ON p.pelada_id = mp.pelada_id AND cp.jogador_id = mp.jogador_id
            WHERE cp.partida_id = %s AND cp.jogador_id = %s AND mp.status = 'ativo'
        ''', (partida_id, jogador_id))
        
        if not cursor.fetchone():
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        # Buscar estatísticas da partida
        cursor.execute('''
            SELECT ep.*, j.nome, j.posicao, j.foto_url
            FROM estatisticas_partida ep
            JOIN jogadores j ON ep.jogador_id = j.id
            WHERE ep.partida_id = %s
            ORDER BY ep.pontos_total DESC
        ''', (partida_id,))
        
        estatisticas = cursor.fetchall()
        
        # Buscar destaques
        cursor.execute('''
            SELECT 
                (SELECT j.nome FROM estatisticas_partida ep JOIN jogadores j ON ep.jogador_id = j.id 
                 WHERE ep.partida_id = %s ORDER BY ep.gols DESC, ep.pontos_total DESC LIMIT 1) as artilheiro,
                (SELECT j.nome FROM estatisticas_partida ep JOIN jogadores j ON ep.jogador_id = j.id 
                 WHERE ep.partida_id = %s ORDER BY ep.assistencias DESC, ep.pontos_total DESC LIMIT 1) as garcom,
                (SELECT j.nome FROM estatisticas_partida ep JOIN jogadores j ON ep.jogador_id = j.id 
                 WHERE ep.partida_id = %s ORDER BY ep.desarmes DESC, ep.pontos_total DESC LIMIT 1) as xerife,
                (SELECT j.nome FROM estatisticas_partida ep JOIN jogadores j ON ep.jogador_id = j.id 
                 WHERE ep.partida_id = %s ORDER BY ep.defesas DESC, ep.pontos_total DESC LIMIT 1) as paredao,
                (SELECT j.nome FROM estatisticas_partida ep JOIN jogadores j ON ep.jogador_id = j.id 
                 WHERE ep.partida_id = %s ORDER BY ep.pontos_total DESC LIMIT 1) as mvp,
                (SELECT j.nome FROM estatisticas_partida ep JOIN jogadores j ON ep.jogador_id = j.id 
                 WHERE ep.partida_id = %s ORDER BY ep.pontos_total ASC LIMIT 1) as bola_murcha
        ''', (partida_id, partida_id, partida_id, partida_id, partida_id, partida_id))
        
        destaques = cursor.fetchone()
        cursor.close()
        conn.close()
        
        return jsonify({
            'success': True,
            'ranking': [dict(stat) for stat in estatisticas],
            'destaques': dict(destaques) if destaques else {}
        })
        
    except Exception as e:
        logger.error(f"❌ Erro ao buscar ranking da partida: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

