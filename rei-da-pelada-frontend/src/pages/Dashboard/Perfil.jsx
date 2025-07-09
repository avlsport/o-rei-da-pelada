import React, { useState, useEffect } from 'react';
import DashboardLayout from '../../components/layout/DashboardLayout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import FifaCard from '../../components/profile/FifaCard';

const Perfil = () => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [file, setFile] = useState(null);

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const userResponse = await fetch('/api/auth/me');
        const userData = await userResponse.json();

        if (!userResponse.ok) {
          setError(userData.error || 'Erro ao buscar dados do usuário.');
          return;
        }
        
        // Fetch user stats separately and combine
        const statsResponse = await fetch(`/api/ranking/user/${userData.user.id}/stats`);
        const statsData = await statsResponse.json();

        if (!statsResponse.ok) {
          setError(statsData.error || 'Erro ao buscar estatísticas do usuário.');
          return;
        }

        setUser({ ...userData.user, estatisticas: statsData.stats });

      } catch (err) {
        setError('Erro de conexão ao buscar dados do perfil.');
        console.error('Erro ao buscar perfil:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchUserData();
  }, []);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleUpload = async () => {
    if (!file) {
      alert('Por favor, selecione um arquivo para upload.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch('/api/auth/upload-photo', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        alert(data.error || 'Erro ao fazer upload da foto.');
        return;
      }
      alert(data.message);
      // Atualizar a URL da foto no estado do usuário
      setUser(prevUser => ({ ...prevUser, foto_perfil_url: data.foto_url }));
      setFile(null); // Limpar o arquivo selecionado
    } catch (err) {
      alert('Erro de conexão ao fazer upload.');
      console.error('Erro de upload:', err);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <h2 className="text-3xl font-bold text-primary mb-6">Perfil</h2>
        <p>Carregando perfil...</p>
      </DashboardLayout>
    );
  }

  if (error) {
    return (
      <DashboardLayout>
        <h2 className="text-3xl font-bold text-primary mb-6">Perfil</h2>
        <p className="text-red-500">{error}</p>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <h2 className="text-3xl font-bold text-primary mb-6">Meu Perfil</h2>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <FifaCard user={user} />

        {/* User Information and Photo Upload */}
        <Card className="glass-effect p-6 rounded-lg shadow-md">
          <CardHeader>
            <CardTitle className="text-white">Informações Pessoais</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <Label className="text-gray-300">Nome:</Label>
              <p className="text-white font-semibold">{user?.nome}</p>
            </div>
            <div>
              <Label className="text-gray-300">Email:</Label>
              <p className="text-white font-semibold">{user?.email}</p>
            </div>
            <div>
              <Label className="text-gray-300">Posição:</Label>
              <p className="text-white font-semibold">{user?.posicao}</p>
            </div>
            <div className="mt-6">
              <Label htmlFor="photo-upload" className="text-gray-300 block mb-2">Atualizar Foto de Perfil</Label>
              <Input
                id="photo-upload"
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="block w-full text-sm text-gray-400
                  file:mr-4 file:py-2 file:px-4
                  file:rounded-full file:border-0
                  file:text-sm file:font-semibold
                  file:bg-primary file:text-primary-foreground
                  hover:file:bg-primary/80"
              />
              <Button onClick={handleUpload} className="mt-4 gradient-primary hover-scale">
                Upload Foto
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
};

export default Perfil;


