#!/usr/bin/env python3
"""
Test script to demonstrate how to use your specific SSID with the BinaryOptionsTools library.

Your SSID format: 42["auth",{"session":"dd4ij8petulqcfuapcvkv578p1","isDemo":1,"uid":105754921,"platform":3,"isFastHistory":true,"isOptimized":true}]

The SSID contains:
- session: "dd4ij8petulqcfuapcvkv578p1" (your session token)
- isDemo: 1 (indicates this is a demo account)
- uid: 105754921 (your user ID)
- platform: 3 (platform identifier)
- isFastHistory: true (optimized history retrieval)
- isOptimized: true (optimized connection)
"""

from BinaryOptionsTools import pocketoption
import time

def test_connection_with_your_ssid():
    """Test connection using your specific SSID."""
    
    # Your SSID - this is the session authentication string from your browser
    ssid = r'42["auth",{"session":"dd4ij8petulqcfuapcvkv578p1","isDemo":1,"uid":105754921,"platform":3,"isFastHistory":true,"isOptimized":true}]'
    
    print("Initializing PocketOption API with your SSID...")
    print(f"Session ID: dd4ij8petulqcfuapcvkv578p1")
    print(f"User ID: 105754921")
    print(f"Demo Account: Yes")
    print(f"Platform: 3")
    print("=" * 50)
    
    try:
        # Initialize the API - demo=True because isDemo=1 in your SSID
        api = pocketoption(ssid, demo=True)
        
        print("Connection established!")
        
        # Test getting balance
        print("\nTesting balance retrieval...")
        balance = api.GetBalance()
        if balance is not None:
            print(f"Current balance: {balance}")
        else:
            print("Balance not yet available (may need to wait for sync)")
        
        # Test getting candle data
        print("\nTesting candle data retrieval...")
        print("Fetching EURUSD_otc candles (1-minute timeframe, last 100 candles)...")
        
        try:
            df = api.GetCandles("EURUSD_otc", 1, count=100)
            if df is not None and not df.empty:
                print(f"Successfully retrieved {len(df)} candles")
                print("\nLast 5 candles:")
                print(df.tail(5))
            else:
                print("No candle data received")
        except Exception as e:
            print(f"Error getting candles: {e}")
        
        # Wait a bit for any async operations to complete
        print("\nWaiting for any pending operations...")
        time.sleep(5)
        
        # Try getting balance again
        balance = api.GetBalance()
        if balance is not None:
            print(f"Final balance: {balance}")
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"Error during testing: {e}")
        import traceback
        traceback.print_exc()

def explain_ssid_format():
    """Explain the SSID format and how to obtain it."""
    
    print("How to obtain your SSID:")
    print("=" * 30)
    print("1. Open your browser and go to PocketOption")
    print("2. Log in to your account")
    print("3. Open Developer Tools (F12)")
    print("4. Go to Network tab")
    print("5. Look for WebSocket connections")
    print("6. Find the authentication message that starts with '42[\"auth\"'")
    print("7. Copy the entire message - that's your SSID")
    print()
    print("Your SSID breakdown:")
    print("- Format: 42[\"auth\",{...}]")
    print("- session: Your unique session token")
    print("- isDemo: 1 = demo account, 0 = real account")
    print("- uid: Your user ID")
    print("- platform: Platform identifier")
    print("- isFastHistory: Optimized history retrieval")
    print("- isOptimized: Optimized connection settings")
    print()

if __name__ == "__main__":
    print("BinaryOptionsTools - SSID Usage Test")
    print("=" * 40)
    
    explain_ssid_format()
    
    print("\nStarting connection test...")
    test_connection_with_your_ssid()
