import pandas as pd
import numpy as np

def calculate_sma(data: pd.DataFrame, window: int, column: str = 'Close') -> pd.Series:
    return data[column].rolling(window=window).mean()

def calculate_rsi(data: pd.DataFrame, window: int = 14, column: str = 'Close') -> pd.Series:
    delta = data[column].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    return rsi

def calculate_macd(data: pd.DataFrame, short_window: int = 12, long_window: int = 26, signal_window: int = 9, column: str = 'Close'):
    short_ema = data[column].ewm(span=short_window, adjust=False).mean()
    long_ema = data[column].ewm(span=long_window, adjust=False).mean()
    
    macd_line = short_ema - long_ema
    signal_line = macd_line.ewm(span=signal_window, adjust=False).mean()
    
    return macd_line, signal_line

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    
    df['SMA_10'] = calculate_sma(df, 10)
    df['SMA_50'] = calculate_sma(df, 50)
    df['RSI_14'] = calculate_rsi(df, 14)
    
    macd, signal = calculate_macd(df)
    df['MACD'] = macd
    df['MACD_Signal'] = signal
    
    # Target: 1 if close price increases tomorrow, 0 if decreases
    df['Target'] = (df['Close'].shift(-1) > df['Close']).astype(int)
    
    df.dropna(inplace=True)
    return df
