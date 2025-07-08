#!/usr/bin/env python3
"""
Health check script para verificar se o aplicativo está funcionando
"""
import os
import sys
import time
import requests
from urllib.parse import urljoin

def check_health():
    """Verifica se o aplicativo está respondendo"""
    base_url = os.environ.get('RAILWAY_STATIC_URL', 'http://localhost:5000')
    
    endpoints = [
        '/api/test',
        '/api/auth/check'
    ]
    
    print(f"🔍 Verificando saúde do aplicativo em: {base_url}")
    
    for endpoint in endpoints:
        url = urljoin(base_url, endpoint)
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                print(f"✅ {endpoint} - OK")
            else:
                print(f"❌ {endpoint} - Status: {response.status_code}")
        except Exception as e:
            print(f"❌ {endpoint} - Erro: {e}")
    
    print("🏁 Verificação concluída")

if __name__ == '__main__':
    check_health()

