import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { PlusCircle, Trash2 } from 'lucide-react';

const FinancialMovements = ({ peladaId, isAdmin }) => {
  const [movimentos, setMovimentos] = useState([]);
  const [resumo, setResumo] = useState({ total_entradas: 0, total_saidas: 0, saldo: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [isAddingMovement, setIsAddingMovement] = useState(false);
  const [tipoMovimento, setTipoMovimento] = useState('entrada');
  const [descricao, setDescricao] = useState('');
  const [valor, setValor] = useState('');
  const [addError, setAddError] = useState('');

  const fetchMovimentos = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/financeiro/pelada/${peladaId}/movimentos`);
      const data = await response.json();

      if (!response.ok) {
        setError(data.error || 'Erro ao buscar movimentos financeiros.');
        return;
      }
      setMovimentos(data.movimentos);
      setResumo(data.resumo);
    } catch (err) {
      setError('Erro de conexão ao buscar movimentos financeiros.');
      console.error('Erro ao buscar movimentos financeiros:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMovimentos();
  }, [peladaId]);

  const handleAddMovement = async (e) => {
    e.preventDefault();
    setAddError('');

    if (!descricao || !valor) {
      setAddError('Por favor, preencha a descrição e o valor.');
      return;
    }
    if (isNaN(parseFloat(valor)) || parseFloat(valor) <= 0) {
      setAddError('Por favor, insira um valor numérico válido.');
      return;
    }

    try {
      const response = await fetch(`/api/financeiro/pelada/${peladaId}/movimento`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          tipo_movimento: tipoMovimento,
          descricao,
          valor: parseFloat(valor),
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        setAddError(data.error || 'Erro ao adicionar movimento.');
        return;
      }

      alert('Movimento adicionado com sucesso!');
      setIsAddingMovement(false);
      setDescricao('');
      setValor('');
      fetchMovimentos(); // Recarrega a lista

    } catch (err) {
      setAddError('Erro de conexão ao adicionar movimento.');
      console.error('Erro ao adicionar movimento:', err);
    }
  };

  const handleDeleteMovement = async (movimentoId) => {
    if (!window.confirm('Tem certeza que deseja excluir este movimento?')) {
      return;
    }

    try {
      const response = await fetch(`/api/financeiro/movimento/${movimentoId}`, {
        method: 'DELETE',
      });

      const data = await response.json();

      if (!response.ok) {
        alert(data.error || 'Erro ao excluir movimento.');
        return;
      }

      alert('Movimento excluído com sucesso!');
      fetchMovimentos(); // Recarrega a lista

    } catch (err) {
      alert('Erro de conexão ao excluir movimento.');
      console.error('Erro ao excluir movimento:', err);
    }
  };

  if (loading) {
    return <p>Carregando movimentos financeiros...</p>;
  }

  if (error) {
    return <p className="text-red-500">{error}</p>;
  }

  return (
    <Card className="glass-effect">
      <CardHeader className="flex flex-row justify-between items-center">
        <CardTitle className="text-white">Movimentos Financeiros</CardTitle>
        {isAdmin && (
          <Button className="gradient-primary hover-scale" onClick={() => setIsAddingMovement(!isAddingMovement)}>
            <PlusCircle className="mr-2 h-5 w-5" />
            {isAddingMovement ? 'Cancelar' : 'Adicionar Movimento'}
          </Button>
        )}
      </CardHeader>
      <CardContent>
        {isAddingMovement && isAdmin && (
          <form onSubmit={handleAddMovement} className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6 p-4 border border-gray-700 rounded-md">
            <div className="col-span-1">
              <Label htmlFor="tipoMovimento" className="text-gray-300">Tipo</Label>
              <Select value={tipoMovimento} onValueChange={setTipoMovimento}>
                <SelectTrigger className="w-full bg-gray-800 border-gray-700 text-white">
                  <SelectValue placeholder="Tipo de Movimento" />
                </SelectTrigger>
                <SelectContent className="bg-gray-800 text-white border-gray-700">
                  <SelectItem value="entrada">Entrada</SelectItem>
                  <SelectItem value="saida">Saída</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="col-span-1">
              <Label htmlFor="descricao" className="text-gray-300">Descrição</Label>
              <Input
                id="descricao"
                type="text"
                value={descricao}
                onChange={(e) => setDescricao(e.target.value)}
                className="bg-gray-800 border-gray-700 text-white placeholder-gray-500 focus:border-primary focus:ring-primary"
                placeholder="Ex: Compra de bolas"
                required
              />
            </div>
            <div className="col-span-1">
              <Label htmlFor="valor" className="text-gray-300">Valor</Label>
              <Input
                id="valor"
                type="number"
                step="0.01"
                value={valor}
                onChange={(e) => setValor(e.target.value)}
                className="bg-gray-800 border-gray-700 text-white placeholder-gray-500 focus:border-primary focus:ring-primary"
                placeholder="Ex: 50.00"
                required
              />
            </div>
            {addError && <p className="text-red-500 text-sm col-span-3">{addError}</p>}
            <Button type="submit" className="gradient-primary hover-scale col-span-3">
              Adicionar
            </Button>
          </form>
        )}

        <div className="mb-6 p-4 bg-muted rounded-md flex justify-around items-center text-center">
          <div>
            <p className="text-gray-300">Entradas</p>
            <p className="text-primary font-bold text-lg">R$ {resumo.total_entradas.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-gray-300">Saídas</p>
            <p className="text-destructive font-bold text-lg">R$ {resumo.total_saidas.toFixed(2)}</p>
          </div>
          <div>
            <p className="text-gray-300">Saldo</p>
            <p className={`font-bold text-lg ${resumo.saldo >= 0 ? 'text-primary' : 'text-destructive'}`}>R$ {resumo.saldo.toFixed(2)}</p>
          </div>
        </div>

        {movimentos.length === 0 ? (
          <p className="text-gray-400">Nenhum movimento financeiro registrado ainda.</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="text-primary">Data</TableHead>
                <TableHead className="text-primary">Tipo</TableHead>
                <TableHead className="text-primary">Descrição</TableHead>
                <TableHead className="text-primary text-right">Valor</TableHead>
                {isAdmin && <TableHead className="text-primary text-center">Ações</TableHead>}
              </TableRow>
            </TableHeader>
            <TableBody>
              {movimentos.map((mov) => (
                <TableRow key={mov.id}>
                  <TableCell>{new Date(mov.data_movimento).toLocaleDateString()}</TableCell>
                  <TableCell className={mov.tipo_movimento === 'entrada' ? 'text-primary' : 'text-destructive'}>
                    {mov.tipo_movimento === 'entrada' ? 'Entrada' : 'Saída'}
                  </TableCell>
                  <TableCell>{mov.descricao}</TableCell>
                  <TableCell className="text-right">R$ {parseFloat(mov.valor).toFixed(2)}</TableCell>
                  {isAdmin && (
                    <TableCell className="text-center">
                      <Button variant="ghost" size="sm" onClick={() => handleDeleteMovement(mov.id)}>
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </TableCell>
                  )}
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
};

FinancialMovements.propTypes = {
  peladaId: PropTypes.number.isRequired,
  isAdmin: PropTypes.bool.isRequired,
};

export default FinancialMovements;


