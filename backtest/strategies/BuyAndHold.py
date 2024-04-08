# Trade logics use for backtesting and live trading
from __future__ import (absolute_import, division, print_function, unicode_literals)
import argparse
import datetime
# Algo trading libs
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.indicators as btind
import math            

class BuyAndHold(bt.Strategy):
    """
    A simple buy and hold strategy that buys all available cash at the start and holds the position until the end.

    This strategy aims to capture the long-term upward trend of an asset by buying and holding it throughout the entire backtest period.

    Strategy Steps:
    1. At the start of the backtest, buy all available cash.
    2. Hold the position until the end of the backtest period.

    This strategy does not involve any active trading decisions or timing the market. It assumes that the asset will appreciate over time.
    """
    def start(self):
        self.val_start = self.broker.get_cash()  # keep the starting cash

    def nextstart(self):
        # Buy all the available cash
        size = int(self.broker.get_cash() / self.data)
        self.buy(size=size)

    def stop(self):
        # calculate the actual returns
        self.roi = (self.broker.get_value() / self.val_start) - 1.0
        print('ROI:        {:.2f}%'.format(100.0 * self.roi))