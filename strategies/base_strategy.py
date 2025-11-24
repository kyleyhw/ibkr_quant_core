from backtesting import Strategy
from backtesting.lib import TrailingStrategy

class BaseStrategy(TrailingStrategy):
    """
    A base class for trading strategies that provides a framework for consistent
    risk management, including dynamic position sizing and trailing stop-loss.

    Why this exists:
    - To enforce a consistent risk management approach across all strategies.
    - To abstract away the boilerplate logic of position sizing and stop-loss calculation.
    - To allow child strategies to focus purely on entry and exit signals.

    This class inherits from TrailingStrategy to utilize a percentage-based
    trailing stop-loss, a more dynamic approach than a fixed stop.
    """
    
    # --- Risk Management Parameters ---
    # These can be overridden by child strategies or during backtest optimization.
    
    # The percentage of total equity to risk on a single trade.
    risk_percent: float = 0.01  # e.g., 1% of equity

    # The percentage below the entry price to set the initial stop-loss.
    # This also serves as the trailing stop percentage.
    stop_loss_pct: float = 0.02  # e.g., 2% trailing stop

    # The percentage above the entry price to set the take-profit level.
    # If set to 0, no take-profit limit is used.
    take_profit_pct: float = 0.05  # e.g., 5% take-profit
    
    def init(self):
        """
        Initializes the strategy.
        """
        super().init()
        self.set_trailing_sl(self.stop_loss_pct)
        self.entry_price = None
        self.size_factor = 1.0 # Default sizing factor

    def next(self):
        """
        Main strategy logic loop.
        """
        if self.take_profit_pct > 0 and self.position and self.entry_price is not None:
            if self.position.is_long:
                take_profit_price = self.entry_price * (1 + self.take_profit_pct)
                if self.data.Close[-1] >= take_profit_price:
                    self.position.close()
                    self.entry_price = None
            elif self.position.is_short:
                take_profit_price = self.entry_price * (1 - self.take_profit_pct)
                if self.data.Close[-1] <= take_profit_price:
                    self.position.close()
                    self.entry_price = None
        
        super().next()

    def calculate_position_size(self) -> float:
        """
        Calculates the base position size.
        """
        return 0.1

    def get_params(self) -> dict:
        """
        Returns a dictionary of the base strategy's parameters.
        """
        return {
            "risk_percent": self.risk_percent,
            "stop_loss_pct": self.stop_loss_pct,
            "take_profit_pct": self.take_profit_pct,
        }

    def buy_instrument(self):
        """
        Executes a long entry with the calculated and adjusted position size.
        """
        size = self.calculate_position_size() * self.size_factor
        self.buy(size=size)
        self.entry_price = self.data.Close[-1]

    def sell_instrument(self):
        """
        Executes a short entry with the calculated and adjusted position size.
        """
        size = self.calculate_position_size() * self.size_factor
        self.sell(size=size)
        self.entry_price = self.data.Close[-1]
