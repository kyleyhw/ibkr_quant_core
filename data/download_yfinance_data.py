import yfinance as yf
import pandas as pd

def download_data(ticker, start_date, end_date, filepath):
    """Downloads historical daily data from Yahoo Finance and saves it to a CSV."""
    print(f"Downloading {ticker} data from {start_date} to {end_date}...")
    data = yf.download(ticker, start=start_date, end=end_date, interval='1d')
    if data.empty:
        print(f"Error: No data found for {ticker}.")
        return
    data.to_csv(filepath)
    print(f"Data saved to {filepath}")

if __name__ == "__main__":
    # Define parameters
    START_DATE = "2010-01-01"
    END_DATE = "2023-12-31"
    
    # --- Download PEP data ---
    download_data(
        ticker="PEP",
        start_date=START_DATE,
        end_date=END_DATE,
        filepath="data/PEP_daily_2010_2023.csv"
    )
    
    # --- Download KO data ---
    download_data(
        ticker="KO",
        start_date=START_DATE,
        end_date=END_DATE,
        filepath="data/KO_daily_2010_2023.csv"
    )
