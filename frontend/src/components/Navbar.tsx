"use client";

import Link from 'next/link';
import { useRouter } from 'next/navigation';

export default function Navbar() {
  const router = useRouter();

  const handleLogout = () => {
    localStorage.removeItem("token");
    router.push("/login");
  };

  return (
    <nav className="fixed top-0 w-full bg-[#0a0e17] border-b border-gray-800 z-50 px-6 py-4 flex justify-between items-center h-16 shadow-xl backdrop-blur-md bg-opacity-90">
      <div className="flex items-center space-x-8">
        <Link href="/dashboard" className="text-2xl font-black bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-emerald-400 tracking-tighter">
          TradeVision<span className="text-white">AI</span>
        </Link>
        <div className="hidden md:flex space-x-6 text-sm font-medium text-gray-400">
          <Link href="/dashboard" className="hover:text-emerald-400 transition-colors">Dashboard</Link>
          <Link href="/portfolio" className="hover:text-emerald-400 transition-colors">Portfolio</Link>
          <Link href="/orders" className="hover:text-emerald-400 transition-colors">Orders</Link>
          <Link href="/ipo" className="hover:text-emerald-400 transition-colors">IPO & SIP</Link>
        </div>
      </div>

      <div className="flex flex-row items-center space-x-4">
        <div className="hidden md:flex items-center space-x-2 bg-gray-900 px-3 py-1.5 rounded-full border border-gray-700">
          <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></div>
          <span className="text-xs text-gray-300 font-medium">Market Open</span>
        </div>
        
        <button className="text-gray-400 hover:text-white transition-colors">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"></path></svg>
        </button>

        <button onClick={handleLogout} className="bg-gray-800 hover:bg-gray-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-all shadow-md">
          Logout
        </button>
      </div>
    </nav>
  );
}
