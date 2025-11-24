import unittest
import sys
import os

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ib_insync import Order, Contract
from src.execution import ExecutionManager

class TestExecutionSafety(unittest.TestCase):
    
    def setUp(self):
        self.em = ExecutionManager()

    def test_execution_safety(self):
        print("\n--- Testing Execution Safety ---")
        contract = Contract(symbol='AAPL', secType='STK', exchange='SMART', currency='USD')
        current_price = 150.0
        
        # 1. Valid Order
        print("\n[TEST 1] Valid order (10 shares @ market)...")
        order_valid = Order(action='BUY', totalQuantity=10, orderType='MKT')
        self.assertTrue(self.em.check_order_limits(order_valid, contract, current_price))
        print("✓ Valid order passed.")

        # 2. Max Shares Violation
        print("\n[TEST 2] Max shares violation (101 shares > 100 limit)...")
        order_shares = Order(action='BUY', totalQuantity=101, orderType='MKT')
        with self.assertRaises(ValueError) as cm:
            self.em.check_order_limits(order_shares, contract, current_price)
        print(f"✓ Max Shares caught: {cm.exception}")

        # 3. Max Dollars Violation
        print("\n[TEST 3] Max dollars violation (50 shares * $150 = $7,500 > $5,000 limit)...")
        order_dollars = Order(action='BUY', totalQuantity=50, orderType='MKT')
        with self.assertRaises(ValueError) as cm:
            self.em.check_order_limits(order_dollars, contract, current_price)
        print(f"✓ Max Dollars caught: {cm.exception}")

        # 4. Fat Finger Price Violation
        print("\n[TEST 4] Fat finger price violation (Limit $200 vs Market $150 = 33% deviation > 5% limit)...")
        order_fat_finger = Order(action='BUY', totalQuantity=1, orderType='LMT', lmtPrice=200.0)
        with self.assertRaises(ValueError) as cm:
            self.em.check_order_limits(order_fat_finger, contract, current_price)
        print(f"✓ Fat Finger caught: {cm.exception}")

        # 5. Valid Limit Order (within 5% deviation)
        print("\n[TEST 5] Valid limit order (within 5% price deviation)...")
        order_valid_limit = Order(action='BUY', totalQuantity=10, orderType='LMT', lmtPrice=155.0)
        self.assertTrue(self.em.check_order_limits(order_valid_limit, contract, current_price))
        print("✓ Valid limit order passed.")

if __name__ == '__main__':
    print("="*60)
    print("IBKR Quant Core - Execution Safety Tests")
    print("="*60)
    unittest.main(verbosity=2)
