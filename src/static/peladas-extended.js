/**
 * Funcionalidades Estendidas - Partidas, Rankings e Financeiro
 * Extensão do sistema de peladas
 */

// Rankings da Pelada
async function loadPeladaRankings() {
    if (!window.PeladasApp.currentPelada) return;
    
    const peladaId = window.PeladasApp.currentPelada.id;
    const currentYear = new Date().getFullYear();
    
    try {
        // Carregar ranking geral da pelada
        const rankingGeral = await apiCall(`/peladas/${peladaId}/rankings/geral`);
        if (rankingGeral.success) {
            renderRankingPelada(rankingGeral.ranking, 'ranking-geral-pelada');
        }
        
        // Carregar ranking do ano
        const rankingAno = await apiCall(`/peladas/${peladaId}/rankings/ano/${currentYear}`);
        if (rankingAno.success) {
            renderRankingPelada(rankingAno.ranking, 'ranking-ano-pelada');
        }
        
        // Carregar ranking do mês
        const rankingMes = await apiCall(`/peladas/${peladaId}/rankings/mes`);
        if (rankingMes.success) {
            renderRankingPelada(rankingMes.ranking, 'ranking-mes-pelada');
        }
        
    } catch (error) {
        console.error('Erro ao carregar rankings da pelada:', error);
    }
}

