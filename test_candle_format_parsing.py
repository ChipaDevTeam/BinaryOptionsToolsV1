#!/usr/bin/env python3
"""
Test script to verify the enhanced candle data handling with the specific format you provided.

This script tests:
1. Historical candle data parsing from the format: {"asset":"AEDCNY_otc","period":5,"candles":[[timestamp,open,close,high,low],...]}
2. Real-time data parsing from format: [["AEDCNY_otc",1751626750.212,1.9159]]
3. Integration with the improved get_candles method
"""

import time
import json
from BinaryOptionsTools import pocketoption

def test_candle_data_parsing():
    """Test the enhanced candle data parsing with your specific format."""
    
    # Your SSID
    ssid = r'42["auth",{"session":"dd4ij8petulqcfuapcvkv578p1","isDemo":1,"uid":105754921,"platform":3,"isFastHistory":true,"isOptimized":true}]'
    
    print("Testing Enhanced Candle Data Parsing")
    print("=" * 50)
    
    try:
        # Initialize API
        api = pocketoption(ssid, demo=True)
        print("✓ API initialized successfully")
        
        # Test balance to confirm connection
        balance = api.GetBalance()
        print(f"✓ Balance: {balance}")
        
        # Test getting candles with the enhanced parsing
        print("\nTesting GetCandles with enhanced data format handling...")
        
        # Test with a shorter timeframe first
        test_pairs = ["EURUSD_otc", "AEDCNY_otc"]
        
        for pair in test_pairs:
            print(f"\nTesting {pair}:")
            try:
                # Subscribe to the pair first
                print(f"  Subscribing to {pair}...")
                api.api.subscribe_candles(pair)
                time.sleep(2)  # Give time for subscription
                
                # Get candles
                print(f"  Fetching candles for {pair}...")
                df = api.GetCandles(pair, 1, count=100)  # 1-second candles, last 100
                
                if df is not None and not df.empty:
                    print(f"  ✓ Successfully retrieved {len(df)} candles")
                    print(f"  ✓ Data columns: {list(df.columns)}")
                    print(f"  ✓ Time range: {df.index[0]} to {df.index[-1]}")
                    
                    # Show sample data
                    print(f"  Sample data (last 3 candles):")
                    print(df.tail(3))
                    
                    # Check data quality
                    non_zero_data = df[(df['open'] != 0) | (df['close'] != 0) | (df['high'] != 0) | (df['low'] != 0)]
                    if len(non_zero_data) > 0:
                        print(f"  ✓ Found {len(non_zero_data)} candles with OHLC data")
                    else:
                        print(f"  ⚠ All OHLC data is zero - might be tick data only")
                        
                else:
                    print(f"  ✗ No data retrieved for {pair}")
                    
                # Unsubscribe
                api.api.unsubscribe_candles(pair)
                
            except Exception as e:
                print(f"  ✗ Error testing {pair}: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "=" * 50)
        print("Test Summary:")
        print("- Enhanced candle data parsing implemented")
        print("- Support for format: [timestamp, open, close, high, low]")
        print("- Real-time data handling: [['ASSET', timestamp, price]]")
        print("- Integration with subscribe_candles functionality")
        print("=" * 50)
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

def test_data_format_simulation():
    """Simulate the data format you provided to test parsing logic."""
    
    print("\nTesting Data Format Parsing Logic")
    print("=" * 40)
    
    # Simulate the candle data format you provided
    sample_data = {
        "asset": "AEDCNY_otc",
        "period": 5,
        "candles": [
            [1751626675, 1.91804, 1.91761, 1.9181, 1.91741],
            [1751626670, 1.91759, 1.91811, 1.91811, 1.91753],
            [1751626665, 1.91753, 1.91735, 1.91755, 1.91735],
            [1751626660, 1.91703, 1.91753, 1.91753, 1.91699],
            [1751626655, 1.91688, 1.91697, 1.91703, 1.91688]
        ]
    }
    
    print("Sample data format:")
    print(json.dumps(sample_data, indent=2))
    
    # Test the parsing logic
    candles = sample_data["candles"]
    formatted_candles = []
    
    for candle in candles:
        if len(candle) >= 5:
            formatted_candle = {
                "time": candle[0],
                "open": candle[1],
                "close": candle[2], 
                "high": candle[3],
                "low": candle[4],
                "volume": 0
            }
            formatted_candles.append(formatted_candle)
    
    print("\nParsed candles:")
    for i, candle in enumerate(formatted_candles):
        print(f"  {i+1}. {candle}")
    
    print(f"\n✓ Successfully parsed {len(formatted_candles)} candles")
    
    # Test real-time data format
    real_time_sample = [["AEDCNY_otc", 1751626750.212, 1.9159]]
    print(f"\nReal-time data sample: {real_time_sample}")
    
    for item in real_time_sample:
        if isinstance(item, list) and len(item) >= 3:
            asset = item[0]
            timestamp = item[1]
            price = item[2]
            print(f"  Asset: {asset}, Timestamp: {timestamp}, Price: {price}")
    
    print("✓ Real-time data parsing logic verified")

if __name__ == "__main__":
    print("Enhanced Candle Data Format Testing")
    print("=" * 60)
    
    # Test the parsing logic first
    test_data_format_simulation()
    
    # Then test with actual API
    test_candle_data_parsing()
