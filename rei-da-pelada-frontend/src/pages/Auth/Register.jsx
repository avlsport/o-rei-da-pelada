import React, { useState } from 'react';
import AuthLayout from '../../components/layout/AuthLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Link } from 'react-router-dom';

const Register = () => {
  const [nome, setNome] = useState('');
  const [posicao, setPosicao] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    if (password !== confirmPassword) {
      setError('As senhas não coincidem.');
      return;
    }

    try {
      const response = await fetch(`${import.meta.env.VITE_API_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ nome, posicao, email, senha: password }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || 'Erro ao cadastrar usuário.');
        return;
      }

      setSuccess('Cadastro realizado com sucesso! Redirecionando para o login...');
      setTimeout(() => {
        window.location.href = '/login';
      }, 2000);

    } catch (err) {
      setError('Erro de conexão. Tente novamente.');
      console.error('Erro de cadastro:', err);
    }
  };

  return (
    <AuthLayout>
      <form onSubmit={handleSubmit} className="space-y-4">
        {error && <p className="text-red-500 text-sm">{error}</p>}
        {success && <p className="text-green-500 text-sm">{success}</p>}
        <div>
          <Label htmlFor="nome" className="text-left text-gray-300">Nome</Label>
          <Input
            id="nome"
            type="text"
            placeholder="Seu nome completo"
            value={nome}
            onChange={(e) => setNome(e.target.value)}
            required
            className="mt-1 block w-full bg-gray-800 border-gray-700 text-white placeholder-gray-500 focus:border-primary focus:ring-primary"
          />
        </div>
        <div>
          <Label htmlFor="posicao" className="text-left text-gray-300">Posição</Label>
          <select
            id="posicao"
            value={posicao}
            onChange={(e) => setPosicao(e.target.value)}
            required
            className="mt-1 block w-full bg-gray-800 border-gray-700 text-white focus:border-primary focus:ring-primary rounded-md shadow-sm py-2 px-3"
          >
            <option value="">Selecione sua posição</option>
            <option value="Goleiro">Goleiro</option>
            <option value="Zagueiro">Zagueiro</option>
            <option value="Meio Campo">Meio Campo</option>
            <option value="Atacante">Atacante</option>
          </select>
        </div>
        <div>
          <Label htmlFor="email" className="text-left text-gray-300">Email</Label>
          <Input
            id="email"
            type="email"
            placeholder="seuemail@exemplo.com"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="mt-1 block w-full bg-gray-800 border-gray-700 text-white placeholder-gray-500 focus:border-primary focus:ring-primary"
          />
        </div>
        <div>
          <Label htmlFor="password" className="text-left text-gray-300">Senha</Label>
          <Input
            id="password"
            type="password"
            placeholder="********"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="mt-1 block w-full bg-gray-800 border-gray-700 text-white placeholder-gray-500 focus:border-primary focus:ring-primary"
          />
        </div>
        <div>
          <Label htmlFor="confirmPassword" className="text-left text-gray-300">Confirmar Senha</Label>
          <Input
            id="confirmPassword"
            type="password"
            placeholder="********"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            className="mt-1 block w-full bg-gray-800 border-gray-700 text-white placeholder-gray-500 focus:border-primary focus:ring-primary"
          />
        </div>
        <Button type="submit" className="w-full gradient-primary text-white py-2 rounded-md hover-scale">
          Cadastrar
        </Button>
      </form>
      <p className="mt-6 text-gray-400">
        Já tem uma conta?{' '}
        <Link to="/login" className="text-primary hover:underline">
          Entrar
        </Link>
      </p>
    </AuthLayout>
  );
};

export default Register;


