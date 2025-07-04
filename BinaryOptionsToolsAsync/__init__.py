# Made by © Vigo Walker and © Alenxendre Portner at Chipa

# Pocket Option
from BinaryOptionsToolsAsync.platforms.pocketoption.stable_api import PocketOption
# New async wrapper and tracing for V2 compatibility
# from BinaryOptionsToolsAsync.pocketoption import PocketOptionAsync
# from BinaryOptionsToolsAsync.tracing import start_logs, get_logger

import time
#--------------------- Pocket Option Wrapper ---------------------#
class pocketoption:
    def __init__(self, ssid: str, demo: bool = True) -> None:
        self.ssid = ssid
        self.api = PocketOption(ssid, demo)
        self.api.connect()
        print("Connecting...")
        time.sleep(10)
    def GetBalance(self) -> int | float:
        data = self.api.get_balance()
        return data
    def Reconnect(self, retries: int = 1) -> bool:
        for i in range(1, retries):
            self.api.connect()
            print("Connecting...")
            time.sleep(5)
        if self.api.check_connect():
            return True
        elif self.api.check_connect() is False:
            return False
        return None
    def Call(self, amount: int = 1, active: str = "EURUSD_otc", expiration: int = 60, add_check_win: bool = False):
        if add_check_win:
            ido = self.api.buy(amount, active, "call", expiration)[1]
            print(ido)
            data = self.api.check_win(ido)
            return data
        elif add_check_win is False:
            ido = self.api.buy(amount, active, "call", expiration)
            return ido
        return None
    def Put(self, amount: int = 1, active: str = "EURUSD_otc", expiration: int = 60, add_check_win: bool = False):
        if add_check_win:
            ido = self.api.buy(amount, active, "put", expiration)
            data = self.api.check_win(ido)
            return data
        elif add_check_win is False:
            ido = self.api.buy(amount, active, "put", expiration)
            return ido
        return None
    def GetCandles(self, active, period, start_time=None, count=6000, count_request=1):
        data = self.api.get_candles(active, period, start_time, count, count_request)
        return data
    def CheckWin(self, id):
        data = self.api.check_win(id)
        return data
    
    def GetPayout(self, pair):
        return self.api.GetPayout(pair)
    
    def SubscribePair(self, active):
        """Subscribe to a trading pair using new PO message format: 42["subfor","AEDCNY_otc"]"""
        return self.api.subscribe_pair(active)
    
    def UnsubscribePair(self, active):
        """Unsubscribe from a trading pair using new PO message format: 42["unsubfor","AEDCNY_otc"]"""
        return self.api.unsubscribe_pair(active)
    
    def SubscribeCandles(self, active):
        """Subscribe to candle data for a trading pair"""
        return self.api.subscribe_candles(active)
    
    def UnsubscribeCandles(self, active):
        """Unsubscribe from candle data for a trading pair"""
        return self.api.unsubscribe_candles(active)
    
    def SubscribeTradingPair(self, active):
        """Subscribe to trading pair data"""
        return self.api.subscribe_trading_pair(active)
    
    def UnsubscribeTradingPair(self, active):
        """Unsubscribe from trading pair data"""
        return self.api.unsubscribe_trading_pair(active)