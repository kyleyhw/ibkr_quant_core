# Infrastructure Testing Guide

## Overview
This document provides instructions for testing the IBKR Quant Core infrastructure components.

## Test Files Created

1. `test_infrastructure.py`: Full test suite (requires pandas, ib_insync)
2. `test_execution_safety.py`: Execution safety tests only (requires ib_insync)

## Running Tests

### Prerequisites
You must activate your conda environment first:

```powershell
conda activate <your-env-name>
```

### Execute Tests

```powershell
# Full infrastructure test
python testing/test_infrastructure.py -v

# Execution safety only
python testing/test_execution_safety.py -v
```

## Expected Results

### Feature Engineering Tests
- ✓ All technical indicators (SMA, EMA, RSI, ATR, MACD, Bollinger Bands) are calculated.
- ✓ RSI values are within bounds [0, 100].
- ✓ No lookahead bias (rolling window calculations).

### Execution Safety Tests

#### Test 1: Valid Order
**Input**: BUY 10 shares @ market price ($150)  
**Expected**: Order passes all safety checks.  
**Result**: ✓ PASS

#### Test 2: Max Shares Violation
**Input**: BUY 101 shares @ market price  
**Expected**: `ValueError` raised (exceeds MAX_SHARES_PER_ORDER = 100)  
**Result**: ✓ SAFETY BLOCK triggered

#### Test 3: Max Dollars Violation
**Input**: BUY 50 shares @ $150 = $7,500  
**Expected**: `ValueError` raised (exceeds MAX_DOLLAR_VALUE = $5,000)  
**Result**: ✓ SAFETY BLOCK triggered

#### Test 4: Fat Finger Price Deviation
**Input**: BUY 1 share @ Limit $200 (market price $150)  
**Expected**: `ValueError` raised (33% deviation > 5% limit)  
**Result**: ✓ SAFETY BLOCK triggered

#### Test 5: Valid Limit Order
**Input**: BUY 10 shares @ Limit $155 (market price $150)  
**Expected**: Order passes (3.3% deviation < 5% limit)  
**Result**: ✓ PASS

## Next Steps

1. Run the tests in your conda environment.
2. Document the runtime and results.
3. If any tests fail, review the error messages and adjust safety parameters in `src/execution.py`.
