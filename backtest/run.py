import os
import sys
import backtrader as bt
import pandas as pd

# Get the directory of the current script
script_dir = os.path.dirname(os.path.realpath(__file__))
# Add the parent directory to the system path
sys.path.append(os.path.join(script_dir, '..'))

from backtest.algos.strategies import *
from backtest.util.analyzer import AnalyzerSuite

dataname = "./data/raw/5EMA_45BN.csv"

if __name__ == "__main__":
    # ------------------------------------------------------------------------------------
    # Create a cerebro entity
    cerebro = bt.Cerebro()
    data = bt.feeds.GenericCSVData(
        dataname=dataname,
        # fromdate = pd.Timestamp('2021-01-01'),
        # todate = pd.Timestamp('2021-05-05'),
        datetime=0,
        open=1,
        high=2,
        low=3,
        close=4,
        volume=-1,
        openinterest=-1,
    )
    cerebro.adddata(data)
    # Add a strategy
    cerebro.addstrategy(EMA_BUY)
    # # Add log export
    # cerebro.addwriter(bt.WriterFile, csv=True, out = 'log.csv')

    # Set our desired cash start
    cerebro.broker.setcash(100_000.0)
    # Set the commission
    # cerebro.broker.setcommission(commission=0.001)

    # ------------------------------------------------------------------------------------

    # Print out the starting conditions
    print("Starting Portfolio Value: %.2f" % cerebro.broker.getvalue())
    # Analyzer
    AnalyzerSuite.defineAnalyzers(AnalyzerSuite, cerebro)
    # Run over everything
    thestrats = cerebro.run()

    # -----------------------------------------------------------------------------------

    print(AnalyzerSuite.returnAnalyzers(AnalyzerSuite, thestrats))
    # Print out the final result
    print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())
    # Plot the result
    cerebro.plot()
