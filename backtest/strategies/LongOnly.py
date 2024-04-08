from __future__ import (absolute_import, division, print_function, unicode_literals)
import argparse
import datetime
import backtrader as bt
import backtrader.feeds as btfeeds
import backtrader.indicators as btind
import math

class Long1(bt.Strategy):
    """
    if CrossDown Bollinger Top and vol condition : 
        long
    if CrossDown Bollinger Bot and vol condition : 
        close
    """
    params = (
        ('volume_short', 10),
        ('volume_long', 50),
        ('printlog', False),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Define indicators
        self.volume = self.datas[0].volume
        self.volume_short = btind.MovingAverageSimple(self.volume, period = self.params.volume_short,plotname =  'Short Volume MA', subplot = True)
        self.volume_long = btind.MovingAverageSimple(self.volume, period = self.params.volume_long, plotname = 'Long Volume MA', subplot = True)
        self.volume_condition = self.volume_short > self.volume_long
        bt.LinePlotterIndicator(self.volume_condition, name='Volume Condition')
        self.bb = btind.BollingerBands(period = 20, devfactor = 2.0)

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

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return
        
        # Check if we are in the market
        if not self.position:
            if self.dataclose[0] < self.bb.lines.top and self.volume_condition[0]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.order_target_percent(target=0.95)
        else:
            if self.dataclose[0] < self.bb.lines.bot and self.volume_condition[0]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.close()
    
    def stop(self):
        # calculate the actual returns
        self.roi = (self.broker.get_value() / self.val_start) - 1.0
        print('ROI:        {:.2f}%'.format(100.0 * self.roi))                

class Long2(bt.Strategy):
    """
    if CrossDown Bollinger Top and vol condition : 
        long
    if CrossDown Bollinger Bot and vol condition : 
        close
    
    stoploss : at 5% below low of entry candle
    """
    params = (
        ('volume_short', 10),
        ('volume_long', 50),
        ('printlog', False),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.datalow = self.datas[0].low
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Define indicators
        self.volume = self.datas[0].volume
        self.volume_short = btind.MovingAverageSimple(self.volume, period = self.params.volume_short,plotname =  'Short Volume MA', subplot = True)
        self.volume_long = btind.MovingAverageSimple(self.volume, period = self.params.volume_long, plotname = 'Long Volume MA', subplot = True)
        self.volume_condition = self.volume_short > self.volume_long
        bt.LinePlotterIndicator(self.volume_condition, name='Volume Condition')
        self.bb = btind.BollingerBands(period = 20, devfactor = 2.0)

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

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return
        
        # Check if we are in the market
        if not self.position:
            if self.dataclose[0] < self.bb.lines.top and self.volume_condition[0]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.order_target_percent(target=0.95)
                self.stop_loss = self.datalow[0] * 0.95
        else:
            if self.dataclose[0] < self.stop_loss:
                self.log('STOP LOSS, %.2f' % self.dataclose[0])
                self.order = self.close()
            elif self.dataclose[0] < self.bb.lines.bot and self.volume_condition[0]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.close()

class Long3(bt.Strategy):
    """
    if CrossDown Bollinger Top and vol condition : 
        long
    if CrossDown Bollinger Bot and vol condition : 
        close
    stoploss : at 5% below low of entry candle
    stopwin:    if trade profit over 20% add stopwin at 15% 
                if trade profit over 25% add stopwin at 20% 
                if trade profit over 30% add stopwin at 25%
                if trade profit over 35% add stopwin at 30% 
                if trade profit over 40% add stopwin at 35%
    """
    params = (
        ('volume_short', 10),
        ('volume_long', 50),
        ('printlog', False),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.datalow = self.datas[0].low
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Define indicators
        self.volume = self.datas[0].volume
        self.volume_short = btind.MovingAverageSimple(self.volume, period = self.params.volume_short,plotname =  'Short Volume MA', subplot = True)
        self.volume_long = btind.MovingAverageSimple(self.volume, period = self.params.volume_long, plotname = 'Long Volume MA', subplot = True)
        self.volume_condition = self.volume_short > self.volume_long
        bt.LinePlotterIndicator(self.volume_condition, name='Volume Condition')
        self.bb = btind.BollingerBands(period = 20, devfactor = 2.0)
        self.stop_win = 0

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

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return
        
        # Check if we are in the market
        if not self.position:
            if self.dataclose[0] < self.bb.lines.top and self.volume_condition[0]:
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.order_target_percent(target=0.95)
                self.stop_loss = self.datalow[0] * 0.95
                self.buyprice = self.dataclose[0]
                
        else:
            self.trade_profit = (self.dataclose[0] - self.buyprice) / self.buyprice

            stop_win_values = {
                0.2: 1.15,
                0.25: 1.20,
                0.3: 1.25,
                0.35: 1.30,
                0.4: 1.35
            }

            for profit, multiplier in reversed(sorted(stop_win_values.items())):
                if self.trade_profit > profit:
                    self.stop_win = self.dataclose[0] * multiplier
                    break

            if self.dataclose[0] < self.stop_loss:
                self.log('STOP LOSS, %.2f' % self.dataclose[0])
                self.order = self.close()
            elif self.dataclose[0] < self.bb.lines.bot and self.volume_condition[0]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.close()
            elif self.dataclose[0] > self.stop_win:
                self.log('STOP WIN, %.2f' % self.dataclose[0])
                self.order = self.close()
                           
class Long4(bt.Strategy):
    """
    if CrossDown Bollinger Top and vol condition :
        if close price of candle > sma fast (per20):
            long 

    if CrossDown Bollinger Bot and vol condition : 
        close
    stoploss : at 5% below low of entry candle
    stopwin:    if trade profit over 20% add stopwin at 15% 
                if trade profit over 25% add stopwin at 20%
                if trade profit over 30% add stopwin at 25%
                if trade profit over 35% add stopwin at 30% 
                if trade profit over 40% add stopwin at 35%
    """
    params = (
        ('volume_short', 10),
        ('volume_long', 50),
        ('smafast', 20),
        ('printlog', False),
    )

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.datalow = self.datas[0].low
        # To keep track of pending orders and buy price/commission
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Define indicators
        self.volume = self.datas[0].volume
        self.volume_short = btind.MovingAverageSimple(self.volume, period = self.params.volume_short,plotname =  'Short Volume MA', subplot = True)
        self.volume_long = btind.MovingAverageSimple(self.volume, period = self.params.volume_long, plotname = 'Long Volume MA', subplot = True)
        self.volume_condition = self.volume_short > self.volume_long
        bt.LinePlotterIndicator(self.volume_condition, name='Volume Condition')
        self.bb = btind.BollingerBands(period = 20, devfactor = 2.0)
        self.stop_win = 0
        self.sma_fast = btind.SimpleMovingAverage(self.dataclose, period = self.params.smafast, plotname = 'SMA Fast', subplot = True)
        # Add indicator in the same subplot
        self.volume_short.plotinfo.plotmaster = self.volume_long

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

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return
        
        # Check if we are in the market
        if not self.position:
            if self.dataclose[0] < self.bb.lines.top and self.volume_condition[0]:
                if self.dataclose[0] > self.sma_fast:
                    self.log('BUY CREATE, %.2f' % self.dataclose[0])
                    self.order = self.order_target_percent(target=0.95)
                    self.stop_loss = self.datalow[0] * 0.95
                    self.buyprice = self.dataclose[0]
                
        else:
            self.trade_profit = (self.dataclose[0] - self.buyprice) / self.buyprice

            stop_win_values = {
                0.2: 1.15,
                0.25: 1.20,
                0.3: 1.25,
                0.35: 1.30,
                0.4: 1.35
            }

            for profit, multiplier in reversed(sorted(stop_win_values.items())):
                if self.trade_profit > profit:
                    self.stop_win = self.dataclose[0] * multiplier
                    break

            if self.dataclose[0] < self.stop_loss:
                self.log('STOP LOSS, %.2f' % self.dataclose[0])
                self.order = self.close()
            elif self.dataclose[0] < self.bb.lines.bot and self.volume_condition[0]:
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.close()
            elif self.dataclose[0] > self.stop_win:
                self.log('STOP WIN, %.2f' % self.dataclose[0])
                self.order = self.close()
                                                      