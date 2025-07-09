import os
import sqlite3
import threading
import time
from contextlib import contextmanager

class DatabaseManager:
    """Gerenciador de conexões SQLite thread-safe"""
    
    def __init__(self, db_path):
        self.db_path = db_path
        self._local = threading.local()
        self._lock = threading.Lock()
        
    def get_db_path(self):
        """Retorna o caminho do banco de dados"""
        return self.db_path
    
    @contextmanager
    def get_connection(self, timeout=30):
        """Context manager para conexões SQLite com timeout e retry"""
        conn = None
        max_retries = 3
        retry_delay = 0.1
        
        for attempt in range(max_retries):
            try:
                conn = sqlite3.connect(
                    self.db_path,
                    timeout=timeout,
                    check_same_thread=False
                )
                conn.row_factory = sqlite3.Row
                # Configurações para evitar locks
                conn.execute('PRAGMA journal_mode=WAL')
                conn.execute('PRAGMA synchronous=NORMAL')
                conn.execute('PRAGMA temp_store=MEMORY')
                conn.execute('PRAGMA mmap_size=268435456')  # 256MB
                break
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e) and attempt < max_retries - 1:
                    time.sleep(retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                raise
        
        try:
            yield conn
        finally:
            if conn:
                try:
                    conn.close()
                except:
                    pass
    
    def execute_query(self, query, params=None, fetch_one=False, fetch_all=False):
        """Executa query com gerenciamento automático de conexão"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            else:
                conn.commit()
                return cursor.lastrowid
    
    def execute_many(self, query, params_list):
        """Executa múltiplas queries em uma transação"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)
            conn.commit()
            return cursor.rowcount

# Instância global do gerenciador
_db_manager = None

def get_db_manager():
    """Retorna a instância do gerenciador de banco"""
    global _db_manager
    if _db_manager is None:
        db_path = os.path.join(os.path.dirname(__file__), 'app.db')
        _db_manager = DatabaseManager(db_path)
    return _db_manager

def init_database():
    """Inicializa todas as tabelas do banco"""
    db_manager = get_db_manager()
    
    with db_manager.get_connection() as conn:
        # Tabela de jogadores
        conn.execute('''
            CREATE TABLE IF NOT EXISTS jogadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                email TEXT UNIQUE NOT NULL,
                senha TEXT NOT NULL,
                posicao TEXT NOT NULL,
                foto_url TEXT,
                data_cadastro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ativo BOOLEAN DEFAULT 1
            )
        ''')
        
        # Tabela de peladas
        conn.execute('''
            CREATE TABLE IF NOT EXISTS peladas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                descricao TEXT,
                local TEXT NOT NULL,
                foto_url TEXT,
                criador_id INTEGER NOT NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ativa BOOLEAN DEFAULT 1,
                FOREIGN KEY (criador_id) REFERENCES jogadores (id)
            )
        ''')
        
        # Tabela de membros das peladas
        conn.execute('''
            CREATE TABLE IF NOT EXISTS pelada_membros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pelada_id INTEGER NOT NULL,
                jogador_id INTEGER NOT NULL,
                data_entrada TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ativo BOOLEAN DEFAULT 1,
                FOREIGN KEY (pelada_id) REFERENCES peladas (id),
                FOREIGN KEY (jogador_id) REFERENCES jogadores (id),
                UNIQUE(pelada_id, jogador_id)
            )
        ''')
        
        # Tabela de partidas
        conn.execute('''
            CREATE TABLE IF NOT EXISTS partidas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pelada_id INTEGER NOT NULL,
                data_partida DATE NOT NULL,
                hora_partida TIME NOT NULL,
                local TEXT NOT NULL,
                descricao TEXT,
                status TEXT DEFAULT 'agendada',
                finalizada BOOLEAN DEFAULT 0,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pelada_id) REFERENCES peladas (id)
            )
        ''')
        
        # Tabela de confirmações de partidas
        conn.execute('''
            CREATE TABLE IF NOT EXISTS partida_confirmacoes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partida_id INTEGER NOT NULL,
                jogador_id INTEGER NOT NULL,
                confirmado BOOLEAN DEFAULT 0,
                data_confirmacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (partida_id) REFERENCES partidas (id),
                FOREIGN KEY (jogador_id) REFERENCES jogadores (id),
                UNIQUE(partida_id, jogador_id)
            )
        ''')
        
        # Tabela de estatísticas de partidas
        conn.execute('''
            CREATE TABLE IF NOT EXISTS partida_estatisticas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                partida_id INTEGER NOT NULL,
                jogador_id INTEGER NOT NULL,
                gols INTEGER DEFAULT 0,
                assistencias INTEGER DEFAULT 0,
                defesas INTEGER DEFAULT 0,
                gols_sofridos INTEGER DEFAULT 0,
                mvp BOOLEAN DEFAULT 0,
                bola_murcha BOOLEAN DEFAULT 0,
                pontos INTEGER DEFAULT 0,
                FOREIGN KEY (partida_id) REFERENCES partidas (id),
                FOREIGN KEY (jogador_id) REFERENCES jogadores (id),
                UNIQUE(partida_id, jogador_id)
            )
        ''')
        
        # Tabela de transações financeiras
        conn.execute('''
            CREATE TABLE IF NOT EXISTS transacoes_financeiras (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pelada_id INTEGER NOT NULL,
                tipo TEXT NOT NULL CHECK (tipo IN ('receita', 'despesa')),
                descricao TEXT NOT NULL,
                valor DECIMAL(10,2) NOT NULL,
                categoria TEXT,
                data_transacao DATE NOT NULL,
                criado_por INTEGER NOT NULL,
                data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pelada_id) REFERENCES peladas (id),
                FOREIGN KEY (criado_por) REFERENCES jogadores (id)
            )
        ''')
        
        # Tabela de contribuições dos jogadores
        conn.execute('''
            CREATE TABLE IF NOT EXISTS contribuicoes_jogadores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pelada_id INTEGER NOT NULL,
                jogador_id INTEGER NOT NULL,
                valor_contribuido DECIMAL(10,2) DEFAULT 0,
                ultima_atualizacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (pelada_id) REFERENCES peladas (id),
                FOREIGN KEY (jogador_id) REFERENCES jogadores (id),
                UNIQUE(pelada_id, jogador_id)
            )
        ''')
        
        conn.commit()

