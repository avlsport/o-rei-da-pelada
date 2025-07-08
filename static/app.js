// Estado global da aplicação
let currentUser = null;
let currentPelada = null;

// Elementos DOM
const elements = {
    loading: document.getElementById('loading'),
    authScreen: document.getElementById('auth-screen'),
    mainApp: document.getElementById('main-app'),
    loginForm: document.getElementById('login-form'),
    registerForm: document.getElementById('register-form'),
    dashboardScreen: document.getElementById('dashboard-screen'),
    peladaDashboard: document.getElementById('pelada-dashboard')
};

// Utilitários
const API_BASE = '/api';

async function apiCall(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            credentials: 'include',
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            },
            ...options
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.message || 'Erro na requisição');
        }
        
        return data;
    } catch (error) {
        console.error('Erro na API:', error);
        throw error;
    }
}

function showAlert(message, type = 'info') {
    // Criar elemento de alerta
    const alert = document.createElement('div');
    alert.className = `fixed top-4 right-4 z-50 p-4 rounded-lg text-white max-w-sm ${
        type === 'success' ? 'bg-green-500' : 
        type === 'error' ? 'bg-red-500' : 
        'bg-blue-500'
    }`;
    alert.innerHTML = `
        <div class="flex items-center justify-between">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    
    document.body.appendChild(alert);
    
    // Remover automaticamente após 5 segundos
    setTimeout(() => {
        if (alert.parentElement) {
            alert.remove();
        }
    }, 5000);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('pt-BR');
}

function formatCurrency(value) {
    return new Intl.NumberFormat('pt-BR', {
        style: 'currency',
        currency: 'BRL'
    }).format(value);
}

// Inicialização
async function init() {
    console.log('🚀 Inicializando aplicação...');
    
    try {
        // Verificar se usuário está logado
        const response = await apiCall('/auth/me');
        
        if (response.success) {
            currentUser = response.user;
            showMainApp();
        } else {
            showAuthScreen();
        }
    } catch (error) {
        console.log('Usuário não autenticado, mostrando tela de login');
        showAuthScreen();
    } finally {
        elements.loading.style.display = 'none';
    }
}

// Telas
function showAuthScreen() {
    elements.authScreen.style.display = 'flex';
    elements.mainApp.style.display = 'none';
}

function showMainApp() {
    elements.authScreen.style.display = 'none';
    elements.mainApp.style.display = 'block';
    
    // Atualizar informações do usuário
    updateUserInfo();
    
    // Carregar dashboard
    showDashboard();
}

function showDashboard() {
    elements.dashboardScreen.style.display = 'block';
    elements.peladaDashboard.style.display = 'none';
    
    // Carregar dados do dashboard
    loadRankingGeral();
    loadPeladas();
}

function showPeladaDashboard(pelada) {
    currentPelada = pelada;
    elements.dashboardScreen.style.display = 'none';
    elements.peladaDashboard.style.display = 'block';
    
    // Atualizar título
    document.getElementById('peladaTitle').textContent = pelada.nome;
    
    // Ativar primeira aba
    showTab('rankings');
}

// Autenticação
async function login(email, senha) {
    try {
        console.log('Tentando fazer login...');
        
        const response = await apiCall('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ email, senha })
        });
        
        console.log('Resposta do login:', response);
        
        if (response.success) {
            currentUser = response.user;
            showAlert('Login realizado com sucesso!', 'success');
            showMainApp();
        } else {
            showAlert(response.message || 'Erro no login', 'error');
        }
    } catch (error) {
        console.error('Erro no login:', error);
        showAlert('Erro ao fazer login: ' + error.message, 'error');
    }
}

async function register(formData) {
    try {
        console.log('Tentando fazer cadastro...');
        
        const response = await fetch(`${API_BASE}/auth/register`, {
            method: 'POST',
            credentials: 'include',
            body: formData // FormData para upload de arquivo
        });
        
        const data = await response.json();
        console.log('Resposta do cadastro:', data);
        
        if (data.success) {
            showAlert('Cadastro realizado com sucesso! Faça login para continuar.', 'success');
            showLoginForm();
        } else {
            showAlert(data.message || 'Erro no cadastro', 'error');
        }
    } catch (error) {
        console.error('Erro no cadastro:', error);
        showAlert('Erro ao fazer cadastro: ' + error.message, 'error');
    }
}

async function logout() {
    try {
        await apiCall('/auth/logout', { method: 'POST' });
        currentUser = null;
        currentPelada = null;
        showAlert('Logout realizado com sucesso!', 'success');
        showAuthScreen();
    } catch (error) {
        console.error('Erro no logout:', error);
        showAlert('Erro ao fazer logout', 'error');
    }
}

// Interface do usuário
function updateUserInfo() {
    if (!currentUser) return;
    
    document.getElementById('userName').textContent = currentUser.nome;
    
    const userPhoto = document.getElementById('userPhoto');
    const userInitial = document.getElementById('userInitial');
    
    if (currentUser.foto_url) {
        userPhoto.src = currentUser.foto_url;
        userPhoto.style.display = 'block';
        userInitial.style.display = 'none';
    } else {
        userPhoto.style.display = 'none';
        userInitial.style.display = 'flex';
        userInitial.textContent = currentUser.nome.charAt(0).toUpperCase();
    }
}

// Ranking Geral
async function loadRankingGeral() {
    try {
        const response = await apiCall('/rankings/geral');
        
        if (response.success) {
            renderRankingGeral(response.ranking);
        }
    } catch (error) {
        console.error('Erro ao carregar ranking geral:', error);
        document.getElementById('ranking-geral').innerHTML = `
            <div class="text-center py-4 text-red-500">
                <i class="fas fa-exclamation-triangle mb-2"></i>
                <p>Erro ao carregar ranking</p>
            </div>
        `;
    }
}

function renderRankingGeral(ranking) {
    const container = document.getElementById('ranking-geral');
    
    if (!ranking.top_10 || ranking.top_10.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8 text-gray-500">
                <i class="fas fa-trophy text-4xl mb-4"></i>
                <p>Nenhum jogador no ranking ainda</p>
                <p class="text-sm">Jogue partidas para aparecer aqui!</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="space-y-3">';
    
    // Top 10
    ranking.top_10.forEach((jogador, index) => {
        const posicao = index + 1;
        const isCurrentUser = jogador.id === currentUser.id;
        
        html += `
            <div class="flex items-center justify-between p-3 rounded-lg ${isCurrentUser ? 'bg-blue-50 border-2 border-blue-200' : 'bg-gray-50'}">
                <div class="flex items-center space-x-3">
                    <div class="flex-shrink-0">
                        ${posicao <= 3 ? 
                            `<span class="text-2xl">${posicao === 1 ? '🥇' : posicao === 2 ? '🥈' : '🥉'}</span>` :
                            `<span class="w-8 h-8 bg-gray-300 text-gray-700 rounded-full flex items-center justify-center font-bold text-sm">${posicao}</span>`
                        }
                    </div>
                    <div class="flex items-center space-x-2">
                        ${jogador.foto_url ? 
                            `<img src="${jogador.foto_url}" alt="${jogador.nome}" class="w-8 h-8 rounded-full object-cover">` :
                            `<div class="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold text-sm">${jogador.nome.charAt(0)}</div>`
                        }
                        <div>
                            <p class="font-medium ${isCurrentUser ? 'text-blue-700' : 'text-gray-800'}">${jogador.nome}</p>
                            <p class="text-sm text-gray-500">${jogador.posicao || 'Sem posição'}</p>
                        </div>
                    </div>
                </div>
                <div class="text-right">
                    <p class="font-bold text-lg ${isCurrentUser ? 'text-blue-700' : 'text-gray-800'}">${jogador.pontos_totais}</p>
                    <p class="text-sm text-gray-500">pontos</p>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    
    // Mostrar posição do usuário se não estiver no top 10
    if (ranking.posicao_usuario > 10) {
        html += `
            <div class="mt-6 p-4 bg-blue-50 border-2 border-blue-200 rounded-lg">
                <h4 class="font-bold text-blue-700 mb-2">Sua Posição</h4>
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                        <span class="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold text-sm">${ranking.posicao_usuario}</span>
                        <div>
                            <p class="font-medium text-blue-700">${ranking.usuario_atual.nome}</p>
                            <p class="text-sm text-blue-600">${ranking.usuario_atual.posicao || 'Sem posição'}</p>
                        </div>
                    </div>
                    <div class="text-right">
                        <p class="font-bold text-lg text-blue-700">${ranking.usuario_atual.pontos_totais}</p>
                        <p class="text-sm text-blue-600">pontos</p>
                    </div>
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

// Peladas
async function loadPeladas() {
    try {
        const response = await apiCall('/peladas');
        
        if (response.success) {
            renderPeladas(response.peladas);
        }
    } catch (error) {
        console.error('Erro ao carregar peladas:', error);
        document.getElementById('peladas-list').innerHTML = `
            <div class="text-center py-8 text-red-500">
                <i class="fas fa-exclamation-triangle text-4xl mb-4"></i>
                <p>Erro ao carregar peladas</p>
            </div>
        `;
    }
}

function renderPeladas(peladas) {
    const container = document.getElementById('peladas-list');
    
    if (!peladas || peladas.length === 0) {
        container.innerHTML = `
            <div class="text-center py-12 text-gray-500">
                <i class="fas fa-futbol text-6xl mb-4"></i>
                <h3 class="text-xl font-bold mb-2">Nenhuma pelada encontrada</h3>
                <p class="mb-4">Crie sua primeira pelada para começar!</p>
                <button onclick="openNewPeladaModal()" class="bg-green-500 hover:bg-green-600 text-white px-6 py-3 rounded-lg transition duration-200">
                    <i class="fas fa-plus mr-2"></i>Criar Primeira Pelada
                </button>
            </div>
        `;
        return;
    }
    
    let html = '<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">';
    
    peladas.forEach(pelada => {
        html += `
            <div class="bg-white rounded-lg shadow-md card-hover cursor-pointer" onclick="openPelada(${pelada.id})">
                ${pelada.foto_url ? 
                    `<img src="${pelada.foto_url}" alt="${pelada.nome}" class="w-full h-48 object-cover rounded-t-lg">` :
                    `<div class="w-full h-48 bg-gradient-to-br from-blue-400 to-purple-500 rounded-t-lg flex items-center justify-center">
                        <i class="fas fa-futbol text-6xl text-white"></i>
                    </div>`
                }
                <div class="p-6">
                    <h3 class="text-xl font-bold text-gray-800 mb-2">${pelada.nome}</h3>
                    <p class="text-gray-600 mb-2">
                        <i class="fas fa-map-marker-alt mr-2"></i>${pelada.local}
                    </p>
                    ${pelada.descricao ? `<p class="text-gray-500 text-sm mb-4">${pelada.descricao}</p>` : ''}
                    <div class="flex items-center justify-between">
                        <span class="text-sm text-gray-500">
                            Criado por ${pelada.criador_nome}
                        </span>
                        ${pelada.is_admin ? 
                            '<span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">Admin</span>' :
                            '<span class="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded-full">Membro</span>'
                        }
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

async function createPelada(formData) {
    try {
        console.log('Criando pelada...');
        
        const response = await fetch(`${API_BASE}/peladas`, {
            method: 'POST',
            credentials: 'include',
            body: formData // FormData para upload de arquivo
        });
        
        const data = await response.json();
        console.log('Resposta da criação:', data);
        
        if (data.success) {
            showAlert('Pelada criada com sucesso!', 'success');
            closeNewPeladaModal();
            loadPeladas(); // Recarregar lista
        } else {
            showAlert(data.message || 'Erro ao criar pelada', 'error');
        }
    } catch (error) {
        console.error('Erro ao criar pelada:', error);
        showAlert('Erro ao criar pelada: ' + error.message, 'error');
    }
}

function openPelada(peladaId) {
    // Encontrar pelada na lista atual
    // Por simplicidade, vamos simular os dados da pelada
    const pelada = {
        id: peladaId,
        nome: 'Pelada Exemplo',
        local: 'Campo do Bairro'
    };
    
    showPeladaDashboard(pelada);
}

// Modais
function openNewPeladaModal() {
    document.getElementById('newPeladaModal').classList.add('show');
}

function closeNewPeladaModal() {
    document.getElementById('newPeladaModal').classList.remove('show');
    document.getElementById('newPeladaForm').reset();
}

// Tabs
function showTab(tabName) {
    // Remover classe active de todas as abas
    document.querySelectorAll('.tab-button').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
        content.classList.remove('active');
    });
    
    // Ativar aba selecionada
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');
    document.getElementById(`${tabName}-tab`).classList.add('active');
    
    // Carregar conteúdo da aba se necessário
    if (tabName === 'partidas') {
        loadPartidas();
    } else if (tabName === 'financeiro') {
        loadFinanceiro();
    } else if (tabName === 'jogadores') {
        loadJogadores();
    }
}

