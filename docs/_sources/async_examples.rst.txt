Async Usage & Strategy Examples
==============================

This page provides practical examples for using the async API (`BinaryOptionsToolsAsync`) in trading bots and data analysis.

Minimal Async Example
---------------------

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


Advanced Async Trading Example
-----------------------------

This example fetches candles, calculates a simple moving average (SMA), and places a trade based on the indicator.

.. code-block:: python

    import asyncio
    import pandas as pd
    from BinaryOptionsToolsAsync.pocketoption import PocketOptionAsync

    async def main():
        ssid = input("Enter your ssid: ")
        api = PocketOptionAsync(ssid, demo=True)
        candles = await api.get_candles("EURUSD_otc", period=60, duration=1200)
        df = pd.DataFrame(candles)
        df['SMA_5'] = df['close'].rolling(window=5).mean()
        if df['close'].iloc[-1] > df['SMA_5'].iloc[-1]:
            trade_id, success = await api.buy("EURUSD_otc", amount=1, time=60)
        else:
            trade_id, success = await api.sell("EURUSD_otc", amount=1, time=60)
        await api.close()

    if __name__ == "__main__":
        asyncio.run(main())


Tips
----
- Always close the API connection with `await api.close()`.
- Use `asyncio.sleep()` to wait for trade expiration.
- Use pandas or numpy for indicator calculations.

See also: :doc:`BinaryOptionsToolsAsync` for full async API reference.
