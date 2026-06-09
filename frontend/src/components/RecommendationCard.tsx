"use client";

import React from 'react';
import RecommendationIndicators from './RecommendationIndicators';

export interface Recommendation {
  id: string;
  symbol: string;
  signal: 'BUY' | 'SELL' | 'HOLD';
  confidence: number;
  rsi_score: number;
  macd_score: number;
  sma_score: number;
  indicators: {
    rsi_14?: number;
    macd?: number;
    macd_signal?: number;
    sma_10?: number;
    sma_50?: number;
    current_price: number;
  };
  updated_at: string;
}

interface RecommendationCardProps {
  recommendation: Recommendation;
  onClick?: () => void;
}

export default function RecommendationCard({
  recommendation,
  onClick,
}: RecommendationCardProps) {
  const getSignalColor = (signal: string) => {
    switch (signal) {
      case 'BUY':
        return 'bg-green-500/20 border-green-500/50 text-green-400';
      case 'SELL':
        return 'bg-red-500/20 border-red-500/50 text-red-400';
      case 'HOLD':
        return 'bg-yellow-500/20 border-yellow-500/50 text-yellow-400';
      default:
        return 'bg-gray-500/20 border-gray-500/50 text-gray-400';
    }
  };

  const getSignalIcon = (signal: string) => {
    switch (signal) {
      case 'BUY':
        return '📈';
      case 'SELL':
        return '📉';
      case 'HOLD':
        return '⏸️';
      default:
        return '❓';
    }
  };

  const getScoreColor = (score: number) => {
    if (score >= 0.7) return 'text-green-400';
    if (score <= 0.3) return 'text-red-400';
    return 'text-yellow-400';
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleTimeString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div
      onClick={onClick}
      className={`bg-gray-900 border rounded-lg p-4 hover:bg-gray-800 transition-all cursor-pointer ${getSignalColor(
        recommendation.signal
      )}`}
    >
      {/* Header */}
      <div className="flex items-start justify-between mb-3">
        <div>
          <div className="flex items-center space-x-2 mb-1">
            <span className="text-2xl">{getSignalIcon(recommendation.signal)}</span>
            <h3 className="text-xl font-bold text-white">{recommendation.symbol}</h3>
            <span className={`px-2 py-1 rounded font-bold text-xs ${getSignalColor(recommendation.signal)}`}>
              {recommendation.signal}
            </span>
          </div>
          <p className="text-xs text-gray-500">
            Updated: {formatDate(recommendation.updated_at)}
          </p>
        </div>
      </div>

      {/* Confidence and Price */}
      <div className="flex items-center justify-between mb-3">
        <div>
          <p className="text-xs text-gray-500 mb-1">Confidence</p>
          <div className="flex items-center space-x-2">
            <div className="w-32 bg-gray-700 rounded-full h-2">
              <div
                className={`h-2 rounded-full transition-all ${
                  recommendation.signal === 'BUY'
                    ? 'bg-green-500'
                    : recommendation.signal === 'SELL'
                    ? 'bg-red-500'
                    : 'bg-yellow-500'
                }`}
                style={{ width: `${recommendation.confidence * 100}%` }}
              ></div>
            </div>
            <span className="text-sm font-semibold text-white">
              {(recommendation.confidence * 100).toFixed(0)}%
            </span>
          </div>
        </div>

        <div className="text-right">
          <p className="text-xs text-gray-500 mb-1">Current Price</p>
          <p className="text-lg font-bold text-blue-400">
            ${recommendation.indicators.current_price.toFixed(2)}
          </p>
        </div>
      </div>

      {/* Score Breakdown */}
      <div className="grid grid-cols-3 gap-2 mb-3">
        <div className="bg-gray-800 p-2 rounded text-center">
          <p className="text-xs text-gray-500">RSI</p>
          <p className={`text-sm font-bold ${getScoreColor(recommendation.rsi_score)}`}>
            {(recommendation.rsi_score * 100).toFixed(0)}
          </p>
        </div>
        <div className="bg-gray-800 p-2 rounded text-center">
          <p className="text-xs text-gray-500">MACD</p>
          <p className={`text-sm font-bold ${getScoreColor(recommendation.macd_score)}`}>
            {(recommendation.macd_score * 100).toFixed(0)}
          </p>
        </div>
        <div className="bg-gray-800 p-2 rounded text-center">
          <p className="text-xs text-gray-500">SMA</p>
          <p className={`text-sm font-bold ${getScoreColor(recommendation.sma_score)}`}>
            {(recommendation.sma_score * 100).toFixed(0)}
          </p>
        </div>
      </div>

      {/* Technical Indicators */}
      <RecommendationIndicators
        rsi={recommendation.indicators.rsi_14}
        macd={recommendation.indicators.macd}
        sma10={recommendation.indicators.sma_10}
        sma50={recommendation.indicators.sma_50}
        currentPrice={recommendation.indicators.current_price}
      />
    </div>
  );
}
