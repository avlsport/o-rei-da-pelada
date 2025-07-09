import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './pages/Auth/Login';
import Register from './pages/Auth/Register';
import Home from './pages/Dashboard/Home';
import MinhasPeladas from './pages/Dashboard/MinhasPeladas';
import BuscarPeladas from './pages/Dashboard/BuscarPeladas';
import Perfil from './pages/Dashboard/Perfil';
import RankingGeral from './pages/Dashboard/RankingGeral';
import PeladaDetails from './pages/Dashboard/PeladaDetails';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/dashboard" element={<Home />} /> {/* Rota padrão do dashboard */}
        <Route path="/dashboard/inicio" element={<Home />} />
        <Route path="/dashboard/minhas-peladas" element={<MinhasPeladas />} />
        <Route path="/dashboard/buscar-peladas" element={<BuscarPeladas />} />
        <Route path="/dashboard/perfil" element={<Perfil />} />
        <Route path="/dashboard/ranking-geral" element={<RankingGeral />} />
        <Route path="/dashboard/pelada/:peladaId" element={<PeladaDetails />} />
        <Route path="*" element={<Navigate to="/login" replace />} /> {/* Redireciona rotas não encontradas para login */}
      </Routes>
    </Router>
  );
}

export default App;


