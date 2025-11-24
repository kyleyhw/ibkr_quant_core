# RSI(2) Period Strategy

This document provides the mathematical formulation and trading logic for the 2-period Relative Strength Index (RSI) strategy, a mean-reversion trading model.

---

### **1. Mathematical Formulation**

The Relative Strength Index (RSI) is a momentum oscillator that measures the speed and change of price movements. The RSI oscillates between zero and 100.

The standard RSI calculation is as follows:

1.  **Calculate Price Changes:**
    -   Upward changes ($U$): $U_t = p_t - p_{t-1}$ if $p_t > p_{t-1}$, else 0.
    -   Downward changes ($D$): $D_t = p_{t-1} - p_t$ if $p_t < p_{t-1}$, else 0.

2.  **Calculate Average Gains and Losses:** The standard RSI uses a smoothed or exponential moving average. For a lookback period $n$:
    -   AvgU(t) = $\frac{1}{n} \sum_{i=0}^{n-1} U_{t-i}$
    -   AvgD(t) = $\frac{1}{n} \sum_{i=0}^{n-1} D_{t-i}$

3.  **Calculate Relative Strength (RS):**
    $$\text{RS} = \frac{\text{AvgU}}{\text{AvgD}}$$

4.  **Calculate RSI:**
    $$\text{RSI} = 100 - \frac{100}{1 + \text{RS}}$$

This strategy uses a very short lookback period of **n=2**. This makes the indicator extremely sensitive to the most recent price action, which is the core of this mean-reversion system.

---

### **2. Trading Logic**

This strategy operates on the principle of mean reversion, identifying extremely overbought or oversold conditions with the intent that the price will revert to its mean.

#### **State Variables:**

-   `rsi`: The current value of the 2-period RSI.
-   `upper_bound`: The threshold for an overbought signal (e.g., 90).
-   `lower_bound`: The threshold for an oversold signal (e.g., 10).
-   `position`: A boolean indicating if a position is currently open.

#### **Entry Conditions:**

1.  **Oversold Signal (Buy):** A signal to enter a **long position**.
    -   **Condition:** The RSI crosses *below* the `lower_bound`, indicating an extreme oversold state.
    -   **Implementation:** `IF rsi[-2] > lower_bound AND rsi[-1] < lower_bound`
    -   **Action:** `IF NOT position`, `buy()`

2.  **Overbought Signal (Sell):** A signal to enter a **short position**.
    -   **Condition:** The RSI crosses *above* the `upper_bound`, indicating an extreme overbought state.
    -   **Implementation:** `IF rsi[-2] < upper_bound AND rsi[-1] > upper_bound`
    -   **Action:** `IF NOT position`, `sell()`

#### **Exit Conditions:**

Positions are closed when the RSI moves back into a neutral zone, suggesting the mean-reversion process has begun.

1.  **Exit Long Position:**
    -   **Condition:** The RSI crosses back *above* a neutral level (e.g., 40) while in a long position.
    -   **Implementation:** `IF position IS LONG AND rsi[-1] > 40`
    -   **Action:** `position.close()`

2.  **Exit Short Position:**
    -   **Condition:** The RSI crosses back *below* a neutral level (e.g., 60) while in a short position.
    -   **Implementation:** `IF position IS SHORT AND rsi[-1] < 60`
    -   **Action:** `position.close()`

---

### **3. Rationale and Assumptions**

-   **Mean Reversion:** The core assumption is that after a sharp, recent price movement (captured by the 2-period RSI), the price is likely to revert back towards its recent average.
-   **Extreme Sensitivity:** Using `n=2` makes the RSI highly sensitive. It is not intended to capture long-term trends but rather to capitalize on very short-term, sentiment-driven price extremes.
-   **Parameter Choice:** The `upper_bound` and `lower_bound` are set to extreme levels (e.g., 90/10) to filter out noise and only act on the most significant price moves. The exit levels are set closer to the mean to capture the reversion promptly.