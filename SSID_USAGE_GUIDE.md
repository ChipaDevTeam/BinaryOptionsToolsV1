# SSID Usage Guide for BinaryOptionsTools

## What is SSID?

SSID (Session String ID) is the authentication token used to connect to PocketOption's WebSocket API. It contains your session information and allows the library to authenticate with PocketOption servers without requiring username/password.

## Your SSID Format

Your SSID is:
```
42["auth",{"session":"dd4ij8petulqcfuapcvkv578p1","isDemo":1,"uid":105754921,"platform":3,"isFastHistory":true,"isOptimized":true}]
```

### SSID Components Breakdown:

1. **Protocol Prefix**: `42` - This is the Socket.IO protocol identifier
2. **Event Type**: `"auth"` - Indicates this is an authentication message
3. **Session Data**:
   - `session`: `"dd4ij8petulqcfuapcvkv578p1"` - Your unique session token
   - `isDemo`: `1` - Indicates this is a demo account (1=demo, 0=real)
   - `uid`: `105754921` - Your unique user ID
   - `platform`: `3` - Platform identifier (3 seems to be an updated platform version)
   - `isFastHistory`: `true` - Enables optimized historical data retrieval
   - `isOptimized`: `true` - Enables optimized connection settings

## How to Use Your SSID

### Basic Usage:

```python
from BinaryOptionsTools import pocketoption

# Your SSID
ssid = r'42["auth",{"session":"dd4ij8petulqcfuapcvkv578p1","isDemo":1,"uid":105754921,"platform":3,"isFastHistory":true,"isOptimized":true}]'

# Initialize API (demo=True because isDemo=1 in your SSID)
api = pocketoption(ssid, demo=True)

# Get balance
balance = api.GetBalance()
print(f"Balance: {balance}")

# Get candle data
df = api.GetCandles("EURUSD_otc", 1, count=100)
print(df)
```

### Advanced Usage with Candle Subscription:

```python
import time
from BinaryOptionsTools import pocketoption

ssid = r'42["auth",{"session":"dd4ij8petulqcfuapcvkv578p1","isDemo":1,"uid":105754921,"platform":3,"isFastHistory":true,"isOptimized":true}]'

api = pocketoption(ssid, demo=True)

# Subscribe to real-time candles
api.api.subscribe_candles("EURUSD_otc", 1)

# Wait for subscription to establish
time.sleep(5)

# Get historical data with subscription active
df = api.GetCandles("EURUSD_otc", 1, count=500)
print(f"Retrieved {len(df)} candles")
```

## How the SSID Works in the Code

### 1. Initialization:
- When you create `pocketoption(ssid, demo)`, the SSID is stored in `global_value.SSID`
- The demo flag should match the `isDemo` value in your SSID

### 2. WebSocket Connection:
- The WebSocket client connects to PocketOption servers
- When the server sends a handshake message containing "40" and "sid", the client responds with your SSID
- This authenticates your session and establishes the connection

### 3. Session Validation:
- The server validates your session token
- If valid, you'll receive balance updates and can make API calls
- If invalid, you'll get an "User not Authorized" error

## How to Obtain a New SSID

If your current SSID expires, you need to get a new one:

1. **Open PocketOption in your browser**
2. **Log in to your account**
3. **Open Developer Tools** (F12)
4. **Go to Network tab**
5. **Filter by "WS" (WebSocket)**
6. **Look for the WebSocket connection**
7. **Find the authentication message** starting with `42["auth"`
8. **Copy the entire message** - that's your new SSID

## SSID Security Notes

- **Keep your SSID private** - it provides access to your account
- **SSID expires** - you'll need to get a new one periodically
- **Demo vs Real**: Make sure the `demo` parameter matches the `isDemo` value in your SSID
- **Session tokens are unique** to each login session

## Troubleshooting

### Common Issues:

1. **"User not Authorized" error**:
   - Your SSID has expired
   - Get a new SSID from your browser

2. **Connection fails**:
   - Check that demo parameter matches isDemo in SSID
   - Ensure you have internet connection
   - Try getting a fresh SSID

3. **No data received**:
   - Wait longer for connection to establish (10-15 seconds)
   - Check that the trading pair is correct (e.g., "EURUSD_otc")
   - Verify your account has access to the requested data

### Debug Tips:

- Enable logging to see detailed connection information
- Check global_value.websocket_is_connected status
- Monitor balance updates to confirm authentication

## Code Integration

The improved `get_candles` method now:
1. **Subscribes to real-time candles** for the requested pair
2. **Uses both historical and live data** for better reliability
3. **Handles connection issues** more gracefully
4. **Leverages your SSID's optimized settings** (isFastHistory, isOptimized)

Your SSID's `isFastHistory` and `isOptimized` flags should provide better performance for data retrieval operations.
