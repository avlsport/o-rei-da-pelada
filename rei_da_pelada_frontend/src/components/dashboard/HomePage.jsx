import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { useNavigate } from 'react-router-dom'
import { 
  Users, 
  Calendar, 
  Trophy, 
  Target, 
  TrendingUp, 
  Clock,
  MapPin,
  Star,
  Plus,
  ArrowRight,
  Zap,
  Award
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'

const HomePage = ({ user }) => {
  const navigate = useNavigate()
  const [stats, setStats] = useState({
    totalPeladas: 0,
    upcomingMatches: 0,
    totalGoals: 0,
    avgPoints: 0
  })
  const [recentMatches, setRecentMatches] = useState([])
  const [myPeladas, setMyPeladas] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      // Buscar peladas do usuário
      const peladasResponse = await fetch('/api/peladas/my', {
        credentials: 'include'
      })
      const peladasData = await peladasResponse.json()
      setMyPeladas(peladasData)

      // Buscar estatísticas do usuário
      const statsResponse = await fetch(`/api/users/${user.id}/stats`, {
        credentials: 'include'
      })
      const statsData = await statsResponse.json()
      
      setStats({
        totalPeladas: peladasData.length,
        upcomingMatches: 0, // Será implementado quando tivermos as partidas
        totalGoals: statsData.general_stats?.total_goals || 0,
        avgPoints: statsData.general_stats?.avg_points || 0
      })

    } catch (error) {
      console.error('Erro ao buscar dados do dashboard:', error)
    } finally {
      setLoading(false)
    }
  }

  const statsCards = [
    {
      title: 'Peladas',
      value: stats.totalPeladas,
      icon: Users,
      color: 'from-blue-500 to-blue-600',
      description: 'Grupos ativos'
    },
    {
      title: 'Próximas Partidas',
      value: stats.upcomingMatches,
      icon: Calendar,
      color: 'from-green-500 to-green-600',
      description: 'Esta semana'
    },
    {
      title: 'Gols Marcados',
      value: stats.totalGoals,
      icon: Target,
      color: 'from-orange-500 to-orange-600',
      description: 'Total histórico'
    },
    {
      title: 'Média de Pontos',
      value: stats.avgPoints.toFixed(1),
      icon: TrendingUp,
      color: 'from-purple-500 to-purple-600',
      description: 'Por partida'
    }
  ]

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {[...Array(4)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-20 bg-gray-200 rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Boas-vindas */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 rounded-2xl p-8 text-white relative overflow-hidden"
      >
        <div className="absolute inset-0 bg-black/10"></div>
        <div className="relative z-10">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold mb-2">
                Olá, {user.name.split(' ')[0]}! ⚽
              </h1>
              <p className="text-blue-100 text-lg">
                Pronto para dominar as peladas hoje?
              </p>
            </div>
            <div className="hidden md:block">
              <div className="w-24 h-24 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                <Trophy className="w-12 h-12 text-yellow-300" />
              </div>
            </div>
          </div>
        </div>
        
        {/* Efeitos decorativos */}
        <div className="absolute top-0 right-0 w-32 h-32 bg-white/5 rounded-full -translate-y-16 translate-x-16"></div>
        <div className="absolute bottom-0 left-0 w-24 h-24 bg-white/5 rounded-full translate-y-12 -translate-x-12"></div>
      </motion.div>

      {/* Cards de estatísticas */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statsCards.map((stat, index) => (
          <motion.div
            key={stat.title}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: index * 0.1 }}
          >
            <Card className="relative overflow-hidden group hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1">
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600 mb-1">{stat.title}</p>
                    <p className="text-3xl font-bold text-gray-900">{stat.value}</p>
                    <p className="text-xs text-gray-500 mt-1">{stat.description}</p>
                  </div>
                  <div className={`w-12 h-12 bg-gradient-to-r ${stat.color} rounded-xl flex items-center justify-center shadow-lg group-hover:scale-110 transition-transform duration-300`}>
                    <stat.icon className="w-6 h-6 text-white" />
                  </div>
                </div>
                <div className={`absolute bottom-0 left-0 h-1 bg-gradient-to-r ${stat.color} w-full transform scale-x-0 group-hover:scale-x-100 transition-transform duration-300`}></div>
              </CardContent>
            </Card>
          </motion.div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Minhas Peladas */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
        >
          <Card className="h-full">
            <CardHeader className="flex flex-row items-center justify-between">
              <div>
                <CardTitle className="flex items-center space-x-2">
                  <Users className="w-5 h-5 text-blue-600" />
                  <span>Minhas Peladas</span>
                </CardTitle>
                <CardDescription>Seus grupos de futebol</CardDescription>
              </div>
              <Button
                variant="outline"
                size="sm"
                onClick={() => navigate('/dashboard/my-peladas')}
                className="hover:bg-blue-50"
              >
                Ver todas
                <ArrowRight className="w-4 h-4 ml-1" />
              </Button>
            </CardHeader>
            <CardContent>
              {myPeladas.length === 0 ? (
                <div className="text-center py-8">
                  <Users className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                  <p className="text-gray-500 mb-4">Você ainda não faz parte de nenhuma pelada</p>
                  <Button
                    onClick={() => navigate('/dashboard/search')}
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                  >
                    <Plus className="w-4 h-4 mr-2" />
                    Buscar Peladas
                  </Button>
                </div>
              ) : (
                <div className="space-y-3">
                  {myPeladas.slice(0, 3).map((pelada) => (
                    <motion.div
                      key={pelada.id}
                      whileHover={{ scale: 1.02 }}
                      className="p-4 bg-gradient-to-r from-gray-50 to-blue-50 rounded-xl border border-gray-200 hover:border-blue-300 transition-all duration-300 cursor-pointer"
                      onClick={() => navigate(`/dashboard/my-peladas/${pelada.id}`)}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                            <Users className="w-5 h-5 text-white" />
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-900">{pelada.name}</h3>
                            <p className="text-sm text-gray-500 flex items-center">
                              <MapPin className="w-3 h-3 mr-1" />
                              {pelada.location}
                            </p>
                          </div>
                        </div>
                        <div className="text-right">
                          <Badge variant={pelada.is_admin ? "default" : "secondary"}>
                            {pelada.is_admin ? 'Admin' : 'Membro'}
                          </Badge>
                          <p className="text-xs text-gray-500 mt-1">
                            {pelada.members_count} membros
                          </p>
                        </div>
                      </div>
                    </motion.div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </motion.div>

        {/* Ações Rápidas */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 }}
        >
          <Card className="h-full">
            <CardHeader>
              <CardTitle className="flex items-center space-x-2">
                <Zap className="w-5 h-5 text-yellow-600" />
                <span>Ações Rápidas</span>
              </CardTitle>
              <CardDescription>Acesso rápido às principais funcionalidades</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 gap-4">
                <Button
                  onClick={() => navigate('/dashboard/search')}
                  className="h-16 bg-gradient-to-r from-green-500 to-emerald-600 hover:from-green-600 hover:to-emerald-700 text-white justify-start space-x-4 text-left"
                >
                  <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
                    <Users className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="font-semibold">Buscar Peladas</p>
                    <p className="text-sm opacity-90">Encontre novos grupos</p>
                  </div>
                </Button>

                <Button
                  onClick={() => navigate('/dashboard/ranking')}
                  className="h-16 bg-gradient-to-r from-yellow-500 to-orange-600 hover:from-yellow-600 hover:to-orange-700 text-white justify-start space-x-4 text-left"
                >
                  <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
                    <Trophy className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="font-semibold">Ranking Geral</p>
                    <p className="text-sm opacity-90">Veja sua posição</p>
                  </div>
                </Button>

                <Button
                  onClick={() => navigate('/dashboard/profile')}
                  className="h-16 bg-gradient-to-r from-purple-500 to-pink-600 hover:from-purple-600 hover:to-pink-700 text-white justify-start space-x-4 text-left"
                >
                  <div className="w-10 h-10 bg-white/20 rounded-lg flex items-center justify-center">
                    <Award className="w-5 h-5" />
                  </div>
                  <div>
                    <p className="font-semibold">Meu Perfil</p>
                    <p className="text-sm opacity-90">Estatísticas e card</p>
                  </div>
                </Button>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      </div>

      {/* Dica do dia */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.5 }}
      >
        <Card className="bg-gradient-to-r from-indigo-500 via-purple-500 to-pink-500 text-white border-0">
          <CardContent className="p-6">
            <div className="flex items-center space-x-4">
              <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center backdrop-blur-sm">
                <Star className="w-6 h-6 text-yellow-300" />
              </div>
              <div>
                <h3 className="font-bold text-lg mb-1">Dica do Rei</h3>
                <p className="text-indigo-100">
                  "O futebol é simples, mas jogar simples é a coisa mais difícil que existe." - Johan Cruyff
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </motion.div>
    </div>
  )
}

export default HomePage

