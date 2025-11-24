import pandas as pd
import pandas_ta as ta
from typing import List, Optional

class FeatureEngineer:
    """
    Centralized logic for calculating technical indicators.
    Ensures consistency between Backtesting (Training) and Live Trading (Inference).
    """

    def __init__(self):
        pass

    def calculate_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Applies all defined technical indicators to the dataframe.
        
        Args:
            df: OHLCV DataFrame.
            
        Returns:
            DataFrame with added feature columns.
        """
        # Ensure we have a copy to avoid SettingWithCopy warnings on the original df
        df = df.copy()
        
        # --- Trend Indicators ---
        # Simple Moving Averages
        df['SMA_50'] = ta.sma(df['close'], length=50)
        df['SMA_200'] = ta.sma(df['close'], length=200)
        
        # Exponential Moving Averages
        df['EMA_20'] = ta.ema(df['close'], length=20)
        
        # MACD (12, 26, 9)
        macd = ta.macd(df['close'], fast=12, slow=26, signal=9)
        # pandas_ta returns columns like MACD_12_26_9, MACDh_12_26_9, MACDs_12_26_9
        # We rename them for consistency
        if macd is not None:
            df = pd.concat([df, macd], axis=1)
            # Standardize names if needed, but default pandas_ta names are usually fine:
            # MACD_12_26_9 (Line), MACDh_12_26_9 (Histogram), MACDs_12_26_9 (Signal)

        # --- Momentum Indicators ---
        # RSI (14)
        df['RSI_14'] = ta.rsi(df['close'], length=14)
        
        # Stochastic Oscillator
        stoch = ta.stoch(df['high'], df['low'], df['close'])
        if stoch is not None:
            df = pd.concat([df, stoch], axis=1)
            # STOCHk_14_3_3, STOCHd_14_3_3

        # --- Volatility Indicators ---
        # Bollinger Bands (20, 2)
        bbands = ta.bbands(df['close'], length=20, std=2)
        if bbands is not None:
            df = pd.concat([df, bbands], axis=1)
            # BBL_20_2.0, BBM_20_2.0, BBU_20_2.0
            
        # ATR (14)
        df['ATR_14'] = ta.atr(df['high'], df['low'], df['close'], length=14)

        # --- Volume Indicators ---
        # VWAP - Note: VWAP requires a datetime index to reset correctly, 
        # but pandas_ta handles it if the index is datetime.
        # For simplicity in standard OHLCV without intraday resets, we might skip or use a rolling VWAP approximation
        # df['VWAP'] = ta.vwap(df['high'], df['low'], df['close'], df['volume'])

        return df

    def get_required_lookback(self) -> int:
        """
        Returns the minimum number of rows required to calculate all indicators.
        Useful for live trading to fetch just enough data.
        """
        return 200  # Based on SMA_200
