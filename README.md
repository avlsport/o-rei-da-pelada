# O Rei da Pelada

Um aplicativo web moderno e espetacular para gerenciamento de peladas de futebol.

## 🚀 Deploy Automático no Railway.com

Este projeto está configurado para deploy automático no Railway.com. Basta conectar seu repositório GitHub ao Railway e o deploy será feito automaticamente.

### Configuração no Railway:

1. **Conecte seu repositório GitHub** ao Railway
2. **Adicione um banco de dados PostgreSQL** ao seu projeto
3. **Configure a variável de ambiente DATABASE_URL** para conectar o banco ao seu serviço web
4. O deploy será feito automaticamente!

## 🎨 Características

- **Design Moderno e Espetacular**: Interface moderna com animações suaves e design responsivo
- **Tela de Login/Cadastro**: Sistema completo de autenticação com design atrativo
- **Dashboard Interativo**: Painel principal com estatísticas e ações rápidas
- **Gerenciamento de Peladas**: Criação e gerenciamento de grupos de futebol
- **Sistema de Rankings**: Ranking geral e por pelada baseado em estatísticas
- **Perfil de Jogador**: Card estilo FIFA com estatísticas detalhadas
- **Sistema de Votação**: Votação para MVP e pior jogador da partida
- **Controle Financeiro**: Gestão de mensalidades e gastos da pelada

## 🛠️ Tecnologias Utilizadas

- **Backend**: Flask (Python) com SQLAlchemy
- **Frontend**: React 18 com Vite, Tailwind CSS, Framer Motion
- **Banco de Dados**: PostgreSQL (Railway) / SQLite (desenvolvimento local)
- **Deploy**: Railway.com com deploy automático

## 📦 Estrutura do Projeto

```
rei_da_pelada/
├── src/
│   ├── main.py              # Aplicação Flask principal
│   ├── static/              # Arquivos estáticos do React compilado
│   └── database/            # Banco de dados SQLite (desenvolvimento)
├── Procfile                 # Configuração de deploy para Railway
├── requirements.txt         # Dependências Python
├── runtime.txt             # Versão do Python
└── README.md               # Este arquivo
```

## 🎮 Funcionalidades Implementadas

### ✅ Sistema de Autenticação
- Registro de usuários com upload de foto
- Login/logout seguro
- Sessões persistentes

### ✅ Dashboard Principal
- Boas-vindas personalizadas
- Cards de estatísticas animados
- Ações rápidas
- Design responsivo e moderno

### ✅ Gerenciamento de Peladas
- Criação de novas peladas
- Listagem de peladas do usuário
- Busca por peladas disponíveis
- Sistema de membros

### ✅ Sistema de Rankings
- Ranking global de jogadores
- Estatísticas detalhadas
- Pontuação baseada em performance

### ✅ Perfil do Jogador
- Card estilo FIFA
- Estatísticas completas
- Upload de foto de perfil

## 🔧 Configuração Local (Opcional)

Se você quiser rodar o projeto localmente para desenvolvimento:

1. **Clone o repositório**:
   ```bash
   git clone <seu-repositorio>
   cd rei_da_pelada
   ```

2. **Instale as dependências**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Execute a aplicação**:
   ```bash
   python src/main.py
   ```

4. **Acesse**: `http://localhost:5001`

## 🌐 Deploy no Railway

O projeto está pré-configurado para deploy automático no Railway.com:

- **Procfile**: Define como iniciar a aplicação
- **requirements.txt**: Lista todas as dependências Python
- **runtime.txt**: Especifica a versão do Python
- **Configuração de banco**: Usa automaticamente o PostgreSQL do Railway

**Não é necessária nenhuma configuração manual!**

---

**Desenvolvido com ⚽ e muito código!**

