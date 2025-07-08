"""
Health check independente para Railway
Permite verificar se o serviço está funcionando sem depender do banco
"""

import os
import sys
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_health():
    """Verifica saúde básica do serviço"""
    try:
        # Verificações básicas
        checks = {
            'python_version': sys.version,
            'environment': os.environ.get('RAILWAY_ENVIRONMENT', 'local'),
            'port': os.environ.get('PORT', '5000'),
            'database_url_exists': bool(os.environ.get('DATABASE_URL')),
            'timestamp': datetime.now().isoformat()
        }
        
        # Verificar se consegue importar módulos principais
        try:
            import flask
            import psycopg2
            checks['flask_version'] = flask.__version__
            checks['psycopg2_available'] = True
        except ImportError as e:
            checks['import_error'] = str(e)
            checks['psycopg2_available'] = False
        
        # Verificar se consegue conectar ao banco (se DATABASE_URL existir)
        if checks['database_url_exists']:
            try:
                import psycopg2
                from urllib.parse import urlparse
                
                database_url = os.environ.get('DATABASE_URL')
                if database_url.startswith('postgres://'):
                    database_url = database_url.replace('postgres://', 'postgresql://', 1)
                
                parsed = urlparse(database_url)
                
                conn = psycopg2.connect(
                    host=parsed.hostname,
                    database=parsed.path[1:],
                    user=parsed.username,
                    password=parsed.password,
                    port=parsed.port,
                    sslmode='require',
                    connect_timeout=10
                )
                
                cursor = conn.cursor()
                cursor.execute('SELECT 1')
                cursor.close()
                conn.close()
                
                checks['database_status'] = 'connected'
                
            except Exception as db_error:
                checks['database_status'] = 'error'
                checks['database_error'] = str(db_error)
        else:
            checks['database_status'] = 'not_configured'
        
        return {
            'status': 'healthy',
            'checks': checks
        }
        
    except Exception as e:
        logger.error(f"Erro no health check: {e}")
        return {
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }

if __name__ == '__main__':
    result = check_health()
    print(f"Health Check Result: {result}")
    
    # Exit code baseado no status
    if result['status'] == 'healthy':
        sys.exit(0)
    else:
        sys.exit(1)

