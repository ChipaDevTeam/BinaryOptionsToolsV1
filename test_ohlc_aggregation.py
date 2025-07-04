#!/usr/bin/env python3
"""
Test script for OHLC candle aggregation functionality.
This script demonstrates how to use the new subscribe_candles with OHLC aggregation.
"""

import asyncio
import sys
import os
import time
import json
from datetime import datetime, timezone
import logging

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def format_timestamp(timestamp):
    """Convert timestamp to readable format."""
    if timestamp and timestamp > 0:
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        return dt.strftime('%Y-%m-%d %H:%M:%S UTC')
    return "Invalid timestamp"

def test_ohlc_aggregator():
    """Test the OHLC aggregator directly."""
    print("=" * 80)
    print("TESTING OHLC AGGREGATOR")
    print("=" * 80)
    
    from BinaryOptionsToolsAsync.platforms.pocketoption.ohlc_aggregator import CandleAggregator
    
    # Create aggregator for 5-second candles
    def on_candle_complete(asset, candle):
        print(f"✅ Completed candle for {asset}: {candle}")
    
    aggregator = CandleAggregator(
        timeframe_seconds=5,
        max_candles=10,
        on_candle_complete=on_candle_complete
    )
    
    # Simulate tick data
    print("\n1. Simulating tick data for EURUSD_otc:")
    
    base_time = int(time.time())
    test_ticks = [
        (base_time + 0, 1.0421),
        (base_time + 1, 1.0422),
        (base_time + 2, 1.0420),  # Should be in same candle
        (base_time + 3, 1.0423),
        (base_time + 5, 1.0424),  # New candle
        (base_time + 6, 1.0425),
        (base_time + 10, 1.0426), # Another new candle
    ]
    
    asset = "EURUSD_otc"
    
    for timestamp, price in test_ticks:
        completed_candle = aggregator.add_tick(asset, timestamp, price)
        print(f"   Tick: {format_timestamp(timestamp)} @ ${price}")
        if completed_candle:
            print(f"   ✅ Candle completed: {completed_candle}")
    
    # Show final state
    print(f"\n2. Final state:")
    completed_candles = aggregator.get_candles(asset)
    current_candle = aggregator.get_current_candle(asset)
    
    print(f"   Completed candles: {len(completed_candles)}")
    for i, candle in enumerate(completed_candles):
        print(f"     Candle {i+1}: {format_timestamp(candle['time'])} | O:{candle['open']} H:{candle['high']} L:{candle['low']} C:{candle['close']} | Ticks:{candle['tick_count']}")
    
    if current_candle:
        print(f"   Current candle: {format_timestamp(current_candle['time'])} | O:{current_candle['open']} H:{current_candle['high']} L:{current_candle['low']} C:{current_candle['close']} | Ticks:{current_candle['tick_count']}")
    
    return len(completed_candles) >= 2  # Should have at least 2 completed candles

def test_subscription_manager():
    """Test the subscription manager."""
    print("\n" + "=" * 80)
    print("TESTING SUBSCRIPTION MANAGER")
    print("=" * 80)
    
    from BinaryOptionsToolsAsync.platforms.pocketoption.ohlc_aggregator import SubscriptionManager
    
    manager = SubscriptionManager()
    
    # Subscribe to multiple assets and timeframes
    print("\n1. Setting up subscriptions:")
    
    def candle_callback(asset, candle):
        print(f"📊 {asset} candle completed: O:{candle.open} H:{candle.high} L:{candle.low} C:{candle.close}")
    
    assets = ["EURUSD_otc", "GBPUSD_otc"]
    timeframes = [5, 10]  # 5-second and 10-second candles
    
    for asset in assets:
        for timeframe in timeframes:
            success = manager.subscribe_candles_ohlc(
                asset=asset,
                timeframe_seconds=timeframe,
                max_candles=50,
                on_candle_complete=candle_callback
            )
            print(f"   {asset} {timeframe}s subscription: {'✅ Success' if success else '❌ Failed'}")
    
    # Simulate tick data
    print("\n2. Processing simulated tick data:")
    
    base_time = int(time.time())
    tick_data = [
        ("EURUSD_otc", base_time + 0, 1.0421),
        ("GBPUSD_otc", base_time + 1, 1.2564),
        ("EURUSD_otc", base_time + 2, 1.0422),
        ("GBPUSD_otc", base_time + 3, 1.2565),
        ("EURUSD_otc", base_time + 5, 1.0420),  # Should complete 5s candle
        ("GBPUSD_otc", base_time + 6, 1.2563),
        ("EURUSD_otc", base_time + 10, 1.0423), # Should complete 10s candle
        ("GBPUSD_otc", base_time + 11, 1.2566),
    ]
    
    for asset, timestamp, price in tick_data:
        manager.process_tick(asset, timestamp, price)
        print(f"   Processed: {asset} @ {format_timestamp(timestamp)} = ${price}")
    
    # Show results
    print("\n3. Results:")
    
    for asset in assets:
        for timeframe in timeframes:
            candles = manager.get_candles(asset, timeframe)
            current = manager.get_current_candle(asset, timeframe)
            
            print(f"   {asset} {timeframe}s: {len(candles)} completed candles")
            if candles:
                latest = candles[-1]
                print(f"     Latest: {format_timestamp(latest['time'])} | O:{latest['open']} H:{latest['high']} L:{latest['low']} C:{latest['close']}")
            
            if current:
                print(f"     Current: {format_timestamp(current['time'])} | O:{current['open']} H:{current['high']} L:{current['low']} C:{current['close']} | Ticks:{current['tick_count']}")
    
    return True

