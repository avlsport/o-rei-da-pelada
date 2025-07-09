import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Routes, Route, useNavigate } from 'react-router-dom'
import { 
  Users, 
  Plus, 
  MapPin, 
  Calendar, 
  Settings, 
  Crown,
  Upload,
  X,
  Check,
  Clock,
  Trophy,
  Target,
  TrendingUp
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'

const MyPeladas = ({ user }) => {
  const navigate = useNavigate()
  const [peladas, setPeladas] = useState([])
  const [loading, setLoading] = useState(true)
  const [showCreateModal, setShowCreateModal] = useState(false)
  const [creating, setCreating] = useState(false)
  const [error, setError] = useState('')
  
  const [newPelada, setNewPelada] = useState({
    name: '',
    location: '',
    description: '',
    photo: null
  })

  useEffect(() => {
    fetchMyPeladas()
  }, [])

  const fetchMyPeladas = async () => {
    try {
      const response = await fetch('/api/peladas/my', {
        credentials: 'include'
      })
      const data = await response.json()
      setPeladas(data)
    } catch (error) {
      console.error('Erro ao buscar peladas:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleCreatePelada = async (e) => {
    e.preventDefault()
    setCreating(true)
    setError('')

    try {
      const formData = new FormData()
      Object.keys(newPelada).forEach(key => {
        if (newPelada[key] !== null && newPelada[key] !== '') {
          formData.append(key, newPelada[key])
        }
      })

      const response = await fetch('/api/peladas', {
        method: 'POST',
        credentials: 'include',
        body: formData
      })

      const data = await response.json()

      if (response.ok) {
        setShowCreateModal(false)
        setNewPelada({ name: '', location: '', description: '', photo: null })
        fetchMyPeladas()
      } else {
        setError(data.error || 'Erro ao criar pelada')
      }
    } catch (error) {
      setError('Erro de conexão. Tente novamente.')
    } finally {
      setCreating(false)
    }
  }

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setNewPelada(prev => ({ ...prev, photo: file }))
    }
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div className="h-8 bg-gray-200 rounded w-48 animate-pulse"></div>
          <div className="h-10 bg-gray-200 rounded w-32 animate-pulse"></div>
        </div>
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
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Minhas Peladas</h1>
          <p className="text-gray-600">Gerencie seus grupos de futebol</p>
        </div>
        
        <Dialog open={showCreateModal} onOpenChange={setShowCreateModal}>
          <DialogTrigger asChild>
            <Button className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 shadow-lg">
              <Plus className="w-4 h-4 mr-2" />
              Nova Pelada
            </Button>
          </DialogTrigger>
          <DialogContent className="sm:max-w-md">
            <DialogHeader>
              <DialogTitle>Criar Nova Pelada</DialogTitle>
              <DialogDescription>
                Crie um novo grupo para organizar suas partidas de futebol
              </DialogDescription>
            </DialogHeader>
            
            <form onSubmit={handleCreatePelada} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Nome da Pelada *</Label>
                <Input
                  id="name"
                  placeholder="Ex: Pelada do Domingo"
                  value={newPelada.name}
                  onChange={(e) => setNewPelada(prev => ({ ...prev, name: e.target.value }))}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="location">Local *</Label>
                <Input
                  id="location"
                  placeholder="Ex: Campo do Bairro"
                  value={newPelada.location}
                  onChange={(e) => setNewPelada(prev => ({ ...prev, location: e.target.value }))}
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="description">Descrição</Label>
                <Textarea
                  id="description"
                  placeholder="Descreva sua pelada..."
                  value={newPelada.description}
                  onChange={(e) => setNewPelada(prev => ({ ...prev, description: e.target.value }))}
                  rows={3}
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="photo">Foto da Pelada</Label>
                <div className="relative">
                  <Input
                    id="photo"
                    type="file"
                    accept="image/*"
                    onChange={handleFileChange}
                    className="file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100"
                  />
                  <Upload className="absolute right-3 top-3 h-4 w-4 text-gray-400" />
                </div>
              </div>

              {error && (
                <div className="text-red-500 text-sm bg-red-50 p-2 rounded">
                  {error}
                </div>
              )}

              <div className="flex justify-end space-x-2 pt-4">
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => setShowCreateModal(false)}
                >
                  Cancelar
                </Button>
                <Button
                  type="submit"
                  disabled={creating}
                  className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
                >
                  {creating ? (
                    <div className="flex items-center">
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Criando...
                    </div>
                  ) : (
                    'Criar Pelada'
                  )}
                </Button>
              </div>
            </form>
          </DialogContent>
        </Dialog>
      </div>

      {/* Lista de Peladas */}
      {peladas.length === 0 ? (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center py-16"
        >
          <div className="w-24 h-24 bg-gradient-to-br from-gray-100 to-gray-200 rounded-full flex items-center justify-center mx-auto mb-6">
            <Users className="w-12 h-12 text-gray-400" />
          </div>
          <h3 className="text-xl font-semibold text-gray-900 mb-2">Nenhuma pelada encontrada</h3>
          <p className="text-gray-600 mb-6 max-w-md mx-auto">
            Você ainda não faz parte de nenhuma pelada. Crie uma nova ou busque por peladas existentes.
          </p>
          <div className="flex flex-col sm:flex-row gap-3 justify-center">
            <Button
              onClick={() => setShowCreateModal(true)}
              className="bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700"
            >
              <Plus className="w-4 h-4 mr-2" />
              Criar Pelada
            </Button>
            <Button
              variant="outline"
              onClick={() => navigate('/dashboard/search')}
            >
              Buscar Peladas
            </Button>
          </div>
        </motion.div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {peladas.map((pelada, index) => (
            <motion.div
              key={pelada.id}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: index * 0.1 }}
            >
              <Card className="group hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 cursor-pointer overflow-hidden">
                <div 
                  className="relative h-48 bg-gradient-to-br from-green-400 via-blue-500 to-purple-600"
                  onClick={() => navigate(`/dashboard/my-peladas/${pelada.id}`)}
                >
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
                  
                  {/* Badge de Admin */}
                  {pelada.is_admin && (
                    <div className="absolute top-4 right-4">
                      <Badge className="bg-yellow-500 text-yellow-900 border-0">
                        <Crown className="w-3 h-3 mr-1" />
                        Admin
                      </Badge>
                    </div>
                  )}
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

                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <div className="flex items-center text-gray-600">
                          <Users className="w-4 h-4 mr-1" />
                          <span className="text-sm font-medium">{pelada.members_count}</span>
                        </div>
                        <span className="text-gray-400">•</span>
                        <div className="flex items-center text-gray-600">
                          <Calendar className="w-4 h-4 mr-1" />
                          <span className="text-sm">Ativo</span>
                        </div>
                      </div>

                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation()
                          navigate(`/dashboard/my-peladas/${pelada.id}/settings`)
                        }}
                        className="opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <Settings className="w-4 h-4" />
                      </Button>
                    </div>

                    <Button
                      onClick={() => navigate(`/dashboard/my-peladas/${pelada.id}`)}
                      className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white"
                    >
                      Acessar Pelada
                    </Button>
                  </div>
                </CardContent>
              </Card>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  )
}

export default MyPeladas