function renderRankingPelada(ranking, containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    if (!ranking || ranking.length === 0) {
        container.innerHTML = `
            <div class="text-center py-4 text-gray-500">
                <i class="fas fa-trophy mb-2"></i>
                <p class="text-sm">Nenhum dado ainda</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="space-y-2">';
    
    ranking.slice(0, 5).forEach((jogador, index) => {
        const posicao = index + 1;
        const pontos = containerId.includes('geral') ? jogador.pontos_pelada : 
                      containerId.includes('ano') ? jogador.pontos_ano : 
                      jogador.pontos_mes;
        
        html += `
            <div class="flex items-center justify-between text-sm">
                <div class="flex items-center space-x-2">
                    <span class="w-6 h-6 ${posicao === 1 ? 'bg-yellow-400' : posicao === 2 ? 'bg-gray-400' : posicao === 3 ? 'bg-orange-400' : 'bg-gray-300'} text-white rounded-full flex items-center justify-center text-xs font-bold">${posicao}</span>
                    ${jogador.foto_url ? 
                        `<img src="${jogador.foto_url}" alt="${jogador.nome}" class="w-6 h-6 rounded-full object-cover">` :
                        `<div class="w-6 h-6 bg-blue-500 text-white rounded-full flex items-center justify-center text-xs font-bold">${jogador.nome.charAt(0)}</div>`
                    }
                    <span class="font-medium">${jogador.nome}</span>
                </div>
                <span class="font-bold">${pontos}</span>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

// Partidas
async function loadPartidas() {
    if (!window.PeladasApp.currentPelada) return;
    
    const peladaId = window.PeladasApp.currentPelada.id;
    
    try {
        const response = await apiCall(`/peladas/${peladaId}/partidas`);
        
        if (response.success) {
            renderPartidas(response.partidas);
        }
    } catch (error) {
        console.error('Erro ao carregar partidas:', error);
        const container = document.getElementById('partidas-list');
        if (container) {
            container.innerHTML = `
                <div class="text-center py-8 text-red-500">
                    <i class="fas fa-exclamation-triangle text-4xl mb-4"></i>
                    <p>Erro ao carregar partidas</p>
                </div>
            `;
        }
    }
}

function renderPartidas(partidas) {
    const container = document.getElementById('partidas-list');
    if (!container) return;
    
    if (!partidas || partidas.length === 0) {
        container.innerHTML = `
            <div class="text-center py-12 text-gray-500">
                <i class="fas fa-calendar-plus text-6xl mb-4"></i>
                <h3 class="text-xl font-bold mb-2">Nenhuma partida agendada</h3>
                <p class="mb-4">Crie a primeira partida para começar!</p>
                <button onclick="openNewPartidaModal()" class="bg-blue-500 hover:bg-blue-600 text-white px-6 py-3 rounded-lg transition duration-200">
                    <i class="fas fa-plus mr-2"></i>Criar Primeira Partida
                </button>
            </div>
        `;
        return;
    }
    
    let html = '<div class="space-y-4">';
    
    partidas.forEach(partida => {
        const dataPartida = new Date(partida.data_partida);
        const hoje = new Date();
        const isPassada = dataPartida < hoje;
        
        html += `
            <div class="bg-gray-50 rounded-lg p-4 border-l-4 ${
                partida.status === 'finalizada' ? 'border-green-500' :
                partida.status === 'em_votacao' ? 'border-yellow-500' :
                isPassada ? 'border-red-500' : 'border-blue-500'
            }">
                <div class="flex justify-between items-start mb-2">
                    <div>
                        <h4 class="font-bold text-lg">${formatDate(partida.data_partida)}</h4>
                        <p class="text-gray-600">
                            ${partida.horario_inicio} ${partida.horario_fim ? `- ${partida.horario_fim}` : ''}
                        </p>
                        ${partida.local ? `<p class="text-gray-500 text-sm"><i class="fas fa-map-marker-alt mr-1"></i>${partida.local}</p>` : ''}
                    </div>
                    <div class="text-right">
                        <span class="inline-block px-2 py-1 text-xs rounded-full ${
                            partida.status === 'finalizada' ? 'bg-green-100 text-green-800' :
                            partida.status === 'em_votacao' ? 'bg-yellow-100 text-yellow-800' :
                            'bg-blue-100 text-blue-800'
                        }">
                            ${partida.status === 'finalizada' ? 'Finalizada' :
                              partida.status === 'em_votacao' ? 'Em Votação' :
                              'Agendada'}
                        </span>
                    </div>
                </div>
                
                <div class="flex items-center justify-between">
                    <div class="flex space-x-4 text-sm">
                        <span class="text-green-600">
                            <i class="fas fa-check mr-1"></i>${partida.confirmados} confirmados
                        </span>
                        <span class="text-red-600">
                            <i class="fas fa-times mr-1"></i>${partida.nao_confirmados} recusaram
                        </span>
                        <span class="text-gray-600">
                            <i class="fas fa-clock mr-1"></i>${partida.pendentes} pendentes
                        </span>
                    </div>
                    
                    <div class="flex space-x-2">
                        <button onclick="viewPartidaDetails(${partida.id})" class="bg-blue-500 hover:bg-blue-600 text-white px-3 py-1 rounded text-sm">
                            Ver Detalhes
                        </button>
                        ${partida.status === 'agendada' ? 
                            `<button onclick="confirmarPresenca(${partida.id})" class="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm">
                                Confirmar
                            </button>` : ''
                        }
                    </div>
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

// Financeiro
async function loadFinanceiro() {
    if (!window.PeladasApp.currentPelada) return;
    
    const peladaId = window.PeladasApp.currentPelada.id;
    
    try {
        const [financeiroResponse, mensalidadesResponse] = await Promise.all([
            apiCall(`/peladas/${peladaId}/financeiro`),
            apiCall(`/peladas/${peladaId}/mensalidades`)
        ]);
        
        if (financeiroResponse.success && mensalidadesResponse.success) {
            renderFinanceiro(financeiroResponse.financeiro, mensalidadesResponse.mensalidades);
        }
    } catch (error) {
        console.error('Erro ao carregar financeiro:', error);
        const container = document.getElementById('financeiro-content');
        if (container) {
            container.innerHTML = `
                <div class="text-center py-8 text-red-500">
                    <i class="fas fa-exclamation-triangle text-4xl mb-4"></i>
                    <p>Erro ao carregar dados financeiros</p>
                </div>
            `;
        }
    }
}

function renderFinanceiro(financeiro, mensalidades) {
    const container = document.getElementById('financeiro-content');
    if (!container) return;
    
    const saldoColor = financeiro.saldo_atual >= 0 ? 'text-green-600' : 'text-red-600';
    
    let html = `
        <!-- Resumo Financeiro -->
        <div class="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
            <div class="bg-green-50 p-4 rounded-lg">
                <h4 class="font-bold text-green-800">Total Entradas</h4>
                <p class="text-2xl font-bold text-green-600">${formatCurrency(financeiro.total_entradas)}</p>
            </div>
            <div class="bg-red-50 p-4 rounded-lg">
                <h4 class="font-bold text-red-800">Total Saídas</h4>
                <p class="text-2xl font-bold text-red-600">${formatCurrency(financeiro.total_saidas)}</p>
            </div>
            <div class="bg-blue-50 p-4 rounded-lg">
                <h4 class="font-bold text-blue-800">Saldo Atual</h4>
                <p class="text-2xl font-bold ${saldoColor}">${formatCurrency(financeiro.saldo_atual)}</p>
            </div>
            <div class="bg-gray-50 p-4 rounded-lg">
                <h4 class="font-bold text-gray-800">Mensalidades</h4>
                <p class="text-2xl font-bold text-gray-600">${mensalidades.filter(m => m.pago).length}/${mensalidades.length}</p>
            </div>
        </div>
        
        <!-- Tabs Financeiro -->
        <div class="bg-white border rounded-lg">
            <div class="border-b">
                <nav class="flex space-x-8 px-6">
                    <button class="financeiro-tab-button py-3 px-2 border-b-2 border-blue-500 font-medium text-blue-600" data-tab="transacoes">
                        Transações
                    </button>
                    <button class="financeiro-tab-button py-3 px-2 border-b-2 border-transparent hover:border-gray-300 font-medium text-gray-500 hover:text-gray-700" data-tab="mensalidades">
                        Mensalidades
                    </button>
                </nav>
            </div>
            
            <div class="p-6">
                <!-- Transações -->
                <div id="transacoes-tab" class="financeiro-tab-content">
                    <div class="space-y-3">
    `;
    
    if (financeiro.transacoes && financeiro.transacoes.length > 0) {
        financeiro.transacoes.forEach(transacao => {
            const isEntrada = transacao.tipo === 'entrada';
            html += `
                <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div class="flex items-center space-x-3">
                        <div class="w-10 h-10 ${isEntrada ? 'bg-green-100' : 'bg-red-100'} rounded-full flex items-center justify-center">
                            <i class="fas ${isEntrada ? 'fa-arrow-up text-green-600' : 'fa-arrow-down text-red-600'}"></i>
                        </div>
                        <div>
                            <p class="font-medium">${transacao.descricao}</p>
                            <p class="text-sm text-gray-500">${formatDate(transacao.data_transacao)} • ${transacao.responsavel_nome || 'Sistema'}</p>
                        </div>
                    </div>
                    <div class="text-right">
                        <p class="font-bold ${isEntrada ? 'text-green-600' : 'text-red-600'}">
                            ${isEntrada ? '+' : '-'}${formatCurrency(transacao.valor)}
                        </p>
                        <p class="text-xs text-gray-500">${transacao.categoria}</p>
                    </div>
                </div>
            `;
        });
    } else {
        html += `
            <div class="text-center py-8 text-gray-500">
                <i class="fas fa-receipt text-4xl mb-4"></i>
                <p>Nenhuma transação registrada</p>
            </div>
        `;
    }
    
    html += `
                    </div>
                </div>
                
                <!-- Mensalidades -->
                <div id="mensalidades-tab" class="financeiro-tab-content" style="display: none;">
                    <div class="space-y-3">
    `;
    
    if (mensalidades && mensalidades.length > 0) {
        mensalidades.forEach(mensalidade => {
            html += `
                <div class="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                    <div class="flex items-center space-x-3">
                        ${mensalidade.foto_url ? 
                            `<img src="${mensalidade.foto_url}" alt="${mensalidade.jogador_nome}" class="w-10 h-10 rounded-full object-cover">` :
                            `<div class="w-10 h-10 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold">${mensalidade.jogador_nome.charAt(0)}</div>`
                        }
                        <div>
                            <p class="font-medium">${mensalidade.jogador_nome}</p>
                            <p class="text-sm text-gray-500">${mensalidade.mes}/${mensalidade.ano}</p>
                        </div>
                    </div>
                    <div class="flex items-center space-x-4">
                        <div class="text-right">
                            <p class="font-bold">${formatCurrency(mensalidade.valor)}</p>
                            <p class="text-xs ${mensalidade.pago ? 'text-green-600' : 'text-red-600'}">
                                ${mensalidade.pago ? 'Pago' : 'Pendente'}
                            </p>
                        </div>
                        <div class="w-6 h-6 rounded-full ${mensalidade.pago ? 'bg-green-500' : 'bg-red-500'} flex items-center justify-center">
                            <i class="fas ${mensalidade.pago ? 'fa-check' : 'fa-times'} text-white text-xs"></i>
                        </div>
                    </div>
                </div>
            `;
        });
    } else {
        html += `
            <div class="text-center py-8 text-gray-500">
                <i class="fas fa-calendar-check text-4xl mb-4"></i>
                <p>Nenhuma mensalidade registrada</p>
            </div>
        `;
    }
    
    html += `
                    </div>
                </div>
            </div>
        </div>
    `;
    
    container.innerHTML = html;
    
    // Adicionar event listeners para as abas do financeiro
    document.querySelectorAll('.financeiro-tab-button').forEach(button => {
        button.addEventListener('click', function() {
            const tabName = this.getAttribute('data-tab');
            showFinanceiroTab(tabName);
        });
    });
}

function showFinanceiroTab(tabName) {
    // Remover classe active de todas as abas
    document.querySelectorAll('.financeiro-tab-button').forEach(btn => {
        btn.classList.remove('border-blue-500', 'text-blue-600');
        btn.classList.add('border-transparent', 'text-gray-500');
    });
    
    document.querySelectorAll('.financeiro-tab-content').forEach(content => {
        content.style.display = 'none';
    });
    
    // Ativar aba selecionada
    const activeButton = document.querySelector(`[data-tab="${tabName}"]`);
    if (activeButton) {
        activeButton.classList.remove('border-transparent', 'text-gray-500');
        activeButton.classList.add('border-blue-500', 'text-blue-600');
    }
    
    const activeContent = document.getElementById(`${tabName}-tab`);
    if (activeContent) {
        activeContent.style.display = 'block';
    }
}

// Jogadores
async function loadJogadores() {
    if (!window.PeladasApp.currentPelada) return;
    
    const peladaId = window.PeladasApp.currentPelada.id;
    
    try {
        const response = await apiCall(`/peladas/${peladaId}/membros`);
        
        if (response.success) {
            renderJogadores(response.membros);
        }
    } catch (error) {
        console.error('Erro ao carregar jogadores:', error);
        const container = document.getElementById('jogadores-list');
        if (container) {
            container.innerHTML = `
                <div class="text-center py-8 text-red-500">
                    <i class="fas fa-exclamation-triangle text-4xl mb-4"></i>
                    <p>Erro ao carregar membros</p>
                </div>
            `;
        }
    }
}

function renderJogadores(jogadores) {
    const container = document.getElementById('jogadores-list');
    if (!container) return;
    
    if (!jogadores || jogadores.length === 0) {
        container.innerHTML = `
            <div class="text-center py-12 text-gray-500">
                <i class="fas fa-users text-6xl mb-4"></i>
                <h3 class="text-xl font-bold mb-2">Nenhum membro encontrado</h3>
                <p>Esta pelada ainda não tem membros.</p>
            </div>
        `;
        return;
    }
    
    let html = '<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">';
    
    jogadores.forEach(jogador => {
        html += `
            <div class="bg-gray-50 rounded-lg p-4">
                <div class="flex items-center space-x-3 mb-3">
                    ${jogador.foto_url ? 
                        `<img src="${jogador.foto_url}" alt="${jogador.nome}" class="w-12 h-12 rounded-full object-cover">` :
                        `<div class="w-12 h-12 bg-blue-500 text-white rounded-full flex items-center justify-center font-bold text-lg">${jogador.nome.charAt(0)}</div>`
                    }
                    <div class="flex-1">
                        <h4 class="font-bold text-lg">${jogador.nome}</h4>
                        <p class="text-gray-600 text-sm">${jogador.posicao || 'Posição não informada'}</p>
                    </div>
                    ${jogador.is_admin ? 
                        '<span class="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded-full">Admin</span>' :
                        '<span class="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded-full">Membro</span>'
                    }
                </div>
                
                <div class="grid grid-cols-2 gap-4 text-sm">
                    <div class="text-center">
                        <p class="font-bold text-lg">${jogador.pontos_totais || 0}</p>
                        <p class="text-gray-500">Pontos Totais</p>
                    </div>
                    <div class="text-center">
                        <p class="font-bold text-lg">${jogador.media_pontos || '0.00'}</p>
                        <p class="text-gray-500">Média</p>
                    </div>
                </div>
                
                <div class="mt-3 text-xs text-gray-500 text-center">
                    Membro desde ${formatDate(jogador.joined_at)}
                </div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

// Funções de modal e interação
function openNewPartidaModal() {
    // Implementar modal de nova partida
    showAlert('Funcionalidade em desenvolvimento', 'info');
}

function openNewTransacaoModal() {
    // Implementar modal de nova transação
    showAlert('Funcionalidade em desenvolvimento', 'info');
}

function openSearchPeladaModal() {
    // Implementar modal de busca de peladas
    showAlert('Funcionalidade em desenvolvimento', 'info');
}

function viewPartidaDetails(partidaId) {
    // Implementar visualização de detalhes da partida
    showAlert('Funcionalidade em desenvolvimento', 'info');
}

function confirmarPresenca(partidaId) {
    // Implementar confirmação de presença
    showAlert('Funcionalidade em desenvolvimento', 'info');
}

// Atualizar referências globais
window.loadPeladaRankings = loadPeladaRankings;
window.loadPartidas = loadPartidas;
window.loadFinanceiro = loadFinanceiro;
window.loadJogadores = loadJogadores;
window.openNewPartidaModal = openNewPartidaModal;
window.openNewTransacaoModal = openNewTransacaoModal;
window.openSearchPeladaModal = openSearchPeladaModal;
window.viewPartidaDetails = viewPartidaDetails;
window.confirmarPresenca = confirmarPresenca;

