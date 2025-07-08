/**
 * Funcionalidades de Peladas
 * Adiciona ao sistema existente sem quebrar o que já funciona
 */

// Estado global para peladas
window.PeladasApp = {
    currentUser: null,
    currentPelada: null,
    peladas: [],
    rankings: null
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
    alert.className = `fixed top-4 right-4 z-50 p-4 rounded-lg text-white max-w-sm shadow-lg ${
        type === 'success' ? 'bg-green-500' : 
        type === 'error' ? 'bg-red-500' : 
        'bg-blue-500'
    }`;
    alert.innerHTML = `
        <div class="flex items-center justify-between">
            <span>${message}</span>
            <button onclick="this.parentElement.parentElement.remove()" class="ml-4 text-white hover:text-gray-200">
                ×
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

// Ranking Geral
async function loadRankingGeral() {
    try {
        const response = await apiCall('/rankings/geral');
        
        if (response.success) {
            renderRankingGeral(response.ranking);
        }
    } catch (error) {
        console.error('Erro ao carregar ranking geral:', error);
        const container = document.getElementById('ranking-geral-container');
        if (container) {
            container.innerHTML = `
                <div class="text-center py-4 text-red-500">
                    <i class="fas fa-exclamation-triangle mb-2"></i>
                    <p>Erro ao carregar ranking</p>
                </div>
            `;
        }
    }
}

function renderRankingGeral(ranking) {
    const container = document.getElementById('ranking-geral-container');
    if (!container) return;
    
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
        const isCurrentUser = window.PeladasApp.currentUser && jogador.id === window.PeladasApp.currentUser.id;
        
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
                            <p class="text-sm text-gray-500">${jogador.pelada_principal || 'Sem pelada'}</p>
                        </div>
                    </div>
                </div>
                <div class="text-right">
                    <p class="font-bold text-lg ${isCurrentUser ? 'text-blue-700' : 'text-gray-800'}">${jogador.media_pontos}</p>
                    <p class="text-sm text-gray-500">média</p>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    
    // Mostrar posição do usuário se não estiver no top 10
    if (ranking.posicao_usuario > 10 && ranking.usuario_atual) {
        html += `
            <div class="mt-6 p-4 bg-blue-50 border-2 border-blue-200 rounded-lg">
                <h4 class="font-bold text-blue-700 mb-2">Sua Posição</h4>
                <div class="flex items-center justify-between">
                    <div class="flex items-center space-x-3">
                        <span class="w-8 h-8 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold text-sm">${ranking.posicao_usuario}</span>
                        <div>
                            <p class="font-medium text-blue-700">${ranking.usuario_atual.nome}</p>
                            <p class="text-sm text-blue-600">${ranking.usuario_atual.pelada_principal || 'Sem pelada'}</p>
                        </div>
                    </div>
                    <div class="text-right">
                        <p class="font-bold text-lg text-blue-700">${ranking.usuario_atual.media_pontos}</p>
                        <p class="text-sm text-blue-600">média</p>
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
            window.PeladasApp.peladas = response.peladas;
            renderPeladas(response.peladas);
        }
    } catch (error) {
        console.error('Erro ao carregar peladas:', error);
        const container = document.getElementById('peladas-list-container');
        if (container) {
            container.innerHTML = `
                <div class="text-center py-8 text-red-500">
                    <i class="fas fa-exclamation-triangle text-4xl mb-4"></i>
                    <p>Erro ao carregar peladas</p>
                </div>
            `;
        }
    }
}

function renderPeladas(peladas) {
    const container = document.getElementById('peladas-list-container');
    if (!container) return;
    
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
            <div class="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow cursor-pointer" onclick="openPelada(${pelada.id})">
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
    const pelada = window.PeladasApp.peladas.find(p => p.id === peladaId);
    if (pelada) {
        window.PeladasApp.currentPelada = pelada;
        showPeladaDashboard(pelada);
    }
}

