# strategy development

the strategies for this trading bot are built upon a hierarchical framework designed to separate risk management from signal generation. this is achieved through a parent `basestrategy` class and child classes for specific strategies.

## the base strategy (`strategies/base_strategy.py`)

### purpose
the `basestrategy` class serves as the foundation for all trading strategies within the project. its primary purpose is to enforce a consistent risk management framework and to provide common utilities that can be inherited by all child strategies. this promotes code reuse and ensures that core logic is not duplicated.

### design and logic
-   **inheritance**: `basestrategy` inherits from `backtesting.lib.trailingstrategy`. this choice was made to natively incorporate a percentage-based trailing stop-loss, which is a more dynamic risk management technique than a fixed stop-loss price.
-   **configurable risk parameters**: the class defines several key risk parameters at the class level:
    -   `risk_percent`: the portion of equity to risk on a single trade.
    -   `stop_loss_pct`: the percentage drop from the entry price that triggers the initial stop-loss. this is also used as the trailing stop percentage.
    -   `take_profit_pct`: the percentage gain from the entry price that triggers a take-profit order.
    these parameters can be easily overridden in child strategies or tuned during optimization.
-   **position sizing**: the `calculate_position_size` method is intended to provide a standardized way to determine the size of a trade. in its current implementation for the `backtesting.py` library, it returns a fixed fraction of the portfolio to invest. *note: a more sophisticated implementation would calculate the exact number of shares based on the stop-loss distance and the amount of equity being risked, but this often requires a more complex setup in many backtesting libraries.*
-   **exit logic**: the `next` method in `basestrategy` contains generic logic to close a position if the `take_profit_pct` is reached. the trailing stop-loss is handled automatically by the parent `trailingstrategy`. by calling `super().next()` from a child strategy, this exit logic is preserved.

## example strategy (`strategies/simple_demo.py`)

### purpose
the `simplemacrossover` class is a public, example strategy that demonstrates how to build upon the `basestrategy`. it implements a classic and easily understood trading signal: the moving average crossover.

### design and logic
-   **inheritance**: it inherits directly from `basestrategy`, and therefore gains all of its risk management features.
-   **signal generation**: the core logic is in the `next` method:
    1.  it uses the `crossover()` function from the `backtesting.lib` to detect the exact bar on which the fast moving average crosses above the slow one.
    2.  if this signal occurs and no position is currently open, it calls `self.buy_instrument()`, a method inherited from `basestrategy`.
    3.  a sell signal is generated if the slow ma crosses back over the fast ma, which closes the open position.
-   **indicator handling**: the strategy expects the moving average indicators to be **pre-calculated** on the data `dataframe` before being passed to the `backtest` object. in the `init` method, it accesses these indicator columns (e.g., `self.data.sma_10`) and assigns them to class attributes for use in the `next` method. this design choice is explained further in the backtesting documentation.

-   **[mathematical formulation](./formulations/simple_ma_crossover_formulation.md)**: for a detailed mathematical description of the strategy's signals.