async function loadPartidas() {
    if (!currentPelada) return;
    
    try {
        const response = await apiCall(`/peladas/${currentPelada.id}/partidas`);
        
        if (response.success) {
            renderPartidas(response.partidas);
        }
    } catch (error) {
        console.error('Erro ao carregar partidas:', error);
        document.getElementById('partidas-list').innerHTML = `
            <div class="text-center py-8 text-red-500">
                <p>Erro ao carregar partidas</p>
            </div>
        `;
    }
}

function renderPartidas(partidas) {
    const container = document.getElementById('partidas-list');
    
    if (!partidas || partidas.length === 0) {
        container.innerHTML = `
            <div class="text-center py-8 text-gray-500">
                <i class="fas fa-calendar-alt text-4xl mb-4"></i>
                <p>Nenhuma partida agendada</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="space-y-4">';
    
    partidas.forEach(partida => {
        html += `
            <div class="bg-gray-50 p-4 rounded-lg">
                <div class="flex justify-between items-center">
                    <div>
                        <h4 class="font-bold">${formatDate(partida.data_partida)}</h4>
                        <p class="text-gray-600">${partida.horario_inicio || 'Horário não definido'}</p>
                        <p class="text-sm text-gray-500">${partida.local || currentPelada.local}</p>
                    </div>
                    <div class="text-right">
                        <span class="px-3 py-1 rounded-full text-sm ${
                            partida.status === 'realizada' ? 'bg-green-100 text-green-800' :
                            partida.status === 'cancelada' ? 'bg-red-100 text-red-800' :
                            'bg-blue-100 text-blue-800'
                        }">
                            ${partida.status}
                        </span>
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

async function loadFinanceiro() {
    if (!currentPelada) return;
    
    try {
        const response = await apiCall(`/peladas/${currentPelada.id}/financeiro`);
        
        if (response.success) {
            renderFinanceiro(response.financeiro);
        }
    } catch (error) {
        console.error('Erro ao carregar financeiro:', error);
        document.getElementById('financeiro-content').innerHTML = `
            <div class="text-center py-8 text-red-500">
                <p>Erro ao carregar dados financeiros</p>
            </div>
        `;
    }
}

function renderFinanceiro(financeiro) {
    const container = document.getElementById('financeiro-content');
    
    let html = `
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div class="bg-green-50 p-4 rounded-lg text-center">
                <h4 class="font-bold text-green-800">Total Entradas</h4>
                <p class="text-2xl font-bold text-green-600">${formatCurrency(financeiro.total_entradas)}</p>
            </div>
            <div class="bg-red-50 p-4 rounded-lg text-center">
                <h4 class="font-bold text-red-800">Total Saídas</h4>
                <p class="text-2xl font-bold text-red-600">${formatCurrency(financeiro.total_saidas)}</p>
            </div>
            <div class="bg-blue-50 p-4 rounded-lg text-center">
                <h4 class="font-bold text-blue-800">Saldo Atual</h4>
                <p class="text-2xl font-bold ${financeiro.saldo_atual >= 0 ? 'text-green-600' : 'text-red-600'}">
                    ${formatCurrency(financeiro.saldo_atual)}
                </p>
            </div>
        </div>
    `;
    
    if (financeiro.transacoes && financeiro.transacoes.length > 0) {
        html += '<div class="space-y-3">';
        
        financeiro.transacoes.forEach(transacao => {
            html += `
                <div class="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                    <div>
                        <h5 class="font-medium">${transacao.descricao}</h5>
                        <p class="text-sm text-gray-500">${formatDate(transacao.data_transacao)}</p>
                        ${transacao.responsavel_nome ? `<p class="text-xs text-gray-400">Por: ${transacao.responsavel_nome}</p>` : ''}
                    </div>
                    <div class="text-right">
                        <p class="font-bold ${transacao.tipo === 'entrada' ? 'text-green-600' : 'text-red-600'}">
                            ${transacao.tipo === 'entrada' ? '+' : '-'}${formatCurrency(transacao.valor)}
                        </p>
                        <p class="text-xs text-gray-500 capitalize">${transacao.tipo}</p>
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
    } else {
        html += `
            <div class="text-center py-8 text-gray-500">
                <i class="fas fa-money-bill-wave text-4xl mb-4"></i>
                <p>Nenhuma transação registrada</p>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

function loadJogadores() {
    document.getElementById('jogadores-list').innerHTML = `
        <div class="text-center py-8 text-gray-500">
            <i class="fas fa-users text-4xl mb-4"></i>
            <p>Funcionalidade em desenvolvimento</p>
        </div>
    `;
}

// Formulários
function showLoginForm() {
    elements.loginForm.style.display = 'block';
    elements.registerForm.style.display = 'none';
}

function showRegisterForm() {
    elements.loginForm.style.display = 'none';
    elements.registerForm.style.display = 'block';
}

// Event Listeners
document.addEventListener('DOMContentLoaded', function() {
    // Inicializar aplicação
    init();
    
    // Formulário de login
    document.getElementById('loginForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const email = document.getElementById('loginEmail').value;
        const senha = document.getElementById('loginPassword').value;
        login(email, senha);
    });
    
    // Formulário de cadastro
    document.getElementById('registerForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        formData.append('nome', document.getElementById('registerName').value);
        formData.append('email', document.getElementById('registerEmail').value);
        formData.append('senha', document.getElementById('registerPassword').value);
        formData.append('posicao', document.getElementById('registerPosition').value);
        
        const foto = document.getElementById('registerPhoto').files[0];
        if (foto) {
            formData.append('foto', foto);
        }
        
        register(formData);
    });
    
    // Formulário nova pelada
    document.getElementById('newPeladaForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        formData.append('nome', document.getElementById('peladaNome').value);
        formData.append('local', document.getElementById('peladaLocal').value);
        formData.append('descricao', document.getElementById('peladaDescricao').value);
        
        const foto = document.getElementById('peladaFoto').files[0];
        if (foto) {
            formData.append('foto', foto);
        }
        
        createPelada(formData);
    });
    
    // Navegação entre formulários
    document.getElementById('showRegister').addEventListener('click', function(e) {
        e.preventDefault();
        showRegisterForm();
    });
    
    document.getElementById('showLogin').addEventListener('click', function(e) {
        e.preventDefault();
        showLoginForm();
    });
    
    // Logout
    document.getElementById('logoutBtn').addEventListener('click', logout);
    
    // Botões do dashboard
    document.getElementById('newPeladaBtn').addEventListener('click', openNewPeladaModal);
    document.getElementById('backToDashboard').addEventListener('click', showDashboard);
    
    // Modal nova pelada
    document.getElementById('closeNewPeladaModal').addEventListener('click', closeNewPeladaModal);
    document.getElementById('cancelNewPelada').addEventListener('click', closeNewPeladaModal);
    
    // Fechar modal clicando fora
    document.getElementById('newPeladaModal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeNewPeladaModal();
        }
    });
    
    // Tabs
    document.querySelectorAll('.tab-button').forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            showTab(tabName);
        });
    });
});

// Funções globais para uso inline
window.openPelada = openPelada;
window.openNewPeladaModal = openNewPeladaModal;

