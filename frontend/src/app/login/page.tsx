"use client";

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { api } from '@/utils/api';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLogin, setIsLogin] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    try {
      if (isLogin) {
        const res = await api.post('/auth/login', { email, password });
        localStorage.setItem('token', res.data.access_token);
        router.push('/dashboard');
      } else {
        await api.post('/auth/register', { email, password });
        setIsLogin(true);
        setError('Registration successful. Please login.');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'An error occurred. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-[#050B14] flex items-center justify-center p-4">
      <div className="max-w-md w-full bg-[#0a0e17] rounded-2xl shadow-2xl border border-gray-800 p-8 transform transition-all hover:scale-[1.01]">
        <div className="text-center mb-10">
          <h1 className="text-4xl font-black bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400 tracking-tighter mb-2">
            TradeVision<span className="text-white">AI</span>
          </h1>
          <p className="text-gray-400 font-medium">Next-Generation Trading Platform</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {error && (
            <div className={`p-4 rounded-lg text-sm font-semibold ${error.includes('successful') ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' : 'bg-red-500/10 text-red-400 border border-red-500/20'}`}>
              {error}
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Email Address</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-[#131B2B] text-white border border-gray-700 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
              placeholder="trader@tradevision.ai"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-[#131B2B] text-white border border-gray-700 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all"
              placeholder="••••••••"
              required
            />
          </div>

          <button
            type="submit"
            className="w-full bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-400 hover:to-teal-400 text-white font-bold py-3.5 px-4 rounded-xl shadow-lg transform transition-all active:scale-95"
          >
            {isLogin ? 'Secure Login' : 'Create Account'}
          </button>
        </form>

        <div className="mt-8 text-center">
          <button
            onClick={() => setIsLogin(!isLogin)}
            className="text-emerald-400 hover:text-emerald-300 text-sm font-medium transition-colors"
          >
            {isLogin ? "Don't have an account? Sign up" : "Already have an account? Log in"}
          </button>
        </div>
      </div>
    </div>
  );
}
