import React from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';

const Home = () => {
  return (
    <DashboardLayout>
      <h2 className="text-3xl font-bold text-primary mb-6">Início</h2>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {/* Placeholder for statistics cards */}
        <div className="bg-card p-6 rounded-lg shadow-md glass-effect">
          <h3 className="text-xl font-semibold text-white mb-2">Total de Partidas</h3>
          <p className="text-4xl font-bold text-primary">120</p>
        </div>
        <div className="bg-card p-6 rounded-lg shadow-md glass-effect">
          <h3 className="text-xl font-semibold text-white mb-2">Gols Marcados</h3>
          <p className="text-4xl font-bold text-secondary">350</p>
        </div>
        <div className="bg-card p-6 rounded-lg shadow-md glass-effect">
          <h3 className="text-xl font-semibold text-white mb-2">Assistências</h3>
          <p className="text-4xl font-bold text-accent">180</p>
        </div>
      </div>
      {/* Placeholder for recent activity or news */}
      <div className="mt-8 bg-card p-6 rounded-lg shadow-md glass-effect">
        <h3 className="text-xl font-semibold text-white mb-4">Atividade Recente</h3>
        <ul className="space-y-3">
          <li className="text-gray-300">Você participou de uma pelada em 05/07/2025.</li>
          <li className="text-gray-300">Nova pelada 'Futebol de Quinta' criada por João.</li>
          <li className="text-gray-300">Você subiu 2 posições no Ranking Geral.</li>
        </ul>
      </div>
    </DashboardLayout>
  );
};

export default Home;


