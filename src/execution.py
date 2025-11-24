import logging
from ib_insync import Order, Contract

# Configure logging
logger = logging.getLogger(__name__)

class ExecutionManager:
    """
    Handles order validation and safety checks before submission to IBKR.
    Acts as the 'Fat Finger' defense layer.
    """

    # Hard limits - strictly enforced
    MAX_SHARES_PER_ORDER = 100
    MAX_DOLLAR_VALUE_PER_ORDER = 5000.0
    MAX_PRICE_DEVIATION_PERCENT = 0.05  # 5% deviation from current price

    def __init__(self):
        pass

    def check_order_limits(self, order: Order, contract: Contract, current_price: float) -> bool:
        """
        Validates an order against hard-coded safety limits.
        
        Args:
            order: The IBKR Order object.
            contract: The IBKR Contract object.
            current_price: The current market price of the asset.
            
        Returns:
            True if the order is safe to execute.
            
        Raises:
            ValueError: If any safety limit is violated.
        """
        
        # 1. Check Max Shares
        if order.totalQuantity > self.MAX_SHARES_PER_ORDER:
            msg = (f"SAFETY BLOCK: Order quantity {order.totalQuantity} exceeds "
                   f"limit of {self.MAX_SHARES_PER_ORDER} for {contract.symbol}.")
            logger.critical(msg)
            raise ValueError(msg)

        # 2. Check Max Dollar Value
        # If it's a Market order, use current_price. If Limit, use lmtPrice.
        # Note: For Stop orders, we might use auxPrice, but for simplicity let's assume MKT/LMT.
        exec_price = order.lmtPrice if order.orderType in ['LMT', 'STOP_LIMIT'] else current_price
        
        # If lmtPrice is 0 (e.g. Market order), ensure we have a valid current_price
        if exec_price == 0 or exec_price is None:
            exec_price = current_price
            
        estimated_value = exec_price * order.totalQuantity
        
        if estimated_value > self.MAX_DOLLAR_VALUE_PER_ORDER:
            msg = (f"SAFETY BLOCK: Order value ${estimated_value:.2f} exceeds "
                   f"limit of ${self.MAX_DOLLAR_VALUE_PER_ORDER} for {contract.symbol}.")
            logger.critical(msg)
            raise ValueError(msg)

        # 3. Fat Finger Price Check (only for Limit orders)
        if order.orderType in ['LMT', 'STOP_LIMIT'] and order.lmtPrice > 0:
            deviation = abs(order.lmtPrice - current_price) / current_price
            if deviation > self.MAX_PRICE_DEVIATION_PERCENT:
                msg = (f"SAFETY BLOCK: Limit price {order.lmtPrice} deviates "
                       f"{deviation*100:.2f}% from market price {current_price} for {contract.symbol}. "
                       f"Max allowed is {self.MAX_PRICE_DEVIATION_PERCENT*100}%.")
                logger.critical(msg)
                raise ValueError(msg)

        logger.info(f"Order validated: {order.action} {order.totalQuantity} {contract.symbol} @ {exec_price}")
        return True