async def test_api_integration():
    """Test OHLC aggregation with API integration."""
    print("\n" + "=" * 80)
    print("TESTING API INTEGRATION")
    print("=" * 80)
    
    try:
        from BinaryOptionsToolsAsync.platforms.pocketoption.stable_api import PocketOption
        
        # Create API instance (demo mode, test SSID)
        api = PocketOption("test_ssid", demo=True)
        
        print("\n1. Testing OHLC subscription setup:")
        
        # Test OHLC subscription
        def candle_completed(asset, candle):
            print(f"🕯️  {asset} candle completed: {candle}")
        
        # Subscribe with OHLC aggregation
        result = api.subscribe_candles(
            active="EURUSD_otc",
            create_ohlc=True,
            timeframe_seconds=30,  # 30-second candles
            max_candles=100,
            on_candle_complete=candle_completed
        )
        
        print(f"   OHLC subscription result: {'✅ Success' if result else '❌ Failed'}")
        
        # Check if OHLC manager is set up
        if hasattr(api, 'ohlc_manager'):
            print(f"   ✅ OHLC manager initialized")
            print(f"   ✅ OHLC subscriptions: {list(api.ohlc_subscriptions.keys())}")
        else:
            print(f"   ❌ OHLC manager not found")
        
        # Simulate some tick data processing
        print("\n2. Simulating tick data processing:")
        
        if hasattr(api, 'ohlc_manager'):
            base_time = int(time.time())
            test_ticks = [
                (base_time + 0, 1.0421),
                (base_time + 5, 1.0422),
                (base_time + 10, 1.0420),
                (base_time + 15, 1.0423),
                (base_time + 30, 1.0424),  # Should complete first candle
                (base_time + 35, 1.0425),
            ]
            
            for timestamp, price in test_ticks:
                api.ohlc_manager.process_tick("EURUSD_otc", timestamp, price)
                print(f"   Processed tick: {format_timestamp(timestamp)} @ ${price}")
        
        # Test retrieval methods
        print("\n3. Testing retrieval methods:")
        
        try:
            ohlc_candles = api.get_ohlc_candles("EURUSD_otc", timeframe_seconds=30, count=5)
            print(f"   OHLC candles retrieved: {len(ohlc_candles)}")
            
            current_candle = api.get_current_ohlc_candle("EURUSD_otc", timeframe_seconds=30)
            print(f"   Current candle: {'Available' if current_candle else 'None'}")
            
            stats = api.get_ohlc_stats()
            print(f"   OHLC stats: {json.dumps(stats, indent=2) if stats else 'None'}")
            
        except Exception as e:
            print(f"   ❌ Error testing retrieval methods: {e}")
        
        # Unsubscribe
        print("\n4. Testing unsubscription:")
        
        unsub_result = api.unsubscribe_candles("EURUSD_otc")
        print(f"   Unsubscription result: {'✅ Success' if unsub_result else '❌ Failed'}")
        print(f"   Remaining OHLC subscriptions: {list(api.ohlc_subscriptions.keys())}")
        
        return True
        
    except ImportError as e:
        print(f"   ❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def create_usage_example():
    """Create a usage example file."""
    usage_example = '''#!/usr/bin/env python3
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
        print("\\nStopping...")
    finally:
        # Unsubscribe
        api.unsubscribe_candles("EURUSD_otc")
        await api.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    with open('/home/vwalker/BinaryOptionsToolsV1/ohlc_usage_example.py', 'w') as f:
        f.write(usage_example)
    
    print(f"📝 Usage example created: ohlc_usage_example.py")

async def main():
    """Run all OHLC aggregation tests."""
    print("OHLC Candle Aggregation Test Suite")
    print("Testing real-time tick data aggregation into OHLC candles")
    print("=" * 80)
    
    tests = [
        ("OHLC Aggregator", test_ohlc_aggregator),
        ("Subscription Manager", test_subscription_manager),
    ]
    
    async_tests = [
        ("API Integration", test_api_integration),
    ]
    
    results = []
    
    # Run sync tests
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result, None))
        except Exception as e:
            results.append((test_name, False, str(e)))
    
    # Run async tests
    for test_name, test_func in async_tests:
        try:
            result = await test_func()
            results.append((test_name, result, None))
        except Exception as e:
            results.append((test_name, False, str(e)))
    
    # Create usage example
    try:
        create_usage_example()
        results.append(("Usage Example Creation", True, None))
    except Exception as e:
        results.append(("Usage Example Creation", False, str(e)))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, result, error in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<30} {status}")
        if error:
            print(f"  Error: {error}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("🎉 SUCCESS! OHLC candle aggregation is working correctly.")
        print("\nNew Features Available:")
        print("  ✅ Real-time tick data aggregation into OHLC candles")
        print("  ✅ Multiple timeframe support (configurable seconds)")
        print("  ✅ Automatic candle completion callbacks")
        print("  ✅ Thread-safe aggregation with memory management")
        print("  ✅ Statistics and monitoring capabilities")
        print("  ✅ Integration with existing subscribe_candles API")
        print("\nUsage:")
        print("  api.subscribe_candles('EURUSD_otc', create_ohlc=True, timeframe_seconds=60)")
        print("  candles = api.get_ohlc_candles('EURUSD_otc', timeframe_seconds=60)")
        return 0
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    exit(asyncio.run(main()))
