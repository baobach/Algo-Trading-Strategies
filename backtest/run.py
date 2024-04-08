import os
import sys
import backtrader as bt
import pandas as pd
from util.analyzer import AnalyzerSuite
from strategies.LongOnly import *

strategy = Long4

dataname = "./data/raw/BTCUSDT_1hour.csv"

# Create a cerebro entity
cerebro = bt.Cerebro()
data = bt.feeds.GenericCSVData(
    dataname=dataname,
    fromdate = pd.Timestamp('2021-01-01'),
    todate = pd.Timestamp('2021-05-05'),
    # Check column names for the data feed
    datetime=0,
    open=1,
    high=2,
    low=3,
    close=4,
    volume=6,
    openinterest=5,
)

# Set the colors of the bar plot
data.plotinfo.plot = True
data.plotinfo.barup = "green"
data.plotinfo.bardown = "red"

# Add the Data Feed to Cerebro
cerebro.adddata(data)
# Add a strategy
cerebro.addstrategy(strategy, printlog=False)
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
