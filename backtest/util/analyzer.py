import backtrader.analyzers as btanalyzers

riskfreerate = 0.04616

class AnalyzerSuite():
    def defineAnalyzers(self, cerebro):
        cerebro.addanalyzer(btanalyzers.DrawDown, _name='mydrawdown')
        cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe', riskfreerate = riskfreerate)
        cerebro.addanalyzer(btanalyzers.SortinoRatio, _name='mysortino', riskfreerate = riskfreerate)
        cerebro.addanalyzer(btanalyzers.Returns, _name='myreturn')
        cerebro.addanalyzer(btanalyzers.TradeAnalyzer, _name='mytradeanalyzer')

    def returnAnalyzers(self, thestrats):
        thestrat = thestrats[0]
        return {
            'Maximum DrawDown %': round(thestrat.analyzers.mydrawdown.get_analysis()['max']['drawdown'], 4),
            'Sharpe Ratio:': round(thestrat.analyzers.mysharpe.get_analysis()['sharperatio'], 4),
            'Sortino Ratio': round(thestrat.analyzers.mysortino.get_analysis()['sortinoratio'], 4),
            'Annualized return %:': round(thestrat.analyzers.myreturn.get_analysis()['rnorm100'], 4),
            'Average holding bars:': round(thestrat.analyzers.mytradeanalyzer.get_analysis()['len']['average'], 4),
        }