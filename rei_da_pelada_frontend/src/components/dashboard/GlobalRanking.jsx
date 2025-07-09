import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Trophy, 
  Medal, 
  Crown, 
  Target, 
  Users, 
  TrendingUp,
  Star,
  Award,
  Zap,
  Filter,
  RefreshCw
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'

const GlobalRanking = ({ user }) => {
  const [ranking, setRanking] = useState({ top_10: [], user_position: null })
  const [loading, setLoading] = useState(true)
  const [refreshing, setRefreshing] = useState(false)

  useEffect(() => {
    fetchGlobalRanking()
  }, [])

  const fetchGlobalRanking = async () => {
    try {
      setRefreshing(true)
      const response = await fetch('/api/ranking/global', {
        credentials: 'include'
      })
      const data = await response.json()
      setRanking(data)
    } catch (error) {
      console.error('Erro ao buscar ranking global:', error)
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }

  const getPositionIcon = (position) => {
    switch (position) {
      case 1: return Crown
      case 2: return Trophy
      case 3: return Medal
      default: return Star
    }
  }

  const getPositionColor = (position) => {
    switch (position) {
      case 1: return 'from-yellow-400 to-yellow-600'
      case 2: return 'from-gray-300 to-gray-500'
      case 3: return 'from-orange-400 to-orange-600'
      default: return 'from-blue-400 to-blue-600'
    }
  }

  const getPositionBadgeColor = (position) => {
    switch (position) {
      case 1: return 'bg-gradient-to-r from-yellow-500 to-yellow-600 text-white'
      case 2: return 'bg-gradient-to-r from-gray-400 to-gray-500 text-white'
      case 3: return 'bg-gradient-to-r from-orange-500 to-orange-600 text-white'
      default: return 'bg-gray-100 text-gray-700'
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 bg-gray-200 rounded animate-pulse"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[...Array(3)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-32 bg-gray-200 rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
        <Card className="animate-pulse">
          <CardContent className="p-6">
            <div className="h-64 bg-gray-200 rounded"></div>
          </CardContent>
        </Card>
      </div>
    )
  }

  const topThree = ranking.top_10.slice(0, 3)
  const restOfTop10 = ranking.top_10.slice(3)

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Ranking Geral</h1>
          <p className="text-gray-600">Os melhores jogadores de todas as peladas</p>
        </div>
        <Button
          onClick={fetchGlobalRanking}
          disabled={refreshing}
          variant="outline"
          className="hover:bg-blue-50"
        >
          {refreshing ? (
            <div className="flex items-center">
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
              Atualizando...
            </div>
          ) : (
            <>
              <RefreshCw className="w-4 h-4 mr-2" />
              Atualizar
            </>
          )}
        </Button>
      </div>

      {ranking.top_10.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-16"
        >
          <div className="w-24 h-24 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center mx-auto mb-6">
            <Trophy className="w-12 h-12 text-gray-400" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Ranking ainda não disponível</h3>
          <p className="text-gray-600 max-w-md mx-auto">
            O ranking será gerado após as primeiras partidas serem jogadas e avaliadas.
          </p>
        </motion.div>
      ) : (
        <>
          {/* Pódio - Top 3 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {topThree.map((player, index) => {
              const position = index + 1
              const PositionIcon = getPositionIcon(position)
              
              return (
                <motion.div
                  key={player.user_id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`${position === 1 ? 'md:order-2' : position === 2 ? 'md:order-1' : 'md:order-3'}`}
                >
                  <Card className={`relative overflow-hidden ${position === 1 ? 'ring-2 ring-yellow-400 transform scale-105' : ''}`}>
                    <div className={`absolute inset-0 bg-gradient-to-br ${getPositionColor(position)} opacity-10`}></div>
                    <CardContent className="p-6 relative z-10">
                      <div className="text-center space-y-4">
                        {/* Ícone da posição */}
                        <div className={`w-16 h-16 bg-gradient-to-br ${getPositionColor(position)} rounded-full flex items-center justify-center mx-auto shadow-lg`}>
                          <PositionIcon className="w-8 h-8 text-white" />
                        </div>

                        {/* Avatar do jogador */}
                        <div className="relative">
                          <Avatar className="h-20 w-20 mx-auto ring-4 ring-white shadow-xl">
                            <AvatarImage src={player.user_photo_url} alt={player.user_name} />
                            <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white text-lg font-bold">
                              {player.user_name.charAt(0).toUpperCase()}
                            </AvatarFallback>
                          </Avatar>
                          <Badge className={`absolute -bottom-2 left-1/2 transform -translate-x-1/2 ${getPositionBadgeColor(position)} border-0`}>
                            #{position}
                          </Badge>
                        </div>

                        {/* Informações do jogador */}
                        <div>
                          <h3 className="text-lg font-bold text-gray-900">{player.user_name}</h3>
                          <p className="text-sm text-gray-600">{player.user_position}</p>
                        </div>

                        {/* Estatísticas */}
                        <div className="grid grid-cols-2 gap-4 text-center">
                          <div>
                            <div className="text-2xl font-bold text-gray-900">{player.avg_points}</div>
                            <div className="text-xs text-gray-600">Média</div>
                          </div>
                          <div>
                            <div className="text-2xl font-bold text-gray-900">{player.total_matches}</div>
                            <div className="text-xs text-gray-600">Partidas</div>
                          </div>
                        </div>

                        {/* Indicador se é o usuário atual */}
                        {player.user_id === user.id && (
                          <Badge className="bg-blue-100 text-blue-800 border-blue-200">
                            Você
                          </Badge>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                </motion.div>
              )
            })}
          </div>

          {/* Ranking completo */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Trophy className="w-5 h-5 text-yellow-600" />
                <span>Top 10 Jogadores</span>
              </CardTitle>
              <CardDescription>Ranking baseado na média de pontos por partida</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {ranking.top_10.map((player, index) => (
                  <motion.div
                    key={player.user_id}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: index * 0.05 }}
                    className={`flex items-center justify-between p-4 rounded-lg transition-all duration-300 hover:shadow-md ${
                      player.user_id === user.id 
                        ? 'bg-blue-50 border-2 border-blue-200' 
                        : 'bg-gray-50 hover:bg-gray-100'
                    }`}
                  >
                    <div className="flex items-center space-x-4">
                      {/* Posição */}
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-sm ${
                        index < 3 
                          ? `bg-gradient-to-r ${getPositionColor(index + 1)} text-white` 
                          : 'bg-gray-200 text-gray-700'
                      }`}>
                        {player.position}
                      </div>

                      {/* Avatar e informações */}
                      <Avatar className="h-12 w-12 ring-2 ring-white shadow-md">
                        <AvatarImage src={player.user_photo_url} alt={player.user_name} />
                        <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white font-semibold">
                          {player.user_name.charAt(0).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>

                      <div>
                        <div className="flex items-center space-x-2">
                          <h3 className="font-semibold text-gray-900">{player.user_name}</h3>
                          {player.user_id === user.id && (
                            <Badge variant="secondary" className="text-xs">Você</Badge>
                          )}
                        </div>
                        <p className="text-sm text-gray-600">{player.user_position}</p>
                      </div>
                    </div>

                    {/* Estatísticas */}
                    <div className="flex items-center space-x-6 text-sm">
                      <div className="text-center">
                        <div className="font-bold text-gray-900">{player.avg_points}</div>
                        <div className="text-gray-600">Média</div>
                      </div>
                      <div className="text-center">
                        <div className="font-bold text-gray-900">{player.total_matches}</div>
                        <div className="text-gray-600">Partidas</div>
                      </div>
                      <div className="text-center">
                        <div className="font-bold text-gray-900">{player.total_goals}</div>
                        <div className="text-gray-600">Gols</div>
                      </div>
                      <div className="text-center">
                        <div className="font-bold text-gray-900">{player.total_assists}</div>
                        <div className="text-gray-600">Assistências</div>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Posição do usuário se não estiver no top 10 */}
          {ranking.user_position && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.5 }}
            >
              <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
                <CardHeader>
                  <CardTitle className="flex items-center space-x-2 text-blue-900">
                    <Target className="w-5 h-5" />
                    <span>Sua Posição</span>
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="flex items-center justify-between p-4 bg-white rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center font-bold text-sm text-white">
                        {ranking.user_position.position}
                      </div>
                      <Avatar className="h-12 w-12 ring-2 ring-blue-200 shadow-md">
                        <AvatarImage src={ranking.user_position.user_photo_url} alt={ranking.user_position.user_name} />
                        <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white font-semibold">
                          {ranking.user_position.user_name.charAt(0).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <h3 className="font-semibold text-gray-900">{ranking.user_position.user_name}</h3>
                        <p className="text-sm text-gray-600">{ranking.user_position.user_position}</p>
                      </div>
                    </div>
                    <div className="flex items-center space-x-6 text-sm">
                      <div className="text-center">
                        <div className="font-bold text-gray-900">{ranking.user_position.avg_points}</div>
                        <div className="text-gray-600">Média</div>
                      </div>
                      <div className="text-center">
                        <div className="font-bold text-gray-900">{ranking.user_position.total_matches}</div>
                        <div className="text-gray-600">Partidas</div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Informações sobre o ranking */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.6 }}
          >
            <Card className="bg-gradient-to-r from-yellow-50 to-orange-50 border-yellow-200">
              <CardContent className="p-6">
                <div className="flex items-start space-x-4">
                  <div className="w-10 h-10 bg-yellow-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <Award className="w-5 h-5 text-yellow-600" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-yellow-900 mb-1">Como funciona o ranking?</h3>
                    <p className="text-yellow-800 text-sm">
                      O ranking é baseado na média de pontos por partida. Os pontos são calculados considerando 
                      gols (8 pts), assistências (5 pts), desarmes (1 pt), defesas para goleiros (2 pts), 
                      votos de MVP (+3 pts) e votos de pior jogador (-3 pts). Apenas partidas com votação 
                      encerrada são consideradas.
                    </p>
                  </div>
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </>
      )}
    </div>
  )
}

export default GlobalRanking

