"""
Technical analysis service for calculating indicators and generating scores.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple


class TechnicalAnalysisService:
    """Service for technical analysis and indicator calculation"""

    @staticmethod
    def fetch_historical_data(symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Fetch historical price data for a symbol.
        
        Args:
            symbol: Stock ticker symbol
            period: Period for historical data (default: 1 year)
            
        Returns:
            DataFrame with OHLCV data or None if fetch fails
        """
        try:
            ticker = yf.Ticker(symbol)
            df = ticker.history(period=period)
            if df.empty:
                return None
            return df
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None

    @staticmethod
    def calculate_rsi(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI).
        
        RSI measures momentum and oscillates between 0-100.
        - RSI > 70: Overbought (sell signal)
        - RSI < 30: Oversold (buy signal)
        - RSI 40-60: Neutral
        """
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calculate_macd(
        df: pd.DataFrame,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Returns:
            Tuple of (MACD, Signal line, Histogram)
        """
        ema_fast = df['Close'].ewm(span=fast).mean()
        ema_slow = df['Close'].ewm(span=slow).mean()
        macd = ema_fast - ema_slow
        signal_line = macd.ewm(span=signal).mean()
        histogram = macd - signal_line
        return macd, signal_line, histogram

    @staticmethod
    def calculate_sma(df: pd.DataFrame, period: int) -> pd.Series:
        """
        Calculate Simple Moving Average (SMA).
        
        SMA helps identify trend direction:
        - Price above SMA: Uptrend
        - Price below SMA: Downtrend
        """
        return df['Close'].rolling(window=period).mean()

    @staticmethod
    def calculate_indicators(symbol: str) -> Optional[Dict]:
        """
        Calculate all technical indicators for a symbol.
        
        Returns:
            Dictionary with latest indicator values or None if fails
        """
        try:
            df = TechnicalAnalysisService.fetch_historical_data(symbol, period="6mo")
            if df is None or len(df) < 50:  # Need at least 50 days for SMA_50
                return None

            # Calculate indicators
            rsi = TechnicalAnalysisService.calculate_rsi(df, period=14)
            macd, macd_signal, macd_hist = TechnicalAnalysisService.calculate_macd(df)
            sma_10 = TechnicalAnalysisService.calculate_sma(df, period=10)
            sma_50 = TechnicalAnalysisService.calculate_sma(df, period=50)

            # Get latest values
            latest_idx = -1
            indicators = {
                'symbol': symbol,
                'current_price': float(df['Close'].iloc[latest_idx]),
                'rsi_14': float(rsi.iloc[latest_idx]) if pd.notna(rsi.iloc[latest_idx]) else None,
                'macd': float(macd.iloc[latest_idx]) if pd.notna(macd.iloc[latest_idx]) else None,
                'macd_signal': float(macd_signal.iloc[latest_idx]) if pd.notna(macd_signal.iloc[latest_idx]) else None,
                'macd_histogram': float(macd_hist.iloc[latest_idx]) if pd.notna(macd_hist.iloc[latest_idx]) else None,
                'sma_10': float(sma_10.iloc[latest_idx]) if pd.notna(sma_10.iloc[latest_idx]) else None,
                'sma_50': float(sma_50.iloc[latest_idx]) if pd.notna(sma_50.iloc[latest_idx]) else None,
                'price_above_sma_10': float(df['Close'].iloc[latest_idx]) > float(sma_10.iloc[latest_idx]),
                'price_above_sma_50': float(df['Close'].iloc[latest_idx]) > float(sma_50.iloc[latest_idx]),
                'sma_10_above_sma_50': float(sma_10.iloc[latest_idx]) > float(sma_50.iloc[latest_idx]),
            }
            
            return indicators
            
        except Exception as e:
            print(f"Error calculating indicators for {symbol}: {e}")
            return None

    @staticmethod
    def calculate_rsi_score(rsi: Optional[float]) -> float:
        """
        Convert RSI to a score (0.0 to 1.0).
        - RSI < 30: Strong buy signal (0.9)
        - RSI 30-40: Buy signal (0.7)
        - RSI 40-60: Neutral (0.5)
        - RSI 60-70: Sell signal (0.3)
        - RSI > 70: Strong sell signal (0.1)
        """
        if rsi is None:
            return 0.5

        if rsi < 30:
            return 0.9
        elif rsi < 40:
            return 0.7
        elif rsi < 60:
            return 0.5
        elif rsi < 70:
            return 0.3
        else:
            return 0.1

    @staticmethod
    def calculate_macd_score(macd: Optional[float], macd_signal: Optional[float], histogram: Optional[float]) -> float:
        """
        Convert MACD to a score (0.0 to 1.0).
        - MACD above signal line & positive: Strong buy (0.8)
        - MACD above signal line: Buy (0.6)
        - MACD below signal line & negative: Strong sell (0.2)
        - MACD below signal line: Sell (0.4)
        - Otherwise: Neutral (0.5)
        """
        if macd is None or macd_signal is None:
            return 0.5

        if macd > macd_signal:
            if histogram is not None and histogram > 0:
                return 0.8  # Strong buy
            return 0.6  # Buy
        else:
            if histogram is not None and histogram < 0:
                return 0.2  # Strong sell
            return 0.4  # Sell

    @staticmethod
    def calculate_sma_score(
        current_price: float,
        sma_10: Optional[float],
        sma_50: Optional[float],
        sma_10_above_sma_50: bool
    ) -> float:
        """
        Convert SMA positions to a score (0.0 to 1.0).
        - Price > SMA_10 > SMA_50: Strong uptrend (0.8)
        - Price > SMA_10 or Price > SMA_50: Uptrend (0.6)
        - Price < SMA_10 < SMA_50: Strong downtrend (0.2)
        - Price < SMA_10 or Price < SMA_50: Downtrend (0.4)
        - Otherwise: Neutral (0.5)
        """
        if sma_10 is None or sma_50 is None:
            return 0.5

        price_above_10 = current_price > sma_10
        price_above_50 = current_price > sma_50

        if price_above_10 and sma_10_above_sma_50:
            return 0.8  # Strong uptrend
        elif price_above_10 or price_above_50:
            return 0.6  # Uptrend
        elif not price_above_10 and not sma_10_above_sma_50:
            return 0.2  # Strong downtrend
        elif not price_above_10 or not price_above_50:
            return 0.4  # Downtrend
        else:
            return 0.5  # Neutral

    @staticmethod
    def score_to_signal(score: float) -> Tuple[str, float]:
        """
        Convert composite score to trading signal.
        
        Returns:
            Tuple of (signal, confidence)
        """
        if score >= 0.65:
            return "BUY", min(score, 1.0)
        elif score <= 0.35:
            return "SELL", 1.0 - min(score, 1.0)
        else:
            return "HOLD", 0.5
