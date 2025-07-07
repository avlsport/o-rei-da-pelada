# 🚀 Guia Completo de Deploy - O Rei da Pelada

Este guia te ajudará a fazer o deploy do aplicativo no Railway passo a passo.

## 📋 Pré-requisitos

✅ Conta no Railway criada  
✅ Conta no GitHub criada  
✅ Repositório `o-rei-da-pelada` criado no GitHub  
✅ Códigos já estão no repositório  

## 🎯 Passo a Passo

### **1. Criar Banco de Dados PostgreSQL**

1. **Acesse o Railway** → https://railway.app
2. **Clique em "Deploy a new project"**
3. **Selecione "Deploy PostgreSQL"**
4. **Aguarde a criação** (alguns segundos)
5. **Anote o nome do projeto** (ex: `beautiful-spontaneity`)

### **2. Adicionar o Aplicativo ao Projeto**

1. **No mesmo projeto**, clique em **"+ Create"**
2. **Selecione "Deploy from GitHub repo"**
3. **Escolha o repositório** `o-rei-da-pelada`
4. **Aguarde o deploy automático**

### **3. Configurar Variáveis de Ambiente**

1. **Clique no serviço do aplicativo** (não no PostgreSQL)
2. **Vá em "Variables"** ou "Settings"
3. **Adicione as seguintes variáveis:**

```bash
DATABASE_URL = ${{Postgres.DATABASE_URL}}
SECRET_KEY = sua_chave_secreta_aqui
FLASK_ENV = production
PORT = 5000
```

**IMPORTANTE:** O `DATABASE_URL` deve referenciar o PostgreSQL criado no passo 1.

### **4. Conectar Banco ao Aplicativo**

1. **No PostgreSQL**, vá em **"Connect"**
2. **Copie a "Database URL"**
3. **No aplicativo**, cole como valor da variável `DATABASE_URL`

**OU** use a referência automática: `${{Postgres.DATABASE_URL}}`

### **5. Verificar Deploy**

1. **Aguarde o build terminar** (2-5 minutos)
2. **Clique na URL gerada** pelo Railway
3. **Teste o aplicativo:**
   - ✅ Página inicial carrega
   - ✅ Cadastro funciona
   - ✅ Login funciona
   - ✅ Criação de peladas funciona

## 🔧 Configurações Avançadas

### **Domínio Personalizado**

1. **Compre seu domínio** (ex: `oreidapelada.com`)
2. **No Railway**, vá em **"Settings" → "Domains"**
3. **Clique em "Custom Domain"**
4. **Digite seu domínio**
5. **Configure DNS** conforme instruções

### **Monitoramento**

- **Logs**: Railway → Projeto → "Logs"
- **Métricas**: Railway → Projeto → "Metrics"
- **Alertas**: Railway → Projeto → "Settings" → "Alerts"

## 🐛 Solução de Problemas

### **Erro: "Application failed to start"**

**Causa:** Variáveis de ambiente incorretas  
**Solução:**
1. Verifique se `DATABASE_URL` está correto
2. Confirme se `PORT` está definido como `5000`
3. Verifique se `FLASK_ENV` está como `production`

### **Erro: "Database connection failed"**

**Causa:** PostgreSQL não conectado  
**Solução:**
1. Verifique se PostgreSQL está rodando
2. Confirme se `DATABASE_URL` está correto
3. Teste conexão no Railway

### **Erro: "Static files not found"**

**Causa:** Frontend não foi buildado  
**Solução:**
1. Verifique se pasta `src/static/` existe
2. Confirme se contém `index.html`
3. Re-faça o build se necessário

### **Erro: "CORS policy"**

**Causa:** Configuração de CORS  
**Solução:**
1. Verifique se `FLASK_ENV=production`
2. Confirme configurações de CORS no código
3. Teste em navegador privado

## 📊 Monitoramento de Performance

### **Métricas Importantes**
- **Response Time**: < 500ms
- **Memory Usage**: < 512MB
- **CPU Usage**: < 50%
- **Error Rate**: < 1%

### **Logs para Monitorar**
```bash
# Logs de sucesso
[INFO] Starting application
[INFO] Database connected
[INFO] User logged in

# Logs de erro
[ERROR] Database connection failed
[ERROR] Authentication failed
[WARNING] High memory usage
```

## 💰 Custos Estimados

### **Railway Hobby Plan**
- **Custo**: $5/mês (≈ R$ 25/mês)
- **Recursos**: 8GB RAM, 8 vCPU
- **Tráfego**: Ilimitado
- **Banco**: PostgreSQL incluído

### **Domínio**
- **Custo**: $10-15/ano (≈ R$ 50-75/ano)
- **Renovação**: Anual
- **DNS**: Gratuito

## 🎯 Próximos Passos

1. ✅ **Deploy funcionando**
2. ✅ **Domínio configurado**
3. ✅ **Testes completos**
4. 🚀 **Lançamento oficial**
5. 📈 **Monitoramento e melhorias**

## 📞 Suporte

Se encontrar problemas:

1. **Verifique os logs** no Railway
2. **Consulte este guia** novamente
3. **Teste em ambiente local** primeiro
4. **Documente o erro** com screenshots

---

🎉 **Parabéns! Seu aplicativo está no ar!** 🎉

Agora você tem um aplicativo profissional rodando 24/7 na nuvem! ⚽🏆

