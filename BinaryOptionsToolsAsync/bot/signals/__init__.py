from BinaryOptionsTools.indicators.trend import sma

class StreamSignals:
    def __init__(self) -> None:
        pass
    def sma(self, period):
        pass

class signals:
    def __init__(self) -> None:
        pass
    def sma_cross_over(self, api, FAST_SMA_PERIOD: int = 9, SLOW_SMA_PERIOD: int = 14, timeframe: int = 60, ticker: str = "EURUSD_otc"):
        fast_sma = sma(api, timeframe, ticker, FAST_SMA_PERIOD)
        slow_sma = sma(api, timeframe, ticker, SLOW_SMA_PERIOD)

        if fast_sma["latest"] > slow_sma["latest"]:
            return "Bullish"
        elif fast_sma["latest"] < slow_sma["latest"]:
            return "Bearish"
        else:
            return "No trend"
