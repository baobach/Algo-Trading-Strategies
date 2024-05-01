# Trade logics use for backtesting and live trading
from __future__ import absolute_import, division, print_function, unicode_literals
import argparse
import datetime

# Algo trading libs
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.indicators as btind
import math


class SimpleRSI(bt.Strategy):
    """
    SimpleRSI strategy is a basic trading strategy based on the Relative Strength Index (RSI) indicator.

    Parameters:
        - printlog (bool): Flag to enable/disable logging (default: True)
        - period (int): Period used for calculating the RSI indicator (default: 14)
        - upperband (float): Upper threshold for the RSI indicator (default: 60.0)
        - lowerband (float): Lower threshold for the RSI indicator (default: 40.0)
    """

    params = (
        ("printlog", True),
        ("period", 14),
        ("upperband", 60.0),
        ("lowerband", 40.0),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        # Add a RSI indicator
        self.rsi = btind.RelativeStrengthIndex(
            period=self.params.period,
            upperband=self.params.upperband,
            lowerband=self.params.lowerband,
        )

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print("%s, %s" % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    "BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log(
                    "SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f"
                    % (order.executed.price, order.executed.value, order.executed.comm)
                )

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log("Order Canceled/Margin/Rejected")

        self.order = None

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log("Close, %.2f" % self.dataclose[0])

        # Check for open orders
        if self.order:
            return

        # Check if we are not in the market
        if not self.position:
            # Not yet ... we MIGHT BUY if ...
            if self.rsi[0] > 60:
                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log("BUY CREATE, %.2f" % self.dataclose[0])
                # Keep track of the created order to avoid a 2nd order
                size = self.broker.getvalue() / self.dataclose[0]
                self.order = self.buy(size=size)
                self.stoploss = self.dataclose[0] * 0.99
                self.takeprofit = self.dataclose[0] * 1.03
        else:
            if self.dataclose[0] < self.stoploss:
                self.log("STOP LOSS, %.2f" % self.dataclose[0])
                self.order = self.sell(size=self.position.size)
            elif self.dataclose[0] > self.takeprofit:
                self.log("TAKE PROFIT, %.2f" % self.dataclose[0])
                self.order = self.sell(size=self.position.size)
