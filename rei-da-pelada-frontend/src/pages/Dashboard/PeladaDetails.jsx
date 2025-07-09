import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import DashboardLayout from '../../components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { User, Calendar, DollarSign, ListChecks, Trophy, PlusCircle } from 'lucide-react';
import RankingPelada from './RankingPelada';
import CreateMatchDialog from '../../components/dialogs/CreateMatchDialog';
import FinancialMovements from '../../components/financeiro/FinancialMovements';
import MonthlyPlayers from '../../components/financeiro/MonthlyPlayers';

const PeladaDetails = () => {
  const { peladaId } = useParams();
  const [pelada, setPelada] = useState(null);
  const [matches, setMatches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isCreateMatchDialogOpen, setIsCreateMatchDialogOpen] = useState(false);

  const fetchPeladaDetails = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/peladas/${peladaId}`);
      const data = await response.json();

      if (!response.ok) {
        setError(data.error || 'Erro ao buscar detalhes da pelada.');
        return;
      }
      setPelada(data.pelada);
    } catch (err) {
      setError('Erro de conexão ao buscar detalhes da pelada.');
      console.error('Erro ao buscar detalhes da pelada:', err);
    } finally {
      setLoading(false);
    }
  };

  const fetchMatches = async () => {
    try {
      const response = await fetch(`/api/partidas/pelada/${peladaId}`);
      const data = await response.json();

      if (!response.ok) {
        setError(data.error || 'Erro ao buscar partidas da pelada.');
        return;
      }
      setMatches(data.partidas);
    } catch (err) {
      setError('Erro de conexão ao buscar partidas.');
      console.error('Erro ao buscar partidas:', err);
    }
  };

  useEffect(() => {
    fetchPeladaDetails();
    fetchMatches();
  }, [peladaId]);

  const handleCreateMatchSuccess = () => {
    fetchMatches(); // Recarrega a lista de partidas após a criação bem-sucedida
  };

  if (loading) {
    return (
      <DashboardLayout>
        <h2 className="text-3xl font-bold text-primary mb-6">Detalhes da Pelada</h2>
        <p>Carregando detalhes da pelada...</p>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout>
        <h2 className="text-3xl font-bold text-primary mb-6">Detalhes da Pelada</h2>
        <p className="text-red-500">{error}</p>
      </DashboardLayout>
    );
  }

  if (!pelada) {
    return (
      <DashboardLayout>
        <h2 className="text-3xl font-bold text-primary mb-6">Detalhes da Pelada</h2>
        <p className="text-gray-400">Pelada não encontrada.</p>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <h2 className="text-3xl font-bold text-primary mb-6">{pelada.nome}</h2>
      <p className="text-gray-300 mb-4">Local: {pelada.local}</p>
      <p className="text-gray-400 mb-6">{pelada.descricao}</p>

      <Tabs defaultValue="membros" className="w-full">
        <TabsList className="grid w-full grid-cols-4 bg-card text-primary">
          <TabsTrigger value="membros" className="flex items-center justify-center space-x-2">
            <User className="h-4 w-4" />
            <span>Membros</span>
          </TabsTrigger>
          <TabsTrigger value="partidas" className="flex items-center justify-center space-x-2">
            <Calendar className="h-4 w-4" />
            <span>Partidas</span>
          </TabsTrigger>
          <TabsTrigger value="financeiro" className="flex items-center justify-center space-x-2">
            <DollarSign className="h-4 w-4" />
            <span>Financeiro</span>
          </TabsTrigger>
          <TabsTrigger value="ranking" className="flex items-center justify-center space-x-2">
            <Trophy className="mr-2 h-5 w-5" />
            <span>Ranking</span>
          </TabsTrigger>
          {pelada.is_admin && (
            <TabsTrigger value="solicitacoes" className="flex items-center justify-center space-x-2">
              <ListChecks className="h-4 w-4" />
              <span>Solicitações</span>
            </TabsTrigger>
          )}
        </TabsList>

        <TabsContent value="membros" className="mt-6">
          <Card className="glass-effect">
            <CardHeader>
              <CardTitle className="text-white">Membros da Pelada</CardTitle>
            </CardHeader>
            <CardContent>
              {pelada.membros && pelada.membros.length > 0 ? (
                <ul className="space-y-2">
                  {pelada.membros.map((membro) => (
                    <li key={membro.usuario.id} className="flex items-center justify-between text-gray-300">
                      <span>{membro.usuario.nome} ({membro.usuario.posicao})</span>
                      {membro.is_admin && <span className="text-primary text-sm">Admin</span>}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-gray-400">Nenhum membro nesta pelada ainda.</p>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="partidas" className="mt-6">
          <Card className="glass-effect">
            <CardHeader className="flex flex-row justify-between items-center">
              <CardTitle className="text-white">Partidas</CardTitle>
              {pelada.is_admin && (
                <Button className="gradient-primary hover-scale" onClick={() => setIsCreateMatchDialogOpen(true)}>
                  <PlusCircle className="mr-2 h-5 w-5" />
                  Criar Partida
                </Button>
              )}
            </CardHeader>
            <CardContent>
              {matches.length === 0 ? (
                <p className="text-gray-400">Nenhuma partida agendada para esta pelada.</p>
              ) : (
                <ul className="space-y-4">
                  {matches.map((match) => (
                    <li key={match.id} className="bg-muted p-4 rounded-md flex justify-between items-center">
                      <div>
                        <p className="text-white font-semibold">Data: {new Date(match.data_partida).toLocaleDateString()}</p>
                        <p className="text-gray-300">Horário: {match.hora_inicio} - {match.hora_fim || 'A definir'}</p>
                        <p className="text-gray-400 text-sm">Status: {match.status}</p>
                      </div>
                      <div className="text-right">
                        <p className="text-gray-300">Confirmados: {match.confirmados}</p>
                        <p className="text-gray-300">Não Confirmados: {match.nao_confirmados}</p>
                        <p className="text-gray-300">Pendentes: {match.pendentes}</p>
                        <Button variant="outline" size="sm" className="mt-2 border-primary text-primary hover:bg-primary hover:text-white">
                          Ver Detalhes
                        </Button>
                      </div>
                    </li>
                  ))}
                </ul>
              )}
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="financeiro" className="mt-6">
          <Tabs defaultValue="movimentos" className="w-full">
            <TabsList className="grid w-full grid-cols-2 bg-card text-primary">
              <TabsTrigger value="movimentos">Movimentos</TabsTrigger>
              <TabsTrigger value="mensalistas">Mensalistas</TabsTrigger>
            </TabsList>
            <TabsContent value="movimentos" className="mt-6">
              <FinancialMovements peladaId={pelada.id} isAdmin={pelada.is_admin} />
            </TabsContent>
            <TabsContent value="mensalistas" className="mt-6">
              <MonthlyPlayers peladaId={pelada.id} isAdmin={pelada.is_admin} />
            </TabsContent>
          </Tabs>
        </TabsContent>

        <TabsContent value="ranking" className="mt-6">
          <RankingPelada peladaId={pelada.id} />
        </TabsContent>

        {pelada.is_admin && (
          <TabsContent value="solicitacoes" className="mt-6">
            <Card className="glass-effect">
              <CardHeader>
                <CardTitle className="text-white">Solicitações de Entrada</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-400">Funcionalidade de solicitações em desenvolvimento.</p>
                {/* Aqui você listaria as solicitações pendentes e permitiria aprovar/rejeitar */}
              </CardContent>
            </Card>
          </TabsContent>
        )}
      </Tabs>

      <CreateMatchDialog
        isOpen={isCreateMatchDialogOpen}
        onClose={() => setIsCreateMatchDialogOpen(false)}
        onCreateSuccess={handleCreateMatchSuccess}
        peladaId={pelada.id}
      />
    </DashboardLayout>
  );
};

export default PeladaDetails;


