import React, { useState, useEffect } from 'react';
import PropTypes from 'prop-types';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { CheckCircle, XCircle } from 'lucide-react';

const MonthlyPlayers = ({ peladaId, isAdmin }) => {
  const [mensalistas, setMensalistas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchMensalistas = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await fetch(`/api/financeiro/pelada/${peladaId}/mensalistas`);
      const data = await response.json();

      if (!response.ok) {
        setError(data.error || 'Erro ao buscar mensalistas.');
        return;
      }
      setMensalistas(data.mensalistas);
    } catch (err) {
      setError('Erro de conexão ao buscar mensalistas.');
      console.error('Erro ao buscar mensalistas:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMensalistas();
  }, [peladaId]);

  const handleUpdatePaymentStatus = async (usuarioId, status) => {
    if (!isAdmin) return;

    try {
      const response = await fetch(`/api/financeiro/pelada/${peladaId}/mensalista/${usuarioId}/pagamento`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status_pagamento: status }),
      });

      const data = await response.json();

      if (!response.ok) {
        alert(data.error || 'Erro ao atualizar status de pagamento.');
        return;
      }

      alert('Status de pagamento atualizado com sucesso!');
      fetchMensalistas(); // Recarrega a lista

    } catch (err) {
      alert('Erro de conexão ao atualizar status de pagamento.');
      console.error('Erro ao atualizar status de pagamento:', err);
    }
  };

  if (loading) {
    return <p>Carregando mensalistas...</p>;
  }

  if (error) {
    return <p className="text-red-500">{error}</p>;
  }

  return (
    <Card className="glass-effect">
      <CardHeader>
        <CardTitle className="text-white">Mensalistas</CardTitle>
      </CardHeader>
      <CardContent>
        {mensalistas.length === 0 ? (
          <p className="text-gray-400">Nenhum mensalista registrado ainda.</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="text-primary">Nome</TableHead>
                <TableHead className="text-primary">Status Pagamento</TableHead>
                <TableHead className="text-primary">Último Pagamento</TableHead>
                {isAdmin && <TableHead className="text-primary text-center">Ações</TableHead>}
              </TableRow>
            </TableHeader>
            <TableBody>
              {mensalistas.map((mensalista) => (
                <TableRow key={mensalista.usuario.id}>
                  <TableCell>{mensalista.usuario.nome}</TableCell>
                  <TableCell
                    className={mensalista.status_pagamento === 'pago' ? 'text-primary' : 'text-destructive'}
                  >
                    {mensalista.status_pagamento === 'pago' ? 'Pago' : 'Pendente'}
                  </TableCell>
                  <TableCell>
                    {mensalista.data_ultimo_pagamento
                      ? new Date(mensalista.data_ultimo_pagamento).toLocaleDateString()
                      : 'N/A'}
                  </TableCell>
                  {isAdmin && (
                    <TableCell className="text-center">
                      {mensalista.status_pagamento === 'pendente' ? (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleUpdatePaymentStatus(mensalista.usuario.id, 'pago')}
                        >
                          <CheckCircle className="h-4 w-4 text-primary" />
                        </Button>
                      ) : (
                        <Button
                          variant="ghost"
                          size="sm"
                          onClick={() => handleUpdatePaymentStatus(mensalista.usuario.id, 'pendente')}
                        >
                          <XCircle className="h-4 w-4 text-destructive" />
                        </Button>
                      )}
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

MonthlyPlayers.propTypes = {
  peladaId: PropTypes.number.isRequired,
  isAdmin: PropTypes.bool.isRequired,
};

export default MonthlyPlayers;