function showPeladaDashboard(pelada) {
    // Esconder dashboard principal
    const mainDashboard = document.getElementById('main-dashboard');
    if (mainDashboard) {
        mainDashboard.style.display = 'none';
    }
    
    // Mostrar dashboard da pelada
    let peladaDashboard = document.getElementById('pelada-dashboard');
    if (!peladaDashboard) {
        createPeladaDashboard();
        peladaDashboard = document.getElementById('pelada-dashboard');
    }
    
    peladaDashboard.style.display = 'block';
    
    // Atualizar título
    const title = document.getElementById('pelada-title');
    if (title) {
        title.textContent = pelada.nome;
    }
    
    // Carregar primeira aba (rankings)
    showPeladaTab('rankings');
}

function createPeladaDashboard() {
    const container = document.querySelector('.container');
    if (!container) return;
    
    const dashboardHTML = `
        <div id="pelada-dashboard" style="display: none;">
            <div class="mb-6">
                <button onclick="backToMainDashboard()" class="text-blue-500 hover:text-blue-700 mb-4">
                    <i class="fas fa-arrow-left mr-2"></i>Voltar ao Dashboard
                </button>
                <h2 id="pelada-title" class="text-3xl font-bold text-gray-800"></h2>
            </div>

            <!-- Tabs -->
            <div class="bg-white rounded-lg shadow-lg mb-6">
                <div class="border-b">
                    <nav class="flex space-x-8 px-6">
                        <button class="pelada-tab-button py-4 px-2 border-b-2 border-blue-500 font-medium text-blue-600" data-tab="rankings">
                            🏆 Rankings
                        </button>
                        <button class="pelada-tab-button py-4 px-2 border-b-2 border-transparent hover:border-gray-300 font-medium text-gray-500 hover:text-gray-700" data-tab="partidas">
                            ⚽ Partidas
                        </button>
                        <button class="pelada-tab-button py-4 px-2 border-b-2 border-transparent hover:border-gray-300 font-medium text-gray-500 hover:text-gray-700" data-tab="financeiro">
                            💰 Financeiro
                        </button>
                        <button class="pelada-tab-button py-4 px-2 border-b-2 border-transparent hover:border-gray-300 font-medium text-gray-500 hover:text-gray-700" data-tab="jogadores">
                            👥 Jogadores
                        </button>
                    </nav>
                </div>

                <!-- Tab Contents -->
                <div class="p-6">
                    <!-- Rankings Tab -->
                    <div id="rankings-tab-content" class="pelada-tab-content">
                        <h3 class="text-xl font-bold mb-4">Rankings da Pelada</h3>
                        <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
                            <div class="bg-gray-50 p-4 rounded-lg">
                                <h4 class="font-bold text-lg mb-2">Geral</h4>
                                <div id="ranking-geral-pelada">Carregando...</div>
                            </div>
                            <div class="bg-gray-50 p-4 rounded-lg">
                                <h4 class="font-bold text-lg mb-2">Este Ano</h4>
                                <div id="ranking-ano-pelada">Carregando...</div>
                            </div>
                            <div class="bg-gray-50 p-4 rounded-lg">
                                <h4 class="font-bold text-lg mb-2">Último Mês</h4>
                                <div id="ranking-mes-pelada">Carregando...</div>
                            </div>
                        </div>
                    </div>

                    <!-- Partidas Tab -->
                    <div id="partidas-tab-content" class="pelada-tab-content" style="display: none;">
                        <div class="flex justify-between items-center mb-4">
                            <h3 class="text-xl font-bold">Partidas</h3>
                            <button onclick="openNewPartidaModal()" class="bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg">
                                <i class="fas fa-plus mr-2"></i>Nova Partida
                            </button>
                        </div>
                        <div id="partidas-list">Carregando partidas...</div>
                    </div>

                    <!-- Financeiro Tab -->
                    <div id="financeiro-tab-content" class="pelada-tab-content" style="display: none;">
                        <div class="flex justify-between items-center mb-4">
                            <h3 class="text-xl font-bold">Controle Financeiro</h3>
                            <button onclick="openNewTransacaoModal()" class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg">
                                <i class="fas fa-plus mr-2"></i>Nova Transação
                            </button>
                        </div>
                        <div id="financeiro-content">Carregando dados financeiros...</div>
                    </div>

                    <!-- Jogadores Tab -->
                    <div id="jogadores-tab-content" class="pelada-tab-content" style="display: none;">
                        <div class="flex justify-between items-center mb-4">
                            <h3 class="text-xl font-bold">Membros da Pelada</h3>
                            <button onclick="openSearchPeladaModal()" class="bg-purple-500 hover:bg-purple-600 text-white px-4 py-2 rounded-lg">
                                <i class="fas fa-search mr-2"></i>Buscar Peladas
                            </button>
                        </div>
                        <div id="jogadores-list">Carregando membros...</div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', dashboardHTML);
    
    // Adicionar event listeners para as abas
    document.querySelectorAll('.pelada-tab-button').forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            showPeladaTab(tabName);
        });
    });
}

function showPeladaTab(tabName) {
    // Remover classe active de todas as abas
    document.querySelectorAll('.pelada-tab-button').forEach(btn => {
        btn.classList.remove('border-blue-500', 'text-blue-600');
        btn.classList.add('border-transparent', 'text-gray-500');
    });
    
    document.querySelectorAll('.pelada-tab-content').forEach(content => {
        content.style.display = 'none';
    });
    
    // Ativar aba selecionada
    const activeButton = document.querySelector(`[data-tab="${tabName}"]`);
    if (activeButton) {
        activeButton.classList.remove('border-transparent', 'text-gray-500');
        activeButton.classList.add('border-blue-500', 'text-blue-600');
    }
    
    const activeContent = document.getElementById(`${tabName}-tab-content`);
    if (activeContent) {
        activeContent.style.display = 'block';
    }
    
    // Carregar conteúdo da aba se necessário
    if (tabName === 'rankings') {
        loadPeladaRankings();
    } else if (tabName === 'partidas') {
        loadPartidas();
    } else if (tabName === 'financeiro') {
        loadFinanceiro();
    } else if (tabName === 'jogadores') {
        loadJogadores();
    }
}

function backToMainDashboard() {
    const mainDashboard = document.getElementById('main-dashboard');
    const peladaDashboard = document.getElementById('pelada-dashboard');
    
    if (mainDashboard) {
        mainDashboard.style.display = 'block';
    }
    if (peladaDashboard) {
        peladaDashboard.style.display = 'none';
    }
    
    window.PeladasApp.currentPelada = null;
}

// Modais
function openNewPeladaModal() {
    let modal = document.getElementById('new-pelada-modal');
    if (!modal) {
        createNewPeladaModal();
        modal = document.getElementById('new-pelada-modal');
    }
    modal.style.display = 'flex';
}

function createNewPeladaModal() {
    const modalHTML = `
        <div id="new-pelada-modal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50" style="display: none;">
            <div class="bg-white rounded-lg p-6 w-full max-w-md mx-4">
                <div class="flex justify-between items-center mb-4">
                    <h3 class="text-xl font-bold">Nova Pelada</h3>
                    <button onclick="closeNewPeladaModal()" class="text-gray-500 hover:text-gray-700">
                        <i class="fas fa-times"></i>
                    </button>
                </div>
                <form id="new-pelada-form" enctype="multipart/form-data">
                    <div class="mb-4">
                        <label class="block text-gray-700 text-sm font-bold mb-2">Nome da Pelada</label>
                        <input type="text" id="pelada-nome" class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500" required>
                    </div>
                    <div class="mb-4">
                        <label class="block text-gray-700 text-sm font-bold mb-2">Local</label>
                        <input type="text" id="pelada-local" class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500" required>
                    </div>
                    <div class="mb-4">
                        <label class="block text-gray-700 text-sm font-bold mb-2">Descrição</label>
                        <textarea id="pelada-descricao" class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500" rows="3"></textarea>
                    </div>
                    <div class="mb-6">
                        <label class="block text-gray-700 text-sm font-bold mb-2">Foto da Pelada</label>
                        <input type="file" id="pelada-foto" accept="image/*" class="w-full px-3 py-2 border rounded-lg focus:outline-none focus:border-blue-500">
                    </div>
                    <div class="flex space-x-4">
                        <button type="button" onclick="closeNewPeladaModal()" class="flex-1 bg-gray-500 text-white py-2 px-4 rounded-lg hover:bg-gray-600 transition duration-200">
                            Cancelar
                        </button>
                        <button type="submit" class="flex-1 bg-blue-500 text-white py-2 px-4 rounded-lg hover:bg-blue-600 transition duration-200">
                            Criar Pelada
                        </button>
                    </div>
                </form>
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    
    // Adicionar event listener para o formulário
    document.getElementById('new-pelada-form').addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData();
        formData.append('nome', document.getElementById('pelada-nome').value);
        formData.append('local', document.getElementById('pelada-local').value);
        formData.append('descricao', document.getElementById('pelada-descricao').value);
        
        const foto = document.getElementById('pelada-foto').files[0];
        if (foto) {
            formData.append('foto', foto);
        }
        
        createPelada(formData);
    });
}

