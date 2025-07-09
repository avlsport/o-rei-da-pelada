import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { Eye, EyeOff, Crown, Trophy, Target, Users, Upload } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import footballFieldBg from '../assets/football-field-bg.jpg'
import { API_ENDPOINTS } from '../config/api'

const LoginPage = ({ onLogin }) => {
  const [isLogin, setIsLogin] = useState(true)
  const [showPassword, setShowPassword] = useState(false)
  const [showConfirmPassword, setShowConfirmPassword] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  
  const [loginData, setLoginData] = useState({
    email: '',
    password: ''
  })
  
  const [registerData, setRegisterData] = useState({
    name: '',
    email: '',
    password: '',
    confirm_password: '',
    position: '',
    photo: null
  })

  const positions = [
    { value: 'Goleiro', label: 'Goleiro', icon: Target },
    { value: 'Zagueiro', label: 'Zagueiro', icon: Users },
    { value: 'Meio Campo', label: 'Meio Campo', icon: Crown },
    { value: 'Atacante', label: 'Atacante', icon: Trophy }
  ]

  const handleLogin = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch(API_ENDPOINTS.LOGIN, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify(loginData)
      })

      const data = await response.json()

      if (response.ok) {
        onLogin(data.user)
      } else {
        setError(data.error || 'Erro ao fazer login')
      }
    } catch (error) {
      setError('Erro de conexão. Tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  const handleRegister = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    if (registerData.password !== registerData.confirm_password) {
      setError('Senhas não coincidem')
      setLoading(false)
      return
    }

    try {
      const formData = new FormData()
      Object.keys(registerData).forEach(key => {
        if (registerData[key] !== null) {
          formData.append(key, registerData[key])
        }
      })

      const response = await fetch(API_ENDPOINTS.REGISTER, {
        method: 'POST',
        credentials: 'include',
        body: formData
      })

      const data = await response.json()

      if (response.ok) {
        onLogin(data.user)
      } else {
        setError(data.error || 'Erro ao criar conta')
      }
    } catch (error) {
      setError('Erro de conexão. Tente novamente.')
    } finally {
      setLoading(false)
    }
  }

  const handleFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
      setRegisterData(prev => ({ ...prev, photo: file }))
    }
  }

  return (
    <div 
      className="min-h-screen relative overflow-hidden"
      style={{
        backgroundImage: `url(${footballFieldBg})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        backgroundRepeat: 'no-repeat'
      }}
    >
      {/* Overlay escuro */}
      <div className="absolute inset-0 bg-black/60 backdrop-blur-sm"></div>
      
      {/* Efeitos de partículas animadas */}
      <div className="absolute inset-0">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-white/20 rounded-full"
            initial={{
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
            }}
            animate={{
              x: Math.random() * window.innerWidth,
              y: Math.random() * window.innerHeight,
            }}
            transition={{
              duration: Math.random() * 10 + 10,
              repeat: Infinity,
              ease: "linear"
            }}
          />
        ))}
      </div>

      <div className="relative z-10 min-h-screen flex items-center justify-center p-4">
        <motion.div
          initial={{ opacity: 0, y: 50 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
          className="w-full max-w-md"
        >
          {/* Logo e título */}
          <motion.div 
            className="text-center mb-8"
            initial={{ opacity: 0, y: -30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2, duration: 0.6 }}
          >
            <motion.div
              className="inline-flex items-center justify-center w-20 h-20 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full mb-4 shadow-2xl"
              whileHover={{ scale: 1.1, rotate: 5 }}
              transition={{ type: "spring", stiffness: 300 }}
            >
              <Crown className="w-10 h-10 text-white" />
            </motion.div>
            <h1 className="text-4xl font-bold text-white mb-2 bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
              O Rei da Pelada
            </h1>
            <p className="text-xl text-gray-200 font-medium">
              Sua pelada em outro nível
            </p>
          </motion.div>

          {/* Card principal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.4, duration: 0.6 }}
          >
            <Card className="bg-white/95 backdrop-blur-md border-0 shadow-2xl">
              <CardHeader className="text-center pb-4">
                <div className="flex justify-center space-x-1 mb-4">
                  <Button
                    variant={isLogin ? "default" : "ghost"}
                    onClick={() => setIsLogin(true)}
                    className={`px-8 py-2 rounded-full transition-all duration-300 ${
                      isLogin 
                        ? 'bg-gradient-to-r from-green-600 to-emerald-600 text-white shadow-lg' 
                        : 'text-gray-600 hover:text-green-600'
                    }`}
                  >
                    Entrar
                  </Button>
                  <Button
                    variant={!isLogin ? "default" : "ghost"}
                    onClick={() => setIsLogin(false)}
                    className={`px-8 py-2 rounded-full transition-all duration-300 ${
                      !isLogin 
                        ? 'bg-gradient-to-r from-green-600 to-emerald-600 text-white shadow-lg' 
                        : 'text-gray-600 hover:text-green-600'
                    }`}
                  >
                    Cadastrar
                  </Button>
                </div>
                <CardTitle className="text-2xl font-bold text-gray-800">
                  {isLogin ? 'Bem-vindo de volta!' : 'Junte-se ao time!'}
                </CardTitle>
                <CardDescription className="text-gray-600">
                  {isLogin 
                    ? 'Entre na sua conta para continuar' 
                    : 'Crie sua conta e comece a jogar'
                  }
                </CardDescription>
              </CardHeader>

              <CardContent>
                <AnimatePresence mode="wait">
                  {isLogin ? (
                    <motion.form
                      key="login"
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 20 }}
                      transition={{ duration: 0.3 }}
                      onSubmit={handleLogin}
                      className="space-y-4"
                    >
                      <div className="space-y-2">
                        <Label htmlFor="email" className="text-gray-700 font-medium">Email</Label>
                        <Input
                          id="email"
                          type="email"
                          placeholder="seu@email.com"
                          value={loginData.email}
                          onChange={(e) => setLoginData(prev => ({ ...prev, email: e.target.value }))}
                          className="border-gray-300 focus:border-green-500 focus:ring-green-500"
                          required
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="password" className="text-gray-700 font-medium">Senha</Label>
                        <div className="relative">
                          <Input
                            id="password"
                            type={showPassword ? "text" : "password"}
                            placeholder="••••••••"
                            value={loginData.password}
                            onChange={(e) => setLoginData(prev => ({ ...prev, password: e.target.value }))}
                            className="border-gray-300 focus:border-green-500 focus:ring-green-500 pr-10"
                            required
                          />
                          <Button
                            type="button"
                            variant="ghost"
                            size="sm"
                            className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                            onClick={() => setShowPassword(!showPassword)}
                          >
                            {showPassword ? (
                              <EyeOff className="h-4 w-4 text-gray-400" />
                            ) : (
                              <Eye className="h-4 w-4 text-gray-400" />
                            )}
                          </Button>
                        </div>
                      </div>

                      {error && (
                        <motion.div
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="text-red-500 text-sm text-center bg-red-50 p-2 rounded"
                        >
                          {error}
                        </motion.div>
                      )}

                      <Button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-semibold py-3 rounded-lg shadow-lg transition-all duration-300 transform hover:scale-105"
                      >
                        {loading ? (
                          <div className="flex items-center justify-center">
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                            Entrando...
                          </div>
                        ) : (
                          'Entrar'
                        )}
                      </Button>
                    </motion.form>
                  ) : (
                    <motion.form
                      key="register"
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                      transition={{ duration: 0.3 }}
                      onSubmit={handleRegister}
                      className="space-y-4"
                    >
                      <div className="space-y-2">
                        <Label htmlFor="name" className="text-gray-700 font-medium">Nome completo</Label>
                        <Input
                          id="name"
                          type="text"
                          placeholder="Seu nome"
                          value={registerData.name}
                          onChange={(e) => setRegisterData(prev => ({ ...prev, name: e.target.value }))}
                          className="border-gray-300 focus:border-green-500 focus:ring-green-500"
                          required
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="register-email" className="text-gray-700 font-medium">Email</Label>
                        <Input
                          id="register-email"
                          type="email"
                          placeholder="seu@email.com"
                          value={registerData.email}
                          onChange={(e) => setRegisterData(prev => ({ ...prev, email: e.target.value }))}
                          className="border-gray-300 focus:border-green-500 focus:ring-green-500"
                          required
                        />
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="position" className="text-gray-700 font-medium">Posição</Label>
                        <Select
                          value={registerData.position}
                          onValueChange={(value) => setRegisterData(prev => ({ ...prev, position: value }))}
                          required
                        >
                          <SelectTrigger className="border-gray-300 focus:border-green-500 focus:ring-green-500">
                            <SelectValue placeholder="Selecione sua posição" />
                          </SelectTrigger>
                          <SelectContent>
                            {positions.map((position) => {
                              const Icon = position.icon
                              return (
                                <SelectItem key={position.value} value={position.value}>
                                  <div className="flex items-center">
                                    <Icon className="w-4 h-4 mr-2" />
                                    {position.label}
                                  </div>
                                </SelectItem>
                              )
                            })}
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <Label htmlFor="photo" className="text-gray-700 font-medium">Foto (opcional)</Label>
                        <div className="relative">
                          <Input
                            id="photo"
                            type="file"
                            accept="image/*"
                            onChange={handleFileChange}
                            className="border-gray-300 focus:border-green-500 focus:ring-green-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-green-50 file:text-green-700 hover:file:bg-green-100"
                          />
                          <Upload className="absolute right-3 top-3 h-4 w-4 text-gray-400" />
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-4">
                        <div className="space-y-2">
                          <Label htmlFor="register-password" className="text-gray-700 font-medium">Senha</Label>
                          <div className="relative">
                            <Input
                              id="register-password"
                              type={showPassword ? "text" : "password"}
                              placeholder="••••••••"
                              value={registerData.password}
                              onChange={(e) => setRegisterData(prev => ({ ...prev, password: e.target.value }))}
                              className="border-gray-300 focus:border-green-500 focus:ring-green-500 pr-10"
                              required
                            />
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                              onClick={() => setShowPassword(!showPassword)}
                            >
                              {showPassword ? (
                                <EyeOff className="h-4 w-4 text-gray-400" />
                              ) : (
                                <Eye className="h-4 w-4 text-gray-400" />
                              )}
                            </Button>
                          </div>
                        </div>

                        <div className="space-y-2">
                          <Label htmlFor="confirm-password" className="text-gray-700 font-medium">Confirmar</Label>
                          <div className="relative">
                            <Input
                              id="confirm-password"
                              type={showConfirmPassword ? "text" : "password"}
                              placeholder="••••••••"
                              value={registerData.confirm_password}
                              onChange={(e) => setRegisterData(prev => ({ ...prev, confirm_password: e.target.value }))}
                              className="border-gray-300 focus:border-green-500 focus:ring-green-500 pr-10"
                              required
                            />
                            <Button
                              type="button"
                              variant="ghost"
                              size="sm"
                              className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                            >
                              {showConfirmPassword ? (
                                <EyeOff className="h-4 w-4 text-gray-400" />
                              ) : (
                                <Eye className="h-4 w-4 text-gray-400" />
                              )}
                            </Button>
                          </div>
                        </div>
                      </div>

                      {error && (
                        <motion.div
                          initial={{ opacity: 0, y: -10 }}
                          animate={{ opacity: 1, y: 0 }}
                          className="text-red-500 text-sm text-center bg-red-50 p-2 rounded"
                        >
                          {error}
                        </motion.div>
                      )}

                      <Button
                        type="submit"
                        disabled={loading}
                        className="w-full bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 text-white font-semibold py-3 rounded-lg shadow-lg transition-all duration-300 transform hover:scale-105"
                      >
                        {loading ? (
                          <div className="flex items-center justify-center">
                            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                            Criando conta...
                          </div>
                        ) : (
                          'Criar conta'
                        )}
                      </Button>
                    </motion.form>
                  )}
                </AnimatePresence>
              </CardContent>
            </Card>
          </motion.div>
        </motion.div>
      </div>
    </div>
  )
}

export default LoginPage

