import sys
sys.path.append("/Users/baobach/Algo-Trading-Strategies")
import backtrader as bt
import pandas as pd
from src.strategies import *
from src.analyzer import AnalyzerSuite

if __name__ == '__main__':
    # ------------------------------------------------------------------------------------
    # Create a cerebro entity
    cerebro = bt.Cerebro()
    data = bt.feeds.GenericCSVData(
        dataname = './data/raw/niftybank.csv',
        # fromdate = pd.Timestamp('2021-01-01'),
        # todate = pd.Timestamp('2021-05-05'),
        datetime=0,
        high=1,
        low=2,
        open=3,
        close=4,
        volume=5,
        openinterest=-1
        )
    cerebro.adddata(data)
    # Add a strategy
    cerebro.addstrategy(EMA_BUY)
    # # Add log export
    # cerebro.addwriter(bt.WriterFile, csv=True, out = 'log.csv')

    # Set our desired cash start
    cerebro.broker.setcash(100_000.0)
    # Set the commission
    #cerebro.broker.setcommission(commission=0.001)

    # ------------------------------------------------------------------------------------

    # Print out the starting conditions
    print('Starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # Analyzer
    AnalyzerSuite.defineAnalyzers(AnalyzerSuite,cerebro)
    # Run over everything
    thestrats = cerebro.run()

    # -----------------------------------------------------------------------------------

    print(AnalyzerSuite.returnAnalyzers(AnalyzerSuite,thestrats))
    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # Plot the result
    cerebro.plot()  