import React from 'react';
import PropTypes from 'prop-types';
import { Link } from 'react-router-dom';
import { Home, Users, Search, User, Trophy } from 'lucide-react';
import logo from '../../assets/logo_rei_da_pelada.png';

const DashboardLayout = ({ children }) => {
  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground">
      {/* Header */}
      <header className="w-full bg-card border-b border-border p-4 flex items-center justify-between shadow-md">
        <div className="flex items-center">
          <img src={logo} alt="O Rei da Pelada Logo" className="w-10 h-10 mr-3" />
          <h1 className="text-2xl font-bold gradient-text">O Rei da Pelada</h1>
        </div>
        {/* User Profile/Logout - Placeholder */}
        <div className="flex items-center space-x-4">
          <span className="text-muted-foreground">Olá, Usuário!</span>
          <Button variant="ghost" size="sm">Sair</Button>
        </div>
      </header>

      {/* Main Content */}
      <div className="flex flex-1">
        {/* Sidebar Navigation */}
        <nav className="w-64 bg-sidebar border-r border-sidebar-border p-4 shadow-lg flex flex-col">
          <ul className="space-y-2">
            <li>
              <Link to="/dashboard/inicio" className="flex items-center p-2 rounded-md text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-colors">
                <Home className="mr-3 h-5 w-5" />
                Início
              </Link>
            </li>
            <li>
              <Link to="/dashboard/minhas-peladas" className="flex items-center p-2 rounded-md text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-colors">
                <Users className="mr-3 h-5 w-5" />
                Minhas Peladas
              </Link>
            </li>
            <li>
              <Link to="/dashboard/buscar-peladas" className="flex items-center p-2 rounded-md text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-colors">
                <Search className="mr-3 h-5 w-5" />
                Buscar Peladas
              </Link>
            </li>
            <li>
              <Link to="/dashboard/perfil" className="flex items-center p-2 rounded-md text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-colors">
                <User className="mr-3 h-5 w-5" />
                Perfil
              </Link>
            </li>
            <li>
              <Link to="/dashboard/ranking-geral" className="flex items-center p-2 rounded-md text-sidebar-foreground hover:bg-sidebar-accent hover:text-sidebar-accent-foreground transition-colors">
                <Trophy className="mr-3 h-5 w-5" />
                Ranking Geral
              </Link>
            </li>
          </ul>
        </nav>

        {/* Content Area */}
        <main className="flex-1 p-6 overflow-auto">
          {children}
        </main>
      </div>
    </div>
  );
};

DashboardLayout.propTypes = {
  children: PropTypes.node.isRequired,
};

export default DashboardLayout;


