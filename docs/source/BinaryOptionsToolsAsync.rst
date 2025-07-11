BinaryOptionsToolsAsync
======================

Async API for BinaryOptionsTools
--------------------------------

This module provides an async interface for trading and data collection with PocketOption.

.. automodule:: BinaryOptionsToolsAsync.pocketoption
   :members:
   :undoc-members:
   :show-inheritance:

Example Usage
-------------

.. code-block:: python

    import asyncio
    from BinaryOptionsToolsAsync.pocketoption import PocketOptionAsync

    async def main():
        ssid = input("Enter your ssid: ")
        api = PocketOptionAsync(ssid, demo=True)
        balance = await api.balance()
        print(f"[ASYNC] GET BALANCE: {balance}")
        await api.close()

    if __name__ == "__main__":
        asyncio.run(main())
