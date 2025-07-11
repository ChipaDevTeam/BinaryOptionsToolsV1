"""
BinaryOptionsToolsAsync.indicators.momentum
------------------------------------------

Async-compatible momentum indicators for technical analysis.
Includes RSI calculation using ta-lib and pandas.
"""
from ta.momentum import RSIIndicator
import pandas as pd
import time

def _fetch_candles(api, active, period, num_candles):
    """
    Fetches candle data for a given asset and period.
    Returns a DataFrame with required columns.
    """
    try:
        candles_df = api.GetCandles(active, period)
        candles_df['volume'] = 0

        if len(candles_df) > num_candles:
            candles_df = candles_df.iloc[-num_candles:]

        required_columns = ['time', 'open', 'high', 'low', 'close']
        if not all(col in candles_df.columns for col in required_columns):
            raise ValueError("Missing required columns in candle data.")
        
        candles_df.ffill(inplace=True)
        candles_df['time'] = pd.to_datetime(candles_df['time'], unit='s')

        return candles_df

    except Exception as e:
        print(f"Error fetching candles: {e}")
        time.sleep(5)
        return pd.DataFrame()

def rsi(api, timeframe: int = 60, ticker: str = "EURUSD_otc", rsi_period: int = 14):
    """
    Calculate the Relative Strength Index (RSI) for a given asset and timeframe.

    Args:
        api: API instance for fetching candles.
        timeframe: Candle period in seconds.
        ticker: Trading asset symbol.
        rsi_period: RSI window length.
    Returns:
        dict: RSI values and the latest RSI value.
    """
    close = _fetch_candles(api=api, active=ticker, period=timeframe, num_candles=420)
    rsi_data = RSIIndicator(close=close["close"], window=rsi_period, fillna=True).rsi()
    return {
        "rsi_values" : rsi_data,
        "latest" : rsi_data.iloc[-1]
    }
