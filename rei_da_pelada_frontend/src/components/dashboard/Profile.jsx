import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  User, 
  Trophy, 
  Target, 
  Users, 
  TrendingUp, 
  Calendar,
  Award,
  Star,
  Shield,
  Zap,
  Edit,
  Camera
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Progress } from '@/components/ui/progress'

const Profile = ({ user }) => {
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchUserStats()
  }, [])

  const fetchUserStats = async () => {
    try {
      const response = await fetch(`/api/users/${user.id}/stats`, {
        credentials: 'include'
      })
      const data = await response.json()
      setStats(data)
    } catch (error) {
      console.error('Erro ao buscar estatísticas:', error)
    } finally {
      setLoading(false)
    }
  }

  const getPositionIcon = (position) => {
    switch (position) {
      case 'Goleiro': return Shield
      case 'Zagueiro': return Users
      case 'Meio Campo': return Zap
      case 'Atacante': return Target
      default: return User
    }
  }

  const getPositionColor = (position) => {
    switch (position) {
      case 'Goleiro': return 'from-yellow-400 to-orange-500'
      case 'Zagueiro': return 'from-blue-400 to-blue-600'
      case 'Meio Campo': return 'from-green-400 to-green-600'
      case 'Atacante': return 'from-red-400 to-red-600'
      default: return 'from-gray-400 to-gray-600'
    }
  }

  const calculateOverall = () => {
    if (!stats?.general_stats) return 75
    
    const { total_matches, avg_points, total_goals, total_assists } = stats.general_stats
    
    // Fórmula simples para calcular overall baseado nas estatísticas
    let overall = 60 // Base
    
    if (total_matches > 0) overall += Math.min(total_matches * 2, 20) // Máximo 20 pontos por experiência
    if (avg_points > 0) overall += Math.min(avg_points, 15) // Máximo 15 pontos por média
    if (total_goals > 0) overall += Math.min(total_goals * 0.5, 10) // Máximo 10 pontos por gols
    if (total_assists > 0) overall += Math.min(total_assists * 0.3, 5) // Máximo 5 pontos por assistências
    
    return Math.min(Math.round(overall), 99)
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="animate-pulse">
            <CardContent className="p-6">
              <div className="h-64 bg-gray-200 rounded"></div>
            </CardContent>
          </Card>
          <div className="lg:col-span-2">
            <Card className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-64 bg-gray-200 rounded"></div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    )
  }

  const PositionIcon = getPositionIcon(user.position)
  const overall = calculateOverall()

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Meu Perfil</h1>
          <p className="text-gray-600">Suas estatísticas e informações pessoais</p>
        </div>
        <Button variant="outline" className="hover:bg-blue-50">
          <Edit className="w-4 h-4 mr-2" />
          Editar Perfil
        </Button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Card FIFA */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:col-span-1"
        >
          <Card className="relative overflow-hidden bg-gradient-to-br from-blue-900 via-blue-800 to-blue-900 text-white border-0 shadow-2xl">
            {/* Background pattern */}
            <div className="absolute inset-0 opacity-10">
              <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent"></div>
              <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -translate-y-16 translate-x-16"></div>
              <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full translate-y-12 -translate-x-12"></div>
            </div>

            <CardContent className="p-6 relative z-10">
              <div className="space-y-6">
                {/* Header do card */}
                <div className="flex items-center justify-between">
                  <div className="text-xs font-bold tracking-wider opacity-80">
                    O REI DA PELADA
                  </div>
                  <div className="text-right">
                    <div className="text-2xl font-bold">{overall}</div>
                    <div className="text-xs opacity-80">OVR</div>
                  </div>
                </div>

                {/* Foto do jogador */}
                <div className="flex justify-center">
                  <div className="relative">
                    <div className="w-32 h-32 rounded-full overflow-hidden border-4 border-white/30 shadow-xl">
                      {user.photo_url ? (
                        <img 
                          src={user.photo_url} 
                          alt={user.name}
                          className="w-full h-full object-cover"
                        />
                      ) : (
                        <div className="w-full h-full bg-gradient-to-br from-gray-400 to-gray-600 flex items-center justify-center">
                          <User className="w-16 h-16 text-white" />
                        </div>
                      )}
                    </div>
                    <Button
                      size="sm"
                      className="absolute bottom-0 right-0 w-8 h-8 rounded-full p-0 bg-blue-600 hover:bg-blue-700 border-2 border-white"
                    >
                      <Camera className="w-3 h-3" />
                    </Button>
                  </div>
                </div>

                {/* Informações do jogador */}
                <div className="text-center space-y-2">
                  <h2 className="text-xl font-bold">{user.name}</h2>
                  <div className="flex items-center justify-center space-x-2">
                    <div className={`w-6 h-6 bg-gradient-to-r ${getPositionColor(user.position)} rounded-full flex items-center justify-center`}>
                      <PositionIcon className="w-3 h-3 text-white" />
                    </div>
                    <span className="text-sm font-medium">{user.position}</span>
                  </div>
                </div>

                {/* Estatísticas principais */}
                <div className="grid grid-cols-2 gap-4">
                  <div className="text-center">
                    <div className="text-2xl font-bold">
                      {stats?.general_stats?.total_matches || 0}
                    </div>
                    <div className="text-xs opacity-80">PARTIDAS</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">
                      {stats?.general_stats?.total_goals || 0}
                    </div>
                    <div className="text-xs opacity-80">GOLS</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">
                      {stats?.general_stats?.total_assists || 0}
                    </div>
                    <div className="text-xs opacity-80">ASSISTÊNCIAS</div>
                  </div>
                  <div className="text-center">
                    <div className="text-2xl font-bold">
                      {stats?.general_stats?.avg_points?.toFixed(1) || '0.0'}
                    </div>
                    <div className="text-xs opacity-80">MÉDIA</div>
                  </div>
                </div>

                {/* Estatísticas específicas por posição */}
                {user.position === 'Goleiro' && (
                  <div className="grid grid-cols-2 gap-4 pt-4 border-t border-white/20">
                    <div className="text-center">
                      <div className="text-xl font-bold">
                        {stats?.general_stats?.total_saves || 0}
                      </div>
                      <div className="text-xs opacity-80">DEFESAS</div>
                    </div>
                    <div className="text-center">
                      <div className="text-xl font-bold">
                        {stats?.general_stats?.total_goals_conceded || 0}
                      </div>
                      <div className="text-xs opacity-80">GOLS SOFRIDOS</div>
                    </div>
                  </div>
                )}

                {/* Rating visual */}
                <div className="space-y-2">
                  <div className="flex justify-between text-xs">
                    <span>Desempenho</span>
                    <span>{overall}%</span>
                  </div>
                  <Progress value={overall} className="h-2 bg-white/20" />
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>

        {/* Informações detalhadas */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:col-span-2 space-y-6"
        >
          {/* Estatísticas gerais */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Trophy className="w-5 h-5 text-yellow-600" />
                <span>Estatísticas Gerais</span>
              </CardTitle>
              <CardDescription>Seu desempenho em todas as peladas</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-2">
                    <Calendar className="w-6 h-6 text-blue-600" />
                  </div>
                  <div className="text-2xl font-bold text-gray-900">
                    {stats?.general_stats?.total_matches || 0}
                  </div>
                  <div className="text-sm text-gray-600">Partidas Jogadas</div>
                </div>

                <div className="text-center">
                  <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-2">
                    <Target className="w-6 h-6 text-green-600" />
                  </div>
                  <div className="text-2xl font-bold text-gray-900">
                    {stats?.general_stats?.total_goals || 0}
                  </div>
                  <div className="text-sm text-gray-600">Gols Marcados</div>
                </div>

                <div className="text-center">
                  <div className="w-12 h-12 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-2">
                    <Users className="w-6 h-6 text-purple-600" />
                  </div>
                  <div className="text-2xl font-bold text-gray-900">
                    {stats?.general_stats?.total_assists || 0}
                  </div>
                  <div className="text-sm text-gray-600">Assistências</div>
                </div>

                <div className="text-center">
                  <div className="w-12 h-12 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-2">
                    <TrendingUp className="w-6 h-6 text-orange-600" />
                  </div>
                  <div className="text-2xl font-bold text-gray-900">
                    {stats?.general_stats?.avg_points?.toFixed(1) || '0.0'}
                  </div>
                  <div className="text-sm text-gray-600">Média de Pontos</div>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Estatísticas por pelada */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Award className="w-5 h-5 text-blue-600" />
                <span>Desempenho por Pelada</span>
              </CardTitle>
              <CardDescription>Suas estatísticas em cada grupo</CardDescription>
            </CardHeader>
            <CardContent>
              {stats?.pelada_stats?.length === 0 ? (
                <div className="text-center py-8">
                  <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500">Você ainda não jogou em nenhuma pelada</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {stats?.pelada_stats?.map((peladaStat) => (
                    <div key={peladaStat.pelada_id} className="p-4 bg-gray-50 rounded-lg">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-semibold text-gray-900">{peladaStat.pelada_name}</h3>
                        <Badge variant="secondary">{peladaStat.matches} partidas</Badge>
                      </div>
                      <div className="grid grid-cols-4 gap-4 text-center">
                        <div>
                          <div className="text-lg font-bold text-gray-900">{peladaStat.goals}</div>
                          <div className="text-xs text-gray-600">Gols</div>
                        </div>
                        <div>
                          <div className="text-lg font-bold text-gray-900">{peladaStat.assists}</div>
                          <div className="text-xs text-gray-600">Assistências</div>
                        </div>
                        <div>
                          <div className="text-lg font-bold text-gray-900">{peladaStat.tackles}</div>
                          <div className="text-xs text-gray-600">Desarmes</div>
                        </div>
                        <div>
                          <div className="text-lg font-bold text-gray-900">{peladaStat.avg_points?.toFixed(1)}</div>
                          <div className="text-xs text-gray-600">Média</div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {/* Conquistas */}
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Star className="w-5 h-5 text-yellow-600" />
                <span>Conquistas</span>
              </CardTitle>
              <CardDescription>Seus títulos e reconhecimentos</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                {/* Conquistas baseadas nas estatísticas */}
                {(stats?.general_stats?.total_matches || 0) >= 10 && (
                  <div className="text-center p-4 bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg">
                    <div className="w-12 h-12 bg-blue-500 rounded-full flex items-center justify-center mx-auto mb-2">
                      <Calendar className="w-6 h-6 text-white" />
                    </div>
                    <div className="font-semibold text-blue-900">Veterano</div>
                    <div className="text-xs text-blue-700">10+ partidas</div>
                  </div>
                )}

                {(stats?.general_stats?.total_goals || 0) >= 5 && (
                  <div className="text-center p-4 bg-gradient-to-br from-green-50 to-green-100 rounded-lg">
                    <div className="w-12 h-12 bg-green-500 rounded-full flex items-center justify-center mx-auto mb-2">
                      <Target className="w-6 h-6 text-white" />
                    </div>
                    <div className="font-semibold text-green-900">Artilheiro</div>
                    <div className="text-xs text-green-700">5+ gols</div>
                  </div>
                )}

                {(stats?.general_stats?.avg_points || 0) >= 10 && (
                  <div className="text-center p-4 bg-gradient-to-br from-yellow-50 to-yellow-100 rounded-lg">
                    <div className="w-12 h-12 bg-yellow-500 rounded-full flex items-center justify-center mx-auto mb-2">
                      <Trophy className="w-6 h-6 text-white" />
                    </div>
                    <div className="font-semibold text-yellow-900">Destaque</div>
                    <div className="text-xs text-yellow-700">Média 10+</div>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>
    </div>
  )
}

export default Profile

