import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { 
  Search, 
  Users, 
  MapPin, 
  Calendar, 
  UserPlus,
  Filter,
  Clock,
  CheckCircle,
  XCircle
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'

const SearchPeladas = ({ user }) => {
  const [peladas, setPeladas] = useState([])
  const [filteredPeladas, setFilteredPeladas] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [joinRequests, setJoinRequests] = useState({})

  useEffect(() => {
    fetchAllPeladas()
  }, [])

  useEffect(() => {
    filterPeladas()
  }, [searchTerm, peladas])

  const fetchAllPeladas = async () => {
    try {
      const response = await fetch('/api/peladas', {
        credentials: 'include'
      })
      const data = await response.json()
      setPeladas(data)
      setFilteredPeladas(data)
    } catch (error) {
      console.error('Erro ao buscar peladas:', error)
    } finally {
      setLoading(false)
    }
  }

  const filterPeladas = () => {
    if (!searchTerm.trim()) {
      setFilteredPeladas(peladas)
      return
    }

    const filtered = peladas.filter(pelada =>
      pelada.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      pelada.location.toLowerCase().includes(searchTerm.toLowerCase()) ||
      pelada.description?.toLowerCase().includes(searchTerm.toLowerCase())
    )
    setFilteredPeladas(filtered)
  }

  const handleJoinRequest = async (peladaId) => {
    try {
      setJoinRequests(prev => ({ ...prev, [peladaId]: 'loading' }))

      const response = await fetch('/api/peladas/join', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({ pelada_id: peladaId })
      })

      const data = await response.json()

      if (response.ok) {
        setJoinRequests(prev => ({ ...prev, [peladaId]: 'success' }))
      } else {
        setJoinRequests(prev => ({ ...prev, [peladaId]: 'error' }))
        console.error('Erro ao solicitar entrada:', data.error)
      }
    } catch (error) {
      setJoinRequests(prev => ({ ...prev, [peladaId]: 'error' }))
      console.error('Erro ao solicitar entrada:', error)
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-12 bg-gray-200 rounded animate-pulse"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, i) => (
            <Card key={i} className="animate-pulse">
              <CardContent className="p-6">
                <div className="h-32 bg-gray-200 rounded"></div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="space-y-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Buscar Peladas</h1>
          <p className="text-gray-600">Encontre novos grupos para jogar futebol</p>
        </div>

        {/* Barra de pesquisa */}
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
          <Input
            placeholder="Buscar por nome, local ou descrição..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-10 pr-4 py-2 border-gray-300 focus:border-blue-500 focus:ring-blue-500"
          />
        </div>

        {/* Estatísticas */}
        <div className="flex items-center space-x-6 text-sm text-gray-600">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span>{filteredPeladas.length} peladas encontradas</span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-green-500 rounded-full"></div>
            <span>{peladas.reduce((acc, p) => acc + p.members_count, 0)} jogadores ativos</span>
          </div>
        </div>
      </div>

      {/* Lista de Peladas */}
      {filteredPeladas.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-16"
        >
          <div className="w-24 h-24 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center mx-auto mb-6">
            <Search className="w-12 h-12 text-gray-400" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">
            {searchTerm ? 'Nenhuma pelada encontrada' : 'Nenhuma pelada disponível'}
          </h3>
          <p className="text-gray-600 max-w-md mx-auto">
            {searchTerm 
              ? 'Tente buscar com outros termos ou verifique a ortografia.'
              : 'Ainda não há peladas criadas. Que tal criar a primeira?'
            }
          </p>
        </motion.div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredPeladas.map((pelada, index) => (
            <motion.div
              key={pelada.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="group hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 overflow-hidden">
                <div className="relative h-48 bg-gradient-to-br from-blue-400 via-purple-500 to-pink-600">
                  {pelada.photo_url ? (
                    <img 
                      src={pelada.photo_url} 
                      alt={pelada.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center">
                      <Users className="w-16 h-16 text-white/80" />
                    </div>
                  )}
                  
                  {/* Overlay */}
                  <div className="absolute inset-0 bg-black/20 group-hover:bg-black/30 transition-all duration-300"></div>
                  
                  {/* Badge de status */}
                  <div className="absolute top-4 right-4">
                    <Badge className="bg-green-500 text-white border-0">
                      Ativo
                    </Badge>
                  </div>
                </div>

                <CardContent className="p-6">
                  <div className="space-y-4">
                    <div>
                      <h3 className="text-xl font-bold text-gray-900 mb-2 group-hover:text-blue-600 transition-colors">
                        {pelada.name}
                      </h3>
                      <div className="flex items-center text-gray-600 mb-2">
                        <MapPin className="w-4 h-4 mr-2" />
                        <span className="text-sm">{pelada.location}</span>
                      </div>
                      {pelada.description && (
                        <p className="text-gray-600 text-sm line-clamp-2">
                          {pelada.description}
                        </p>
                      )}
                    </div>

                    {/* Informações do criador */}
                    <div className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                      <Avatar className="h-8 w-8">
                        <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white text-xs">
                          {pelada.creator_name?.charAt(0).toUpperCase()}
                        </AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="text-sm font-medium text-gray-900">
                          Criado por {pelada.creator_name}
                        </p>
                        <div className="flex items-center text-gray-600">
                          <Users className="w-3 h-3 mr-1" />
                          <span className="text-xs">{pelada.members_count} membros</span>
                        </div>
                      </div>
                    </div>

                    {/* Botão de ação */}
                    <div className="pt-2">
                      {joinRequests[pelada.id] === 'loading' ? (
                        <Button disabled className="w-full">
                          <div className="flex items-center">
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                            Enviando...
                          </div>
                        </Button>
                      ) : joinRequests[pelada.id] === 'success' ? (
                        <Button disabled className="w-full bg-green-600 hover:bg-green-600">
                          <CheckCircle className="w-4 h-4 mr-2" />
                          Solicitação Enviada
                        </Button>
                      ) : joinRequests[pelada.id] === 'error' ? (
                        <Button 
                          variant="destructive" 
                          onClick={() => handleJoinRequest(pelada.id)}
                          className="w-full"
                        >
                          <XCircle className="w-4 h-4 mr-2" />
                          Tentar Novamente
                        </Button>
                      ) : (
                        <Button
                          onClick={() => handleJoinRequest(pelada.id)}
                          className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white"
                        >
                          <UserPlus className="w-4 h-4 mr-2" />
                          Solicitar Entrada
                        </Button>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}

      {/* Dica */}
      {filteredPeladas.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
        >
          <Card className="bg-gradient-to-r from-blue-50 to-indigo-50 border-blue-200">
            <CardContent className="p-6">
              <div className="flex items-start space-x-4">
                <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <Users className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h3 className="font-semibold text-blue-900 mb-1">Dica</h3>
                  <p className="text-blue-700 text-sm">
                    Após solicitar entrada em uma pelada, aguarde a aprovação do administrador. 
                    Você receberá uma notificação quando sua solicitação for processada.
                  </p>
                </div>
              </div>
            </CardContent>
          </Card>
        </motion.div>
      )}
    </div>
  )
}

export default SearchPeladas

