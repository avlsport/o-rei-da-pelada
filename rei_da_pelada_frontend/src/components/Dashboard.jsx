import { useState, useEffect } from 'react'
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom'
import { motion, AnimatePresence } from 'framer-motion'
import { 
  Home, 
  Users, 
  Search, 
  User, 
  Trophy, 
  LogOut, 
  Crown,
  Menu,
  X,
  Bell,
  Settings
} from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar'
import { Badge } from '@/components/ui/badge'

// Componentes das páginas (serão criados depois)
import HomePage from './dashboard/HomePage'
import MyPeladas from './dashboard/MyPeladas'
import SearchPeladas from './dashboard/SearchPeladas'
import Profile from './dashboard/Profile'
import GlobalRanking from './dashboard/GlobalRanking'

const Dashboard = ({ user, onLogout }) => {
  const navigate = useNavigate()
  const location = useLocation()
  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [notifications, setNotifications] = useState(3) // Exemplo

  const menuItems = [
    {
      id: 'home',
      label: 'Início',
      icon: Home,
      path: '/dashboard',
      color: 'from-blue-500 to-blue-600'
    },
    {
      id: 'my-peladas',
      label: 'Minhas Peladas',
      icon: Users,
      path: '/dashboard/my-peladas',
      color: 'from-green-500 to-green-600'
    },
    {
      id: 'search',
      label: 'Buscar Peladas',
      icon: Search,
      path: '/dashboard/search',
      color: 'from-purple-500 to-purple-600'
    },
    {
      id: 'profile',
      label: 'Perfil',
      icon: User,
      path: '/dashboard/profile',
      color: 'from-orange-500 to-orange-600'
    },
    {
      id: 'ranking',
      label: 'Ranking Geral',
      icon: Trophy,
      path: '/dashboard/ranking',
      color: 'from-yellow-500 to-yellow-600'
    }
  ]

  const currentPath = location.pathname
  const activeItem = menuItems.find(item => 
    item.path === currentPath || (item.path !== '/dashboard' && currentPath.startsWith(item.path))
  ) || menuItems[0]

  const handleNavigation = (path) => {
    navigate(path)
    setIsSidebarOpen(false)
  }

  const handleLogout = () => {
    onLogout()
    navigate('/login')
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
      {/* Header */}
      <motion.header 
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        className="bg-white/80 backdrop-blur-md border-b border-gray-200/50 sticky top-0 z-40 shadow-sm"
      >
        <div className="flex items-center justify-between px-4 py-3">
          {/* Logo e Menu Mobile */}
          <div className="flex items-center space-x-4">
            <Button
              variant="ghost"
              size="sm"
              onClick={() => setIsSidebarOpen(!isSidebarOpen)}
              className="lg:hidden"
            >
              {isSidebarOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </Button>
            
            <motion.div 
              className="flex items-center space-x-3"
              whileHover={{ scale: 1.05 }}
            >
              <div className="w-10 h-10 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center shadow-lg">
                <Crown className="w-6 h-6 text-white" />
              </div>
              <div className="hidden sm:block">
                <h1 className="text-xl font-bold bg-gradient-to-r from-yellow-600 to-orange-600 bg-clip-text text-transparent">
                  O Rei da Pelada
                </h1>
              </div>
            </motion.div>
          </div>

          {/* Título da página atual */}
          <motion.div 
            key={activeItem.id}
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="hidden md:flex items-center space-x-2"
          >
            <div className={`w-8 h-8 bg-gradient-to-r ${activeItem.color} rounded-lg flex items-center justify-center shadow-md`}>
              <activeItem.icon className="w-4 h-4 text-white" />
            </div>
            <h2 className="text-lg font-semibold text-gray-800">{activeItem.label}</h2>
          </motion.div>

          {/* User Menu */}
          <div className="flex items-center space-x-3">
            {/* Notificações */}
            <motion.div 
              className="relative"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.95 }}
            >
              <Button variant="ghost" size="sm" className="relative">
                <Bell className="h-5 w-5 text-gray-600" />
                {notifications > 0 && (
                  <Badge className="absolute -top-1 -right-1 h-5 w-5 flex items-center justify-center p-0 bg-red-500 text-white text-xs">
                    {notifications}
                  </Badge>
                )}
              </Button>
            </motion.div>

            {/* Avatar do usuário */}
            <motion.div 
              className="flex items-center space-x-2"
              whileHover={{ scale: 1.05 }}
            >
              <Avatar className="h-8 w-8 ring-2 ring-white shadow-md">
                <AvatarImage src={user.photo_url} alt={user.name} />
                <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white font-semibold">
                  {user.name.charAt(0).toUpperCase()}
                </AvatarFallback>
              </Avatar>
              <div className="hidden sm:block">
                <p className="text-sm font-medium text-gray-800">{user.name}</p>
                <p className="text-xs text-gray-500">{user.position}</p>
              </div>
            </motion.div>

            {/* Logout */}
            <Button
              variant="ghost"
              size="sm"
              onClick={handleLogout}
              className="text-red-600 hover:text-red-700 hover:bg-red-50"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </motion.header>

      <div className="flex">
        {/* Sidebar */}
        <AnimatePresence>
          {(isSidebarOpen || window.innerWidth >= 1024) && (
            <motion.aside
              initial={{ x: -300 }}
              animate={{ x: 0 }}
              exit={{ x: -300 }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
              className="fixed lg:static inset-y-0 left-0 z-30 w-64 bg-white/90 backdrop-blur-md border-r border-gray-200/50 shadow-xl lg:shadow-none"
            >
              <div className="flex flex-col h-full pt-20 lg:pt-6">
                <nav className="flex-1 px-4 space-y-2">
                  {menuItems.map((item, index) => {
                    const isActive = item.path === currentPath || 
                      (item.path !== '/dashboard' && currentPath.startsWith(item.path))
                    
                    return (
                      <motion.div
                        key={item.id}
                        initial={{ opacity: 0, x: -20 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: index * 0.1 }}
                      >
                        <Button
                          variant={isActive ? "default" : "ghost"}
                          onClick={() => handleNavigation(item.path)}
                          className={`w-full justify-start space-x-3 py-3 px-4 rounded-xl transition-all duration-300 ${
                            isActive
                              ? `bg-gradient-to-r ${item.color} text-white shadow-lg transform scale-105`
                              : 'text-gray-700 hover:bg-gray-100 hover:scale-105'
                          }`}
                        >
                          <item.icon className={`h-5 w-5 ${isActive ? 'text-white' : 'text-gray-500'}`} />
                          <span className="font-medium">{item.label}</span>
                        </Button>
                      </motion.div>
                    )
                  })}
                </nav>

                {/* Footer da sidebar */}
                <div className="p-4 border-t border-gray-200/50">
                  <div className="flex items-center space-x-3 p-3 bg-gradient-to-r from-gray-50 to-gray-100 rounded-xl">
                    <Avatar className="h-10 w-10 ring-2 ring-white shadow-md">
                      <AvatarImage src={user.photo_url} alt={user.name} />
                      <AvatarFallback className="bg-gradient-to-br from-blue-500 to-purple-600 text-white font-semibold">
                        {user.name.charAt(0).toUpperCase()}
                      </AvatarFallback>
                    </Avatar>
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-gray-800 truncate">{user.name}</p>
                      <p className="text-xs text-gray-500">{user.position}</p>
                    </div>
                    <Button variant="ghost" size="sm">
                      <Settings className="h-4 w-4 text-gray-500" />
                    </Button>
                  </div>
                </div>
              </div>
            </motion.aside>
          )}
        </AnimatePresence>

        {/* Overlay para mobile */}
        {isSidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setIsSidebarOpen(false)}
            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-20 lg:hidden"
          />
        )}

        {/* Conteúdo principal */}
        <main className="flex-1 min-h-screen">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="p-6"
          >
            <Routes>
              <Route path="/" element={<HomePage user={user} />} />
              <Route path="/my-peladas/*" element={<MyPeladas user={user} />} />
              <Route path="/search" element={<SearchPeladas user={user} />} />
              <Route path="/profile" element={<Profile user={user} />} />
              <Route path="/ranking" element={<GlobalRanking user={user} />} />
            </Routes>
          </motion.div>
        </main>
      </div>
    </div>
  )
}

export default Dashboard