function closeNewPeladaModal() {
    const modal = document.getElementById('new-pelada-modal');
    if (modal) {
        modal.style.display = 'none';
        document.getElementById('new-pelada-form').reset();
    }
}

// Funções placeholder para outras funcionalidades
async function loadPeladaRankings() {
    // Implementar carregamento dos rankings da pelada
    console.log('Carregando rankings da pelada...');
}

async function loadPartidas() {
    // Implementar carregamento das partidas
    console.log('Carregando partidas...');
}

async function loadFinanceiro() {
    // Implementar carregamento do financeiro
    console.log('Carregando financeiro...');
}

async function loadJogadores() {
    // Implementar carregamento dos jogadores
    console.log('Carregando jogadores...');
}

// Funções globais para uso inline
window.openPelada = openPelada;
window.openNewPeladaModal = openNewPeladaModal;
window.closeNewPeladaModal = closeNewPeladaModal;
window.backToMainDashboard = backToMainDashboard;

// Inicialização quando o DOM estiver pronto
document.addEventListener('DOMContentLoaded', function() {
    // Aguardar um pouco para garantir que o React carregou
    setTimeout(() => {
        // Verificar se o usuário está logado
        const userInfo = document.querySelector('[data-user-info]');
        if (userInfo) {
            try {
                window.PeladasApp.currentUser = JSON.parse(userInfo.getAttribute('data-user-info'));
            } catch (e) {
                console.log('Usuário não logado ou dados inválidos');
            }
        }
        
        // Adicionar seção de ranking geral se não existir
        addRankingGeralSection();
        
        // Adicionar seção de peladas se não existir
        addPeladasSection();
        
        // Carregar dados iniciais
        loadRankingGeral();
        loadPeladas();
    }, 1000);
});

