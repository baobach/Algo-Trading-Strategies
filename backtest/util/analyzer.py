import backtrader.analyzers as btanalyzers

class AnalyzerSuite():
    def defineAnalyzers(self, cerebro):
        cerebro.addanalyzer(btanalyzers.DrawDown, _name='mydrawdown')
        cerebro.addanalyzer(btanalyzers.SharpeRatio, _name='mysharpe')
        cerebro.addanalyzer(btanalyzers.Returns, _name='myreturn')

    def returnAnalyzers(self, thestrats):
        thestrat = thestrats[0]
        sharpe_ratio = thestrat.analyzers.mysharpe.get_analysis().get('sharperatio')
        if sharpe_ratio is None:
            sharpe_ratio = 0
        return {'Maximum DrawDown: %.2f%%' % thestrat.analyzers.mydrawdown.get_analysis()['max']['drawdown'],
                'Sharpe Ratio: %.2f' % sharpe_ratio,
                'Annualized return: %.2f%%' % thestrat.analyzers.myreturn.get_analysis()['rnorm100']}
