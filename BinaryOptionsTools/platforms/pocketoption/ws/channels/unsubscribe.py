"""Module for PocketOption unsubscribe websocket channel."""

from BinaryOptionsTools.platforms.pocketoption.ws.channels.base import Base


class Unsubscribe(Base):
    """Class for PocketOption unsubscribe websocket channel."""
    # pylint: disable=too-few-public-methods

    name = "sendMessage"

    def __call__(self, active_id):
        """Method to send message to unsubscribe websocket channel.

        :param active_id: The active/asset identifier (e.g., "AEDCNY_otc").
        """

        # New PocketOption message format: 42["unsubfor","AEDCNY_otc"]
        data = ["unsubfor", active_id]

        self.send_websocket_request(self.name, data)


class UnsubscribeCandles(Unsubscribe):
    """Class for PocketOption candles unsubscription websocket channel."""
    pass


class UnsubscribeTradingPair(Unsubscribe):
    """Class for PocketOption trading pair unsubscription websocket channel."""
    pass
