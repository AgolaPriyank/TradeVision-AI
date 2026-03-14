"use client";

import Navbar from '@/components/Navbar';

export default function IpoSip() {
  return (
    <div className="min-h-screen bg-[#050B14] text-white font-sans overflow-y-auto">
      <Navbar />
      
      <main className="pt-24 px-6 max-w-[1200px] mx-auto pb-12">
        <h1 className="text-3xl font-black mb-8 text-emerald-400">IPO & Systematic Investment Plan (SIP)</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          
          <div className="bg-[#0a0e17] rounded-xl border border-gray-800 shadow-lg overflow-hidden">
             <div className="px-6 py-4 border-b border-gray-800 bg-gray-900/50">
               <h2 className="text-lg font-bold text-gray-200">Active IPOs</h2>
             </div>
             <div className="p-6">
                <div className="border border-gray-800 rounded-lg p-4 bg-[#131B2B]">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-bold text-lg">Stripe Inc. (STRP)</h3>
                      <p className="text-sm text-gray-400">Fintech Infrastructure</p>
                    </div>
                    <span className="px-2 py-1 text-xs font-bold rounded bg-emerald-500/20 text-emerald-400">OPEN</span>
                  </div>
                  <div className="grid grid-cols-2 gap-4 my-4 text-sm">
                    <div>
                      <p className="text-gray-500">Issue Price</p>
                      <p className="font-semibold">$65.00 - $70.00</p>
                    </div>
                    <div>
                      <p className="text-gray-500">Lot Size</p>
                      <p className="font-semibold">10 Shares</p>
                    </div>
                  </div>
                  <button className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-2 rounded-lg transition-colors">
                    Apply for IPO
                  </button>
                </div>

                <div className="mt-6 border border-gray-800 rounded-lg p-4 bg-[#131B2B] opacity-70">
                  <div className="flex justify-between items-start mb-2">
                    <div>
                      <h3 className="font-bold text-lg">Databricks (DBRX)</h3>
                      <p className="text-sm text-gray-400">AI & Data Analytics</p>
                    </div>
                    <span className="px-2 py-1 text-xs font-bold rounded bg-yellow-500/20 text-yellow-500">UPCOMING</span>
                  </div>
                  <p className="text-sm text-gray-400 my-4 text-center">Opens Oct 12, 2024</p>
                </div>
             </div>
          </div>

          <div className="bg-[#0a0e17] rounded-xl border border-gray-800 shadow-lg overflow-hidden">
             <div className="px-6 py-4 border-b border-gray-800 bg-gray-900/50">
               <h2 className="text-lg font-bold text-gray-200">Start New SIP</h2>
             </div>
             <div className="p-6">
                <form className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">Target Stock / ETF</label>
                    <input type="text" placeholder="e.g. SPY, AAPL" className="w-full bg-[#131B2B] text-white border border-gray-700 rounded-lg px-4 py-2" />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">Monthly Investment Amount ($)</label>
                    <input type="number" placeholder="500" className="w-full bg-[#131B2B] text-white border border-gray-700 rounded-lg px-4 py-2" />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-400 mb-2">Deduction Date (AutoPay)</label>
                    <select className="w-full bg-[#131B2B] text-white border border-gray-700 rounded-lg px-4 py-2">
                      <option>1st of every month</option>
                      <option>15th of every month</option>
                    </select>
                  </div>

                  <div className="pt-4">
                    <button type="button" className="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 rounded-lg shadow-lg transition-colors">
                      Activate Auto-SIP
                    </button>
                  </div>
                </form>
             </div>
          </div>

        </div>
      </main>
    </div>
  );
}
