"use client";

import React, { useEffect, useState } from 'react';
import { API_BASE_URL } from '@/utils/api';
import RecommendationCard, { Recommendation } from './RecommendationCard';

interface RecommendationSummary {
  total: number;
  buy_count: number;
  sell_count: number;
  hold_count: number;
  top_buy: Recommendation[];
  top_sell: Recommendation[];
}

interface RecommendationPanelProps {
  autoRefresh?: boolean;
  refreshInterval?: number; // in seconds
}

export default function RecommendationPanel({
  autoRefresh = true,
  refreshInterval = 60,
}: RecommendationPanelProps) {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([]);
  const [summary, setSummary] = useState<RecommendationSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);
  const [selectedFilter, setSelectedFilter] = useState<'all' | 'buy' | 'sell' | 'hold'>('all');

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');

      const response = await fetch(`${API_BASE_URL}/api/v1/recommendations/summary`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch recommendations');

      const data = await response.json();
      setSummary(data);
      
      // Get all recommendations
      const allRecsResponse = await fetch(`${API_BASE_URL}/api/v1/recommendations/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });
      
      if (!allRecsResponse.ok) throw new Error('Failed to fetch all recommendations');
      const allRecs = await allRecsResponse.json();
      setRecommendations(allRecs);
      setLastUpdated(new Date());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const refreshRecommendations = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${API_BASE_URL}/api/v1/recommendations/refresh`, {
        method: 'POST',
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        fetchRecommendations();
      }
    } catch (err) {
      console.error('Error refreshing recommendations:', err);
    }
  };

  useEffect(() => {
    fetchRecommendations();

    if (autoRefresh) {
      const interval = setInterval(fetchRecommendations, refreshInterval * 1000);
      return () => clearInterval(interval);
    }
  }, [autoRefresh, refreshInterval]);

  const getFilteredRecommendations = () => {
    if (selectedFilter === 'all') return recommendations;
    return recommendations.filter((r) => r.signal.toLowerCase() === selectedFilter);
  };

  const filteredRecommendations = getFilteredRecommendations();

  if (loading && !recommendations.length) {
    return (
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-8 bg-gray-800 rounded w-1/4"></div>
          <div className="h-24 bg-gray-800 rounded"></div>
          <div className="h-24 bg-gray-800 rounded"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header and Stats */}
      <div className="bg-gray-900 border border-gray-800 rounded-lg p-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-white mb-1">
              Stock Recommendations
            </h2>
            <p className="text-xs text-gray-500">
              Based on technical analysis (RSI, MACD, SMA)
              {lastUpdated && ` • Updated ${lastUpdated.toLocaleTimeString()}`}
            </p>
          </div>
          <button
            onClick={refreshRecommendations}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium text-sm transition-colors"
          >
            🔄 Refresh
          </button>
        </div>

        {/* Summary Stats */}
        {summary && (
          <div className="grid grid-cols-4 gap-3">
            <div className="bg-gray-800 p-3 rounded-lg border border-gray-700">
              <p className="text-xs text-gray-500 mb-1">Total Holdings</p>
              <p className="text-2xl font-bold text-white">{summary.total}</p>
            </div>
            <div className="bg-green-500/10 p-3 rounded-lg border border-green-500/30">
              <p className="text-xs text-green-400 mb-1">Buy Signals</p>
              <p className="text-2xl font-bold text-green-400">{summary.buy_count}</p>
            </div>
            <div className="bg-red-500/10 p-3 rounded-lg border border-red-500/30">
              <p className="text-xs text-red-400 mb-1">Sell Signals</p>
              <p className="text-2xl font-bold text-red-400">{summary.sell_count}</p>
            </div>
            <div className="bg-yellow-500/10 p-3 rounded-lg border border-yellow-500/30">
              <p className="text-xs text-yellow-400 mb-1">Hold Signals</p>
              <p className="text-2xl font-bold text-yellow-400">{summary.hold_count}</p>
            </div>
          </div>
        )}
      </div>

      {/* Filter Buttons */}
      <div className="flex gap-2">
        {(['all', 'buy', 'sell', 'hold'] as const).map((filter) => (
          <button
            key={filter}
            onClick={() => setSelectedFilter(filter)}
            className={`px-4 py-2 rounded-lg font-medium text-sm transition-all ${
              selectedFilter === filter
                ? filter === 'all'
                  ? 'bg-blue-600 text-white'
                  : filter === 'buy'
                  ? 'bg-green-600 text-white'
                  : filter === 'sell'
                  ? 'bg-red-600 text-white'
                  : 'bg-yellow-600 text-white'
                : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
            }`}
          >
            {filter.charAt(0).toUpperCase() + filter.slice(1)}
          </button>
        ))}
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3 text-red-400 text-sm">
          {error}
        </div>
      )}

      {/* Recommendations Grid */}
      {filteredRecommendations.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {filteredRecommendations.map((recommendation) => (
            <RecommendationCard
              key={recommendation.id}
              recommendation={recommendation}
              onClick={() => {
                // Could navigate to detailed view or open modal
                console.log('Clicked recommendation:', recommendation.symbol);
              }}
            />
          ))}
        </div>
      ) : (
        <div className="bg-gray-900 border border-gray-800 rounded-lg p-8 text-center">
          <p className="text-gray-400">
            {selectedFilter === 'all'
              ? 'No recommendations available yet. Hold some stocks first.'
              : `No ${selectedFilter.toUpperCase()} signals at the moment.`}
          </p>
        </div>
      )}
    </div>
  );
}
