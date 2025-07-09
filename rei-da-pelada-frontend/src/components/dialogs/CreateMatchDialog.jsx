import React, { useState } from 'react';
import PropTypes from 'prop-types';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription, DialogFooter } from '@/components/ui/dialog';

const CreateMatchDialog = ({ isOpen, onClose, onCreateSuccess, peladaId }) => {
  const [dataPartida, setDataPartida] = useState('');
  const [horaInicio, setHoraInicio] = useState('');
  const [horaFim, setHoraFim] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    if (!dataPartida || !horaInicio) {
      setError('Por favor, preencha a data e hora de início da partida.');
      setLoading(false);
      return;
    }

    try {
      const response = await fetch('/api/partidas/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          pelada_id: peladaId,
          data_partida: dataPartida,
          hora_inicio: horaInicio,
          hora_fim: horaFim || null,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || 'Erro ao criar partida.');
        return;
      }

      alert('Partida criada com sucesso!');
      onCreateSuccess();
      onClose();
      setDataPartida('');
      setHoraInicio('');
      setHoraFim('');

    } catch (err) {
      setError('Erro de conexão. Tente novamente.');
      console.error('Erro ao criar partida:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px] glass-effect text-white">
        <DialogHeader>
          <DialogTitle className="text-primary">Criar Nova Partida</DialogTitle>
          <DialogDescription className="text-gray-400">
            Preencha os detalhes para criar uma nova partida.
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit} className="grid gap-4 py-4">
          {error && <p className="text-red-500 text-sm mb-2">{error}</p>}
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="dataPartida" className="text-right text-gray-300">Data</Label>
            <Input
              id="dataPartida"
              type="date"
              value={dataPartida}
              onChange={(e) => setDataPartida(e.target.value)}
              className="col-span-3 bg-gray-800 border-gray-700 text-white placeholder-gray-500 focus:border-primary focus:ring-primary"
              required
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="horaInicio" className="text-right text-gray-300">Hora Início</Label>
            <Input
              id="horaInicio"
              type="time"
              value={horaInicio}
              onChange={(e) => setHoraInicio(e.target.value)}
              className="col-span-3 bg-gray-800 border-gray-700 text-white placeholder-gray-500 focus:border-primary focus:ring-primary"
              required
            />
          </div>
          <div className="grid grid-cols-4 items-center gap-4">
            <Label htmlFor="horaFim" className="text-right text-gray-300">Hora Fim (Opcional)</Label>
            <Input
              id="horaFim"
              type="time"
              value={horaFim}
              onChange={(e) => setHoraFim(e.target.value)}
              className="col-span-3 bg-gray-800 border-gray-700 text-white placeholder-gray-500 focus:border-primary focus:ring-primary"
            />
          </div>
          <DialogFooter>
            <Button type="submit" disabled={loading} className="gradient-primary hover-scale">
              {loading ? 'Criando...' : 'Criar Partida'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  );
};

CreateMatchDialog.propTypes = {
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  onCreateSuccess: PropTypes.func.isRequired,
  peladaId: PropTypes.number.isRequired,
};

export default CreateMatchDialog;


