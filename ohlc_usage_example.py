#!/usr/bin/env python3
"""
Usage example for OHLC candle aggregation with PocketOption API.
"""

import asyncio
import time
from BinaryOptionsToolsAsync.platforms.pocketoption.stable_api import PocketOption

async def main():
    # Your SSID from browser (replace with real value)
    ssid = "your_ssid_here"
    
    # Create API instance
    api = PocketOption(ssid, demo=True)
    
    # Connect to WebSocket
    await api.connect()
    
    # Callback for completed candles
    def on_candle_complete(asset, candle):
        print(f"🕯️ New {asset} candle: O:{candle.open} H:{candle.high} L:{candle.low} C:{candle.close} at {candle.timestamp}")
    
    # Subscribe with OHLC aggregation
    api.subscribe_candles(
        active="EURUSD_otc",
        create_ohlc=True,           # Enable OHLC aggregation
        timeframe_seconds=60,       # 1-minute candles
        max_candles=1000,          # Keep last 1000 candles
        on_candle_complete=on_candle_complete
    )
    
    print("Collecting OHLC data... (press Ctrl+C to stop)")
    
    try:
        while True:
            await asyncio.sleep(10)
            
            # Get completed OHLC candles
            candles = api.get_ohlc_candles("EURUSD_otc", timeframe_seconds=60, count=5)
            print(f"📈 Latest 5 completed candles: {len(candles)}")
            
            # Get current incomplete candle
            current = api.get_current_ohlc_candle("EURUSD_otc", timeframe_seconds=60)
            if current:
                print(f"📊 Current candle: O:{current['open']} H:{current['high']} L:{current['low']} C:{current['close']} | Ticks:{current['tick_count']}")
            
            # Show aggregation stats
            stats = api.get_ohlc_stats()
            if stats:
                print(f"📋 Stats: {stats}")
    
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        # Unsubscribe
        api.unsubscribe_candles("EURUSD_otc")
        await api.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
