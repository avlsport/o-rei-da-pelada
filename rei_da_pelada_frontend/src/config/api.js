// Configuração da API
const API_BASE_URL = 'http://localhost:5001'

export const API_ENDPOINTS = {
  // Auth
  LOGIN: `${API_BASE_URL}/api/auth/login`,
  REGISTER: `${API_BASE_URL}/api/auth/register`,
  CHECK_AUTH: `${API_BASE_URL}/api/auth/check-auth`,
  LOGOUT: `${API_BASE_URL}/api/auth/logout`,
  
  // Peladas
  PELADAS: `${API_BASE_URL}/api/peladas`,
  MY_PELADAS: `${API_BASE_URL}/api/peladas/my`,
  JOIN_PELADA: `${API_BASE_URL}/api/peladas/join`,
  
  // Users
  USER_STATS: (userId) => `${API_BASE_URL}/api/users/${userId}/stats`,
  
  // Rankings
  GLOBAL_RANKING: `${API_BASE_URL}/api/ranking/global`,
  
  // Matches
  MATCHES: `${API_BASE_URL}/api/matches`,
  
  // Financial
  FINANCIAL: `${API_BASE_URL}/api/financial`
}

export default API_BASE_URL

