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
    data = bt.feeds.YahooFinanceCSVData(dataname = './data/raw/BTCUSDT_15min.csv')
    cerebro.adddata(data)
    # Add a strategy
    cerebro.addstrategy(SimpleRSI)

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
    thestrats = cerebro.run(stdstats=True)

    # -----------------------------------------------------------------------------------

    print(AnalyzerSuite.returnAnalyzers(AnalyzerSuite,thestrats))
    # Print out the final result
    print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # Plot the result
    cerebro.plot()  