"""
Script para inicializar o banco de dados com todas as tabelas
Otimizado para Railway com tratamento robusto de erros
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
import time
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)

def get_db_connection():
    """Conecta ao banco PostgreSQL com retry otimizado para Railway"""
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
        raise Exception("DATABASE_URL não encontrada nas variáveis de ambiente")
    
    # Corrigir URL para SQLAlchemy 2.0+ se necessário
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    max_retries = 3  # Reduzido para Railway
    for attempt in range(max_retries):
        try:
            # Parse da URL
            parsed = urlparse(database_url)
            
            conn = psycopg2.connect(
                host=parsed.hostname,
                database=parsed.path[1:],
                user=parsed.username,
                password=parsed.password,
                port=parsed.port,
                sslmode='require',
                connect_timeout=30,  # Reduzido timeout
                application_name='o-rei-da-pelada'
            )
            logger.info(f"✅ Conexão com banco estabelecida (tentativa {attempt + 1})")
            return conn
        except Exception as e:
            logger.error(f"❌ Erro na conexão (tentativa {attempt + 1}): {e}")
            if attempt < max_retries - 1:
                time.sleep(min(2 ** attempt, 5))  # Backoff limitado
            else:
                raise

def init_database():
    """Inicializa o banco de dados com todas as tabelas"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        logger.info("🔄 Criando tabelas do banco de dados...")
        
        # Tabela de jogadores (já existe, mas vamos garantir que tem as colunas necessárias)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS jogadores (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                senha_hash VARCHAR(255) NOT NULL,
                posicao VARCHAR(50),
                foto_url VARCHAR(255),
                pontos_totais INTEGER DEFAULT 0,
                gols_totais INTEGER DEFAULT 0,
                assistencias_totais INTEGER DEFAULT 0,
                defesas_totais INTEGER DEFAULT 0,
                desarmes_totais INTEGER DEFAULT 0,
                partidas_jogadas INTEGER DEFAULT 0,
                media_pontos DECIMAL(5,2) DEFAULT 0.0,
                mvp_count INTEGER DEFAULT 0,
                bola_murcha_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de peladas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS peladas (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(100) NOT NULL,
                local VARCHAR(200) NOT NULL,
                descricao TEXT,
                foto_url VARCHAR(255),
                criador_id INTEGER REFERENCES jogadores(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de membros da pelada
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS membros_pelada (
                id SERIAL PRIMARY KEY,
                pelada_id INTEGER REFERENCES peladas(id) ON DELETE CASCADE,
                jogador_id INTEGER REFERENCES jogadores(id) ON DELETE CASCADE,
                is_admin BOOLEAN DEFAULT FALSE,
                status VARCHAR(20) DEFAULT 'ativo',
                joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(pelada_id, jogador_id)
            )
        ''')
        
        # Tabela de solicitações de entrada
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS solicitacoes_entrada (
                id SERIAL PRIMARY KEY,
                pelada_id INTEGER REFERENCES peladas(id) ON DELETE CASCADE,
                jogador_id INTEGER REFERENCES jogadores(id) ON DELETE CASCADE,
                status VARCHAR(20) DEFAULT 'pendente',
                mensagem TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                respondido_por INTEGER REFERENCES jogadores(id),
                respondido_at TIMESTAMP,
                UNIQUE(pelada_id, jogador_id)
            )
        ''')
        
        # Tabela de partidas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS partidas (
                id SERIAL PRIMARY KEY,
                pelada_id INTEGER REFERENCES peladas(id) ON DELETE CASCADE,
                data_partida DATE NOT NULL,
                horario_inicio TIME,
                horario_fim TIME,
                local VARCHAR(200),
                status VARCHAR(20) DEFAULT 'agendada',
                criado_por INTEGER REFERENCES jogadores(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de confirmações de partida
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS confirmacoes_partida (
                id SERIAL PRIMARY KEY,
                partida_id INTEGER REFERENCES partidas(id) ON DELETE CASCADE,
                jogador_id INTEGER REFERENCES jogadores(id) ON DELETE CASCADE,
                confirmado BOOLEAN,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(partida_id, jogador_id)
            )
        ''')
        
        # Tabela de estatísticas da partida
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS estatisticas_partida (
                id SERIAL PRIMARY KEY,
                partida_id INTEGER REFERENCES partidas(id) ON DELETE CASCADE,
                jogador_id INTEGER REFERENCES jogadores(id) ON DELETE CASCADE,
                gols INTEGER DEFAULT 0,
                assistencias INTEGER DEFAULT 0,
                defesas INTEGER DEFAULT 0,
                gols_sofridos INTEGER DEFAULT 0,
                desarmes INTEGER DEFAULT 0,
                pontos_estatisticas INTEGER DEFAULT 0,
                votos_mvp INTEGER DEFAULT 0,
                votos_bola_murcha INTEGER DEFAULT 0,
                pontos_votacao INTEGER DEFAULT 0,
                pontos_total INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(partida_id, jogador_id)
            )
        ''')
        
        # Tabela de votações da partida
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS votacoes_partida (
                id SERIAL PRIMARY KEY,
                partida_id INTEGER REFERENCES partidas(id) ON DELETE CASCADE,
                votante_id INTEGER REFERENCES jogadores(id) ON DELETE CASCADE,
                mvp_id INTEGER REFERENCES jogadores(id),
                bola_murcha_id INTEGER REFERENCES jogadores(id),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(partida_id, votante_id)
            )
        ''')
        
        # Tabela de transações financeiras
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transacoes_financeiras (
                id SERIAL PRIMARY KEY,
                pelada_id INTEGER REFERENCES peladas(id) ON DELETE CASCADE,
                tipo VARCHAR(20) NOT NULL,
                descricao VARCHAR(200) NOT NULL,
                valor DECIMAL(10,2) NOT NULL,
                data_transacao DATE NOT NULL,
                responsavel_id INTEGER REFERENCES jogadores(id),
                categoria VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de mensalidades
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mensalidades (
                id SERIAL PRIMARY KEY,
                pelada_id INTEGER REFERENCES peladas(id) ON DELETE CASCADE,
                jogador_id INTEGER REFERENCES jogadores(id) ON DELETE CASCADE,
                mes INTEGER NOT NULL,
                ano INTEGER NOT NULL,
                valor DECIMAL(10,2) NOT NULL,
                pago BOOLEAN DEFAULT FALSE,
                data_pagamento DATE,
                observacoes TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(pelada_id, jogador_id, mes, ano)
            )
        ''')
        
        # Criar índices apenas se não existirem
        indices = [
            'CREATE INDEX IF NOT EXISTS idx_peladas_criador ON peladas(criador_id)',
            'CREATE INDEX IF NOT EXISTS idx_membros_pelada ON membros_pelada(pelada_id, jogador_id)',
            'CREATE INDEX IF NOT EXISTS idx_partidas_pelada ON partidas(pelada_id)',
            'CREATE INDEX IF NOT EXISTS idx_estatisticas_partida ON estatisticas_partida(partida_id, jogador_id)',
            'CREATE INDEX IF NOT EXISTS idx_jogadores_pontos ON jogadores(pontos_totais DESC)',
            'CREATE INDEX IF NOT EXISTS idx_jogadores_media ON jogadores(media_pontos DESC)'
        ]
        
        for indice in indices:
            cursor.execute(indice)
        
        conn.commit()
        cursor.close()
        conn.close()
        
        logger.info("✅ Banco de dados inicializado com sucesso")
        
    except Exception as e:
        logger.error(f"❌ Erro ao inicializar banco de dados: {e}")
        raise

if __name__ == '__main__':
    init_database()

