import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import Navbar from './Navbar'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog'
import { Plus, Users, Calendar, MapPin, Upload, Trophy, Crown } from 'lucide-react'

export default function MinhasPeladas({ user }) {
  const [peladas, setPeladas] = useState([])
  const [loading, setLoading] = useState(true)
  const [isCreating, setIsCreating] = useState(false)
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [formData, setFormData] = useState({
    nome: '',
    descricao: '',
    local: '',
    foto: null
  })

  useEffect(() => {
    fetchPeladas()
  }, [])

  const fetchPeladas = async () => {
    try {
      const response = await fetch('/api/peladas/minhas', {
        credentials: 'include'
      })
      if (response.ok) {
        const data = await response.json()
        setPeladas(data.peladas || [])
      }
    } catch (error) {
      console.error('Erro ao carregar peladas:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleInputChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    setFormData(prev => ({
      ...prev,
      foto: file
    }))
  }

  const handleCreatePelada = async (e) => {
    e.preventDefault()
    setIsCreating(true)

    try {
      console.log('Iniciando criação de pelada...', formData)
      
      const formDataToSend = new FormData()
      formDataToSend.append('nome', formData.nome)
      formDataToSend.append('descricao', formData.descricao)
      formDataToSend.append('local', formData.local)
      if (formData.foto) {
        formDataToSend.append('foto', formData.foto)
      }

      console.log('Enviando dados:', {
        nome: formData.nome,
        descricao: formData.descricao,
        local: formData.local,
        foto: formData.foto ? formData.foto.name : 'Nenhuma'
      })

      const response = await fetch('/api/peladas', {
        method: 'POST',
        body: formDataToSend,
        credentials: 'include'
      })

      console.log('Response status:', response.status)
      console.log('Response ok:', response.ok)

      const responseData = await response.json()
      console.log('Response data:', responseData)

      if (response.ok) {
        console.log('Pelada criada com sucesso!')
        setShowCreateDialog(false)
        setFormData({ nome: '', descricao: '', local: '', foto: null })
        fetchPeladas() // Recarregar lista
        alert('Pelada criada com sucesso!')
      } else {
        console.error('Erro na resposta:', responseData)
        alert('Erro ao criar pelada: ' + (responseData.error || 'Erro desconhecido'))
      }
    } catch (error) {
      console.error('Erro ao criar pelada:', error)
      alert('Erro ao criar pelada: ' + error.message)
    } finally {
      setIsCreating(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar user={user} />
        <div className="max-w-7xl mx-auto py-6 px-4">
          <div className="text-center">Carregando...</div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar user={user} />
      
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Minhas Peladas</h1>
            <p className="text-gray-600">
              Gerencie suas peladas e acompanhe as estatísticas
            </p>
          </div>
          
          <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
            <DialogTrigger asChild>
              <Button className="bg-green-600 hover:bg-green-700">
                <Plus className="h-4 w-4 mr-2" />
                Nova Pelada
              </Button>
            </DialogTrigger>
            <DialogContent className="sm:max-w-[425px]">
              <DialogHeader>
                <DialogTitle>Criar Nova Pelada</DialogTitle>
                <DialogDescription>
                  Preencha as informações da sua pelada
                </DialogDescription>
              </DialogHeader>
              <form onSubmit={handleCreatePelada} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="nome">Nome da Pelada</Label>
                  <Input
                    id="nome"
                    name="nome"
                    value={formData.nome}
                    onChange={handleInputChange}
                    placeholder="Ex: Pelada do Sábado"
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="local">Local</Label>
                  <Input
                    id="local"
                    name="local"
                    value={formData.local}
                    onChange={handleInputChange}
                    placeholder="Ex: Campo do Clube"
                    required
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="descricao">Descrição</Label>
                  <Textarea
                    id="descricao"
                    name="descricao"
                    value={formData.descricao}
                    onChange={handleInputChange}
                    placeholder="Descreva sua pelada..."
                    rows={3}
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="foto">Foto da Pelada</Label>
                  <div className="flex items-center space-x-2">
                    <Input
                      id="foto"
                      name="foto"
                      type="file"
                      accept="image/*"
                      onChange={handleFileChange}
                    />
                    <Upload className="h-5 w-5 text-green-600" />
                  </div>
                  <p className="text-xs text-gray-500">
                    Adicione uma foto para identificar sua pelada
                  </p>
                </div>
                
                <div className="flex justify-end space-x-2 pt-4">
                  <Button
                    type="button"
                    variant="outline"
                    onClick={() => setShowCreateDialog(false)}
                  >
                    Cancelar
                  </Button>
                  <Button
                    type="submit"
                    disabled={isCreating}
                    className="bg-green-600 hover:bg-green-700"
                  >
                    {isCreating ? 'Criando...' : 'Criar Pelada'}
                  </Button>
                </div>
              </form>
            </DialogContent>
          </Dialog>
        </div>

        {/* Peladas Grid */}
        {peladas.length > 0 ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {peladas.map((pelada) => (
              <Card key={pelada.id} className="hover:shadow-lg transition-shadow cursor-pointer">
                <Link to={`/peladas/${pelada.id}`}>
                  {pelada.foto_url && (
                    <div className="h-48 bg-gray-200 rounded-t-lg overflow-hidden">
                      <img
                        src={pelada.foto_url}
                        alt={pelada.nome}
                        className="w-full h-full object-cover"
                      />
                    </div>
                  )}
                  <CardHeader>
                    <CardTitle className="flex items-center justify-between">
                      <span className="truncate">{pelada.nome}</span>
                      {pelada.criador_id === user?.id && (
                        <Crown className="h-5 w-5 text-yellow-500 flex-shrink-0" />
                      )}
                    </CardTitle>
                    <CardDescription className="line-clamp-2">
                      {pelada.descricao || 'Sem descrição'}
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-2">
                      <div className="flex items-center text-sm text-gray-600">
                        <MapPin className="h-4 w-4 mr-2" />
                        {pelada.local}
                      </div>
                      <div className="flex items-center text-sm text-gray-600">
                        <Users className="h-4 w-4 mr-2" />
                        {pelada.total_jogadores || 0} jogadores
                      </div>
                      <div className="flex items-center text-sm text-gray-600">
                        <Trophy className="h-4 w-4 mr-2" />
                        {pelada.total_partidas || 0} partidas
                      </div>
                      <div className="flex items-center text-sm text-gray-600">
                        <Calendar className="h-4 w-4 mr-2" />
                        Criada em {new Date(pelada.data_criacao).toLocaleDateString('pt-BR')}
                      </div>
                    </div>
                    
                    <div className="mt-4 pt-4 border-t">
                      <div className="flex justify-between items-center">
                        <span className="text-sm font-medium text-gray-700">
                          Status: {pelada.ativa ? 'Ativa' : 'Inativa'}
                        </span>
                        <div className={`px-2 py-1 rounded-full text-xs ${
                          pelada.ativa 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-gray-100 text-gray-800'
                        }`}>
                          {pelada.ativa ? 'Ativa' : 'Inativa'}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Link>
              </Card>
            ))}
          </div>
        ) : (
          <Card className="text-center py-12">
            <CardContent>
              <Trophy className="h-16 w-16 mx-auto mb-4 text-gray-300" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">
                Nenhuma pelada encontrada
              </h3>
              <p className="text-gray-600 mb-6">
                Você ainda não criou ou participou de nenhuma pelada.
              </p>
              <Button
                onClick={() => setShowCreateDialog(true)}
                className="bg-green-600 hover:bg-green-700"
              >
                <Plus className="h-4 w-4 mr-2" />
                Criar Primeira Pelada
              </Button>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  )
}

