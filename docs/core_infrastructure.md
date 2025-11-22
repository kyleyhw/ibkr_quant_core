# core infrastructure

the core infrastructure of the trading bot is handled by a set of modules within the `src/` directory. these modules provide the foundational services needed for the bot to operate, including connecting to the broker, fetching data, and sending notifications.

## ibkr connection (`src/connection.py`)

### purpose
the `connection.py` module is responsible for establishing and managing the connection to the interactive brokers (ibkr) trader workstation (tws) or gateway. it abstracts the complexities of the `ib_insync` library's connection handling into a simple, reusable class.

### design and logic
-   **asynchronous operations**: the entire connection logic was refactored to be fully asynchronous using python's `asyncio` library. this is a critical design choice because `ib_insync` is an async-native library. using `async`/`await` ensures that network operations (like connecting or requesting data) are non-blocking, allowing the bot to remain responsive.
-   **`ibconnection` class**: this class encapsulates the `ib_insync.ib` object. a single instance of this class can be created and passed to other modules (like the `dataloader`), ensuring that all parts of the application share the same connection. this is an example of **dependency injection**.
-   **environment variables**: to maintain security and avoid hard-coding credentials, the connection parameters (host, port, client id) are loaded from a `.env` file using the `python-dotenv` library. this allows for different configurations between development and production environments without code changes. the `.env` file is explicitly listed in `.gitignore` to prevent it from being committed to the repository.

## data loading (`src/data_loader.py`)

### purpose
the `data_loader.py` module provides a standardized interface for fetching market data from ibkr. its primary goal is to ensure that data is retrieved and formatted consistently for use in other parts of the application, such as strategies or backtesting preparation.

### design and logic
-   **`dataloader` class**: this class requires an active `ibconnection` instance to be passed during initialization.
-   **asynchronous data fetching**: similar to the connection module, all data requests (`qualifycontractsasync`, `reqhistoricaldataasync`) are asynchronous to prevent blocking the application's event loop.
-   **robust contract creation**: the `create_contract` method was designed to be robust. instead of creating a contract with many `none` values (which the ibkr api can reject), it dynamically builds a dictionary of non-none parameters. this ensures that only relevant information is sent to the api, preventing errors for securities that do not have properties like `strike` or `right` (e.g., stocks, forex).
-   **standardized dataframe format**: the `get_historical_data` method returns a `pandas.dataframe` with standardized column names (`open`, `high`, `low`, `close`, `volume`). this consistency is crucial for the `backtesting` library and any other component that consumes this data.

## notifications (`src/notifications.py`)

### purpose
the `notifications.py` module provides a simple way to send alerts to an external service. this is essential for monitoring the bot's status, receiving notifications about trades, or being alerted to critical errors that require manual intervention.

### design and logic
-   **`notifier` class**: a simple class that handles the formatting and sending of messages.
-   **discord webhook**: the initial implementation uses discord webhooks, a common and easy-to-use notification method. the webhook url is loaded from the `discord_webhook_url` environment variable, again ensuring that this secret is not hard-coded.
-   **severity levels**: the `send` method includes a `severity` enum (`info`, `warning`, `error`, `critical`). this allows for color-coded and prioritized messages in discord, making it easy to distinguish between routine updates and urgent problems at a glance.
-   **error handling**: the `send` method includes `try...except` blocks to gracefully handle network errors or an unset webhook url, preventing the entire bot from crashing if a notification fails to send.
