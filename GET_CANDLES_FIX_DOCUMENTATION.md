# Get Candles Fix Using Subscribe Candles

## Overview

This document outlines the improvements made to the `get_candles` method in both the sync and async versions of the PocketOption API to leverage the `subscribe_candles` functionality for better reliability and performance.

## Problem Statement

The original `get_candles` method had several issues:

1. **Poor reliability**: The method relied on a simple timeout mechanism that often failed
2. **Limited retry logic**: No proper retry mechanism for failed requests
3. **No subscription utilization**: Didn't use the available candle subscription functionality
4. **Poor error handling**: Limited error handling and no cleanup mechanisms
5. **Data validation issues**: No duplicate removal or data validation

## Solution

The improved `get_candles` method now includes:

### Key Improvements

1. **Candle Subscription Integration**
   - Automatically subscribes to candle data at the beginning of the process
   - Uses real-time candle data as a fallback when historical data fails
   - Properly unsubscribes at the end to clean up resources

2. **Enhanced Retry Logic**
   - Implements a proper retry mechanism with exponential backoff
   - Configurable maximum retries (default: 3)
   - Progressive delay between retries

3. **Improved Timeout Handling**
   - Increased timeout from 10 seconds to 15 seconds for better reliability
   - Checks for real-time candle data during timeout periods
   - Better timeout counter implementation

4. **Data Quality Improvements**
   - Duplicate removal based on timestamp
   - Data validation and required column checks
   - Proper error handling for empty datasets

5. **Better Logging and Error Handling**
   - Comprehensive logging for debugging (async version)
   - Proper exception handling with cleanup
   - Graceful fallback mechanisms

## Technical Details

### Files Modified

1. `/BinaryOptionsToolsAsync/platforms/pocketoption/stable_api.py`
2. `/BinaryOptionsTools/platforms/pocketoption/stable_api.py`

### Method Signature

```python
def get_candles(self, active, period, start_time=None, count=6000, count_request=1):
```

### New Flow

1. **Subscribe to Candles**: Uses `self.subscribe_candles(active)` to start receiving real-time data
2. **Historical Data Request**: Makes the traditional historical data request
3. **Smart Waiting**: Waits for either historical data or uses real-time data as fallback
4. **Retry Logic**: Implements retry mechanism for failed requests
5. **Data Processing**: Removes duplicates, validates data, and creates DataFrame
6. **Cleanup**: Unsubscribes from candles to prevent resource leaks

### Real-time Data Fallback

When historical data fails, the method now checks for real-time candle data:

```python
if (active in self.api.real_time_candles and 
    period in self.api.real_time_candles[active] and
    len(self.api.real_time_candles[active][period]) > 0):
    # Use real-time data as fallback
```

### Error Handling

The method now includes comprehensive error handling:

- Connection errors
- Timeout errors  
- Data parsing errors
- Subscription errors
- Cleanup on failure

## Benefits

1. **Higher Success Rate**: Better reliability through subscription and retry mechanisms
2. **Faster Recovery**: Real-time data fallback reduces failed requests
3. **Better Resource Management**: Proper subscription cleanup
4. **Improved Data Quality**: Duplicate removal and validation
5. **Enhanced Debugging**: Better logging and error messages

## Usage

The public API remains unchanged, so existing code continues to work:

```python
# Async version
from BinaryOptionsToolsAsync import pocketoption
api = pocketoption("email", "password")
candles = api.GetCandles("EURUSD_otc", 60, count=3600)

# Sync version  
from BinaryOptionsTools import pocketoption
api = pocketoption("email", "password")
candles = api.GetCandles("EURUSD_otc", 60, count=3600)
```

## Testing

A test script has been created (`test_get_candles_fix.py`) to validate the improvements:

- Tests subscription functionality
- Validates data retrieval
- Checks error handling
- Verifies cleanup mechanisms

## Backwards Compatibility

All changes are backwards compatible. The method signature and return values remain the same, ensuring existing code continues to work without modifications.

## Configuration

The following parameters can be adjusted in the code:

- `max_retries`: Number of retry attempts (default: 3)
- `retry_delay`: Delay between retries (default: 0.5 seconds)
- `max_timeout`: Maximum timeout for data waiting (default: 150 iterations = 15 seconds)

## Notes

- The subscription functionality requires an active WebSocket connection
- Real-time data availability depends on the broker's data feed
- The method automatically handles cleanup even if errors occur
- Logging level can be adjusted for debugging purposes

## Enhanced WebSocket Data Format Support

### Version 1.2 - Enhanced Data Format Parsing

The WebSocket clients have been enhanced to support the new data formats from PocketOption's API:

#### Supported Data Formats

1. **Historical Data Format (get_history response):**
```json
{
  "asset": "AEDCNY_otc",
  "period": 5,
  "history": [[timestamp, price], ...],
  "candles": [[timestamp, open, close, high, low], ...]
}
```

2. **Real-time Streaming Format:**
```json
[["ASSET", timestamp, price], ...]
```

#### Enhanced Features

- **Robust Type Conversion**: Automatic conversion of timestamp, price, and OHLC values to appropriate types
- **Data Validation**: Skips incomplete or malformed candle data automatically
- **Enhanced Logging**: Detailed logging for debugging and monitoring data parsing
- **Fallback Mechanisms**: Multiple parsing strategies for different data formats
- **Error Handling**: Graceful handling of invalid data without breaking the connection

#### Parsing Logic

The WebSocket clients now automatically:
- Detect historical data format by checking for `"data"` and `"candles"` keys
- Parse candle arrays in format `[timestamp, open, close, high, low]`
- Convert to standardized OHLC format with volume set to 0
- Store real-time streaming data for fallback use in `real_time_candles`
- Log parsing progress and any issues for debugging

#### Backward Compatibility

All existing functionality remains unchanged. The enhanced parsing is additive and maintains full backward compatibility with existing code.
