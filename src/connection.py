import asyncio
import os
import logging
from typing import Optional

from ib_insync import IB
from ib_insync.objects import AccountValue
from python_dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class IBConnection:
    """
    Manages the connection to Interactive Brokers TWS or Gateway.

    This class encapsulates the `ib_insync` IB object and provides methods
    for connecting, disconnecting, and checking the connection status.
    It loads connection parameters from environment variables to maintain
    security and flexibility.
    """

    def __init__(self,
                 host: Optional[str] = None,
                 port: Optional[int] = None,
                 client_id: Optional[int] = None):
        """
        Initializes the IBConnection with optional host, port, and client ID.
        Parameters are loaded from environment variables if not provided.

        Args:
            host (Optional[str]): The host address of the TWS/Gateway.
                                  Defaults to env var 'IB_HOST' or '127.0.0.1'.
            port (Optional[int]): The port of the TWS/Gateway.
                                  Defaults to env var 'IB_PORT' or 7497.
            client_id (Optional[int]): The client ID for the connection.
                                       Defaults to env var 'IB_CLIENT_ID' or 1.
        """
        self.ib = IB()
        self.host = host if host is not None else os.getenv('IB_HOST', '127.0.0.1')
        self.port = port if port is not None else int(os.getenv('IB_PORT', '7497'))
        self.client_id = client_id if client_id is not None else int(os.getenv('IB_CLIENT_ID', '1'))
        logging.info(f"Initialized IBConnection with host={self.host}, port={self.port}, client_id={self.client_id}")

    async def _connect_async(self) -> bool:
        """
        Asynchronously establishes connection to IB TWS/Gateway.

        Returns:
            bool: True if connection is successful, False otherwise.
        """
        try:
            # Attempt to connect without causing an asyncio RuntimeError if already running
            if not self.ib.isConnected():
                await self.ib.connect(self.host, self.port, self.client_id)
                logging.info(f"Successfully connected to IB TWS/Gateway. Server Version: {self.ib.serverVersion()}")
            else:
                logging.info("Already connected to IB TWS/Gateway.")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to IB TWS/Gateway: {e}")
            return False

    def connect(self) -> bool:
        """
        Establishes connection to IB TWS/Gateway using asyncio.run().

        Returns:
            bool: True if connection is successful, False otherwise.
        """
        # Ensure there's an asyncio event loop running
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # If a loop is already running, schedule the connection task
            logging.warning("An asyncio loop is already running. Scheduling connection as a task.")
            # This might require specific handling depending on where connect() is called.
            # For simplicity, we'll try to run it directly if no loop, otherwise warn.
            # In a real app, you'd await this from within the existing loop.
            return asyncio.run(self._connect_async())
        else:
            # If no loop is running, create and run a new one
            return asyncio.run(self._connect_async())

    def disconnect(self) -> None:
        """
        Disconnects from IB TWS/Gateway.
        """
        if self.ib.isConnected():
            self.ib.disconnect()
            logging.info("Disconnected from IB TWS/Gateway.")
        else:
            logging.info("Not connected to IB TWS/Gateway.")

    @property
    def is_connected(self) -> bool:
        """
        Checks if the connection to IB TWS/Gateway is active.

        Returns:
            bool: True if connected, False otherwise.
        """
        return self.ib.isConnected()

    def get_account_summary(self, account: str = '') -> list[AccountValue]:
        """
        Retrieves the account summary from IB.

        Args:
            account (str): The account code to retrieve summary for.
                           Defaults to primary account if empty.

        Returns:
            list[AccountValue]: A list of AccountValue objects.
        """
        if not self.is_connected:
            logging.error("Not connected to IB. Cannot fetch account summary.")
            return []
        
        # Ensure to run it in an async context if called directly, 
        # or await if called from within an existing async function.
        # For this synchronous wrapper, we'll use asyncio.run if not in an event loop.
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
            # If in an async context, this needs to be awaited
            logging.warning("Called get_account_summary from an existing asyncio loop. "
                            "This method should ideally be awaited if called in an async context.")
            return self.ib.reqAccountSummary(account)
        else:
            return asyncio.run(self._get_account_summary_async(account))

    async def _get_account_summary_async(self, account: str) -> list[AccountValue]:
        """
        Asynchronously retrieves the account summary from IB.
        """
        return await self.ib.reqAccountSummaryAsync(account)


if __name__ == "__main__":
    # Example usage:
    # Create a .env file in the project root with:
    # IB_HOST=127.0.0.1
    # IB_PORT=7497 # or 4002 for gateway
    # IB_CLIENT_ID=1

    conn = IBConnection()
    if conn.connect():
        print("Connection successful! Getting account summary...")
        summary = conn.get_account_summary()
        for item in summary:
            if item.tag == 'NetLiquidation':
                print(f"Net Liquidation: {item.value} {item.currency}")
                break
        conn.disconnect()
    else:
        print("Failed to connect.")

