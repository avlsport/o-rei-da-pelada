"""
Gerenciador de conexão com banco de dados
Implementa retry automático e reconexão
"""

import os
import time
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        self.database_url = None
        self.connection_params = None
        self.is_available = False
        self.last_check = 0
        self.check_interval = 30  # Verificar a cada 30 segundos
        
        self._initialize()
    
    def _initialize(self):
        """Inicializa o gerenciador de banco"""
        try:
            self.database_url = os.environ.get('DATABASE_URL')
            if not self.database_url:
                logger.warning("⚠️ DATABASE_URL não encontrada")
                return
            
            # Corrigir URL para PostgreSQL
            if self.database_url.startswith('postgres://'):
                self.database_url = self.database_url.replace('postgres://', 'postgresql://', 1)
            
            # Parse da URL
            parsed = urlparse(self.database_url)
            self.connection_params = {
                'host': parsed.hostname,
                'database': parsed.path[1:],
                'user': parsed.username,
                'password': parsed.password,
                'port': parsed.port,
                'sslmode': 'require',
                'connect_timeout': 30,
                'application_name': 'o-rei-da-pelada'
            }
            
            # Testar conexão inicial
            self._test_connection()
            
        except Exception as e:
            logger.error(f"❌ Erro na inicialização do banco: {e}")
            self.is_available = False
    
    def _test_connection(self):
        """Testa a conexão com o banco"""
        try:
            if not self.connection_params:
                return False
            
            conn = psycopg2.connect(**self.connection_params)
            cursor = conn.cursor()
            cursor.execute('SELECT 1')
            cursor.close()
            conn.close()
            
            if not self.is_available:
                logger.info("✅ Conexão com banco estabelecida")
            
            self.is_available = True
            self.last_check = time.time()
            return True
            
        except Exception as e:
            if self.is_available:
                logger.error(f"❌ Conexão com banco perdida: {e}")
            
            self.is_available = False
            self.last_check = time.time()
            return False
    
    def get_connection(self):
        """Obtém uma conexão com o banco"""
        # Verificar se precisa testar a conexão novamente
        current_time = time.time()
        if current_time - self.last_check > self.check_interval:
            self._test_connection()
        
        if not self.is_available:
            raise Exception("Banco de dados não disponível")
        
        try:
            return psycopg2.connect(**self.connection_params)
        except Exception as e:
            logger.error(f"❌ Erro ao conectar: {e}")
            self.is_available = False
            raise Exception("Erro na conexão com banco de dados")
    
    def is_database_available(self):
        """Verifica se o banco está disponível"""
        current_time = time.time()
        if current_time - self.last_check > self.check_interval:
            self._test_connection()
        
        return self.is_available
    
    def initialize_tables(self):
        """Inicializa as tabelas do banco"""
        if not self.is_available:
            raise Exception("Banco não disponível para inicialização")
        
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            logger.info("🔄 Criando tabelas do banco de dados...")
            
            # Tabela de jogadores
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
            
            # Outras tabelas essenciais
            tables = [
                '''CREATE TABLE IF NOT EXISTS peladas (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(100) NOT NULL,
                    local VARCHAR(200) NOT NULL,
                    descricao TEXT,
                    foto_url VARCHAR(255),
                    criador_id INTEGER REFERENCES jogadores(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''',
                '''CREATE TABLE IF NOT EXISTS membros_pelada (
                    id SERIAL PRIMARY KEY,
                    pelada_id INTEGER REFERENCES peladas(id) ON DELETE CASCADE,
                    jogador_id INTEGER REFERENCES jogadores(id) ON DELETE CASCADE,
                    is_admin BOOLEAN DEFAULT FALSE,
                    status VARCHAR(20) DEFAULT 'ativo',
                    joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(pelada_id, jogador_id)
                )''',
                '''CREATE TABLE IF NOT EXISTS partidas (
                    id SERIAL PRIMARY KEY,
                    pelada_id INTEGER REFERENCES peladas(id) ON DELETE CASCADE,
                    data_partida DATE NOT NULL,
                    horario_inicio TIME,
                    horario_fim TIME,
                    local VARCHAR(200),
                    status VARCHAR(20) DEFAULT 'agendada',
                    criado_por INTEGER REFERENCES jogadores(id),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )'''
            ]
            
            for table_sql in tables:
                cursor.execute(table_sql)
            
            # Criar índices
            indices = [
                'CREATE INDEX IF NOT EXISTS idx_jogadores_email ON jogadores(email)',
                'CREATE INDEX IF NOT EXISTS idx_jogadores_pontos ON jogadores(pontos_totais DESC)',
                'CREATE INDEX IF NOT EXISTS idx_peladas_criador ON peladas(criador_id)',
                'CREATE INDEX IF NOT EXISTS idx_membros_pelada ON membros_pelada(pelada_id, jogador_id)'
            ]
            
            for indice in indices:
                cursor.execute(indice)
            
            conn.commit()
            cursor.close()
            conn.close()
            
            logger.info("✅ Tabelas criadas/verificadas com sucesso")
            
        except Exception as e:
            logger.error(f"❌ Erro ao criar tabelas: {e}")
            raise

# Instância global do gerenciador
db_manager = DatabaseManager()

def get_db_connection():
    """Função global para obter conexão"""
    return db_manager.get_connection()

def is_database_available():
    """Função global para verificar disponibilidade"""
    return db_manager.is_database_available()

def init_database():
    """Função global para inicializar banco"""
    return db_manager.initialize_tables()

