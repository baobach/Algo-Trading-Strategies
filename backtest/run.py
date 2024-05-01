import os
import sys
import backtrader as bt
import pandas as pd
from util.analyzer import AnalyzerSuite
from strategies.EMA_BUY import *
import quantstats

strategy = EMA_BUY

dataname = "./data/raw/5EMA_45BN.csv"

# Create a cerebro entity
cerebro = bt.Cerebro()
data = bt.feeds.GenericCSVData(
    dataname=dataname,
    # fromdate = pd.Timestamp('2021-01-01'),
    # todate = pd.Timestamp('2021-05-05'),
    # Check column names for the data feed
    datetime=0,
    open=1,
    high=2,
    low=3,
    close=4,
    volume=-1,
    openinterest=-1,
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
# AnalyzerSuite.defineAnalyzers(AnalyzerSuite, cerebro)
cerebro.addanalyzer(bt.analyzers.PyFolio, _name="PyFolio")

# Run over everything
thestrats = cerebro.run()
strat = thestrats[0]

# -----------------------------------------------------------------------------------

print(AnalyzerSuite.returnAnalyzers(AnalyzerSuite, thestrats))
# Print out the final result
print("Final Portfolio Value: %.2f" % cerebro.broker.getvalue())
# Plot the result
cerebro.plot()

# -----------------------------------------------------------------------------------
# # Quantstats
# portfolio_stats = strat.analyzers.getbyname("PyFolio")
# returns, positions, transactions, gross_lev = portfolio_stats.get_pf_items()
# returns.index = returns.index.tz_convert(None)
# quantstats.reports.html(returns, output="bn_strategy.html", title="BN Sentiment")
