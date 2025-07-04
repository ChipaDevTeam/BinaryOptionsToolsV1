from BinaryOptionsToolsAsync import pocketoption
from ta.trend import SMAIndicator
from ta.volatility import AverageTrueRange
import time
# import pandas as pd

ssid = (r'42["auth",{"session":"vtftn12e6f5f5008moitsd6skl","isDemo":1,"uid":27658142,"platform":2}]')
demo = True
api = pocketoption(ssid, demo)

while True:
    try:
        data = api.GetCandles("EURUSD_otc", 1)
        sma5 = SMAIndicator(data["close"], 5).sma_indicator()
        sma10 = SMAIndicator(data["close"], 10).sma_indicator()
        atr = AverageTrueRange(data["high"], data["low"], data["close"], 14).average_true_range()

        print(f"SMA10: {sma10}")
        print(f"SMA5: {sma5}")
        print(f"ATR: {atr}")
        time.sleep(5)
    except KeyboardInterrupt:
        break