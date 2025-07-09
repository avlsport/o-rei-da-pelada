from flask import Blueprint, request, jsonify, session
import os
from werkzeug.utils import secure_filename
from database.connection_manager import get_db_manager

peladas_bp = Blueprint('peladas', __name__)

def allowed_file(filename):
    """Verifica se o arquivo é permitido"""
    if not filename:
        return True
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@peladas_bp.route('/api/peladas', methods=['GET'])
def get_peladas():
    """Retorna peladas do usuário logado"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Usuário não logado'}), 401
        
        db_manager = get_db_manager()
        user_id = session['user_id']
        
        # Buscar peladas do usuário
        peladas = db_manager.execute_query("""
            SELECT p.id, p.nome, p.descricao, p.local, p.foto_url,
                   COUNT(pm.jogador_id) as total_membros,
                   COUNT(DISTINCT pt.id) as total_partidas
            FROM peladas p
            JOIN pelada_membros pm_user ON p.id = pm_user.pelada_id AND pm_user.jogador_id = ? AND pm_user.ativo = 1
            LEFT JOIN pelada_membros pm ON p.id = pm.pelada_id AND pm.ativo = 1
            LEFT JOIN partidas pt ON p.id = pt.pelada_id
            WHERE p.ativa = 1
            GROUP BY p.id, p.nome, p.descricao, p.local, p.foto_url
            ORDER BY p.data_criacao DESC
        """, (user_id,), fetch_all=True)
        
        peladas_list = []
        for pelada in peladas:
            peladas_list.append({
                'id': pelada['id'],
                'nome': pelada['nome'],
                'descricao': pelada['descricao'],
                'local': pelada['local'],
                'foto_url': pelada['foto_url'],
                'total_membros': pelada['total_membros'],
                'total_partidas': pelada['total_partidas']
            })
        
        return jsonify({
            'success': True,
            'peladas': peladas_list
        })
        
    except Exception as e:
        print(f"Erro ao buscar peladas: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@peladas_bp.route('/api/peladas', methods=['POST'])
def criar_pelada():
    """Cria uma nova pelada"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Usuário não logado'}), 401
        
        db_manager = get_db_manager()
        user_id = session['user_id']
        
        # Dados do formulário
        nome = request.form.get('nome')
        local = request.form.get('local')
        descricao = request.form.get('descricao', '')
        
        # Validações
        if not nome or not local:
            return jsonify({'success': False, 'message': 'Nome e local são obrigatórios'}), 400
        
        # Upload da foto (opcional)
        foto_url = None
        if 'foto' in request.files:
            foto = request.files['foto']
            if foto and foto.filename and allowed_file(foto.filename):
                try:
                    filename = secure_filename(foto.filename)
                    # Criar nome único
                    import time
                    timestamp = str(int(time.time()))
                    filename = f"{timestamp}_{filename}"
                    
                    # Salvar arquivo
                    upload_folder = os.path.join(os.path.dirname(__file__), '..', 'static', 'uploads')
                    os.makedirs(upload_folder, exist_ok=True)
                    file_path = os.path.join(upload_folder, filename)
                    foto.save(file_path)
                    foto_url = f'/static/uploads/{filename}'
                except Exception as e:
                    print(f"Erro ao salvar foto: {e}")
        
        # Criar pelada
        pelada_id = db_manager.execute_query("""
            INSERT INTO peladas (nome, descricao, local, foto_url, criador_id, ativa)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (nome, descricao, local, foto_url, user_id))
        
        # Adicionar criador como membro
        db_manager.execute_query("""
            INSERT INTO pelada_membros (pelada_id, jogador_id, ativo)
            VALUES (?, ?, 1)
        """, (pelada_id, user_id))
        
        return jsonify({
            'success': True,
            'message': 'Pelada criada com sucesso!',
            'pelada_id': pelada_id
        })
        
    except Exception as e:
        print(f"Erro ao criar pelada: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@peladas_bp.route('/api/peladas/<int:pelada_id>', methods=['GET'])
def get_pelada(pelada_id):
    """Retorna dados de uma pelada específica"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Usuário não logado'}), 401
        
        db_manager = get_db_manager()
        user_id = session['user_id']
        
        # Verificar se o usuário é membro da pelada
        membro = db_manager.execute_query(
            "SELECT id FROM pelada_membros WHERE pelada_id = ? AND jogador_id = ? AND ativo = 1",
            (pelada_id, user_id),
            fetch_one=True
        )
        
        if not membro:
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        # Buscar dados da pelada
        pelada = db_manager.execute_query("""
            SELECT p.id, p.nome, p.descricao, p.local, p.foto_url,
                   j.nome as criador_nome,
                   COUNT(DISTINCT pm.jogador_id) as total_membros,
                   COUNT(DISTINCT pt.id) as total_partidas
            FROM peladas p
            JOIN jogadores j ON p.criador_id = j.id
            LEFT JOIN pelada_membros pm ON p.id = pm.pelada_id AND pm.ativo = 1
            LEFT JOIN partidas pt ON p.id = pt.pelada_id
            WHERE p.id = ? AND p.ativa = 1
            GROUP BY p.id, p.nome, p.descricao, p.local, p.foto_url, j.nome
        """, (pelada_id,), fetch_one=True)
        
        if not pelada:
            return jsonify({'success': False, 'message': 'Pelada não encontrada'}), 404
        
        return jsonify({
            'success': True,
            'pelada': {
                'id': pelada['id'],
                'nome': pelada['nome'],
                'descricao': pelada['descricao'],
                'local': pelada['local'],
                'foto_url': pelada['foto_url'],
                'criador_nome': pelada['criador_nome'],
                'total_membros': pelada['total_membros'],
                'total_partidas': pelada['total_partidas']
            }
        })
        
    except Exception as e:
        print(f"Erro ao buscar pelada: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500

@peladas_bp.route('/api/peladas/<int:pelada_id>/jogadores', methods=['GET'])
def get_jogadores_pelada(pelada_id):
    """Retorna jogadores da pelada"""
    try:
        if 'user_id' not in session:
            return jsonify({'success': False, 'message': 'Usuário não logado'}), 401
        
        db_manager = get_db_manager()
        user_id = session['user_id']
        
        # Verificar se o usuário é membro da pelada
        membro = db_manager.execute_query(
            "SELECT id FROM pelada_membros WHERE pelada_id = ? AND jogador_id = ? AND ativo = 1",
            (pelada_id, user_id),
            fetch_one=True
        )
        
        if not membro:
            return jsonify({'success': False, 'message': 'Acesso negado'}), 403
        
        # Buscar jogadores da pelada
        jogadores = db_manager.execute_query("""
            SELECT j.id, j.nome, j.posicao, j.foto_url, pm.data_entrada,
                   COUNT(DISTINCT pe.partida_id) as partidas_jogadas,
                   COALESCE(SUM(pe.gols), 0) as total_gols,
                   COALESCE(SUM(pe.assistencias), 0) as total_assistencias,
                   COALESCE(SUM(pe.pontos), 0) as total_pontos
            FROM pelada_membros pm
            JOIN jogadores j ON pm.jogador_id = j.id
            LEFT JOIN partida_estatisticas pe ON j.id = pe.jogador_id 
                AND pe.partida_id IN (SELECT id FROM partidas WHERE pelada_id = ?)
            WHERE pm.pelada_id = ? AND pm.ativo = 1
            GROUP BY j.id, j.nome, j.posicao, j.foto_url, pm.data_entrada
            ORDER BY total_pontos DESC, j.nome
        """, (pelada_id, pelada_id), fetch_all=True)
        
        jogadores_list = []
        for jogador in jogadores:
            jogadores_list.append({
                'id': jogador['id'],
                'nome': jogador['nome'],
                'posicao': jogador['posicao'],
                'foto_url': jogador['foto_url'],
                'data_entrada': jogador['data_entrada'],
                'partidas_jogadas': jogador['partidas_jogadas'],
                'total_gols': jogador['total_gols'],
                'total_assistencias': jogador['total_assistencias'],
                'total_pontos': jogador['total_pontos']
            })
        
        return jsonify({
            'success': True,
            'jogadores': jogadores_list
        })
        
    except Exception as e:
        print(f"Erro ao buscar jogadores: {e}")
        return jsonify({'success': False, 'message': 'Erro interno do servidor'}), 500
