"""Module for Pocket option candles websocket chanel."""

from BinaryOptionsTools.platforms.pocketoption.ws.channels.base import Base
# import time
import random
import time


def index_num():
    # El número mínimo sería 100000000000 (12 dígitos)
    minimo = 5000
    # El número máximo sería 999999999999 (12 dígitos)
    maximo = 10000 - 1
    # Generar y retornar un número aleatorio dentro del rango
    return random.randint(minimo, maximo)


class GetCandles(Base):
    """Class for Pocket option candles websocket chanel."""
    # pylint: disable=too-few-public-methods

    name = "sendMessage"

    def __call__(self, active_id, interval, count, end_time):
        """Method to send message to candles websocket chanel.

        :param active_id: The active/asset identifier.
        :param interval: The candle duration (timeframe for the candles).
        :param count: The number of candles you want to have
        """

        #      {"asset": "AUDNZD_otc", "index": 171201484810, "time": 1712002800, "offset": 9000, "period": 60}]
        rand = str(random.randint(10, 99))
        cu = int(time.time())
        t = str(cu + (2 * 60 * 60))
        index = int(t + rand)
        data = {
            "asset": str(active_id),
            "index": index,
            "offset": count,  # number of candles
            "period": interval,
            "time": end_time,  # time size sample:if interval set 1 mean get time 0~1 candle
        }

        data = ["loadHistoryPeriod", data]
        self.send_websocket_request(self.name, data)
