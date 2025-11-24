# Bollinger Bands® Strategy

This document provides the mathematical formulation and trading logic for the Bollinger Bands® mean-reversion strategy.

---

### **1. Mathematical Formulation**

Bollinger Bands® consist of three lines plotted in relation to an asset's price:

1.  **Middle Band:** A Simple Moving Average (SMA) of the asset's closing price over a specified period, $n$.
    $$
    \text{Middle Band} = \text{SMA}_n(t) = \frac{1}{n} \sum_{i=0}^{n-1} p_{t-i}
    $$

2.  **Upper Band:** The Middle Band plus a certain number of standard deviations ($k$) of the price.
    $$
    \text{Upper Band} = \text{SMA}_n(t) + k \cdot \sigma_n(t)
    $$

3.  **Lower Band:** The Middle Band minus the same number of standard deviations ($k$).
    $$
    \text{Lower Band} = \text{SMA}_n(t) - k \cdot \sigma_n(t)
    $$

Where:
-   $p_t$ is the closing price at time $t$.
-   $n$ is the lookback period for the SMA and standard deviation (e.g., 20).
-   $k$ is the number of standard deviations (e.g., 2).
-   $\sigma_n(t)$ is the standard deviation of the closing price over the last $n$ periods.

---

### **2. Trading Logic**

The strategy is based on the principle of mean reversion. It assumes that when the price touches one of the outer bands, it is statistically likely to revert toward the Middle Band (the moving average).

#### **State Variables:**

-   `price`: The current closing price of the asset.
-   `upper_band`: The current value of the upper Bollinger Band.
-   `lower_band`: The current value of the lower Bollinger Band.
-   `middle_band`: The current value of the SMA (Middle Band).
-   `position`: A boolean indicating if a position is currently open.

#### **Entry Conditions:**

1.  **Price touches Lower Band (Buy):** A signal to enter a **long position**.
    -   **Condition:** The price crosses *below* the `lower_band`, indicating an oversold condition relative to its recent volatility.
    -   **Implementation:** `IF price[-2] > lower_band[-2] AND price[-1] < lower_band[-1]`
    -   **Action:** `IF NOT position`, `buy()`

2.  **Price touches Upper Band (Sell):** A signal to enter a **short position**.
    -   **Condition:** The price crosses *above* the `upper_band`, indicating an overbought condition.
    -   **Implementation:** `IF price[-2] < upper_band[-2] AND price[-1] > upper_band[-1]`
    -   **Action:** `IF NOT position`, `sell()`

#### **Exit Conditions:**

The exit signal is triggered when the price reverts back to the Middle Band, capturing the profit from the mean-reversion move.

1.  **Exit Long Position:**
    -   **Condition:** The price crosses back *above* the `middle_band` while in a long position.
    -   **Implementation:** `IF position IS LONG AND price[-1] > middle_band[-1]`
    -   **Action:** `position.close()`

2.  **Exit Short Position:**
    -   **Condition:** The price crosses back *below* the `middle_band` while in a short position.
    -   **Implementation:** `IF position IS SHORT AND price[-1] < middle_band[-1]`
    -   **Action:** `position.close()`

---

### **3. Rationale and Assumptions**

-   **Mean Reversion:** The strategy assumes that asset prices and volatility tend to revert to their mean over time. The bands represent a measure of relative high and low prices, and touches of the bands are considered statistically significant events.
-   **Volatility Adaptation:** Unlike fixed thresholds, Bollinger Bands® dynamically adapt to market volatility. The bands widen when volatility is high and narrow when volatility is low, adjusting the entry thresholds to the current market conditions.
-   **Non-Directional:** This strategy does not attempt to predict the long-term direction of the market but rather to profit from short-term oscillations within a trend or a range.