# O Rei da Pelada ⚽

Aplicativo para gerenciar peladas de futebol com sistema de pontuação e rankings.

## 🚀 Funcionalidades

### ⚽ **Sistema de Peladas**
- Criação e gerenciamento de peladas
- Sistema de aprovação de membros
- Busca por peladas existentes
- Convites por link

### 🏆 **Sistema de Partidas**
- Criação de partidas dentro das peladas
- Confirmação de presença dos jogadores
- Finalização de partidas
- Sistema completo de estatísticas

### 📊 **Sistema de Pontuação**
- **Gol**: 8 pontos
- **Assistência**: 5 pontos
- **Defesa do goleiro**: 2 pontos
- **Desarme**: 1 ponto
- **Gol sofrido pelo goleiro**: -1 ponto
- **Voto MVP**: +3 pontos
- **Voto Bola Murcha**: -3 pontos

### 🏅 **Destaques Automáticos**
- 👑 **Rei da Pelada** (maior pontuação)
- ⚽ **Artilheiro** (mais gols)
- 🎯 **Garçom** (mais assistências)
- 🥅 **Paredão** (mais defesas)
- 🛡️ **Xerifão** (mais desarmes)
- 💩 **Bola Murcha** (menor pontuação)

### 🎨 **Time da Rodada**
- Layout visual de campo de futebol
- Jogadores posicionados nas posições
- Interface responsiva e moderna

### 🗳️ **Sistema de Votação**
- Votação para MVP e Bola Murcha
- Cronômetro para encerrar votação
- Admin pode encerrar antes do tempo
- Rankings liberados após votação

## 🛠️ Tecnologias

### **Backend**
- **Python 3.11**
- **Flask** - Framework web
- **SQLAlchemy** - ORM para banco de dados
- **PostgreSQL** - Banco de dados (produção)
- **SQLite** - Banco de dados (desenvolvimento)
- **Flask-CORS** - Suporte a CORS

### **Frontend**
- **React 18** - Framework frontend
- **Vite** - Build tool
- **Tailwind CSS** - Framework CSS
- **Lucide React** - Ícones
- **React Router** - Roteamento

## 🚀 Deploy no Railway

### **Pré-requisitos**
1. Conta no Railway
2. Conta no GitHub
3. Repositório conectado ao Railway

### **Configuração do Banco de dados**
1. No Railway, adicione um serviço PostgreSQL
2. Copie a URL de conexão do banco
3. Configure como variável de ambiente `DATABASE_URL`

### **Variáveis de Ambiente**
```bash
DATABASE_URL=postgresql://...  # URL do PostgreSQL
SECRET_KEY=sua_chave_secreta   # Chave secreta do Flask
FLASK_ENV=production           # Ambiente de produção
PORT=5000                      # Porta do servidor
```

### **Deploy Automático**
1. Conecte o repositório ao Railway
2. O Railway detecta automaticamente o projeto Python
3. Instala dependências do `requirements.txt`
4. Executa o comando definido no `Procfile`

## 📁 Estrutura do Projeto

```
o-rei-da-pelada/
├── src/
│   ├── models/          # Modelos do banco de dados
│   │   ├── jogador.py   # Modelo de jogadores
│   │   ├── pelada.py    # Modelo de peladas
│   │   └── partida.py   # Modelo de partidas
│   ├── routes/          # Rotas da API
│   │   ├── auth.py      # Autenticação
│   │   ├── peladas.py   # Gerenciamento de peladas
│   │   └── partidas.py  # Gerenciamento de partidas
│   ├── utils/           # Utilitários
│   │   └── pontuacao.py # Sistema de pontuação
│   ├── static/          # Frontend buildado
│   └── main.py          # Arquivo principal
├── requirements.txt     # Dependências Python
├── Procfile            # Comando de inicialização
├── railway.toml        # Configuração do Railway
├── runtime.txt         # Versão do Python
└── README.md           # Documentação
```

## 🔧 Desenvolvimento Local

### **Backend**
```bash
# Instalar dependências
pip install -r requirements.txt

# Executar servidor
python src/main.py
```

### **Frontend** (se necessário rebuildar)
```bash
# Instalar dependências
npm install

# Build para produção
npm run build

# Copiar para pasta static
cp -r dist/* src/static/
```

## 📱 Funcionalidades Detalhadas

### **Fluxo de Usuário**
1. **Cadastro/Login** - Sistema de autenticação completo
2. **Dashboard** - Visão geral das peladas e estatísticas
3. **Criar Pelada** - Criação de nova pelada
4. **Buscar Peladas** - Busca e solicitação de entrada
5. **Gerenciar Pelada** - Aprovação de membros, criação de partidas
6. **Participar de Partida** - Confirmação de presença
7. **Adicionar Estatísticas** - Inserção de dados da partida
8. **Votar** - Votação para MVP e Bola Murcha
9. **Ver Rankings** - Visualização de rankings e Time da Rodada

### **Permissões**
- **Admin da Pelada**: Pode criar partidas, aprovar membros, adicionar estatísticas
- **Membro da Pelada**: Pode confirmar presença, votar, ver rankings
- **Usuário Comum**: Pode criar peladas, buscar peladas, solicitar entrada

## 🎯 Roadmap Futuro

- [ ] Sistema de pagamento integrado
- [ ] Notificações push
- [ ] Chat entre membros
- [ ] Sistema de ligas e campeonatos
- [ ] Estatísticas avançadas
- [ ] App mobile nativo
- [ ] Sistema de arbitragem
- [ ] Integração com redes sociais

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo LICENSE para mais detalhes.

## 👨‍💻 Desenvolvido por

**Manus AI** - Desenvolvimento completo do sistema

---

⚽ **O Rei da Pelada** - Transformando peladas em experiências profissionais! 🏆

