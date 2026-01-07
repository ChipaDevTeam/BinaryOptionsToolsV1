#!/usr/bin/env python3
"""
Async example script demonstrating multiprocessing support for fetching candles from multiple assets.

This example shows how to use the get_candles_multiple_assets method in async mode
to fetch historical candle data for multiple trading pairs in parallel.
"""

import asyncio
import time
import logging
from BinaryOptionsToolsAsync.pocketoption import PocketOptionAsync

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def main():
    # Get SSID from user
    ssid = input("Enter your ssid: ")
    
    # Initialize async API in demo mode
    print("Initializing PocketOption Async API...")
    api = PocketOptionAsync(ssid, demo=True)
    
    # Define multiple assets to fetch data for
    assets = [
        "EURUSD_otc",
        "GBPUSD_otc",
        "USDJPY_otc",
        "AUDUSD_otc",
        "USDCAD_otc",
        "NZDUSD_otc"
    ]
    
    print(f"\nFetching candles for {len(assets)} assets in parallel using async + multiprocessing...")
    print(f"Assets: {', '.join(assets)}")
    
    # Record start time
    start_time = time.time()
    
    # Fetch candles for multiple assets using multiprocessing
    # Parameters:
    # - assets: List of asset symbols
    # - period: 60 seconds (1 minute candles)
    # - duration: 600 seconds (10 minutes of data)
    # - max_workers: None (automatically determined based on CPU count)
    results = await api.get_candles_multiple_assets(
        assets=assets,
        period=60,
        duration=600,
        max_workers=None
    )
    
    # Record end time
    end_time = time.time()
    elapsed_time = end_time - start_time
    
    print(f"\nCompleted in {elapsed_time:.2f} seconds")
    print("\n" + "="*60)
    print("Results Summary:")
    print("="*60)
    
    # Process and display results
    successful = 0
    failed = 0
    
    for asset, result in results.items():
        if result['success']:
            successful += 1
            df = result['data']
            if df is not None and not df.empty:
                print(f"\n✓ {asset}: Successfully fetched {len(df)} candles")
                print(f"  Time range: {df.index[0]} to {df.index[-1]}")
                print(f"  Latest close price: {df['close'].iloc[-1]:.5f}")
            else:
                print(f"\n✓ {asset}: Completed but no data available")
        else:
            failed += 1
            print(f"\n✗ {asset}: Failed - {result['error']}")
    
    print("\n" + "="*60)
    print(f"Summary: {successful} successful, {failed} failed out of {len(assets)} assets")
    print(f"Average time per asset: {elapsed_time / len(assets):.2f} seconds")
    print("="*60)
    
    # Example: Calculate some basic statistics
    if successful > 0:
        print("\n\nBasic Statistics:")
        for asset, result in results.items():
            if result['success'] and result['data'] is not None and not result['data'].empty:
                df = result['data']
                print(f"\n{asset}:")
                print(f"  Open:  {df['open'].iloc[0]:.5f}")
                print(f"  High:  {df['high'].max():.5f}")
                print(f"  Low:   {df['low'].min():.5f}")
                print(f"  Close: {df['close'].iloc[-1]:.5f}")
    
    # Close the connection
    await api.close()
    print("\n\nConnection closed.")

if __name__ == "__main__":
    asyncio.run(main())