function addRankingGeralSection() {
    // Procurar por um container principal do dashboard
    const dashboard = document.querySelector('.dashboard, .main-content, .container');
    if (!dashboard) return;
    
    // Verificar se já existe
    if (document.getElementById('ranking-geral-section')) return;
    
    const rankingHTML = `
        <div id="ranking-geral-section" class="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h3 class="text-2xl font-bold text-gray-800 mb-4">🏆 Ranking Geral do Aplicativo</h3>
            <div id="ranking-geral-container">
                <div class="text-center py-8">
                    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                    <p class="mt-2 text-gray-600">Carregando ranking...</p>
                </div>
            </div>
        </div>
    `;
    
    dashboard.insertAdjacentHTML('afterbegin', rankingHTML);
}

function addPeladasSection() {
    // Procurar por um container principal do dashboard
    const dashboard = document.querySelector('.dashboard, .main-content, .container');
    if (!dashboard) return;
    
    // Verificar se já existe
    if (document.getElementById('peladas-section')) return;
    
    const peladasHTML = `
        <div id="peladas-section" class="bg-white rounded-lg shadow-lg p-6 mb-8">
            <div class="flex justify-between items-center mb-4">
                <h3 class="text-2xl font-bold text-gray-800">⚽ Minhas Peladas</h3>
                <button onclick="openNewPeladaModal()" class="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg transition duration-200">
                    <i class="fas fa-plus mr-2"></i>Nova Pelada
                </button>
            </div>
            <div id="peladas-list-container">
                <div class="text-center py-8">
                    <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500 mx-auto"></div>
                    <p class="mt-2 text-gray-600">Carregando peladas...</p>
                </div>
            </div>
        </div>
        <div id="main-dashboard"></div>
    `;
    
    dashboard.insertAdjacentHTML('beforeend', peladasHTML);
}

