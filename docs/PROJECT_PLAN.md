# Project Development Plan

This document outlines the planned phases and tasks for developing the IBKR Open-Core Algorithmic Trading Bot.

## Phase 1: Core Infrastructure Setup
1.  [pending] Verify and finalize the project directory structure.
2.  [pending] Populate `requirements.txt` with all necessary libraries.
3.  [pending] Implement the IBKR connection logic in `src/connection.py`.
4.  [pending] Implement standardized data fetching in `src/data_loader.py`.
5.  [pending] Create the base `Notifier` class in `src/notifications.py`.
6.  [pending] Set up initial documentation, including `README.md` and the `/docs` folder structure.

## Phase 2: Base Strategy & Backtesting Framework
7.  [pending] Develop the parent `base_strategy.py` to handle position sizing and stop-loss logic.
8.  [pending] Create a public `simple_demo.py` strategy (e.g., a moving average crossover) inheriting from the base strategy.
9.  [pending] Implement the backtesting script `backtesting/run_backtest.py` to test a single strategy.
10. [pending] Generate the first backtest report and save it to the `reports/` directory.

## Phase 3: Feature Engineering & ML Model Training
11. [pending] Develop the shared `src/feature_engineering.py` module with common technical indicators.
12. [pending] Create a Jupyter notebook in `research/` for model training.
13. [pending] Save the trained model artifact to the `models/` directory.

## Phase 4: Machine Learning Strategy Implementation
14. [pending] Create a private strategy in `strategies/private/` that uses a trained model.
15. [pending] Backtest the ML-based strategy.

## Phase 5: Live Execution & Safety
16. [pending] Implement the `execution.py` module with safety checks.
17. [pending] Integrate the execution module with the base strategy.

## Phase 6: System Finalization
18. [pending] Implement the strategy benchmarking script `backtesting/benchmark.py`.
19. [pending] Integrate the `Notifier` class for alerts.
20. [pending] Complete all documentation.
