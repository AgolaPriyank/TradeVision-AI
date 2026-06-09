"use client";

import { useEffect, useState } from 'react';
import Navbar from '@/components/Navbar';
import { api } from '@/utils/api';
import TradingChart from '@/components/TradingChart';
import RecommendationPanel from '@/components/RecommendationPanel';

interface PortfolioData {
  available_balance: number;
  total_invested: number;
  current_value: number;
  total_pnl: number;
  holdings: any[];
}

interface MLPrediction {
  prediction: number;
  recommendation: string;
  confidence: number;
  latest_close: number;
}

export default function Dashboard() {
  const [portfolio, setPortfolio] = useState<PortfolioData | null>(null);
  const [activeSymbol, setActiveSymbol] = useState('AAPL');
  const [chartData, setChartData] = useState([]);
  const [mlData, setMlData] = useState<MLPrediction | null>(null);

  useEffect(() => {
    fetchPortfolio();
    fetchMarketData(activeSymbol);
    fetchMLPrediction(activeSymbol);
  }, [activeSymbol]);

  const fetchPortfolio = async () => {
    try {
      const res = await api.get('/portfolio');
      setPortfolio(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchMarketData = async (symbol: string) => {
    try {
      const res = await api.get(`/market/history/${symbol}?range=3mo`);
      const formattedData = res.data.history.map((item: any) => ({
        time: item.Date.split(' ')[0],
        open: item.Open,
        high: item.High,
        low: item.Low,
        close: item.Close,
      }));
      setChartData(formattedData);
    } catch (err) {
      console.error(err);
    }
  };

  const fetchMLPrediction = async (symbol: string) => {
    try {
      const mlApi = api.create({ baseURL: 'http://localhost:8001' }); // Suppose ML engine runs on 8001
      const res = await mlApi.get(`/api/v1/ml/predict/${symbol}`);
      setMlData(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="min-h-screen bg-[#050B14] text-white font-sans">
      <Navbar />
      
      <main className="pt-24 px-6 max-w-[1600px] mx-auto grid grid-cols-1 lg:grid-cols-4 gap-6">
        
        {/* Left Sidebar - Portfolio Summary */}
        <div className="lg:col-span-1 space-y-6">
          <div className="bg-[#0a0e17] rounded-xl p-6 border border-gray-800 shadow-xl">
            <h2 className="text-gray-400 text-sm font-bold uppercase tracking-wider mb-4">Total Net Worth</h2>
            <div className="text-4xl font-black mb-2">${portfolio ? (portfolio.available_balance + portfolio.current_value).toLocaleString('en-US', {minimumFractionDigits: 2}) : '0.00'}</div>
            
            <div className={`text-sm font-semibold flex items-center ${(portfolio?.total_pnl || 0) >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
              {(portfolio?.total_pnl || 0) >= 0 ? '+' : ''}
              ${portfolio?.total_pnl?.toLocaleString('en-US', {minimumFractionDigits: 2}) || '0.00'} Overall P&L
            </div>

            <div className="mt-6 pt-6 border-t border-gray-800 grid grid-cols-2 gap-4">
              <div>
                <p className="text-xs text-gray-500 mb-1">Available Cash</p>
                <p className="font-semibold text-lg text-white">${portfolio?.available_balance?.toLocaleString('en-US', {minimumFractionDigits: 2}) || '0.00'}</p>
              </div>
              <div>
                <p className="text-xs text-gray-500 mb-1">Total Invested</p>
                <p className="font-semibold text-lg text-gray-300">${portfolio?.total_invested?.toLocaleString('en-US', {minimumFractionDigits: 2}) || '0.00'}</p>
              </div>
            </div>
          </div>

          <div className="bg-[#0a0e17] rounded-xl border border-gray-800 shadow-xl overflow-hidden">
             <div className="p-4 bg-gradient-to-r from-indigo-900/50 to-purple-900/50 border-b border-gray-700">
               <h3 className="text-indigo-400 font-bold flex items-center text-sm uppercase tracking-wide">
                 <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z"></path></svg>
                 AI Engine Insight
               </h3>
             </div>
             <div className="p-6">
               {mlData ? (
                 <div className="space-y-4">
                   <div className="flex justify-between items-center">
                     <span className="text-gray-400 text-sm">Target Asset</span>
                     <span className="font-bold">{activeSymbol}</span>
                   </div>
                   <div className="flex justify-between items-center">
                     <span className="text-gray-400 text-sm">AI Recommendation</span>
                     <span className={`font-black uppercase px-3 py-1 rounded ${mlData.recommendation === 'BUY' ? 'bg-emerald-500/20 text-emerald-400' : mlData.recommendation === 'SELL' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-500'}`}>
                       {mlData.recommendation}
                     </span>
                   </div>
                   <div className="w-full bg-gray-800 rounded-full h-1.5 mt-2">
                     <div className={`h-1.5 rounded-full ${mlData.recommendation === 'BUY' ? 'bg-emerald-500' : 'bg-red-500'}`} style={{width: `${mlData.confidence * 100}%`}}></div>
                   </div>
                   <p className="text-xs text-right text-gray-500 mt-1">{(mlData.confidence * 100).toFixed(1)}% Confidence Score</p>
                 </div>
               ) : (
                 <p className="text-sm text-gray-500 text-center py-4">Analyzing market telemetry...</p>
               )}
             </div>
          </div>
        </div>

        {/* Center - Charting */}
        <div className="lg:col-span-3 space-y-6">
          <div className="bg-[#0a0e17] rounded-xl p-4 border border-gray-800 shadow-xl flex items-center justify-between">
            <div className="flex space-x-2">
              {['AAPL', 'MSFT', 'TSLA', 'NVDA', 'AMZN'].map(sym => (
                <button 
                  key={sym} 
                  onClick={() => setActiveSymbol(sym)}
                  className={`px-4 py-2 rounded-lg text-sm font-bold transition-all ${activeSymbol === sym ? 'bg-indigo-600 text-white shadow-lg shadow-indigo-500/30' : 'bg-gray-800 text-gray-400 hover:bg-gray-700'}`}
                >
                  {sym}
                </button>
              ))}
            </div>
            
            <div className="flex rounded-lg bg-gray-800 p-1">
               <button className="px-3 py-1 text-xs font-semibold rounded bg-gray-700 text-white shadow">3M</button>
               <button className="px-3 py-1 text-xs font-semibold rounded text-gray-400 hover:text-white">1Y</button>
            </div>
          </div>
          
          <div className="bg-[#0a0e17] rounded-xl p-1 border border-gray-800 shadow-xl h-[500px]">
            {chartData.length > 0 ? (
               <TradingChart data={chartData} />
            ) : (
               <div className="w-full h-full flex items-center justify-center">
                 <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-500"></div>
               </div>
            )}
          </div>
        </div>
      </main>

      {/* Recommendations Section */}
      <section className="pt-6 px-6 max-w-[1600px] mx-auto pb-12">
        <RecommendationPanel autoRefresh={true} refreshInterval={60} />
      </section>
    </div>
  );
}
