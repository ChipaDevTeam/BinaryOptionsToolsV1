#!/usr/bin/env python3
"""
Example script demonstrating multiprocessing support for fetching candles from multiple assets.

This example shows how to use the get_candles_multiple_assets method to fetch
historical candle data for multiple trading pairs in parallel using multiprocessing.
"""

import time
import logging
from BinaryOptionsTools import pocketoption

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def main():
    # Get SSID from user
    ssid = input("Enter your ssid: ")
    
    # Initialize API in demo mode
    print("Initializing PocketOption API...")
    api = pocketoption(ssid, demo=True)
    
    # Define multiple assets to fetch data for
    assets = [
        "EURUSD_otc",
        "GBPUSD_otc",
        "USDJPY_otc",
        "AUDUSD_otc",
        "USDCAD_otc"
    ]
    
    print(f"\nFetching candles for {len(assets)} assets in parallel...")
    print(f"Assets: {', '.join(assets)}")
    
    # Record start time
    start_time = time.time()
    
    # Fetch candles for multiple assets using multiprocessing
    # Parameters:
    # - assets: List of asset symbols
    # - period: 60 seconds (1 minute candles)
    # - count: 3600 seconds (1 hour of data)
    # - count_request: 1 (single request per asset)
    # - max_workers: None (automatically determined based on CPU count)
    results = api.GetCandlesMultipleAssets(
        assets=assets,
        period=60,
        count=3600,
        count_request=1,
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
                print(f"  Sample data (last 3 candles):")
                print(df.tail(3))
            else:
                print(f"\n✓ {asset}: Completed but no data available")
        else:
            failed += 1
            print(f"\n✗ {asset}: Failed - {result['error']}")
    
    print("\n" + "="*60)
    print(f"Summary: {successful} successful, {failed} failed out of {len(assets)} assets")
    print(f"Average time per asset: {elapsed_time / len(assets):.2f} seconds")
    print("="*60)
    
    # Example: Compare with sequential fetching
    print("\n\nFor comparison, sequential fetching would take:")
    print(f"Estimated time: ~{elapsed_time * len(assets):.2f} seconds")
    print(f"Time saved with multiprocessing: ~{elapsed_time * (len(assets) - 1):.2f} seconds")

if __name__ == "__main__":
    main()
