import asyncio
import os
import logging
from typing import Optional, List

from ib_insync import IB
from ib_insync.objects import AccountValue
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class IBConnection:
    """
    Manages the connection to Interactive Brokers TWS or Gateway asynchronously.
    """

    def __init__(self,
                 host: Optional[str] = None,
                 port: Optional[int] = None,
                 client_id: Optional[int] = None):
        """
        Initializes the IBConnection.
        The event loop is no longer started here; it's managed by the application's entry point.
        """
        self.ib = IB()
        self.host = host or os.getenv('IB_HOST', '127.0.0.1')
        self.port = port or int(os.getenv('IB_PORT', '7497'))
        self.client_id = client_id or int(os.getenv('IB_CLIENT_ID', '1'))
        logging.info(f"Initialized IBConnection with host={self.host}, port={self.port}, client_id={self.client_id}")

    async def connect(self) -> bool:
        """
        Establishes connection to IB TWS/Gateway asynchronously.
        """
        try:
            if not self.ib.isConnected():
                # Use the async version of connect
                await self.ib.connectAsync(self.host, self.port, self.client_id)
                # The server version is already logged by ib_insync, so a custom log is not needed.
                logging.info(f"Successfully connected to IB TWS/Gateway.")
            else:
                logging.info("Already connected to IB TWS/Gateway.")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to IB TWS/Gateway: {e}")
            return False

    async def disconnect(self) -> None:
        """
        Disconnects from IB TWS/Gateway asynchronously.
        """
        if self.ib.isConnected():
            self.ib.disconnect()  # disconnect() is synchronous but should be called on a connected client
            logging.info("Disconnected from IB TWS/Gateway.")
        else:
            logging.info("Not connected to IB TWS/Gateway.")

    @property
    def is_connected(self) -> bool:
        """
        Checks if the connection to IB TWS/Gateway is active.
        """
        return self.ib.isConnected()

    async def get_account_summary(self, account: str = '') -> List[AccountValue]:
        """
        Retrieves the account summary from IB asynchronously.
        """
        if not self.is_connected:
            logging.error("Not connected to IB. Cannot fetch account summary.")
            return []
        # Use the async version of accountSummary
        return await self.ib.accountSummaryAsync(account)


async def main():
    """
    Main async function to demonstrate IBConnection usage.
    """
    conn = IBConnection()
    try:
        if await conn.connect():
            print("Connection successful! Getting account summary...")
            # Await the async method
            summary = await conn.get_account_summary()
            if not summary:
                print("Could not retrieve account summary.")
            else:
                for item in summary:
                    if item.tag == 'NetLiquidation':
                        print(f"Net Liquidation: {item.value} {item.currency}")
                        break
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    finally:
        # Await the async method
        await conn.disconnect()


if __name__ == "__main__":
    # Example usage:
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logging.info("Program terminated by user.")
    except Exception as e:
        logging.critical(f"A critical error occurred in connection test: {e}")


