# 👑 O Rei da Pelada

Sistema completo para gerenciamento de peladas de futebol, desenvolvido em Python Flask com interface moderna e responsiva.

## 🚀 Funcionalidades

### 🔐 Sistema de Autenticação
- Login e cadastro de usuários
- Autenticação segura com hash de senhas
- Sessões persistentes
- Interface moderna com imagem de fundo

### ⚽ Gestão de Peladas
- Criar e gerenciar peladas
- Buscar peladas disponíveis
- Solicitar entrada em peladas
- Sistema de aprovação de membros

### 🏆 Sistema de Partidas
- Agendar partidas com data, hora e local
- Visualizar partidas agendadas
- Controle de participantes

### 💰 Controle Financeiro
- Adicionar transações (entradas/saídas)
- Categorização de gastos
- Relatórios financeiros
- Controle de saldo

### 👥 Gestão de Jogadores
- Adicionar jogadores às peladas
- Controle de posições
- Sistema de rankings
- Estatísticas detalhadas

### 📊 Rankings e Estatísticas
- Ranking geral do aplicativo
- Rankings por pelada
- Estatísticas individuais
- Controle de desempenho

## 🛠️ Tecnologias Utilizadas

### Backend
- **Python 3.11+**
- **Flask** - Framework web
- **SQLite** - Banco de dados
- **Werkzeug** - Hash de senhas
- **CORS** - Suporte a requisições cross-origin

### Frontend
- **HTML5** - Estrutura
- **CSS3** - Estilização moderna
- **JavaScript ES6+** - Interatividade
- **Design Responsivo** - Mobile-first

### Banco de Dados
- **SQLite** com estrutura otimizada
- Tabelas: jogadores, peladas, partidas, transacoes, membros_pelada

## 📁 Estrutura do Projeto

```
rei-pelada-novo-limpo/
├── src/
│   ├── main.py                 # Aplicação principal
│   ├── database/
│   │   ├── connection_manager.py
│   │   └── app.db             # Banco SQLite
│   ├── routes/
│   │   ├── auth_ultra_simple.py
│   │   ├── user.py
│   │   ├── peladas.py
│   │   ├── partidas.py
│   │   ├── rankings.py
│   │   └── busca_peladas.py
│   └── static/
│       ├── index.html         # Tela de login
│       ├── dashboard.html     # Dashboard principal
│       ├── pelada.html        # Gestão de peladas
│       └── football-field-bg.jpg
├── README.md
└── requirements.txt
```

## 🚀 Como Executar

### 1. Pré-requisitos
- Python 3.11 ou superior
- pip (gerenciador de pacotes Python)

### 2. Instalação
```bash
# Clone o repositório
git clone <url-do-repositorio>
cd rei-pelada-novo-limpo

# Instale as dependências
pip install -r requirements.txt
```

### 3. Configuração do Banco
```bash
# Execute o script de inicialização (se necessário)
python init_all_tables.py
```

### 4. Executar o Servidor
```bash
# Navegue para o diretório src
cd src

# Execute a aplicação
python -m main

# Ou especifique uma porta
PORT=5000 python -m main
```

### 5. Acessar o Sistema
- Abra o navegador em: `http://localhost:5000`
- Faça login ou crie uma conta

## 👤 Credenciais de Teste

Para testar o sistema, use:
- **Email:** teste2@teste.com
- **Senha:** 123456

## 🎨 Interface

### Tela de Login
- Design moderno com imagem de fundo de campo de futebol
- Formulários de login e cadastro integrados
- Animações suaves e responsividade
- Validações em tempo real

### Dashboard
- Interface intuitiva com abas organizadas
- Perfil do usuário com estatísticas
- Gestão completa de peladas
- Controles financeiros integrados

### Funcionalidades Principais
- **Perfil:** Dados do usuário e estatísticas
- **Minhas Peladas:** Criar e gerenciar peladas
- **Ranking Geral:** Classificações do aplicativo
- **Partidas:** Agendar e controlar jogos
- **Financeiro:** Controle de receitas e despesas
- **Jogadores:** Adicionar e gerenciar membros

## 🔧 Configurações

### Variáveis de Ambiente
- `PORT`: Porta do servidor (padrão: 5000)
- `DEBUG`: Modo debug (padrão: False)

### Banco de Dados
O sistema usa SQLite por padrão. Para produção, considere migrar para PostgreSQL ou MySQL.

## 📱 Responsividade

O sistema é totalmente responsivo e funciona em:
- 📱 Dispositivos móveis
- 📱 Tablets
- 💻 Desktops
- 🖥️ Monitores grandes

## 🛡️ Segurança

- Senhas criptografadas com Werkzeug
- Validação de entrada em todos os formulários
- Proteção contra SQL injection
- Sessões seguras
- Validação de tipos de arquivo

## 🚀 Deploy

### Desenvolvimento Local
```bash
python -m src.main
```

### Produção
Para deploy em produção, considere usar:
- **Gunicorn** como servidor WSGI
- **Nginx** como proxy reverso
- **Docker** para containerização

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 🤝 Contribuição

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📞 Suporte

Para suporte ou dúvidas, entre em contato através dos issues do GitHub.

---

**Desenvolvido com ⚽ para a comunidade de futebol amador**

