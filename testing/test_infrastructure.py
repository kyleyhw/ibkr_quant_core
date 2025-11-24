import unittest
import pandas as pd
import numpy as np
import sys
import os
from ib_insync import Order, Contract

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.feature_engineering import FeatureEngineer
from src.execution import ExecutionManager

class TestInfrastructure(unittest.TestCase):
    
    def setUp(self):
        self.fe = FeatureEngineer()
        self.em = ExecutionManager()

    def test_feature_engineering(self):
        print("\n--- Testing Feature Engineering ---")
        # Create dummy OHLCV data
        dates = pd.date_range(start='2023-01-01', periods=300)
        df = pd.DataFrame({
            'open': np.random.rand(300) * 100,
            'high': np.random.rand(300) * 100,
            'low': np.random.rand(300) * 100,
            'close': np.random.rand(300) * 100,
            'volume': np.random.randint(100, 1000, 300)
        }, index=dates)
        
        # Ensure high is highest and low is lowest
        df['high'] = df[['open', 'close']].max(axis=1) + 1
        df['low'] = df[['open', 'close']].min(axis=1) - 1

        df_features = self.fe.calculate_features(df)
        
        # Check if columns exist
        expected_cols = ['SMA_50', 'SMA_200', 'EMA_20', 'RSI_14', 'ATR_14']
        for col in expected_cols:
            self.assertIn(col, df_features.columns)
            print(f"Column {col} exists.")
            
        # Check RSI bounds
        self.assertTrue(df_features['RSI_14'].between(0, 100).all())
        print("RSI is within bounds [0, 100].")

    def test_execution_safety(self):
        print("\n--- Testing Execution Safety ---")
        contract = Contract(symbol='AAPL', secType='STK', exchange='SMART', currency='USD')
        current_price = 150.0
        
        # 1. Valid Order
        order_valid = Order(action='BUY', totalQuantity=10, orderType='MKT')
        self.assertTrue(self.em.check_order_limits(order_valid, contract, current_price))
        print("Valid order passed.")

        # 2. Max Shares Violation
        order_shares = Order(action='BUY', totalQuantity=101, orderType='MKT')
        with self.assertRaises(ValueError) as cm:
            self.em.check_order_limits(order_shares, contract, current_price)
        print(f"Max Shares caught: {cm.exception}")

        # 3. Max Dollars Violation
        # 50 shares * $150 = $7500 > $5000 limit
        order_dollars = Order(action='BUY', totalQuantity=50, orderType='MKT')
        with self.assertRaises(ValueError) as cm:
            self.em.check_order_limits(order_dollars, contract, current_price)
        print(f"Max Dollars caught: {cm.exception}")

        # 4. Fat Finger Price Violation
        # Limit buy at $200 when price is $150 (33% deviation > 5% limit)
        order_fat_finger = Order(action='BUY', totalQuantity=1, orderType='LMT', lmtPrice=200.0)
        with self.assertRaises(ValueError) as cm:
            self.em.check_order_limits(order_fat_finger, contract, current_price)
        print(f"Fat Finger caught: {cm.exception}")

if __name__ == '__main__':
    unittest.main()
