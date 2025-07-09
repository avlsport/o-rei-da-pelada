import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';

const RankingPelada = () => {
  const { peladaId } = useParams();
  const [ranking, setRanking] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filterType, setFilterType] = useState('geral'); // geral, ano, mes
  const [availableYears, setAvailableYears] = useState([]);
  const [selectedYear, setSelectedYear] = useState('');

  useEffect(() => {
    const fetchRankingData = async () => {
      setLoading(true);
      setError(null);
      try {
        let url = `/api/ranking/pelada/${peladaId}?tipo=${filterType}`;
        if (filterType === 'ano' && selectedYear) {
          url += `&ano=${selectedYear}`;
        }

        const response = await fetch(url);
        const data = await response.json();

        if (!response.ok) {
          setError(data.error || 'Erro ao buscar ranking da pelada.');
          return;
        }
        setRanking(data.ranking);
      } catch (err) {
        setError('Erro de conexão ao buscar ranking.');
        console.error('Erro ao buscar ranking da pelada:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchRankingData();
  }, [peladaId, filterType, selectedYear]);

  useEffect(() => {
    const fetchAvailableYears = async () => {
      try {
        const response = await fetch(`/api/ranking/pelada/${peladaId}/anos`);
        const data = await response.json();
        if (response.ok) {
          setAvailableYears(data.anos);
          if (data.anos.length > 0) {
            setSelectedYear(String(data.anos[data.anos.length - 1])); // Seleciona o ano mais recente por padrão
          }
        }
      } catch (err) {
        console.error('Erro ao buscar anos disponíveis:', err);
      }
    };
    fetchAvailableYears();
  }, [peladaId]);

  if (loading) {
    return <p>Carregando ranking...</p>;
  }

  if (error) {
    return <p className="text-red-500">{error}</p>;
  }

  return (
    <Card className="glass-effect">
      <CardHeader>
        <CardTitle className="text-white">Ranking da Pelada</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex space-x-4 mb-4">
          <Select value={filterType} onValueChange={setFilterType}>
            <SelectTrigger className="w-[180px] bg-gray-800 border-gray-700 text-white">
              <SelectValue placeholder="Filtrar por" />
            </SelectTrigger>
            <SelectContent className="bg-gray-800 text-white border-gray-700">
              <SelectItem value="geral">Geral</SelectItem>
              <SelectItem value="ano">Por Ano</SelectItem>
              <SelectItem value="mes">Último Mês</SelectItem>
            </SelectContent>
          </Select>

          {filterType === 'ano' && availableYears.length > 0 && (
            <Select value={selectedYear} onValueChange={setSelectedYear}>
              <SelectTrigger className="w-[180px] bg-gray-800 border-gray-700 text-white">
                <SelectValue placeholder="Selecione o Ano" />
              </SelectTrigger>
              <SelectContent className="bg-gray-800 text-white border-gray-700">
                {availableYears.map(year => (
                  <SelectItem key={year} value={String(year)}>{year}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          )}
        </div>

        {ranking.length === 0 ? (
          <p className="text-gray-400">Nenhum jogador no ranking desta pelada ainda.</p>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead className="text-primary">Posição</TableHead>
                <TableHead className="text-primary">Nome</TableHead>
                <TableHead className="text-primary">Posição</TableHead>
                <TableHead className="text-primary text-right">Média de Pontos</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {ranking.map((player) => (
                <TableRow key={player.usuario_id}>
                  <TableCell className="font-medium">{player.posicao}</TableCell>
                  <TableCell>{player.nome}</TableCell>
                  <TableCell>{player.posicao_campo}</TableCell>
                  <TableCell className="text-right">{player.media_pontos}</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
};

export default RankingPelada;


