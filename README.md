# O Rei da Pelada

Um aplicativo web moderno e espetacular para gerenciamento de peladas de futebol.

## 🚀 Características

- **Design Moderno e Espetacular**: Interface moderna com animações suaves e design responsivo
- **Tela de Login/Cadastro**: Sistema completo de autenticação com design atrativo
- **Dashboard Interativo**: Painel principal com estatísticas e ações rápidas
- **Gerenciamento de Peladas**: Criação e gerenciamento de grupos de futebol
- **Sistema de Rankings**: Ranking geral e por pelada baseado em estatísticas
- **Perfil de Jogador**: Card estilo FIFA com estatísticas detalhadas
- **Sistema de Votação**: Votação para MVP e pior jogador da partida
- **Controle Financeiro**: Gestão de mensalidades e gastos da pelada

## 🛠️ Tecnologias Utilizadas

### Frontend
- **React 18** com Vite
- **Tailwind CSS** para estilização
- **Framer Motion** para animações
- **Shadcn/UI** para componentes
- **Lucide React** para ícones
- **React Router** para navegação

### Backend
- **Flask** (Python)
- **SQLAlchemy** para ORM
- **Flask-CORS** para CORS
- **SQLite** como banco de dados

## 📦 Estrutura do Projeto

```
rei_da_pelada/
├── rei_da_pelada_frontend/     # Frontend React
│   ├── src/
│   │   ├── components/         # Componentes React
│   │   │   ├── dashboard/      # Páginas do dashboard
│   │   │   └── ui/            # Componentes UI
│   │   ├── config/            # Configurações
│   │   └── assets/            # Imagens e recursos
│   └── package.json
├── rei_da_pelada_backend/      # Backend Flask
│   ├── src/
│   │   ├── models/            # Modelos do banco de dados
│   │   ├── routes/            # Rotas da API
│   │   └── database/          # Banco de dados SQLite
│   └── requirements.txt
└── README.md
```

## 🚀 Como Executar

### Pré-requisitos
- Node.js 18+ 
- Python 3.8+
- pnpm (ou npm)

### Backend (Flask)

1. Navegue para o diretório do backend:
```bash
cd rei_da_pelada_backend
```

2. Crie um ambiente virtual:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Execute o servidor:
```bash
python src/main.py
```

O backend estará rodando em `http://localhost:5001`

### Frontend (React)

1. Navegue para o diretório do frontend:
```bash
cd rei_da_pelada_frontend
```

2. Instale as dependências:
```bash
pnpm install
# ou
npm install
```

3. Execute o servidor de desenvolvimento:
```bash
pnpm run dev
# ou
npm run dev
```

O frontend estará rodando em `http://localhost:5173`

## 🎮 Como Usar

1. **Acesse a aplicação** em `http://localhost:5173`
2. **Crie uma conta** clicando em "Cadastrar"
3. **Faça login** com suas credenciais
4. **Explore o dashboard** moderno e interativo
5. **Crie uma pelada** ou **busque peladas existentes**
6. **Gerencie partidas** e **visualize estatísticas**

## 🎨 Funcionalidades Implementadas

### ✅ Tela de Login/Cadastro
- Design moderno com fundo de campo de futebol
- Animações suaves e transições
- Validação de formulários
- Upload de foto de perfil

### ✅ Dashboard Principal
- Boas-vindas personalizadas
- Cards de estatísticas animados
- Ações rápidas
- Design responsivo e moderno

### ✅ Minhas Peladas
- Listagem de peladas do usuário
- Criação de novas peladas
- Design de cards atrativo
- Modal de criação moderna

### ✅ Buscar Peladas
- Busca por nome, local ou descrição
- Solicitação de entrada em peladas
- Interface intuitiva

### ✅ Perfil do Jogador
- Card estilo FIFA
- Estatísticas detalhadas
- Conquistas baseadas em performance
- Design espetacular

### ✅ Ranking Geral
- Top 10 jogadores
- Pódio com design especial
- Posição do usuário
- Estatísticas completas

## 🔧 Configurações

### API Configuration
O arquivo `src/config/api.js` contém todas as URLs da API. Para alterar a porta do backend, modifique a variável `API_BASE_URL`.

### Banco de Dados
O banco de dados SQLite é criado automaticamente em `src/database/app.db` quando o backend é executado pela primeira vez.

## 🎯 Próximos Passos

- Implementar sistema de notificações
- Adicionar chat em tempo real
- Implementar sistema de pagamentos
- Adicionar mais estatísticas avançadas
- Implementar sistema de torneios

## 🤝 Contribuição

Este projeto foi desenvolvido seguindo as especificações fornecidas, com foco em design moderno e funcionalidades completas para gerenciamento de peladas.

## 📄 Licença

Este projeto é propriedade do solicitante e foi desenvolvido conforme especificações fornecidas.

---

**Desenvolvido com ⚽ e muito código!**

