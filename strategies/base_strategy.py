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
        Initializes the strategy. This method is called by the backtesting
        framework once before the strategy begins.

        We use this to set up the trailing stop-loss mechanism.
        """
        # Call the parent class's init method
        super().init()
        # Set the trailing stop-loss percentage from our parameters
        self.set_trailing_sl(self.stop_loss_pct)
        # Initialize entry price storage
        self.entry_price = None

    def next(self):
        """
        The main strategy logic loop, called for each data point (bar).

        This base implementation contains the logic to manage an open trade's
        exit conditions (take-profit). Entry logic should be implemented
        in the child strategy's `next()` method, which should also call
        `super().next()` to retain this exit logic.
        """
        # --- Take-Profit Logic ---
        # If a take-profit is defined and we have an open position AND we have recorded an entry price
        if self.take_profit_pct > 0 and self.position and self.entry_price is not None:
            # For long positions
            if self.position.is_long:
                take_profit_price = self.entry_price * (1 + self.take_profit_pct)
                # If the current price crosses the take-profit level, close the position
                if self.data.Close[-1] >= take_profit_price:
                    self.position.close()
                    self.entry_price = None # Clear entry price after closing
            # For short positions
            elif self.position.is_short:
                take_profit_price = self.entry_price * (1 - self.take_profit_pct)
                # If the current price crosses the take-profit level, close the position
                if self.data.Close[-1] <= take_profit_price:
                    self.position.close()
                    self.entry_price = None # Clear entry price after closing
        
        # The parent class (TrailingStrategy) handles the trailing stop-loss automatically.
        super().next()

    def calculate_position_size(self) -> float:
        """
        Calculates the position size as a fraction of total equity, based on the
        defined `risk_percent`.

        This standardizes position sizing across all strategies that inherit
        from this base class.

        Returns:
            float: The fraction of equity to allocate to the trade (e.g., 0.9 for 90%).
                   The backtesting library uses this to determine share count.
        """
    # This will be refined later if needed.
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

    # --- Wrapper methods for buying and selling to include our position size ---

    
    def buy_instrument(self):
        """
        Executes a long entry with the calculated position size.
        """
        size = self.calculate_position_size()
        self.buy(size=size)
        self.entry_price = self.data.Close[-1] # Store entry price upon buying

    def sell_instrument(self):
        """
        Executes a short entry with the calculated position size.
        """
        size = self.calculate_position_size()
        self.sell(size=size)
        self.entry_price = self.data.Close[-1] # Store entry price upon selling (for short entry)
