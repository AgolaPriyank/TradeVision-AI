"use client";

import { useEffect, useState } from 'react';
import Navbar from '@/components/Navbar';
import { api } from '@/utils/api';

export default function Portfolio() {
  const [portfolio, setPortfolio] = useState<any>(null);

  useEffect(() => {
    fetchPortfolio();
  }, []);

  const fetchPortfolio = async () => {
    try {
      const res = await api.get('/portfolio');
      setPortfolio(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-[#050B14] text-white font-sans overflow-y-auto">
      <Navbar />
      
      <main className="pt-24 px-6 max-w-[1200px] mx-auto pb-12">
        <h1 className="text-3xl font-black mb-8 text-emerald-400">My Portfolio</h1>

        {portfolio ? (
          <div className="space-y-8">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-[#0a0e17] rounded-xl p-6 border border-gray-800 shadow-lg">
                <p className="text-gray-400 text-sm font-bold uppercase mb-2">Total Equity</p>
                <p className="text-3xl font-black">${(portfolio.available_balance + portfolio.current_value).toLocaleString('en-US', {minimumFractionDigits: 2})}</p>
              </div>
              <div className="bg-[#0a0e17] rounded-xl p-6 border border-gray-800 shadow-lg">
                <p className="text-gray-400 text-sm font-bold uppercase mb-2">Available Cash</p>
                <p className="text-3xl font-black">${portfolio.available_balance.toLocaleString('en-US', {minimumFractionDigits: 2})}</p>
              </div>
              <div className="bg-[#0a0e17] rounded-xl p-6 border border-gray-800 shadow-lg">
                <p className="text-gray-400 text-sm font-bold uppercase mb-2">Total P&L</p>
                <p className={`text-3xl font-black ${portfolio.total_pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                  {portfolio.total_pnl >= 0 ? '+' : ''}${portfolio.total_pnl.toLocaleString('en-US', {minimumFractionDigits: 2})}
                </p>
              </div>
            </div>

            <div className="bg-[#0a0e17] rounded-xl border border-gray-800 shadow-lg overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-800 bg-gray-900/50">
                <h2 className="text-lg font-bold text-gray-200">Current Holdings</h2>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full text-left border-collapse">
                  <thead>
                    <tr className="bg-gray-800/30 text-gray-400 text-xs uppercase tracking-wider">
                      <th className="px-6 py-4 font-semibold">Symbol</th>
                      <th className="px-6 py-4 font-semibold text-right">Shares</th>
                      <th className="px-6 py-4 font-semibold text-right">Avg Price</th>
                      <th className="px-6 py-4 font-semibold text-right">LTP</th>
                      <th className="px-6 py-4 font-semibold text-right">Current Value</th>
                      <th className="px-6 py-4 font-semibold text-right">P&L</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800">
                    {portfolio.holdings && portfolio.holdings.length > 0 ? (
                      portfolio.holdings.map((h: any) => (
                        <tr key={h.symbol} className="hover:bg-gray-800/20 transition-colors">
                          <td className="px-6 py-4 font-bold text-lg">{h.symbol}</td>
                          <td className="px-6 py-4 text-right text-gray-300">{h.shares}</td>
                          <td className="px-6 py-4 text-right text-gray-400">${Number(h.avg_buy_price).toFixed(2)}</td>
                          <td className="px-6 py-4 text-right text-white font-semibold">${Number(h.current_price).toFixed(2)}</td>
                          <td className="px-6 py-4 text-right text-white font-semibold">${Number(h.current_value).toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                          <td className={`px-6 py-4 text-right font-bold ${h.pnl >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
                            {h.pnl >= 0 ? '+' : ''}${h.pnl.toLocaleString('en-US', {minimumFractionDigits: 2})} <br/>
                            <span className="text-xs">({h.pnl_percentage.toFixed(2)}%)</span>
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                          No active holdings. Start trading!
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        ) : (
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-emerald-500"></div>
          </div>
        )}
      </main>
    </div>
  );
}
