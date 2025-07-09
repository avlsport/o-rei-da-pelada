import React, { useState, useEffect } from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Search as SearchIcon } from 'lucide-react';

const BuscarPeladas = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [peladas, setPeladas] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchPeladas = async (name = '') => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/peladas/search?nome=${name}`);
      const data = await response.json();

      if (!response.ok) {
        setError(data.error || 'Erro ao buscar peladas.');
        return;
      }
      setPeladas(data.peladas);
    } catch (err) {
      setError('Erro de conexão ao buscar peladas.');
      console.error('Erro ao buscar peladas:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPeladas(); // Carrega todas as peladas ao montar o componente
  }, []);

  const handleSearch = (e) => {
    e.preventDefault();
    fetchPeladas(searchTerm);
  };

  const handleRequestJoin = async (peladaId) => {
    try {
      const response = await fetch('/api/peladas/request-join', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ pelada_id: peladaId }),
      });

      const data = await response.json();

      if (!response.ok) {
        alert(data.error || 'Erro ao solicitar entrada na pelada.');
        return;
      }
      alert(data.message);
      // Opcional: Atualizar o estado para refletir a solicitação pendente
    } catch (err) {
      alert('Erro de conexão ao solicitar entrada.');
      console.error('Erro ao solicitar entrada:', err);
    }
  };

  return (
    <DashboardLayout>
      <h2 className="text-3xl font-bold text-primary mb-6">Buscar Peladas</h2>
      <form onSubmit={handleSearch} className="flex space-x-4 mb-8">
        <Input
          type="text"
          placeholder="Buscar peladas por nome..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          className="flex-1 bg-gray-800 border-gray-700 text-white placeholder-gray-500 focus:border-primary focus:ring-primary"
        />
        <Button type="submit" className="gradient-primary hover-scale">
          <SearchIcon className="mr-2 h-5 w-5" />
          Buscar
        </Button>
      </form>

      {loading && <p>Carregando peladas...</p>}
      {error && <p className="text-red-500">{error}</p>}

      {!loading && !error && peladas.length === 0 ? (
        <p className="text-gray-400">Nenhuma pelada encontrada.</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {peladas.map((pelada) => (
            <Card key={pelada.id} className="glass-effect hover-scale">
              <CardHeader>
                <CardTitle className="text-white">{pelada.nome}</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-300 mb-2">Local: {pelada.local}</p>
                <p className="text-gray-400 text-sm mb-2">Admin: {pelada.admin_nome}</p>
                <p className="text-gray-400 text-sm mb-4">Membros: {pelada.total_membros}</p>
                <Button
                  onClick={() => handleRequestJoin(pelada.id)}
                  className="w-full border-secondary text-secondary hover:bg-secondary hover:text-white"
                >
                  Solicitar Entrada
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </DashboardLayout>
  );
};

export default BuscarPeladas;


