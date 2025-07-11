import asyncio
import logging
from BinaryOptionsToolsAsync.pocketoption import PocketOptionAsync

logging.basicConfig(level=logging.INFO)

async def main():
    ssid = input("Enter your ssid: ")
    api = PocketOptionAsync(ssid, demo=True)

    # Get current balance
    balance = await api.balance()
    print(f"[ASYNC] GET BALANCE: {balance}")

    # Get candles example
    candles = await api.get_candles("EURUSD_otc", period=60, duration=600)
    print(f"[ASYNC] CANDLES: {candles}")

    await api.close()

if __name__ == "__main__":
    asyncio.run(main())
