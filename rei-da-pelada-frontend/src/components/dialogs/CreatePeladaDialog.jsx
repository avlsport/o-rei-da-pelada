import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';

const CreatePeladaDialog = ({ isOpen, onClose, onCreateSuccess }) => {
  const [nome, setNome] = useState('');
  const [local, setLocal] = useState('');
  const [descricao, setDescricao] = useState('');
  const [fotoPelada, setFotoPelada] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleFileChange = (e) => {
    setFotoPelada(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (!nome || !local || !descricao) {
      setError('Por favor, preencha todos os campos obrigatórios.');
      setLoading(false);
      return;
    }

    try {
      const formData = new FormData();
      formData.append('nome', nome);
      formData.append('local', local);
      formData.append('descricao', descricao);
      if (fotoPelada) {
        formData.append('foto_pelada', fotoPelada);
      }

      // Para simplificar, vamos enviar JSON para os campos de texto e lidar com a foto separadamente se necessário
      // Por enquanto, o backend espera JSON, então vamos adaptar.
      const response = await fetch('/api/peladas/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ nome, local, descricao, foto_pelada_url: fotoPelada ? fotoPelada.name : null }), // A foto será tratada no backend
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || 'Erro ao criar pelada.');
        return;
      }

      alert('Pelada criada com sucesso!');
      onCreateSuccess();
      onClose();
      setNome('');
      setLocal('');
      setDescricao('');
      setFotoPelada(null);

    } catch (err) {
      setError('Erro de conexão. Tente novamente.');
      console.error('Erro ao criar pelada:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px] glass-effect text-white">
        <DialogHeader>
          <DialogTitle className="text-primary">Criar Nova Pelada</DialogTitle>
          <DialogDescription className="text-gray-400">
            Preencha os detalhes para criar sua nova pelada.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="grid gap-4 py-4">
          {error && <p className="text-red-500 text-sm mb-2">{error}</p>}
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="nome" className="text-right text-gray-300">Nome</Label>
            <Input
              id="nome"
              value={nome}
              onChange={(e) => setNome(e.target.value)}
              className="col-span-3 bg-gray-800 border-gray-700 text-white placeholder-gray-500 focus:border-primary focus:ring-primary"
              required
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="local" className="text-right text-gray-300">Local</Label>
            <Input
              id="local"
              value={local}
              onChange={(e) => setLocal(e.target.value)}
              className="col-span-3 bg-gray-800 border-gray-700 text-white placeholder-gray-500 focus:border-primary focus:ring-primary"
              required
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="descricao" className="text-right text-gray-300">Descrição</Label>
            <Textarea
              id="descricao"
              value={descricao}
              onChange={(e) => setDescricao(e.target.value)}
              className="col-span-3 bg-gray-800 border-gray-700 text-white placeholder-gray-500 focus:border-primary focus:ring-primary"
              required
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="foto_pelada" className="text-right text-gray-300">Foto da Pelada</Label>
            <Input
              id="foto_pelada"
              type="file"
              accept="image/*"
              onChange={handleFileChange}
              className="col-span-3 block w-full text-sm text-gray-400
                file:mr-4 file:py-2 file:px-4
                file:rounded-full file:border-0
                file:text-sm file:font-semibold
                file:bg-primary file:text-primary-foreground
                hover:file:bg-primary/80"
            />
          </div>
          <DialogFooter>
            <Button type="submit" disabled={loading} className="gradient-primary hover-scale">
              {loading ? 'Criando...' : 'Criar Pelada'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

CreatePeladaDialog.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onCreateSuccess: PropTypes.func.isRequired,
};

export default CreatePeladaDialog;


