import React, { useState } from 'react';
import AuthLayout from '../../components/layout/AuthLayout';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Link } from 'react-router-dom';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, senha: password }),
      });

      const data = await response.json();

      if (!response.ok) {
        setError(data.error || 'Erro ao fazer login');
        return;
      }

      // Redirecionar ou atualizar estado do usuário após login bem-sucedido
      console.log('Login bem-sucedido:', data);
      // Ex: history.push('/dashboard');

    } catch (err) {
      setError('Erro de conexão. Tente novamente.');
      console.error('Erro de login:', err);
    }
  };

  return (
    <AuthLayout>
      <form onSubmit={handleSubmit} className="space-y-6">
        {error && <p className="text-red-500 text-sm">{error}</p>}
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
        <Button type="submit" className="w-full gradient-primary text-white py-2 rounded-md hover-scale">
          Entrar
        </Button>
      </form>
      <p className="mt-6 text-gray-400">
        Não tem uma conta?{' '}
        <Link to="/register" className="text-primary hover:underline">
          Cadastre-se
        </Link>
      </p>
    </AuthLayout>
  );
};

export default Login;


