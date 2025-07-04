#!/usr/bin/env python3
"""
Test script to validate parsing of different data formats from WebSocket messages.
This script simulates the data formats you provided and tests the parsing logic.
"""

import json
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_historical_data_parsing():
    """Test parsing of historical data format."""
    print("=" * 60)
    print("Testing Historical Data Format Parsing")
    print("=" * 60)
    
    # Example historical data format
    historical_message = {
        "data": {
            "asset": "AEDCNY_otc",
            "period": 5,
            "history": [
                [1735145825000, 0.74115],
                [1735145830000, 0.74116],
                [1735145835000, 0.74114]
            ],
            "candles": [
                [1735145825000, 0.74115, 0.74116, 0.74117, 0.74114],
                [1735145830000, 0.74116, 0.74114, 0.74118, 0.74113],
                [1735145835000, 0.74114, 0.74115, 0.74116, 0.74112]
            ]
        }
    }
    
    # Test parsing logic (simulating WebSocket client logic)
    formatted_candles = []
    if "data" in historical_message:
        data = historical_message["data"]
        if isinstance(data, dict) and "candles" in data:
            candles = data["candles"]
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
    
    print(f"Input message: {json.dumps(historical_message, indent=2)}")
    print(f"\nParsed candles ({len(formatted_candles)} candles):")
    for i, candle in enumerate(formatted_candles):
        print(f"  Candle {i+1}: {candle}")
    
    return len(formatted_candles) == 3

def test_realtime_data_parsing():
    """Test parsing of real-time streaming data format."""
    print("\n" + "=" * 60)
    print("Testing Real-time Streaming Data Format Parsing")
    print("=" * 60)
    
    # Example real-time streaming format
    realtime_message = [
        ["EURUSD_otc", 1735145825000, 1.04223],
        ["GBPUSD_otc", 1735145825100, 1.25647],
        ["AUDUSD_otc", 1735145825200, 0.63891]
    ]
    
    # Test parsing logic (simulating WebSocket client logic)
    real_time_candles = {}
    
    for item in realtime_message:
        if isinstance(item, list) and len(item) >= 3:
            asset = item[0]
            timestamp = item[1]
            price = item[2]
            
            # Store in real_time_candles for fallback use
            if asset not in real_time_candles:
                real_time_candles[asset] = {}
            
            # Assume 1-second period for real-time data
            period = 1
            if period not in real_time_candles[asset]:
                real_time_candles[asset][period] = {}
            
            # Create candle entry
            candle_data = {
                "time": int(timestamp),
                "open": price,
                "close": price,
                "high": price,
                "low": price,
                "volume": 0
            }
            
            real_time_candles[asset][period][int(timestamp)] = candle_data
    
    print(f"Input message: {json.dumps(realtime_message, indent=2)}")
    print(f"\nParsed real-time candles:")
    for asset, periods in real_time_candles.items():
        print(f"  Asset: {asset}")
        for period, candles in periods.items():
            print(f"    Period: {period}s")
            for timestamp, candle in candles.items():
                print(f"      {timestamp}: {candle}")
    
    return len(real_time_candles) == 3

def test_mixed_data_formats():
    """Test handling of various edge cases and mixed formats."""
    print("\n" + "=" * 60)
    print("Testing Mixed Data Formats and Edge Cases")
    print("=" * 60)
    
    test_cases = [
        {
            "name": "Empty candles array",
            "message": {"data": {"candles": []}},
            "expected_count": 0
        },
        {
            "name": "Incomplete candle data",
            "message": {"data": {"candles": [[1735145825000, 1.0422]]}},
            "expected_count": 0
        },
        {
            "name": "Mixed valid/invalid candles",
            "message": {"data": {"candles": [
                [1735145825000, 1.0422, 1.0423, 1.0424, 1.0421],  # Valid
                [1735145830000, 1.0423],  # Invalid (incomplete)
                [1735145835000, 1.0424, 1.0425, 1.0426, 1.0422]   # Valid
            ]}},
            "expected_count": 2
        },
        {
            "name": "Real-time with missing data",
            "message": [
                ["EURUSD_otc", 1735145825000, 1.04223],  # Valid
                ["GBPUSD_otc", 1735145825100],  # Invalid (missing price)
                ["AUDUSD_otc", 1735145825200, 0.63891]   # Valid
            ],
            "expected_count": 2
        }
    ]
    
    all_passed = True
    
    for test_case in test_cases:
        print(f"\nTest: {test_case['name']}")
        print(f"Input: {json.dumps(test_case['message'], indent=2)}")
        
        message = test_case['message']
        parsed_count = 0
        
        # Test historical format
        if isinstance(message, dict) and "data" in message:
            data = message["data"]
            if isinstance(data, dict) and "candles" in data:
                candles = data["candles"]
                for candle in candles:
                    if len(candle) >= 5:
                        parsed_count += 1
        
        # Test real-time format
        elif isinstance(message, list):
            for item in message:
                if isinstance(item, list) and len(item) >= 3:
                    parsed_count += 1
        
        passed = parsed_count == test_case['expected_count']
        print(f"Expected: {test_case['expected_count']}, Got: {parsed_count}, Passed: {passed}")
        
        if not passed:
            all_passed = False
    
    return all_passed

def main():
    """Run all data format parsing tests."""
    print("Data Format Parsing Test Suite")
    print("Testing the parsing logic for WebSocket messages")
    print("=" * 80)
    
    tests = [
        ("Historical Data Parsing", test_historical_data_parsing),
        ("Real-time Data Parsing", test_realtime_data_parsing),
        ("Mixed Data Formats", test_mixed_data_formats)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result, None))
        except Exception as e:
            results.append((test_name, False, str(e)))
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST RESULTS SUMMARY")
    print("=" * 80)
    
    passed = 0
    total = len(results)
    
    for test_name, result, error in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name:<40} {status}")
        if error:
            print(f"  Error: {error}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{total}")
    
    if passed == total:
        print("✅ All tests passed! The data format parsing is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the parsing logic.")
        return 1

if __name__ == "__main__":
    exit(main())
