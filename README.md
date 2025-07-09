# O Rei da Pelada

Sistema de gerenciamento de peladas (futebol entre amigos) desenvolvido em Flask com frontend React integrado.

## Deploy no Railway.com

Este projeto está pré-configurado para deploy automático no Railway.com. Siga os passos:

1. Faça upload dos arquivos para o GitHub
2. Conecte seu repositório ao Railway.com
3. O deploy será feito automaticamente

### Arquivos de configuração inclusos:

- `Procfile`: Define como iniciar a aplicação
- `requirements.txt`: Lista todas as dependências Python
- `runtime.txt`: Especifica a versão do Python
- Configuração de banco: Usa automaticamente o PostgreSQL do Railway

## Estrutura do Projeto

```
rei-da-pelada-monolitico/
├── src/
│   ├── main.py              # Arquivo principal da aplicação
│   ├── models/              # Modelos do banco de dados
│   ├── routes/              # Rotas da API
│   └── static/              # Frontend React (build)
├── Procfile                 # Configuração Railway
├── requirements.txt         # Dependências Python
├── runtime.txt             # Versão Python
└── README.md               # Este arquivo
```

## Funcionalidades

- Sistema de login e cadastro
- Gerenciamento de peladas
- Criação e acompanhamento de partidas
- Sistema de ranking
- Controle financeiro
- Perfil de jogadores com card estilo FIFA

## Tecnologias

- **Backend**: Flask, SQLAlchemy, Flask-CORS
- **Frontend**: React, Vite, TailwindCSS, shadcn/ui
- **Banco de Dados**: SQLite (desenvolvimento) / PostgreSQL (produção)
- **Deploy**: Railway.com

