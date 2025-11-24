import pandas as pd
import talib
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
        df['SMA_50'] = talib.SMA(df['close'].values, timeperiod=50)
        df['SMA_200'] = talib.SMA(df['close'].values, timeperiod=200)
        
        # Exponential Moving Averages
        df['EMA_20'] = talib.EMA(df['close'].values, timeperiod=20)
        
        # MACD (12, 26, 9)
        macd, macdsignal, macdhist = talib.MACD(df['close'].values, fastperiod=12, slowperiod=26, signalperiod=9)
        df['MACD_12_26_9'] = macd
        df['MACDS_12_26_9'] = macdsignal
        df['MACDH_12_26_9'] = macdhist

        # --- Momentum Indicators ---
        # RSI (14)
        df['RSI_14'] = talib.RSI(df['close'].values, timeperiod=14)
        
        # Stochastic Oscillator
        slowk, slowd = talib.STOCH(df['high'].values, df['low'].values, df['close'].values, fastk_period=14, slowk_period=3, slowd_period=3)
        df['STOCHk_14_3_3'] = slowk
        df['STOCHd_14_3_3'] = slowd

        # --- Volatility Indicators ---
        # Bollinger Bands (20, 2)
        upper, middle, lower = talib.BBANDS(df['close'].values, timeperiod=20, nbdevup=2, nbdevdn=2)
        df['BBL_20_2.0'] = lower
        df['BBM_20_2.0'] = middle
        df['BBU_20_2.0'] = upper
            
        # ATR (14)
        df['ATR_14'] = talib.ATR(df['high'].values, df['low'].values, df['close'].values, timeperiod=14)

        # --- Volume Indicators ---
        # VWAP - Note: VWAP requires a datetime index to reset correctly, 
        # but talib does not have a direct VWAP implementation.
        # For simplicity in standard OHLCV without intraday resets, we might skip or use a rolling VWAP approximation
        # df['VWAP'] = ta.vwap(df['high'], df['low'], df['close'], df['volume'])

        return df
        return df

    def get_required_lookback(self) -> int:
        """
        Returns the minimum number of rows required to calculate all indicators.
        Useful for live trading to fetch just enough data.
        """
        return 200  # Based on SMA_200
