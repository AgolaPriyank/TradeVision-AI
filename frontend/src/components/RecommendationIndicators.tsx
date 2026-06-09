"use client";

import React from 'react';

interface RecommendationIndicatorsProps {
  rsi?: number;
  macd?: number;
  sma10?: number;
  sma50?: number;
  currentPrice?: number;
}

export default function RecommendationIndicators({
  rsi,
  macd,
  sma10,
  sma50,
  currentPrice,
}: RecommendationIndicatorsProps) {
  const formatNumber = (num: number | undefined) => {
    if (num === undefined) return 'N/A';
    return num.toFixed(2);
  };

  const getRSIColor = (value: number | undefined) => {
    if (value === undefined) return 'text-gray-400';
    if (value > 70) return 'text-red-400';
    if (value < 30) return 'text-green-400';
    return 'text-yellow-400';
  };

  const getMACDColor = (value: number | undefined) => {
    if (value === undefined) return 'text-gray-400';
    if (value > 0) return 'text-green-400';
    return 'text-red-400';
  };

  const getSMAColor = (price: number | undefined, sma: number | undefined) => {
    if (price === undefined || sma === undefined) return 'text-gray-400';
    if (price > sma) return 'text-green-400';
    return 'text-red-400';
  };

  return (
    <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mt-3">
      {/* RSI */}
      <div className="bg-gray-900 p-3 rounded-lg border border-gray-800">
        <p className="text-xs text-gray-500 mb-1">RSI (14)</p>
        <p className={`text-lg font-semibold ${getRSIColor(rsi)}`}>
          {formatNumber(rsi)}
        </p>
        <p className="text-xs text-gray-600 mt-1">
          {rsi ? (rsi > 70 ? 'Overbought' : rsi < 30 ? 'Oversold' : 'Neutral') : 'N/A'}
        </p>
      </div>

      {/* MACD */}
      <div className="bg-gray-900 p-3 rounded-lg border border-gray-800">
        <p className="text-xs text-gray-500 mb-1">MACD</p>
        <p className={`text-lg font-semibold ${getMACDColor(macd)}`}>
          {formatNumber(macd)}
        </p>
        <p className="text-xs text-gray-600 mt-1">
          {macd ? (macd > 0 ? 'Bullish' : 'Bearish') : 'N/A'}
        </p>
      </div>

      {/* SMA 10 */}
      <div className="bg-gray-900 p-3 rounded-lg border border-gray-800">
        <p className="text-xs text-gray-500 mb-1">SMA 10</p>
        <p className={`text-sm font-semibold ${getSMAColor(currentPrice, sma10)}`}>
          ${formatNumber(sma10)}
        </p>
        <p className="text-xs text-gray-600 mt-1">
          {currentPrice && sma10 ? (currentPrice > sma10 ? 'Above' : 'Below') : 'N/A'}
        </p>
      </div>

      {/* SMA 50 */}
      <div className="bg-gray-900 p-3 rounded-lg border border-gray-800">
        <p className="text-xs text-gray-500 mb-1">SMA 50</p>
        <p className={`text-sm font-semibold ${getSMAColor(currentPrice, sma50)}`}>
          ${formatNumber(sma50)}
        </p>
        <p className="text-xs text-gray-600 mt-1">
          {currentPrice && sma50 ? (currentPrice > sma50 ? 'Above' : 'Below') : 'N/A'}
        </p>
      </div>

      {/* Current Price */}
      <div className="bg-gray-900 p-3 rounded-lg border border-gray-800">
        <p className="text-xs text-gray-500 mb-1">Price</p>
        <p className="text-lg font-semibold text-blue-400">
          ${formatNumber(currentPrice)}
        </p>
      </div>
    </div>
  );
}
