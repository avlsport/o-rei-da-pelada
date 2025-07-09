import React, { useState, useEffect } from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { PlusCircle } from 'lucide-react';
import CreatePeladaDialog from '../../components/dialogs/CreatePeladaDialog';
import { Link } from 'react-router-dom';

const MinhasPeladas = () => {
  const [peladas, setPeladas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isCreatePeladaDialogOpen, setIsCreatePeladaDialogOpen] = useState(false);

  const fetchMyPeladas = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch('/api/peladas/my-peladas');
      const data = await response.json();

      if (!response.ok) {
        setError(data.error || 'Erro ao buscar suas peladas.');
        return;
      }
      setPeladas(data.peladas);
    } catch (err) {
      setError('Erro de conexão ao buscar peladas.');
      console.error('Erro ao buscar minhas peladas:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMyPeladas();
  }, []);

  const handleCreateSuccess = () => {
    fetchMyPeladas(); // Recarrega a lista de peladas após a criação bem-sucedida
  };

  if (loading) {
    return (
      <DashboardLayout>
        <h2 className="text-3xl font-bold text-primary mb-6">Minhas Peladas</h2>
        <p>Carregando suas peladas...</p>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout>
        <h2 className="text-3xl font-bold text-primary mb-6">Minhas Peladas</h2>
        <p className="text-red-500">{error}</p>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-3xl font-bold text-primary">Minhas Peladas</h2>
        <Button className="gradient-primary hover-scale" onClick={() => setIsCreatePeladaDialogOpen(true)}>
          <PlusCircle className="mr-2 h-5 w-5" />
          Criar Nova Pelada
        </Button>
      </div>

      {peladas.length === 0 ? (
        <p className="text-gray-400">Você ainda não participa de nenhuma pelada. Crie uma ou busque por peladas existentes!</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {peladas.map((pelada) => (
            <Card key={pelada.id} className="glass-effect hover-scale">
              <CardHeader>
                <CardTitle className="text-white">{pelada.nome}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300 mb-2">Local: {pelada.local}</p>
                <p className="text-gray-400 text-sm mb-4">{pelada.descricao}</p>
                <Link to={`/dashboard/pelada/${pelada.id}`}>
                  <Button variant="outline" className="w-full border-primary text-primary hover:bg-primary hover:text-white">
                    Ver Detalhes
                  </Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <CreatePeladaDialog
        isOpen={isCreatePeladaDialogOpen}
        onClose={() => setIsCreatePeladaDialogOpen(false)}
        onCreateSuccess={handleCreateSuccess}
      />
    </DashboardLayout>
  );
};

export default MinhasPeladas;


