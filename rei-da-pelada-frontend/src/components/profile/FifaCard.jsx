import React from 'react';
import PropTypes from 'prop-types';
import { Card, CardContent } from '@/components/ui/card';

const FifaCard = ({ user }) => {
  if (!user) {
    return <p className="text-gray-400">Carregando dados do jogador...</p>;
  }

  return (
    <Card className="relative w-full max-w-sm mx-auto overflow-hidden rounded-lg shadow-lg glass-effect-card border border-gray-700">
      <div className="absolute inset-0 bg-gradient-to-br from-green-500/20 via-blue-500/20 to-purple-500/20 opacity-50 z-0"></div>
      <div className="relative z-10 p-4 text-white">
        <div className="flex justify-between items-center mb-4">
          <span className="text-sm font-bold uppercase text-primary">O Rei da Pelada</span>
          <img src="/logo_rei_da_pelada.png" alt="Logo" className="h-8 w-8" />
        </div>

        <div className="text-center mb-4">
          <img
            src={user.avatar_url || `https://ui-avatars.com/api/?name=${user.nome}&background=0D8ABC&color=fff`}
            alt="Avatar do Jogador"
            className="w-24 h-24 rounded-full mx-auto border-2 border-primary object-cover"
          />
          <h3 className="text-2xl font-bold mt-2 text-white">{user.nome}</h3>
          <p className="text-primary text-lg font-semibold">{user.posicao}</p>
        </div>

        <div className="grid grid-cols-2 gap-2 text-sm">
          <div className="bg-gray-800/50 p-2 rounded-md">
            <p className="text-gray-400">Partidas</p>
            <p className="font-bold text-lg text-white">{user.estatisticas?.partidas_jogadas || 0}</p>
          </div>
          <div className="bg-gray-800/50 p-2 rounded-md">
            <p className="text-gray-400">Gols</p>
            <p className="font-bold text-lg text-white">{user.estatisticas?.gols || 0}</p>
          </div>
          <div className="bg-gray-800/50 p-2 rounded-md">
            <p className="text-gray-400">Assistências</p>
            <p className="font-bold text-lg text-white">{user.estatisticas?.assistencias || 0}</p>
          </div>
          <div className="bg-gray-800/50 p-2 rounded-md">
            <p className="text-gray-400">Média Pontos</p>
            <p className="font-bold text-lg text-white">{user.estatisticas?.media_pontos?.toFixed(1) || 0.0}</p>
          </div>
        </div>

        <div className="mt-4 text-center">
          <p className="text-gray-400 text-xs">ID: {user.id}</p>
        </div>
      </div>
    </Card>
  );
};

FifaCard.propTypes = {
  user: PropTypes.object,
};

export default FifaCard;


