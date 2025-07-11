"""
BinaryOptionsToolsAsync.indicators.trend
---------------------------------------

Async-compatible trend indicators for technical analysis.
Includes SMA calculation using ta-lib and pandas.
"""
from ta.trend import SMAIndicator
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

def sma(api, timeframe: int = 60, ticker: str = "EURUSD_otc", sma_period: int = 14):
    """
    Calculate the Simple Moving Average (SMA) for a given asset and timeframe.

    Args:
        api: API instance for fetching candles.
        timeframe: Candle period in seconds.
        ticker: Trading asset symbol.
        sma_period: SMA window length.
    Returns:
        dict: SMA values and the latest SMA value.
    """
    close = _fetch_candles(api=api, active=ticker, period=timeframe, num_candles=420)
    rsi_data = SMAIndicator(close=close["close"], window=sma_period, fillna=True).sma_indicator()
    return {
        "SMA_VALUES" : rsi_data,
        "latest" : rsi_data.iloc[-1]
    }
