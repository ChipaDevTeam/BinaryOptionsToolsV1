# OHLC Candle Aggregation Feature

## Overview

The OHLC (Open, High, Low, Close) candle aggregation feature allows you to automatically aggregate real-time tick data into time-based OHLC candles. Instead of receiving every individual price tick, you can now receive properly formatted candles at your desired timeframe.

## Features

- **Real-time Aggregation**: Converts streaming tick data into OHLC candles
- **Multiple Timeframes**: Support for any timeframe in seconds (1s, 5s, 60s, 300s, etc.)
- **Thread-safe**: Safe for concurrent use in multi-threaded applications
- **Memory Management**: Configurable maximum candle count to prevent memory issues
- **Callbacks**: Optional callback functions when candles complete
- **Statistics**: Built-in monitoring and statistics
- **Both Async/Sync**: Available in both async and synchronous versions

## Basic Usage

### Simple OHLC Subscription

```python
import asyncio
from BinaryOptionsToolsAsync.platforms.pocketoption.stable_api import PocketOption

async def main():
    api = PocketOption("your_ssid", demo=True)
    await api.connect()
    
    # Subscribe with OHLC aggregation enabled
    api.subscribe_candles(
        active="EURUSD_otc",
        create_ohlc=True,           # Enable OHLC aggregation
        timeframe_seconds=60        # 1-minute candles
    )
    
    # Wait a bit for data to accumulate
    await asyncio.sleep(120)
    
    # Get completed candles
    candles = api.get_ohlc_candles("EURUSD_otc", timeframe_seconds=60, count=5)
    print(f"Latest 5 candles: {candles}")
    
    # Get current incomplete candle
    current = api.get_current_ohlc_candle("EURUSD_otc", timeframe_seconds=60)
    if current:
        print(f"Current candle: O:{current['open']} H:{current['high']} L:{current['low']} C:{current['close']}")

if __name__ == "__main__":
    asyncio.run(main())
```

### With Completion Callback

```python
def on_candle_complete(asset, candle):
    """Called when a candle is completed."""
    print(f"🕯️ {asset} candle completed:")
    print(f"   Time: {candle.timestamp}")
    print(f"   OHLC: {candle.open}, {candle.high}, {candle.low}, {candle.close}")
    print(f"   Ticks: {candle.tick_count}")

# Subscribe with callback
api.subscribe_candles(
    active="EURUSD_otc",
    create_ohlc=True,
    timeframe_seconds=60,
    max_candles=1000,
    on_candle_complete=on_candle_complete
)
```

## API Reference

### Enhanced subscribe_candles Method

```python
def subscribe_candles(self, active, create_ohlc=False, timeframe_seconds=60, 
                     max_candles=1000, on_candle_complete=None)
```

**Parameters:**
- `active` (str): Trading pair (e.g., "EURUSD_otc")
- `create_ohlc` (bool): Enable OHLC aggregation (default: False)
- `timeframe_seconds` (int): Candle timeframe in seconds (default: 60)
- `max_candles` (int): Maximum candles to keep in memory (default: 1000)
- `on_candle_complete` (callable): Callback for completed candles (optional)

**Returns:** Result of subscription request

### New OHLC Methods

#### get_ohlc_candles()
```python
def get_ohlc_candles(self, active, timeframe_seconds=60, count=None)
```
Get completed OHLC candles for a trading pair.

**Parameters:**
- `active` (str): Trading pair
- `timeframe_seconds` (int): Timeframe in seconds
- `count` (int): Number of candles to return (None for all)

**Returns:** List of candle dictionaries

#### get_current_ohlc_candle()
```python
def get_current_ohlc_candle(self, active, timeframe_seconds=60)
```
Get the current incomplete candle.

**Returns:** Current candle dictionary or None

#### get_ohlc_stats()
```python
def get_ohlc_stats(self)
```
Get aggregation statistics.

**Returns:** Dictionary with statistics for all timeframes

## Candle Data Format

Each candle is returned as a dictionary with the following structure:

```python
{
    "time": 1751620825,      # Unix timestamp (candle start time)
    "open": 1.0421,          # Opening price
    "high": 1.0423,          # Highest price
    "low": 1.0420,           # Lowest price
    "close": 1.0422,         # Closing price
    "volume": 0,             # Volume (always 0 for tick data)
    "tick_count": 15         # Number of ticks in this candle
}
```

## Advanced Usage

