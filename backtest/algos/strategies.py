# Trade logics use for backtesting and live trading
from __future__ import (absolute_import, division, print_function, unicode_literals)
import argparse
import datetime
# Algo trading libs
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.indicators as btind
import math

class EMA_BUY(bt.Strategy):
    params = (
        ('maperiod', 5),
        ('printlog', False),
        ('trailpercent', 0.02),
    )

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.datahigh = self.datas[0].high
        self.datalow = self.datas[0].low

        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add alert candle
        self.alert_candle = False

        # Add size of buy and sell order
        self.size = 0

        # Add a EMA indicator
        self.ema = btind.ExponentialMovingAverage(period=self.params.maperiod)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log(
                    'SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check if this candle is an alert candle
        if self.ema[0] > self.datahigh[0]:
            self.log('Alert Candle, %.2f' % self.dataclose[0])
            self.alert_candle = True
            self.alert_high = self.datahigh[0]
            self.alert_low = self.datalow[0]

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:
            # Check if we have an alert candle
            if self.alert_candle:
                # Check the buy condition for current `H` vs alert candle `H`
                if self.datas[0].high > self.alert_high:
                    self.log('BUY CREATE, %.2f' % self.dataclose[0])
                    # Buy all the available cash
                    self.size = int(self.broker.get_cash() / self.dataclose[0])
                    self.order = self.buy(size = self.size)
                    self.stoploss = self.alert_low
                    self.takeprofit = self.alert_high + 3*(self.alert_high-self.alert_low)
                    self.alert_candle = False
        else:
            if self.dataclose[0] < self.stoploss:
                self.log('STOP LOSS, %.2f' % self.dataclose[0])
                self.order = self.close()
            elif self.dataclose[0] > self.takeprofit:
                # Traling profit
                temp = self.takeprofit + (self.alert_high - self.stoploss)
                stoploss = self.takeprofit
                takeprofit = temp
                if self.dataclose[0] > takeprofit:
                    temp = takeprofit + (takeprofit - stoploss)
                else:
                    self.log('TAKE PROFIT, %.2f' % self.dataclose[0])
                    self.order = self.close()                                

class BuyAndHold(bt.Strategy):
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

class SimpleRSI(bt.Strategy):
    params = (
        ('printlog', True),
        ('period', 14),
        ('upperband', 60.0),
        ('lowerband', 40.0),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None
        # Add a RSI indicator
        self.rsi = btind.RelativeStrengthIndex(period=self.params.period, upperband=self.params.upperband, lowerband=self.params.lowerband)

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))

                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))

            self.bar_executed = len(self)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def next(self):
        # Simply log the closing price of the series from the reference
        self.log('Close, %.2f' % self.dataclose[0])

        # Check for open orders
        if self.order:
            return

        # Check if we are not in the market
        if not self.position:
            # Not yet ... we MIGHT BUY if ...
            if self.rsi[0] > 60:
                # BUY, BUY, BUY!!! (with all possible default parameters)
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                # Keep track of the created order to avoid a 2nd order
                size = self.broker.getvalue() / self.dataclose[0]
                self.order = self.buy(size = size)
                self.stoploss = self.dataclose[0]*0.99
                self.takeprofit = self.dataclose[0]*1.03
        else:
            if self.dataclose[0] < self.stoploss:
                self.log('STOP LOSS, %.2f' % self.dataclose[0])
                self.order = self.sell(size=self.position.size)
            elif self.dataclose[0] > self.takeprofit:
                self.log('TAKE PROFIT, %.2f' % self.dataclose[0])
                self.order = self.sell(size=self.position.size)
