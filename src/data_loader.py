import asyncio
import logging
from datetime import datetime
from typing import Optional, List

import pandas as pd
from ib_insync import Contract, BarData

from .connection import IBConnection

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class DataLoader:
    """
    Handles standardized data fetching from Interactive Brokers TWS/Gateway
    using an established IBConnection.

    This class provides methods to retrieve historical market data and
    standardize it into a pandas DataFrame format.
    """

    def __init__(self, ib_connection: IBConnection):
        """
        Initializes the DataLoader with an IBConnection instance.

        Args:
            ib_connection (IBConnection): An active or connectable IBConnection instance.
        """
        if not isinstance(ib_connection, IBConnection):
            raise TypeError("ib_connection must be an instance of IBConnection")
        self.ib_connection = ib_connection
        self.ib = ib_connection.ib
        logging.info("DataLoader initialized.")

    async def create_contract(self,
                              symbol: str,
                              sec_type: str,
                              exchange: str,
                              currency: str,
                              last_trade_date_or_contract_month: Optional[str] = None,
                              strike: Optional[float] = None,
                              right: Optional[str] = None,
                              multiplier: Optional[str] = None
                              ) -> Optional[Contract]:
        """
        Creates and qualifies an IB Contract object asynchronously.
        This method dynamically builds the contract to avoid passing irrelevant 'None' parameters.
        """
        contract_args = {
            'symbol': symbol,
            'secType': sec_type,
            'exchange': exchange,
            'currency': currency
        }
        if last_trade_date_or_contract_month:
            contract_args['lastTradeDateOrContractMonth'] = last_trade_date_or_contract_month
        if strike:
            contract_args['strike'] = strike
        if right:
            contract_args['right'] = right
        if multiplier:
            contract_args['multiplier'] = multiplier
        
        contract = Contract(**contract_args)
        logging.info(f"Attempting to qualify contract: {contract}")

        try:
            # Use the asynchronous method to qualify contracts
            qualified_contracts = await self.ib.qualifyContractsAsync(contract)
            if not qualified_contracts:
                logging.warning(f"No contract details found for {symbol} {sec_type} on {exchange}")
                return None
            
            # Log the qualified contract details for clarity
            qualified_contract = qualified_contracts[0]
            logging.info(f"Qualified contract: {qualified_contract.localSymbol}, conId {qualified_contract.conId}")
            return qualified_contract
            
        except Exception as e:
            logging.error(f"Error qualifying contract for {symbol}: {e}", exc_info=True)
            return None

    async def get_historical_data(self,
                                  contract: Contract,
                                  duration_str: str,
                                  bar_size_setting: str,
                                  what_to_show: str,
                                  use_rth: bool = True,
                                  end_date_time: str = '',
                                  timeout: int = 60) -> pd.DataFrame:
        """
        Fetches historical market data for a given contract asynchronously.
        """
        if not self.ib_connection.is_connected:
            logging.error("IB not connected. Cannot fetch historical data.")
            return pd.DataFrame()

        try:
            # Use the asynchronous method for historical data
            bars: List[BarData] = await self.ib.reqHistoricalDataAsync(
                contract,
                endDateTime=end_date_time,
                durationStr=duration_str,
                barSizeSetting=bar_size_setting,
                whatToShow=what_to_show,
                useRTH=use_rth,
                formatDate=1,
                timeout=timeout
            )

            if not bars:
                logging.warning(f"No historical data returned for {contract.symbol}, {bar_size_setting}, {what_to_show}")
                return pd.DataFrame()

            # Convert to DataFrame
            df = pd.DataFrame([b.__dict__ for b in bars])
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')

            # Standardize column names
            df = df[['open', 'high', 'low', 'close', 'volume', 'average', 'barCount']]
            df.columns = ['Open', 'High', 'Low', 'Close', 'Volume', 'Average', 'BarCount']

            logging.info(f"Successfully fetched {len(df)} bars for {contract.symbol}.")
            return df

        except Exception as e:
            logging.error(f"Error fetching historical data for {contract.symbol}: {e}")
            return pd.DataFrame()


async def main():
    """
    Main async function to demonstrate DataLoader usage.
    """
    conn = IBConnection()
    try:
        # Asynchronous connection
        if await conn.connect():
            data_loader = DataLoader(conn)

            # Example 1: Fetch SPY stock data
            logging.info("Attempting to fetch data for SPY...")
            spy_contract = await data_loader.create_contract(
                symbol='SPY',
                sec_type='STK',
                exchange='ARCA',
                currency='USD'
            )

            if spy_contract:
                df_spy = await data_loader.get_historical_data(
                    spy_contract,
                    duration_str='1 D',
                    bar_size_setting='1 min',
                    what_to_show='TRADES',
                    use_rth=True
                )
                if not df_spy.empty:
                    print("\nFetched SPY 1-min data:")
                    print(df_spy.head())
                else:
                    print("\nFailed to fetch SPY data or no data returned.")
            else:
                print("\nFailed to create/qualify SPY contract.")

            # Example 2: Fetch EUR.USD forex data
            logging.info("\nAttempting to fetch data for EUR.USD...")
            eurusd_contract = await data_loader.create_contract(
                symbol='EUR',
                sec_type='CASH',
                exchange='IDEALPRO',
                currency='USD'
            )

            if eurusd_contract:
                df_forex = await data_loader.get_historical_data(
                    eurusd_contract,
                    duration_str='1 M',
                    bar_size_setting='1 day',
                    what_to_show='MIDPOINT',
                    use_rth=False # Forex trades 24/5, so useRTH is typically False
                )
                if not df_forex.empty:
                    print("\nFetched EUR.USD 1-day data:")
                    print(df_forex.head())
                else:
                    print("\nFailed to fetch EUR.USD data or no data returned.")
            else:
                print("\nFailed to create/qualify EUR.USD contract.")

    except Exception as e:
        logging.error(f"An error occurred in the main execution block: {e}")
    finally:
        # Asynchronous disconnection
        if conn.is_connected:
            await conn.disconnect()
            logging.info("IB connection closed.")


if __name__ == "__main__":
    # Ensure TWS/Gateway is running and API connection is enabled
    # Run the main asynchronous function
    # Note: ib_insync's util.patch_asyncio() might be needed in some environments
    # but let's try without it first.
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Program terminated by user.")
    except Exception as e:
        logging.critical(f"A critical error occurred: {e}")