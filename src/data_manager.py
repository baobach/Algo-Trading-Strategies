import os
import pandas as pd
import backtrader as bt

class DataManager:
    def __init__(self):
        """
        Manage the data in the `data` folder. Provides methods to get available tickers and load ticker data.
        - get_available_tickers(): Returns a list of available tickers.
        - load_ticker_data(ticker): Loads the data for a specific ticker.
        - cerebro_add_data(ticker1, ticker2, cerebro): Loads and adds the data for two tickers to the cerebro engine.
        """
        self.data_folder = '/Users/baobach/Backtesting-Algo-Trading/data/raw'

    def get_available_tickers(self):
        """
        Returns a list of available tickers.

        It iterates through the files in the data_folder and extracts the ticker names from the file names.
        Only files with the '.csv' extension are considered.
        """
        tickers = []
        for file_name in os.listdir(self.data_folder):
            if file_name.endswith('.csv'):
                ticker = os.path.splitext(file_name)[0]
                tickers.append(ticker)
        return tickers

    def load_ticker_data(self, ticker):
        """
        Loads the data for a specific ticker.

        It checks if the ticker data file exists in the data_folder.
        If the file does not exist, it raises a ValueError.
        Otherwise, it reads the CSV file using pandas and returns the DataFrame.
        
        Parameters:
        - ticker (str): The ticker symbol for which to load the data.

        Returns:
        - df (pandas.DataFrame): The loaded ticker data as a DataFrame.
        """
        file_path = os.path.join(self.data_folder, f'{ticker}.csv')
        if not os.path.exists(file_path):
            raise ValueError(f'Ticker data for {ticker} does not exist.')
        df = pd.read_csv(file_path)
        df = df.set_index('date')  # Set the index as the date column
        return df
    
    def cerebro_add_data(self, tickers, cerebro):
        """
        Loads and adds the data for multiple tickers to the cerebro engine.

        It checks if the ticker data files exist in the data_folder.
        If any of the files do not exist, it raises a ValueError.
        Otherwise, it reads the CSV files using pandas and adds the data to the cerebro engine.

        Parameters:
        - tickers (list): A list of ticker symbols to load and add.
        - cerebro (backtrader.Cerebro): The cerebro engine to add the data to.
        """
        for ticker in tickers:
            file_path = os.path.join(self.data_folder, f'{ticker}.csv')
            if not os.path.exists(file_path):
                raise ValueError(f'Ticker data for {ticker} does not exist.')
            data = bt.feeds.GenericCSVData(
                dataname=file_path,
                nullvalue=0.0,
                dtformat=('%Y-%m-%d'),
                datetime=0,
                high=1,
                low=2,
                open=3,
                close=4,
                volume=5
                )
            cerebro.adddata(data, name=ticker)
