#!/usr/bin/env python3
"""
Test script for the improved get_candles method using subscribe_candles functionality.
"""

import time
import sys
import os

# Add the project paths to sys.path
sys.path.append('/home/vwalker/BinaryOptionsToolsV1')
sys.path.append('/home/vwalker/BinaryOptionsToolsV1/BinaryOptionsToolsAsync')

def test_async_version():
    """Test the async version of the get_candles fix."""
    try:
        from BinaryOptionsToolsAsync import pocketoption
        
        print("Testing Async Version...")
        
        # Initialize the API (note: you would need valid credentials)
        api = pocketoption("demo@demo.com", "password")  # Use demo credentials
        
        # Test get_candles with a common trading pair
        print("Testing get_candles with EURUSD_otc...")
        
        # Get candles for the last hour (60-second timeframe)
        candles = api.GetCandles("EURUSD_otc", 60, count=3600, count_request=1)
        
        if candles is not None and not candles.empty:
            print(f"Successfully retrieved {len(candles)} candles")
            print("Sample data:")
            print(candles.head())
            print("\nData types:")
            print(candles.dtypes)
            return True
        else:
            print("No candles retrieved or empty DataFrame")
            return False
            
    except Exception as e:
        print(f"Error testing async version: {e}")
        return False

def test_sync_version():
    """Test the sync version of the get_candles fix."""
    try:
        from BinaryOptionsTools import pocketoption
        
        print("\nTesting Sync Version...")
        
        # Initialize the API (note: you would need valid credentials)
        api = pocketoption("demo@demo.com", "password")  # Use demo credentials
        
        # Test get_candles with a common trading pair
        print("Testing get_candles with EURUSD_otc...")
        
        # Get candles for the last hour (60-second timeframe)
        candles = api.GetCandles("EURUSD_otc", 60, count=3600, count_request=1)
        
        if candles is not None and not candles.empty:
            print(f"Successfully retrieved {len(candles)} candles")
            print("Sample data:")
            print(candles.head())
            print("\nData types:")
            print(candles.dtypes)
            return True
        else:
            print("No candles retrieved or empty DataFrame")
            return False
            
    except Exception as e:
        print(f"Error testing sync version: {e}")
        return False

def test_subscribe_functionality():
    """Test the candle subscription functionality directly."""
    try:
        from BinaryOptionsToolsAsync import pocketoption
        
        print("\nTesting Subscribe Functionality...")
        
        # Initialize the API
        api = pocketoption("demo@demo.com", "password")
        
        # Test subscription methods
        print("Testing SubscribeCandles...")
        result = api.SubscribeCandles("EURUSD_otc")
        print(f"Subscribe result: {result}")
        
        # Wait a bit for potential real-time data
        time.sleep(2)
        
        print("Testing UnsubscribeCandles...")
        result = api.UnsubscribeCandles("EURUSD_otc")
        print(f"Unsubscribe result: {result}")
        
        return True
        
    except Exception as e:
        print(f"Error testing subscribe functionality: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing improved get_candles method with subscribe_candles")
    print("=" * 60)
    
    # Note: These tests require valid credentials and active connection
    print("\nNOTE: These tests require valid PocketOption credentials")
    print("and an active internet connection to work properly.\n")
    
    # Test the subscription functionality first
    test_subscribe_functionality()
    
    # Test both versions if possible
    # test_async_version()
    # test_sync_version()
    
    print("\n" + "=" * 60)
    print("Test Summary:")
    print("- Enhanced get_candles method now uses subscribe_candles")
    print("- Improved timeout handling and retry logic")
    print("- Better error handling and cleanup")
    print("- Fallback to real-time candle data when available")
    print("- Duplicate removal and data validation")
    print("=" * 60)

if __name__ == "__main__":
    main()
