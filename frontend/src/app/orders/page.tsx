"use client";

import { useEffect, useState } from 'react';
import Navbar from '@/components/Navbar';
import { api } from '@/utils/api';

export default function Orders() {
  const [orders, setOrders] = useState<any[]>([]);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const res = await api.get('/orders');
      setOrders(res.data);
    } catch (err) {
      console.error(err);
    }
  };

  const placeOrder = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const form = e.currentTarget;
    const submitter = (e.nativeEvent as SubmitEvent).submitter as HTMLButtonElement;
    const orderData = {
      symbol: (form.elements.namedItem('symbol') as HTMLInputElement).value,
      order_side: submitter.value,
      order_type: 'MARKET',
      quantity: Number((form.elements.namedItem('quantity') as HTMLInputElement).value),
    };

    try {
      await api.post('/orders', orderData);
      fetchOrders(); // Refresh table
    } catch (err: any) {
      alert("Trade failed: " + (err?.response?.data?.detail || "Unknown error"));
    }
  };

  return (
    <div className="min-h-screen bg-[#050B14] text-white font-sans overflow-y-auto">
      <Navbar />
      
      <main className="pt-24 px-6 max-w-[1200px] mx-auto pb-12 grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        <div className="lg:col-span-1">
          <div className="bg-[#0a0e17] rounded-xl p-6 border border-gray-800 shadow-lg sticky top-24">
            <h2 className="text-xl font-bold mb-6 text-emerald-400 border-b border-gray-800 pb-4">Execute Trade</h2>
            <form onSubmit={placeOrder} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Symbol / Ticker</label>
                <input required name="symbol" type="text" placeholder="AAPL" className="w-full bg-[#131B2B] text-white border border-gray-700 rounded-lg px-4 py-2 uppercase placeholder:normal-case font-bold" />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-400 mb-2">Quantity</label>
                <input required name="quantity" type="number" min="1" placeholder="10" className="w-full bg-[#131B2B] text-white border border-gray-700 rounded-lg px-4 py-2" />
              </div>

              <div className="pt-4 grid grid-cols-2 gap-4">
                <button type="submit" name="order_side" value="BUY" className="bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 rounded-lg shadow-lg active:scale-95 transition-all w-full">
                  BUY
                </button>
                <button type="submit" name="order_side" value="SELL" className="bg-red-600 hover:bg-red-500 text-white font-bold py-3 rounded-lg shadow-lg active:scale-95 transition-all w-full">
                  SELL
                </button>
              </div>
            </form>
          </div>
        </div>

        <div className="lg:col-span-2">
          <div className="bg-[#0a0e17] rounded-xl border border-gray-800 shadow-lg overflow-hidden">
            <div className="px-6 py-4 border-b border-gray-800 bg-gray-900/50">
              <h2 className="text-lg font-bold text-gray-200">Order History</h2>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-gray-800/30 text-gray-400 text-xs uppercase tracking-wider">
                    <th className="px-6 py-4 font-semibold">Time</th>
                    <th className="px-6 py-4 font-semibold">Symbol</th>
                    <th className="px-6 py-4 font-semibold">Side</th>
                    <th className="px-6 py-4 font-semibold">Qty</th>
                    <th className="px-6 py-4 font-semibold">Price</th>
                    <th className="px-6 py-4 font-semibold">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-800">
                  {orders.length > 0 ? (
                    orders.map((o: any) => (
                      <tr key={o.id} className="hover:bg-gray-800/20 transition-colors">
                        <td className="px-6 py-4 text-sm text-gray-400">{new Date(o.created_at).toLocaleString()}</td>
                        <td className="px-6 py-4 font-bold">{o.symbol}</td>
                        <td className={`px-6 py-4 font-bold ${o.order_side === 'BUY' ? 'text-emerald-400' : 'text-red-400'}`}>{o.order_side}</td>
                        <td className="px-6 py-4 text-gray-300">{o.quantity}</td>
                        <td className="px-6 py-4 text-gray-300 font-medium">${Number(o.executed_price).toFixed(2)}</td>
                        <td className="px-6 py-4">
                          <span className={`px-2 py-1 text-xs font-bold rounded ${o.status === 'EXECUTED' ? 'bg-emerald-500/20 text-emerald-400' : 'bg-yellow-500/20 text-yellow-500'}`}>
                            {o.status}
                          </span>
                        </td>
                      </tr>
                    ))
                  ) : (
                    <tr>
                      <td colSpan={6} className="px-6 py-12 text-center text-gray-500">
                        No orders placed yet.
                      </td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          </div>
        </div>

      </main>
    </div>
  );
}
