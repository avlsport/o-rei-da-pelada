import React, { useState, useEffect } from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';

const RankingGeral = () => {
  const [ranking, setRanking] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRanking = async () => {
      try {
        const response = await fetch('/api/ranking/geral');
        const data = await response.json();

        if (!response.ok) {
          setError(data.error || 'Erro ao buscar ranking geral.');
          return;
        }
        setRanking(data.ranking);
      } catch (err) {
        setError('Erro de conexão ao buscar ranking.');
        console.error('Erro ao buscar ranking geral:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchRanking();
  }, []);

  if (loading) {
    return (
      <DashboardLayout>
        <h2 className="text-3xl font-bold text-primary mb-6">Ranking Geral</h2>
        <p>Carregando ranking...</p>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout>
        <h2 className="text-3xl font-bold text-primary mb-6">Ranking Geral</h2>
        <p className="text-red-500">{error}</p>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <h2 className="text-3xl font-bold text-primary mb-6">Ranking Geral</h2>
      <Card className="glass-effect p-6 rounded-lg shadow-md">
        <CardHeader>
          <CardTitle className="text-white">Top Jogadores</CardTitle>
        </CardHeader>
        <CardContent>
          {ranking.length === 0 ? (
            <p className="text-gray-400">Nenhum jogador no ranking ainda.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="text-primary">Posição</TableHead>
                  <TableHead className="text-primary">Nome</TableHead>
                  <TableHead className="text-primary">Posição</TableHead>
                  <TableHead className="text-primary">Pelada Principal</TableHead>
                  <TableHead className="text-primary text-right">Média de Pontos</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {ranking.map((player) => (
                  <TableRow key={player.usuario_id} className={player.usuario_id === localStorage.getItem('user_id') ? 'bg-primary/20' : ''}>
                    <TableCell className="font-medium">{player.posicao}</TableCell>
                    <TableCell>{player.nome}</TableCell>
                    <TableCell>{player.posicao_campo}</TableCell>
                    <TableCell>{player.pelada || 'N/A'}</TableCell>
                    <TableCell className="text-right">{player.media_pontos}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </DashboardLayout>
  );
};

export default RankingGeral;