### Multiple Timeframes

```python
# Subscribe to multiple timeframes for the same asset
assets_timeframes = [
    ("EURUSD_otc", 60),    # 1-minute candles
    ("EURUSD_otc", 300),   # 5-minute candles
    ("GBPUSD_otc", 60),    # 1-minute candles
]

for asset, timeframe in assets_timeframes:
    api.subscribe_candles(
        active=asset,
        create_ohlc=True,
        timeframe_seconds=timeframe,
        max_candles=500
    )
```

### Monitoring and Statistics

```python
# Get aggregation statistics
stats = api.get_ohlc_stats()
print("OHLC Aggregation Statistics:")
for timeframe, data in stats.items():
    print(f"  {timeframe}:")
    print(f"    Assets: {data['assets_count']}")
    for asset, asset_stats in data['assets'].items():
        print(f"    {asset}: {asset_stats['completed_candles']} completed, "
              f"Current ticks: {asset_stats['current_candle_ticks']}")
```

### Real-time Processing with Callback

```python
class CandleProcessor:
    def __init__(self):
        self.candles = {}
    
    def on_candle_complete(self, asset, candle):
        """Process completed candles."""
        if asset not in self.candles:
            self.candles[asset] = []
        
        candle_data = candle.to_dict()
        self.candles[asset].append(candle_data)
        
        # Your analysis logic here
        self.analyze_candle(asset, candle_data)
    
    def analyze_candle(self, asset, candle):
        """Analyze the completed candle."""
        price_change = candle['close'] - candle['open']
        print(f"{asset}: Price change: {price_change:.5f}")
        
        if len(self.candles[asset]) >= 2:
            prev_candle = self.candles[asset][-2]
            trend = "UP" if candle['close'] > prev_candle['close'] else "DOWN"
            print(f"{asset}: Trend: {trend}")

# Usage
processor = CandleProcessor()
api.subscribe_candles(
    active="EURUSD_otc",
    create_ohlc=True,
    timeframe_seconds=60,
    on_candle_complete=processor.on_candle_complete
)
```

## Synchronous Version

The same functionality is available in the synchronous version:

```python
from BinaryOptionsTools.platforms.pocketoption.stable_api import PocketOption

# Synchronous usage (same API)
api = PocketOption("your_ssid", demo=True)
api.connect()

api.subscribe_candles("EURUSD_otc", create_ohlc=True, timeframe_seconds=60)
# ... rest is the same
```

## Performance Considerations

- **Memory Usage**: Set appropriate `max_candles` to limit memory consumption
- **Timeframes**: Shorter timeframes generate more candles and use more memory
- **Callbacks**: Keep callback functions lightweight to avoid blocking
- **Thread Safety**: All operations are thread-safe and can be used concurrently

## Error Handling

The OHLC aggregation system includes robust error handling:

```python
try:
    # Subscribe with OHLC
    result = api.subscribe_candles("EURUSD_otc", create_ohlc=True)
    if not result:
        print("Subscription failed")
    
    # Get candles with error handling
    candles = api.get_ohlc_candles("EURUSD_otc", timeframe_seconds=60)
    if not candles:
        print("No candles available yet")
    
except Exception as e:
    print(f"Error: {e}")
```

## Troubleshooting

### Common Issues

1. **No candles appearing**: Make sure `create_ohlc=True` and tick data is being received
2. **Memory usage**: Reduce `max_candles` if memory is a concern
3. **Callback errors**: Ensure callback functions don't raise exceptions
4. **Timeframe alignment**: Candles align to timeframe boundaries (e.g., 60s candles start at :00 seconds)

### Debug Information

Enable debug logging to see aggregation details:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Debug output will show:
# - Tick processing
# - Candle completion
# - Subscription status
```

## Examples

See the following example files:
- `test_ohlc_aggregation.py` - Comprehensive test suite
- `ohlc_usage_example.py` - Basic usage example
- `final_data_format_validation.py` - Data format validation

## Integration with Existing Code

The OHLC aggregation is completely optional and doesn't affect existing functionality:

```python
# Regular subscription (no change)
api.subscribe_candles("EURUSD_otc")

# OHLC subscription (new feature)
api.subscribe_candles("EURUSD_otc", create_ohlc=True, timeframe_seconds=60)

# Both can be used simultaneously
```

This feature provides a powerful way to work with candlestick data in real-time while maintaining all existing functionality.
