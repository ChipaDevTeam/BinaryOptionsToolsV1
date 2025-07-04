"""Module for PocketOption subscribe websocket channel."""

from BinaryOptionsTools.platforms.pocketoption.ws.channels.base import Base


class Subscribe(Base):
    """Class for PocketOption subscribe websocket channel."""
    # pylint: disable=too-few-public-methods

    name = "sendMessage"

    def __call__(self, active_id):
        """Method to send message to subscribe websocket channel.

        :param active_id: The active/asset identifier (e.g., "AEDCNY_otc").
        """

        # New PocketOption message format: 42["subfor","AEDCNY_otc"]
        data = ["subfor", active_id]

        self.send_websocket_request(self.name, data)


class SubscribeCandles(Subscribe):
    """Class for PocketOption candles subscription websocket channel."""
    pass


class SubscribeTradingPair(Subscribe):
    """Class for PocketOption trading pair subscription websocket channel."""
    pass
