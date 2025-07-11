"""
async_trading_example.py
-----------------------

Demonstrates advanced async usage of BinaryOptionsToolsAsync:
- Fetches candles
- Calculates a simple moving average (SMA)
- Makes a trade decision based on the indicator
- Places a trade and checks the result

Requirements:
- pandas

Run with: python examples/async_trading_example.py
"""
import asyncio
import logging
import pandas as pd
from BinaryOptionsToolsAsync.pocketoption import PocketOptionAsync

logging.basicConfig(level=logging.INFO)

async def main():
    """
    Main async trading logic:
    1. Connects to PocketOptionAsync
    2. Fetches candles and calculates SMA
    3. Makes a trade decision (buy/sell)
    4. Places trade, waits, and checks result
    """
    ssid = input("Enter your ssid: ")
    api = PocketOptionAsync(ssid, demo=True)

    # Get and print balance
    balance = await api.balance()
    print(f"[ASYNC] Balance: {balance}")

    # Fetch last 20 candles for EURUSD_otc, 1-minute timeframe
    candles = await api.get_candles("EURUSD_otc", period=60, duration=1200)
    print(f"[ASYNC] Last 5 candles: {candles[-5:]}")

    # Convert candles to DataFrame for indicator calculation
    df = pd.DataFrame(candles)
    if 'close' not in df:
        print("Candle data missing 'close' field!")
        await api.close()
        return

    # Calculate a simple moving average (SMA)
    df['SMA_5'] = df['close'].rolling(window=5).mean()
    print(df[['close', 'SMA_5']].tail())

    # Simple strategy: if last close > last SMA, buy; else, sell
    if df['close'].iloc[-1] > df['SMA_5'].iloc[-1]:
        direction = 'buy'
        print("Signal: BUY (close > SMA)")
    else:
        direction = 'sell'
        print("Signal: SELL (close <= SMA)")

    # Place the trade
    print(f"Placing a test trade: {direction.upper()}...")
    if direction == 'buy':
        trade_id, success = await api.buy("EURUSD_otc", amount=1, time=60)
    else:
        trade_id, success = await api.sell("EURUSD_otc", amount=1, time=60)
    if not success:
        print("Trade failed!")
        await api.close()
        return
    print(f"Trade placed! Trade ID: {trade_id}")

    # Wait for trade to expire (simulate 1 minute)
    print("Waiting for trade to expire...")
    await asyncio.sleep(65)

    # Check trade result
    result = await api.check_win(trade_id)
    print(f"Trade result: {result}")

    # Get payout info
    payout = await api.get_payout("EURUSD_otc")
    print(f"Payout for EURUSD_otc: {payout}")

    await api.close()

if __name__ == "__main__":
    asyncio.run(main())
