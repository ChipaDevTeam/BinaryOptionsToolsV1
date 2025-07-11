"""
BinaryOptionsToolsAsync.indicators.technical_analysis
----------------------------------------------------

Comprehensive async-compatible technical analysis module.
Includes indicators, chart patterns, and price action detection.
Supports both ta-lib and ta libraries.
"""

import pandas as pd
import numpy as np
import time
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore')

# Technical Analysis library imports
try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    print("Warning: TA-Lib not available. Some indicators will use ta library alternatives.")

try:
    from ta import trend, momentum, volatility, volume, others
    TA_AVAILABLE = True
except ImportError:
    TA_AVAILABLE = False
    print("Warning: ta library not available. Installing...")

def _fetch_candles(api, active: str, period: int, num_candles: int) -> pd.DataFrame:
    """Fetch candle data and format for analysis."""
    try:
        # Try OHLC candles first
        if hasattr(api, 'get_ohlc_candles'):
            candles_data = api.get_ohlc_candles(active, timeframe_seconds=period, count=num_candles)
            if candles_data:
                df = pd.DataFrame(candles_data)
                df['time'] = pd.to_datetime(df['time'], unit='s')
                return df
        
        # Fallback to regular candles
        if hasattr(api, 'get_candles'):
            candles_data = api.get_candles(active, period, num_candles)
            if candles_data and len(candles_data) > 0:
                df = pd.DataFrame(candles_data)
                if 'time' not in df.columns and 'timestamp' in df.columns:
                    df['time'] = df['timestamp']
                df['time'] = pd.to_datetime(df['time'], unit='s')
                return df
        
        # Legacy method
        if hasattr(api, 'GetCandles'):
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
        
        raise ValueError("No candle fetching method available")
        
    except Exception as e:
        print(f"Error fetching candles: {e}")
        time.sleep(1)
        return pd.DataFrame()

def _validate_data(df: pd.DataFrame, min_periods: int = 1) -> bool:
    """Validate that we have enough data for analysis."""
    if df.empty or len(df) < min_periods:
        return False
    
    required_columns = ['open', 'high', 'low', 'close']
    return all(col in df.columns for col in required_columns)

# ==============================================================================
# TREND INDICATORS
# ==============================================================================

def sma(api, timeframe: int = 60, ticker: str = "EURUSD_otc", period: int = 14, num_candles: int = 100) -> Dict:
    """Simple Moving Average"""
    df = _fetch_candles(api, ticker, timeframe, num_candles)
    if not _validate_data(df, period):
        return {"error": "Insufficient data"}
    
    if TALIB_AVAILABLE:
        sma_values = talib.SMA(df['close'].values, timeperiod=period)
    else:
        sma_values = df['close'].rolling(window=period).mean()
    
    return {
        "indicator": "SMA",
        "values": sma_values.tolist() if hasattr(sma_values, 'tolist') else list(sma_values),
        "latest": float(sma_values[-1]) if not pd.isna(sma_values[-1]) else None,
        "period": period,
        "signal": "BUY" if df['close'].iloc[-1] > sma_values[-1] else "SELL"
    }

def ema(api, timeframe: int = 60, ticker: str = "EURUSD_otc", period: int = 14, num_candles: int = 100) -> Dict:
    """Exponential Moving Average"""
    df = _fetch_candles(api, ticker, timeframe, num_candles)
    if not _validate_data(df, period):
        return {"error": "Insufficient data"}
    
    if TALIB_AVAILABLE:
        ema_values = talib.EMA(df['close'].values, timeperiod=period)
    else:
        ema_values = df['close'].ewm(span=period).mean()
    
    return {
        "indicator": "EMA",
        "values": ema_values.tolist() if hasattr(ema_values, 'tolist') else list(ema_values),
        "latest": float(ema_values[-1]) if not pd.isna(ema_values[-1]) else None,
        "period": period,
        "signal": "BUY" if df['close'].iloc[-1] > ema_values[-1] else "SELL"
    }

def macd(api, timeframe: int = 60, ticker: str = "EURUSD_otc", 
         fast_period: int = 12, slow_period: int = 26, signal_period: int = 9, 
         num_candles: int = 100) -> Dict:
    """MACD (Moving Average Convergence Divergence)"""
    df = _fetch_candles(api, ticker, timeframe, num_candles)
    if not _validate_data(df, slow_period + signal_period):
        return {"error": "Insufficient data"}
    
    if TALIB_AVAILABLE:
        macd_line, macd_signal, macd_histogram = talib.MACD(
            df['close'].values, fastperiod=fast_period, 
            slowperiod=slow_period, signalperiod=signal_period
        )
    else:
        exp1 = df['close'].ewm(span=fast_period).mean()
        exp2 = df['close'].ewm(span=slow_period).mean()
        macd_line = exp1 - exp2
        macd_signal = macd_line.ewm(span=signal_period).mean()
        macd_histogram = macd_line - macd_signal
    
    # Generate signal
    current_macd = macd_line[-1]
    current_signal = macd_signal[-1]
    prev_macd = macd_line[-2] if len(macd_line) > 1 else current_macd
    prev_signal = macd_signal[-2] if len(macd_signal) > 1 else current_signal
    
    signal = "NEUTRAL"
    if current_macd > current_signal and prev_macd <= prev_signal:
        signal = "BUY"
    elif current_macd < current_signal and prev_macd >= prev_signal:
        signal = "SELL"
    
    return {
        "indicator": "MACD",
        "macd": macd_line.tolist() if hasattr(macd_line, 'tolist') else list(macd_line),
        "signal": macd_signal.tolist() if hasattr(macd_signal, 'tolist') else list(macd_signal),
        "histogram": macd_histogram.tolist() if hasattr(macd_histogram, 'tolist') else list(macd_histogram),
        "latest_macd": float(current_macd) if not pd.isna(current_macd) else None,
        "latest_signal": float(current_signal) if not pd.isna(current_signal) else None,
        "latest_histogram": float(macd_histogram[-1]) if not pd.isna(macd_histogram[-1]) else None,
        "trade_signal": signal
    }

def bollinger_bands(api, timeframe: int = 60, ticker: str = "EURUSD_otc", 
                   period: int = 20, std_dev: float = 2.0, num_candles: int = 100) -> Dict:
    """Bollinger Bands"""
    df = _fetch_candles(api, ticker, timeframe, num_candles)
    if not _validate_data(df, period):
        return {"error": "Insufficient data"}
    
    if TALIB_AVAILABLE:
        upper, middle, lower = talib.BBANDS(
            df['close'].values, timeperiod=period, nbdevup=std_dev, nbdevdn=std_dev
        )
    else:
        middle = df['close'].rolling(window=period).mean()
        std = df['close'].rolling(window=period).std()
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
    
    current_price = df['close'].iloc[-1]
    upper_val = upper[-1]
    lower_val = lower[-1]
    middle_val = middle[-1]
    
    # Generate signals
    signal = "NEUTRAL"
    if current_price <= lower_val:
        signal = "BUY"  # Oversold
    elif current_price >= upper_val:
        signal = "SELL"  # Overbought
    
    # Calculate band position (0-1, where 0.5 is middle)
    band_position = (current_price - lower_val) / (upper_val - lower_val) if upper_val != lower_val else 0.5
    
    return {
        "indicator": "Bollinger Bands",
        "upper": upper.tolist() if hasattr(upper, 'tolist') else list(upper),
        "middle": middle.tolist() if hasattr(middle, 'tolist') else list(middle),
        "lower": lower.tolist() if hasattr(lower, 'tolist') else list(lower),
        "latest_upper": float(upper_val) if not pd.isna(upper_val) else None,
        "latest_middle": float(middle_val) if not pd.isna(middle_val) else None,
        "latest_lower": float(lower_val) if not pd.isna(lower_val) else None,
        "band_position": float(band_position),
        "signal": signal,
        "period": period,
        "std_dev": std_dev
    }

# ==============================================================================
# MOMENTUM INDICATORS
# ==============================================================================

def rsi(api, timeframe: int = 60, ticker: str = "EURUSD_otc", period: int = 14, num_candles: int = 100) -> Dict:
    """Relative Strength Index"""
    df = _fetch_candles(api, ticker, timeframe, num_candles)
    if not _validate_data(df, period + 1):
        return {"error": "Insufficient data"}
    
    if TALIB_AVAILABLE:
        rsi_values = talib.RSI(df['close'].values, timeperiod=period)
    else:
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        rsi_values = 100 - (100 / (1 + rs))
    
    current_rsi = rsi_values[-1] if not pd.isna(rsi_values[-1]) else None
    
    # Generate signals
    signal = "NEUTRAL"
    if current_rsi is not None:
        if current_rsi < 30:
            signal = "BUY"  # Oversold
        elif current_rsi > 70:
            signal = "SELL"  # Overbought
    
    return {
        "indicator": "RSI",
        "values": rsi_values.tolist() if hasattr(rsi_values, 'tolist') else list(rsi_values),
        "latest": float(current_rsi) if current_rsi is not None else None,
        "signal": signal,
        "period": period,
        "overbought_level": 70,
        "oversold_level": 30
    }

def stochastic(api, timeframe: int = 60, ticker: str = "EURUSD_otc", 
               k_period: int = 14, d_period: int = 3, num_candles: int = 100) -> Dict:
    """Stochastic Oscillator"""
    df = _fetch_candles(api, ticker, timeframe, num_candles)
    if not _validate_data(df, k_period + d_period):
        return {"error": "Insufficient data"}
    
    if TALIB_AVAILABLE:
        slowk, slowd = talib.STOCH(
            df['high'].values, df['low'].values, df['close'].values,
            fastk_period=k_period, slowk_period=d_period, slowd_period=d_period
        )
    else:
        lowest_low = df['low'].rolling(window=k_period).min()
        highest_high = df['high'].rolling(window=k_period).max()
        k_percent = 100 * ((df['close'] - lowest_low) / (highest_high - lowest_low))
        slowk = k_percent.rolling(window=d_period).mean()
        slowd = slowk.rolling(window=d_period).mean()
    
    current_k = slowk[-1] if not pd.isna(slowk[-1]) else None
    current_d = slowd[-1] if not pd.isna(slowd[-1]) else None
    
    # Generate signals
    signal = "NEUTRAL"
    if current_k is not None and current_d is not None:
        if current_k < 20 and current_d < 20:
            signal = "BUY"  # Oversold
        elif current_k > 80 and current_d > 80:
            signal = "SELL"  # Overbought
        elif current_k > current_d and slowk[-2] <= slowd[-2]:
            signal = "BUY"  # Bullish crossover
        elif current_k < current_d and slowk[-2] >= slowd[-2]:
            signal = "SELL"  # Bearish crossover
    
    return {
        "indicator": "Stochastic",
        "k_values": slowk.tolist() if hasattr(slowk, 'tolist') else list(slowk),
        "d_values": slowd.tolist() if hasattr(slowd, 'tolist') else list(slowd),
        "latest_k": float(current_k) if current_k is not None else None,
        "latest_d": float(current_d) if current_d is not None else None,
        "signal": signal,
        "k_period": k_period,
        "d_period": d_period
    }

def williams_r(api, timeframe: int = 60, ticker: str = "EURUSD_otc", period: int = 14, num_candles: int = 100) -> Dict:
    """Williams %R"""
    df = _fetch_candles(api, ticker, timeframe, num_candles)
    if not _validate_data(df, period):
        return {"error": "Insufficient data"}
    
    if TALIB_AVAILABLE:
        willr = talib.WILLR(df['high'].values, df['low'].values, df['close'].values, timeperiod=period)
    else:
        highest_high = df['high'].rolling(window=period).max()
        lowest_low = df['low'].rolling(window=period).min()
        willr = -100 * ((highest_high - df['close']) / (highest_high - lowest_low))
    
    current_willr = willr[-1] if not pd.isna(willr[-1]) else None
    
    # Generate signals
    signal = "NEUTRAL"
    if current_willr is not None:
        if current_willr < -80:
            signal = "BUY"  # Oversold
        elif current_willr > -20:
            signal = "SELL"  # Overbought
    
    return {
        "indicator": "Williams %R",
        "values": willr.tolist() if hasattr(willr, 'tolist') else list(willr),
        "latest": float(current_willr) if current_willr is not None else None,
        "signal": signal,
        "period": period,
        "overbought_level": -20,
        "oversold_level": -80
    }

# ==============================================================================
# VOLATILITY INDICATORS
# ==============================================================================

def atr(api, timeframe: int = 60, ticker: str = "EURUSD_otc", period: int = 14, num_candles: int = 100) -> Dict:
    """Average True Range"""
    df = _fetch_candles(api, ticker, timeframe, num_candles)
    if not _validate_data(df, period + 1):
        return {"error": "Insufficient data"}
    
    if TALIB_AVAILABLE:
        atr_values = talib.ATR(df['high'].values, df['low'].values, df['close'].values, timeperiod=period)
    else:
        high_low = df['high'] - df['low']
        high_close = np.abs(df['high'] - df['close'].shift())
        low_close = np.abs(df['low'] - df['close'].shift())
        true_range = np.maximum(high_low, np.maximum(high_close, low_close))
        atr_values = true_range.rolling(window=period).mean()
    
    current_atr = atr_values[-1] if not pd.isna(atr_values[-1]) else None
    
    # Calculate volatility level
    volatility_level = "NORMAL"
    if current_atr is not None:
        atr_mean = np.mean(atr_values[-50:]) if len(atr_values) >= 50 else np.mean(atr_values)
        if current_atr > atr_mean * 1.5:
            volatility_level = "HIGH"
        elif current_atr < atr_mean * 0.5:
            volatility_level = "LOW"
    
    return {
        "indicator": "ATR",
        "values": atr_values.tolist() if hasattr(atr_values, 'tolist') else list(atr_values),
        "latest": float(current_atr) if current_atr is not None else None,
        "volatility_level": volatility_level,
        "period": period
    }

# ==============================================================================
# VOLUME INDICATORS
# ==============================================================================

def volume_sma(api, timeframe: int = 60, ticker: str = "EURUSD_otc", period: int = 20, num_candles: int = 100) -> Dict:
    """Volume Simple Moving Average"""
    df = _fetch_candles(api, ticker, timeframe, num_candles)
    if not _validate_data(df, period):
        return {"error": "Insufficient data"}
    
    # For forex/crypto, use tick count as volume proxy
    if 'volume' not in df.columns or df['volume'].sum() == 0:
        if 'tick_count' in df.columns:
            df['volume'] = df['tick_count']
        else:
            df['volume'] = 1  # Default volume
    
    volume_sma = df['volume'].rolling(window=period).mean()
    current_volume = df['volume'].iloc[-1]
    current_sma = volume_sma.iloc[-1]
    
    signal = "NORMAL"
    if current_volume > current_sma * 1.5:
        signal = "HIGH_VOLUME"
    elif current_volume < current_sma * 0.5:
        signal = "LOW_VOLUME"
    
    return {
        "indicator": "Volume SMA",
        "values": volume_sma.tolist(),
        "latest": float(current_sma) if not pd.isna(current_sma) else None,
        "current_volume": float(current_volume),
        "signal": signal,
        "period": period
    }

# ==============================================================================
# SUPPORT AND RESISTANCE
# ==============================================================================

def support_resistance_levels(api, timeframe: int = 60, ticker: str = "EURUSD_otc", 
                             num_candles: int = 200, lookback: int = 20) -> Dict:
    """Calculate Support and Resistance levels"""
    df = _fetch_candles(api, ticker, timeframe, num_candles)
    if not _validate_data(df, lookback * 2):
        return {"error": "Insufficient data"}
    
    highs = df['high'].values
    lows = df['low'].values
    closes = df['close'].values
    
    # Find local maxima and minima
    resistance_levels = []
    support_levels = []
    
    for i in range(lookback, len(highs) - lookback):
        # Check for resistance (local maximum)
        if highs[i] == max(highs[i-lookback:i+lookback+1]):
            resistance_levels.append(highs[i])
        
        # Check for support (local minimum)
        if lows[i] == min(lows[i-lookback:i+lookback+1]):
            support_levels.append(lows[i])
    
    # Remove duplicate levels (within 0.1% of each other)
    def remove_close_levels(levels, tolerance=0.001):
        if not levels:
            return []
        levels = sorted(set(levels))
        filtered = [levels[0]]
        for level in levels[1:]:
            if abs(level - filtered[-1]) / filtered[-1] > tolerance:
                filtered.append(level)
        return filtered
    
    resistance_levels = remove_close_levels(resistance_levels)
    support_levels = remove_close_levels(support_levels)
    
    # Get current price and nearest levels
    current_price = closes[-1]
    nearest_resistance = min([r for r in resistance_levels if r > current_price], default=None)
    nearest_support = max([s for s in support_levels if s < current_price], default=None)
    
    return {
        "indicator": "Support/Resistance",
        "resistance_levels": resistance_levels[-5:],  # Last 5 levels
        "support_levels": support_levels[-5:],  # Last 5 levels
        "nearest_resistance": nearest_resistance,
        "nearest_support": nearest_support,
        "current_price": float(current_price),
        "lookback_period": lookback
    }

# ==============================================================================
# UTILITY FUNCTIONS
# ==============================================================================

def get_all_indicators(api, timeframe: int = 60, ticker: str = "EURUSD_otc", num_candles: int = 200) -> Dict:
    """Get all indicators at once"""
    indicators = {}
    
    try:
        indicators['sma_20'] = sma(api, timeframe, ticker, 20, num_candles)
        indicators['ema_20'] = ema(api, timeframe, ticker, 20, num_candles)
        indicators['rsi'] = rsi(api, timeframe, ticker, 14, num_candles)
        indicators['macd'] = macd(api, timeframe, ticker, 12, 26, 9, num_candles)
        indicators['bollinger_bands'] = bollinger_bands(api, timeframe, ticker, 20, 2.0, num_candles)
        indicators['stochastic'] = stochastic(api, timeframe, ticker, 14, 3, num_candles)
        indicators['williams_r'] = williams_r(api, timeframe, ticker, 14, num_candles)
        indicators['atr'] = atr(api, timeframe, ticker, 14, num_candles)
        indicators['support_resistance'] = support_resistance_levels(api, timeframe, ticker, num_candles, 20)
        
    except Exception as e:
        indicators['error'] = f"Error calculating indicators: {str(e)}"
    
    return indicators

def get_trading_signals(api, timeframe: int = 60, ticker: str = "EURUSD_otc", num_candles: int = 200) -> Dict:
    """Get consolidated trading signals from all indicators"""
    indicators = get_all_indicators(api, timeframe, ticker, num_candles)
    
    if 'error' in indicators:
        return indicators
    
    signals = []
    buy_count = 0
    sell_count = 0
    neutral_count = 0
    
    # Collect signals from all indicators
    for name, indicator in indicators.items():
        if isinstance(indicator, dict) and 'signal' in indicator:
            signal = indicator['signal']
            signals.append(f"{name}: {signal}")
            
            if signal == "BUY":
                buy_count += 1
            elif signal == "SELL":
                sell_count += 1
            else:
                neutral_count += 1
    
    # Determine overall signal
    total_signals = buy_count + sell_count + neutral_count
    if total_signals == 0:
        overall_signal = "NO_DATA"
    elif buy_count > sell_count * 1.5:
        overall_signal = "STRONG_BUY"
    elif buy_count > sell_count:
        overall_signal = "BUY"
    elif sell_count > buy_count * 1.5:
        overall_signal = "STRONG_SELL"
    elif sell_count > buy_count:
        overall_signal = "SELL"
    else:
        overall_signal = "NEUTRAL"
    
    return {
        "overall_signal": overall_signal,
        "buy_signals": buy_count,
        "sell_signals": sell_count,
        "neutral_signals": neutral_count,
        "total_signals": total_signals,
        "signal_strength": max(buy_count, sell_count) / total_signals if total_signals > 0 else 0,
        "individual_signals": signals,
        "indicators": indicators
    }

def detect_chart_patterns(df: pd.DataFrame) -> Dict:
    """Detect common chart patterns in price data"""
    if df.empty or len(df) < 20:
        return {"error": "Insufficient data for pattern detection"}
    
    patterns = {}
    high = df['high'].values
    low = df['low'].values
    close = df['close'].values
    
    # Double Top Pattern
    patterns['double_top'] = _detect_double_top(high, close)
    
    # Double Bottom Pattern
    patterns['double_bottom'] = _detect_double_bottom(low, close)
    
    # Head and Shoulders
    patterns['head_and_shoulders'] = _detect_head_and_shoulders(high, close)
    
    # Inverse Head and Shoulders
    patterns['inverse_head_and_shoulders'] = _detect_inverse_head_and_shoulders(low, close)
    
    # Triangle Patterns
    patterns['ascending_triangle'] = _detect_ascending_triangle(high, low)
    patterns['descending_triangle'] = _detect_descending_triangle(high, low)
    patterns['symmetrical_triangle'] = _detect_symmetrical_triangle(high, low)
    
    # Flag and Pennant
    patterns['bull_flag'] = _detect_bull_flag(high, low, close)
    patterns['bear_flag'] = _detect_bear_flag(high, low, close)
    
    # Wedge Patterns
    patterns['rising_wedge'] = _detect_rising_wedge(high, low)
    patterns['falling_wedge'] = _detect_falling_wedge(high, low)
    
    # Rectangle Pattern
    patterns['rectangle'] = _detect_rectangle(high, low)
    
    return patterns

def _detect_double_top(high: np.ndarray, close: np.ndarray) -> Dict:
    """Detect double top pattern"""
    if len(high) < 20:
        return {"detected": False, "confidence": 0}
    
    # Find peaks
    peaks = []
    for i in range(5, len(high) - 5):
        if all(high[i] >= high[i-j] for j in range(1, 6)) and all(high[i] >= high[i+j] for j in range(1, 6)):
            peaks.append((i, high[i]))
    
    if len(peaks) < 2:
        return {"detected": False, "confidence": 0}
    
    # Look for two similar peaks
    for i in range(len(peaks) - 1):
        for j in range(i + 1, len(peaks)):
            peak1_idx, peak1_val = peaks[i]
            peak2_idx, peak2_val = peaks[j]
            
            # Check if peaks are similar in height (within 2%)
            if abs(peak1_val - peak2_val) / max(peak1_val, peak2_val) <= 0.02:
                # Check if there's a valley between peaks
                valley_low = min(high[peak1_idx:peak2_idx])
                if valley_low < min(peak1_val, peak2_val) * 0.98:
                    # Check if price declined after second peak
                    if len(close) > peak2_idx + 3 and close[-1] < peak2_val * 0.99:
                        confidence = 1 - abs(peak1_val - peak2_val) / max(peak1_val, peak2_val)
                        return {
                            "detected": True,
                            "confidence": confidence,
                            "signal": "SELL",
                            "peak1_idx": int(peak1_idx),
                            "peak2_idx": int(peak2_idx),
                            "peak1_val": float(peak1_val),
                            "peak2_val": float(peak2_val)
                        }
    
    return {"detected": False, "confidence": 0}

def _detect_double_bottom(low: np.ndarray, close: np.ndarray) -> Dict:
    """Detect double bottom pattern"""
    if len(low) < 20:
        return {"detected": False, "confidence": 0}
    
    # Find troughs
    troughs = []
    for i in range(5, len(low) - 5):
        if all(low[i] <= low[i-j] for j in range(1, 6)) and all(low[i] <= low[i+j] for j in range(1, 6)):
            troughs.append((i, low[i]))
    
    if len(troughs) < 2:
        return {"detected": False, "confidence": 0}
    
    # Look for two similar troughs
    for i in range(len(troughs) - 1):
        for j in range(i + 1, len(troughs)):
            trough1_idx, trough1_val = troughs[i]
            trough2_idx, trough2_val = troughs[j]
            
            # Check if troughs are similar in depth (within 2%)
            if abs(trough1_val - trough2_val) / max(trough1_val, trough2_val) <= 0.02:
                # Check if there's a peak between troughs
                peak_high = max(low[trough1_idx:trough2_idx])
                if peak_high > max(trough1_val, trough2_val) * 1.02:
                    # Check if price rose after second trough
                    if len(close) > trough2_idx + 3 and close[-1] > trough2_val * 1.01:
                        confidence = 1 - abs(trough1_val - trough2_val) / max(trough1_val, trough2_val)
                        return {
                            "detected": True,
                            "confidence": confidence,
                            "signal": "BUY",
                            "trough1_idx": int(trough1_idx),
                            "trough2_idx": int(trough2_idx),
                            "trough1_val": float(trough1_val),
                            "trough2_val": float(trough2_val)
                        }
    
    return {"detected": False, "confidence": 0}

def _detect_head_and_shoulders(high: np.ndarray, close: np.ndarray) -> Dict:
    """Detect head and shoulders pattern"""
    if len(high) < 30:
        return {"detected": False, "confidence": 0}
    
    # Find three consecutive peaks
    peaks = []
    for i in range(5, len(high) - 5):
        if all(high[i] >= high[i-j] for j in range(1, 6)) and all(high[i] >= high[i+j] for j in range(1, 6)):
            peaks.append((i, high[i]))
    
    if len(peaks) < 3:
        return {"detected": False, "confidence": 0}
    
    # Look for head and shoulders pattern
    for i in range(len(peaks) - 2):
        left_shoulder = peaks[i]
        head = peaks[i + 1]
        right_shoulder = peaks[i + 2]
        
        # Head should be highest
        if head[1] > left_shoulder[1] and head[1] > right_shoulder[1]:
            # Shoulders should be similar height
            shoulder_diff = abs(left_shoulder[1] - right_shoulder[1]) / max(left_shoulder[1], right_shoulder[1])
            if shoulder_diff <= 0.03:
                # Check neckline break
                if len(close) > right_shoulder[0] + 3:
                    neckline = min(left_shoulder[1], right_shoulder[1])
                    if close[-1] < neckline * 0.99:
                        confidence = 1 - shoulder_diff
                        return {
                            "detected": True,
                            "confidence": confidence,
                            "signal": "SELL",
                            "left_shoulder": {"idx": int(left_shoulder[0]), "val": float(left_shoulder[1])},
                            "head": {"idx": int(head[0]), "val": float(head[1])},
                            "right_shoulder": {"idx": int(right_shoulder[0]), "val": float(right_shoulder[1])},
                            "neckline": float(neckline)
                        }
    
    return {"detected": False, "confidence": 0}

def _detect_inverse_head_and_shoulders(low: np.ndarray, close: np.ndarray) -> Dict:
    """Detect inverse head and shoulders pattern"""
    if len(low) < 30:
        return {"detected": False, "confidence": 0}
    
    # Find three consecutive troughs
    troughs = []
    for i in range(5, len(low) - 5):
        if all(low[i] <= low[i-j] for j in range(1, 6)) and all(low[i] <= low[i+j] for j in range(1, 6)):
            troughs.append((i, low[i]))
    
    if len(troughs) < 3:
        return {"detected": False, "confidence": 0}
    
    # Look for inverse head and shoulders pattern
    for i in range(len(troughs) - 2):
        left_shoulder = troughs[i]
        head = troughs[i + 1]
        right_shoulder = troughs[i + 2]
        
        # Head should be lowest
        if head[1] < left_shoulder[1] and head[1] < right_shoulder[1]:
            # Shoulders should be similar depth
            shoulder_diff = abs(left_shoulder[1] - right_shoulder[1]) / max(left_shoulder[1], right_shoulder[1])
            if shoulder_diff <= 0.03:
                # Check neckline break
                if len(close) > right_shoulder[0] + 3:
                    neckline = max(left_shoulder[1], right_shoulder[1])
                    if close[-1] > neckline * 1.01:
                        confidence = 1 - shoulder_diff
                        return {
                            "detected": True,
                            "confidence": confidence,
                            "signal": "BUY",
                            "left_shoulder": {"idx": int(left_shoulder[0]), "val": float(left_shoulder[1])},
                            "head": {"idx": int(head[0]), "val": float(head[1])},
                            "right_shoulder": {"idx": int(right_shoulder[0]), "val": float(right_shoulder[1])},
                            "neckline": float(neckline)
                        }
    
    return {"detected": False, "confidence": 0}

def _detect_ascending_triangle(high: np.ndarray, low: np.ndarray) -> Dict:
    """Detect ascending triangle pattern"""
    if len(high) < 20:
        return {"detected": False, "confidence": 0}
    
    recent_data = 50
    if len(high) > recent_data:
        high = high[-recent_data:]
        low = low[-recent_data:]
    
    # Find resistance level (horizontal top)
    resistance = np.max(high[-10:])
    resistance_touches = np.sum(high >= resistance * 0.999)
    
    # Check for ascending support line
    support_slope = np.polyfit(range(len(low)), low, 1)[0]
    
    if resistance_touches >= 2 and support_slope > 0:
        confidence = min(resistance_touches / 3.0, 1.0) * min(support_slope * 1000, 1.0)
        return {
            "detected": True,
            "confidence": confidence,
            "signal": "BUY",  # Typically bullish breakout
            "resistance_level": float(resistance),
            "support_slope": float(support_slope)
        }
    
    return {"detected": False, "confidence": 0}

def _detect_descending_triangle(high: np.ndarray, low: np.ndarray) -> Dict:
    """Detect descending triangle pattern"""
    if len(low) < 20:
        return {"detected": False, "confidence": 0}
    
    recent_data = 50
    if len(low) > recent_data:
        high = high[-recent_data:]
        low = low[-recent_data:]
    
    # Find support level (horizontal bottom)
    support = np.min(low[-10:])
    support_touches = np.sum(low <= support * 1.001)
    
    # Check for descending resistance line
    resistance_slope = np.polyfit(range(len(high)), high, 1)[0]
    
    if support_touches >= 2 and resistance_slope < 0:
        confidence = min(support_touches / 3.0, 1.0) * min(abs(resistance_slope) * 1000, 1.0)
        return {
            "detected": True,
            "confidence": confidence,
            "signal": "SELL",  # Typically bearish breakout
            "support_level": float(support),
            "resistance_slope": float(resistance_slope)
        }
    
    return {"detected": False, "confidence": 0}

def _detect_symmetrical_triangle(high: np.ndarray, low: np.ndarray) -> Dict:
    """Detect symmetrical triangle pattern"""
    if len(high) < 20:
        return {"detected": False, "confidence": 0}
    
    recent_data = 50
    if len(high) > recent_data:
        high = high[-recent_data:]
        low = low[-recent_data:]
    
    # Check for converging trend lines
    high_slope = np.polyfit(range(len(high)), high, 1)[0]
    low_slope = np.polyfit(range(len(low)), low, 1)[0]
    
    # High slope should be negative, low slope should be positive
    if high_slope < 0 and low_slope > 0:
        # Check if lines are converging
        convergence = abs(high_slope) + low_slope
        if convergence > 0:
            confidence = min(convergence * 500, 1.0)
            return {
                "detected": True,
                "confidence": confidence,
                "signal": "NEUTRAL",  # Direction depends on breakout
                "high_slope": float(high_slope),
                "low_slope": float(low_slope),
                "convergence_rate": float(convergence)
            }
    
    return {"detected": False, "confidence": 0}

def _detect_bull_flag(high: np.ndarray, low: np.ndarray, close: np.ndarray) -> Dict:
    """Detect bull flag pattern"""
    if len(close) < 30:
        return {"detected": False, "confidence": 0}
    
    # Look for strong uptrend followed by consolidation
    recent_30 = close[-30:]
    first_15 = recent_30[:15]
    last_15 = recent_30[15:]
    
    # Check for strong upward move in first part
    first_trend = np.polyfit(range(len(first_15)), first_15, 1)[0]
    
    # Check for consolidation or slight downward drift in second part
    second_trend = np.polyfit(range(len(last_15)), last_15, 1)[0]
    
    if first_trend > 0 and abs(second_trend) < first_trend * 0.3:
        # Check volume pattern if available (flag should have lower volume)
        price_range_ratio = (np.max(last_15) - np.min(last_15)) / (np.max(first_15) - np.min(first_15))
        
        if price_range_ratio < 0.6:  # Consolidation should be tighter
            confidence = first_trend * 1000 * (1 - price_range_ratio)
            confidence = min(confidence, 1.0)
            return {
                "detected": True,
                "confidence": confidence,
                "signal": "BUY",
                "flagpole_slope": float(first_trend),
                "flag_slope": float(second_trend),
                "consolidation_ratio": float(price_range_ratio)
            }
    
    return {"detected": False, "confidence": 0}

def _detect_bear_flag(high: np.ndarray, low: np.ndarray, close: np.ndarray) -> Dict:
    """Detect bear flag pattern"""
    if len(close) < 30:
        return {"detected": False, "confidence": 0}
    
    # Look for strong downtrend followed by consolidation
    recent_30 = close[-30:]
    first_15 = recent_30[:15]
    last_15 = recent_30[15:]
    
    # Check for strong downward move in first part
    first_trend = np.polyfit(range(len(first_15)), first_15, 1)[0]
    
    # Check for consolidation or slight upward drift in second part
    second_trend = np.polyfit(range(len(last_15)), last_15, 1)[0]
    
    if first_trend < 0 and abs(second_trend) < abs(first_trend) * 0.3:
        # Check volume pattern if available (flag should have lower volume)
        price_range_ratio = (np.max(last_15) - np.min(last_15)) / (np.max(first_15) - np.min(first_15))
        
        if price_range_ratio < 0.6:  # Consolidation should be tighter
            confidence = abs(first_trend) * 1000 * (1 - price_range_ratio)
            confidence = min(confidence, 1.0)
            return {
                "detected": True,
                "confidence": confidence,
                "signal": "SELL",
                "flagpole_slope": float(first_trend),
                "flag_slope": float(second_trend),
                "consolidation_ratio": float(price_range_ratio)
            }
    
    return {"detected": False, "confidence": 0}

def _detect_rising_wedge(high: np.ndarray, low: np.ndarray) -> Dict:
    """Detect rising wedge pattern"""
    if len(high) < 20:
        return {"detected": False, "confidence": 0}
    
    recent_data = 50
    if len(high) > recent_data:
        high = high[-recent_data:]
        low = low[-recent_data:]
    
    # Both trend lines should be rising, but high line rises slower
    high_slope = np.polyfit(range(len(high)), high, 1)[0]
    low_slope = np.polyfit(range(len(low)), low, 1)[0]
    
    if high_slope > 0 and low_slope > 0 and low_slope > high_slope:
        # Lines should be converging
        convergence = low_slope - high_slope
        if convergence > 0:
            confidence = min(convergence * 1000, 1.0)
            return {
                "detected": True,
                "confidence": confidence,
                "signal": "SELL",  # Rising wedge is typically bearish
                "high_slope": float(high_slope),
                "low_slope": float(low_slope),
                "convergence_rate": float(convergence)
            }
    
    return {"detected": False, "confidence": 0}

def _detect_falling_wedge(high: np.ndarray, low: np.ndarray) -> Dict:
    """Detect falling wedge pattern"""
    if len(high) < 20:
        return {"detected": False, "confidence": 0}
    
    recent_data = 50
    if len(high) > recent_data:
        high = high[-recent_data:]
        low = low[-recent_data:]
    
    # Both trend lines should be falling, but low line falls faster
    high_slope = np.polyfit(range(len(high)), high, 1)[0]
    low_slope = np.polyfit(range(len(low)), low, 1)[0]
    
    if high_slope < 0 and low_slope < 0 and low_slope < high_slope:
        # Lines should be converging
        convergence = high_slope - low_slope
        if convergence > 0:
            confidence = min(convergence * 1000, 1.0)
            return {
                "detected": True,
                "confidence": confidence,
                "signal": "BUY",  # Falling wedge is typically bullish
                "high_slope": float(high_slope),
                "low_slope": float(low_slope),
                "convergence_rate": float(convergence)
            }
    
    return {"detected": False, "confidence": 0}

def _detect_rectangle(high: np.ndarray, low: np.ndarray) -> Dict:
    """Detect rectangle pattern (trading range)"""
    if len(high) < 20:
        return {"detected": False, "confidence": 0}
    
    recent_data = 50
    if len(high) > recent_data:
        high = high[-recent_data:]
        low = low[-recent_data:]
    
    # Find resistance and support levels
    resistance = np.percentile(high, 95)
    support = np.percentile(low, 5)
    
    # Check how many times price touches these levels
    resistance_touches = np.sum(high >= resistance * 0.999)
    support_touches = np.sum(low <= support * 1.001)
    
    # Check if trend lines are relatively flat
    high_slope = abs(np.polyfit(range(len(high)), high, 1)[0])
    low_slope = abs(np.polyfit(range(len(low)), low, 1)[0])
    
    if resistance_touches >= 2 and support_touches >= 2 and high_slope < 0.001 and low_slope < 0.001:
        range_size = (resistance - support) / support
        if range_size > 0.01:  # Meaningful range
            confidence = min((resistance_touches + support_touches) / 6.0, 1.0)
            return {
                "detected": True,
                "confidence": confidence,
                "signal": "NEUTRAL",  # Direction depends on breakout
                "resistance_level": float(resistance),
                "support_level": float(support),
                "range_size": float(range_size),
                "resistance_touches": int(resistance_touches),
                "support_touches": int(support_touches)
            }
    
    return {"detected": False, "confidence": 0}

def detect_price_action(df: pd.DataFrame) -> Dict:
    """Detect price action patterns and signals"""
    if df.empty or len(df) < 10:
        return {"error": "Insufficient data for price action analysis"}
    
    high = df['high'].values
    low = df['low'].values
    open_price = df['open'].values
    close = df['close'].values
    
    price_action = {}
    
    # Candlestick patterns
    price_action['candlestick_patterns'] = _detect_candlestick_patterns(open_price, high, low, close)
    
    # Support and resistance levels
    price_action['support_resistance'] = _detect_support_resistance_levels(high, low, close)
    
    # Trend analysis
    price_action['trend_analysis'] = _analyze_trend_strength(close)
    
    # Breakout detection
    price_action['breakout_signals'] = _detect_breakouts(high, low, close)
    
    # Momentum signals
    price_action['momentum_signals'] = _analyze_momentum(high, low, close)
    
    # Price rejection patterns
    price_action['rejection_patterns'] = _detect_rejection_patterns(open_price, high, low, close)
    
    return price_action

def _detect_candlestick_patterns(open_price: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray) -> Dict:
    """Detect major candlestick patterns"""
    if len(close) < 3:
        return {}
    
    patterns = {}
    
    # Get last few candles for pattern detection
    for i in range(max(2, len(close) - 5), len(close)):
        if i >= len(close):
            continue
            
        o, h, l, c = open_price[i], high[i], low[i], close[i]
        body = abs(c - o)
        range_size = h - l
        
        if range_size == 0:
            continue
            
        body_ratio = body / range_size
        upper_shadow = h - max(o, c)
        lower_shadow = min(o, c) - l
        
        # Doji
        if body_ratio < 0.1:
            patterns[f'doji_{i}'] = {
                "pattern": "doji",
                "signal": "NEUTRAL",
                "confidence": 1 - body_ratio * 10,
                "candle_index": i
            }
        
        # Hammer (bullish reversal)
        elif lower_shadow > body * 2 and upper_shadow < body * 0.5 and c > o:
            patterns[f'hammer_{i}'] = {
                "pattern": "hammer",
                "signal": "BUY",
                "confidence": min(lower_shadow / body / 3, 1.0),
                "candle_index": i
            }
        
        # Hanging man (bearish reversal)
        elif lower_shadow > body * 2 and upper_shadow < body * 0.5 and c < o:
            patterns[f'hanging_man_{i}'] = {
                "pattern": "hanging_man",
                "signal": "SELL",
                "confidence": min(lower_shadow / body / 3, 1.0),
                "candle_index": i
            }
        
        # Shooting star (bearish reversal)
        elif upper_shadow > body * 2 and lower_shadow < body * 0.5 and c < o:
            patterns[f'shooting_star_{i}'] = {
                "pattern": "shooting_star",
                "signal": "SELL",
                "confidence": min(upper_shadow / body / 3, 1.0),
                "candle_index": i
            }
        
        # Inverted hammer (bullish reversal)
        elif upper_shadow > body * 2 and lower_shadow < body * 0.5 and c > o:
            patterns[f'inverted_hammer_{i}'] = {
                "pattern": "inverted_hammer",
                "signal": "BUY",
                "confidence": min(upper_shadow / body / 3, 1.0),
                "candle_index": i
            }
    
    # Multi-candle patterns
    if len(close) >= 3:
        # Engulfing patterns
        for i in range(1, len(close)):
            if i >= len(close) - 1:
                continue
                
            prev_body = abs(close[i-1] - open_price[i-1])
            curr_body = abs(close[i] - open_price[i])
            
            # Bullish engulfing
            if (close[i-1] < open_price[i-1] and  # Previous candle red
                close[i] > open_price[i] and      # Current candle green
                open_price[i] < close[i-1] and    # Current open below previous close
                close[i] > open_price[i-1] and    # Current close above previous open
                curr_body > prev_body * 1.1):    # Current body larger
                
                patterns[f'bullish_engulfing_{i}'] = {
                    "pattern": "bullish_engulfing",
                    "signal": "BUY",
                    "confidence": min(curr_body / prev_body / 2, 1.0),
                    "candle_index": i
                }
            
            # Bearish engulfing
            elif (close[i-1] > open_price[i-1] and  # Previous candle green
                  close[i] < open_price[i] and       # Current candle red
                  open_price[i] > close[i-1] and     # Current open above previous close
                  close[i] < open_price[i-1] and     # Current close below previous open
                  curr_body > prev_body * 1.1):     # Current body larger
                
                patterns[f'bearish_engulfing_{i}'] = {
                    "pattern": "bearish_engulfing",
                    "signal": "SELL",
                    "confidence": min(curr_body / prev_body / 2, 1.0),
                    "candle_index": i
                }
    
    return patterns

def _detect_support_resistance_levels(high: np.ndarray, low: np.ndarray, close: np.ndarray) -> Dict:
    """Detect key support and resistance levels"""
    if len(close) < 20:
        return {}
    
    # Use recent data for level detection
    recent_periods = min(100, len(close))
    recent_high = high[-recent_periods:]
    recent_low = low[-recent_periods:]
    recent_close = close[-recent_periods:]
    
    current_price = close[-1]
    
    # Find pivot points
    resistance_levels = []
    support_levels = []
    
    # Look for pivot highs (resistance)
    for i in range(2, len(recent_high) - 2):
        if (recent_high[i] > recent_high[i-1] and recent_high[i] > recent_high[i-2] and
            recent_high[i] > recent_high[i+1] and recent_high[i] > recent_high[i+2]):
            
            # Count how many times this level was tested
            level = recent_high[i]
            touches = np.sum(np.abs(recent_high - level) / level < 0.005)  # Within 0.5%
            
            if touches >= 2:
                distance_from_current = abs(level - current_price) / current_price
                resistance_levels.append({
                    "level": float(level),
                    "strength": int(touches),
                    "distance_from_current": float(distance_from_current),
                    "index": int(i)
                })
    
    # Look for pivot lows (support)
    for i in range(2, len(recent_low) - 2):
        if (recent_low[i] < recent_low[i-1] and recent_low[i] < recent_low[i-2] and
            recent_low[i] < recent_low[i+1] and recent_low[i] < recent_low[i+2]):
            
            # Count how many times this level was tested
            level = recent_low[i]
            touches = np.sum(np.abs(recent_low - level) / level < 0.005)  # Within 0.5%
            
            if touches >= 2:
                distance_from_current = abs(level - current_price) / current_price
                support_levels.append({
                    "level": float(level),
                    "strength": int(touches),
                    "distance_from_current": float(distance_from_current),
                    "index": int(i)
                })
    
    # Sort by strength and proximity
    resistance_levels.sort(key=lambda x: (x['strength'], -x['distance_from_current']), reverse=True)
    support_levels.sort(key=lambda x: (x['strength'], -x['distance_from_current']), reverse=True)
    
    return {
        "resistance_levels": resistance_levels[:5],  # Top 5
        "support_levels": support_levels[:5],        # Top 5
        "current_price": float(current_price)
    }

def _analyze_trend_strength(close: np.ndarray) -> Dict:
    """Analyze trend strength and direction"""
    if len(close) < 20:
        return {}
    
    # Different timeframe trends
    short_term = close[-10:]
    medium_term = close[-20:]
    long_term = close[-50:] if len(close) >= 50 else close
    
    # Calculate trend slopes
    short_slope = np.polyfit(range(len(short_term)), short_term, 1)[0]
    medium_slope = np.polyfit(range(len(medium_term)), medium_term, 1)[0]
    long_slope = np.polyfit(range(len(long_term)), long_term, 1)[0]
    
    # Normalize slopes
    current_price = close[-1]
    short_trend = short_slope / current_price * 1000
    medium_trend = medium_slope / current_price * 1000
    long_trend = long_slope / current_price * 1000
    
    # Determine overall trend
    def get_trend_direction(slope):
        if slope > 0.5:
            return "BULLISH"
        elif slope < -0.5:
            return "BEARISH"
        else:
            return "SIDEWAYS"
    
    # Calculate trend alignment
    trends = [short_trend, medium_trend, long_trend]
    bullish_count = sum(1 for t in trends if t > 0.5)
    bearish_count = sum(1 for t in trends if t < -0.5)
    
    if bullish_count >= 2:
        overall_trend = "BULLISH"
        trend_strength = bullish_count / 3
    elif bearish_count >= 2:
        overall_trend = "BEARISH"
        trend_strength = bearish_count / 3
    else:
        overall_trend = "SIDEWAYS"
        trend_strength = 0.5
    
    return {
        "short_term_trend": get_trend_direction(short_trend),
        "medium_term_trend": get_trend_direction(medium_trend),
        "long_term_trend": get_trend_direction(long_trend),
        "overall_trend": overall_trend,
        "trend_strength": float(trend_strength),
        "short_slope": float(short_trend),
        "medium_slope": float(medium_trend),
        "long_slope": float(long_trend)
    }

def _detect_breakouts(high: np.ndarray, low: np.ndarray, close: np.ndarray) -> Dict:
    """Detect potential breakout situations"""
    if len(close) < 20:
        return {}
    
    current_price = close[-1]
    recent_20_high = np.max(high[-20:])
    recent_20_low = np.min(low[-20:])
    
    # Calculate volatility
    returns = np.diff(close) / close[:-1]
    volatility = np.std(returns[-20:]) if len(returns) >= 20 else np.std(returns)
    
    # Breakout detection
    breakout_signals = []
    
    # Upward breakout
    if current_price > recent_20_high * 1.001:  # Above recent high by 0.1%
        strength = (current_price - recent_20_high) / recent_20_high
        breakout_signals.append({
            "type": "upward_breakout",
            "signal": "BUY",
            "strength": float(min(strength * 100, 1.0)),
            "breakout_level": float(recent_20_high),
            "current_price": float(current_price)
        })
    
    # Downward breakout
    if current_price < recent_20_low * 0.999:  # Below recent low by 0.1%
        strength = (recent_20_low - current_price) / recent_20_low
        breakout_signals.append({
            "type": "downward_breakout",
            "signal": "SELL",
            "strength": float(min(strength * 100, 1.0)),
            "breakout_level": float(recent_20_low),
            "current_price": float(current_price)
        })
    
    # Consolidation detection (potential breakout setup)
    range_size = (recent_20_high - recent_20_low) / recent_20_low
    if range_size < 0.02:  # Tight range (2%)
        breakout_signals.append({
            "type": "consolidation",
            "signal": "NEUTRAL",
            "strength": float(1 - range_size * 50),  # Tighter = stronger signal
            "range_high": float(recent_20_high),
            "range_low": float(recent_20_low),
            "range_size": float(range_size)
        })
    
    return {
        "signals": breakout_signals,
        "volatility": float(volatility),
        "recent_high": float(recent_20_high),
        "recent_low": float(recent_20_low)
    }

def _analyze_momentum(high: np.ndarray, low: np.ndarray, close: np.ndarray) -> Dict:
    """Analyze price momentum"""
    if len(close) < 10:
        return {}
    
    # Rate of change
    roc_5 = (close[-1] - close[-6]) / close[-6] if len(close) > 5 else 0
    roc_10 = (close[-1] - close[-11]) / close[-11] if len(close) > 10 else 0
    
    # Price velocity (acceleration)
    if len(close) >= 3:
        velocity_recent = (close[-1] - close[-2]) / close[-2]
        velocity_prev = (close[-2] - close[-3]) / close[-3]
        acceleration = velocity_recent - velocity_prev
    else:
        acceleration = 0
    
    # Momentum signals
    momentum_signals = []
    
    if roc_5 > 0.01:  # 1% gain in 5 periods
        momentum_signals.append({
            "type": "strong_upward_momentum",
            "signal": "BUY",
            "strength": float(min(roc_5 * 50, 1.0))
        })
    elif roc_5 < -0.01:  # 1% loss in 5 periods
        momentum_signals.append({
            "type": "strong_downward_momentum",
            "signal": "SELL",
            "strength": float(min(abs(roc_5) * 50, 1.0))
        })
    
    if acceleration > 0.005:  # Accelerating upward
        momentum_signals.append({
            "type": "accelerating_upward",
            "signal": "BUY",
            "strength": float(min(acceleration * 200, 1.0))
        })
    elif acceleration < -0.005:  # Accelerating downward
        momentum_signals.append({
            "type": "accelerating_downward",
            "signal": "SELL",
            "strength": float(min(abs(acceleration) * 200, 1.0))
        })
    
    return {
        "roc_5_periods": float(roc_5),
        "roc_10_periods": float(roc_10),
        "acceleration": float(acceleration),
        "signals": momentum_signals
    }

def _detect_rejection_patterns(open_price: np.ndarray, high: np.ndarray, low: np.ndarray, close: np.ndarray) -> Dict:
    """Detect price rejection patterns at key levels"""
    if len(close) < 5:
        return {}
    
    rejection_patterns = []
    
    # Analyze last few candles for rejection
    for i in range(max(0, len(close) - 5), len(close)):
        if i >= len(close):
            continue
            
        o, h, l, c = open_price[i], high[i], low[i], close[i]
        body = abs(c - o)
        total_range = h - l
        
        if total_range == 0:
            continue
        
        upper_wick = h - max(o, c)
        lower_wick = min(o, c) - l
        
        # Upper rejection (bearish)
        if upper_wick > body * 1.5 and upper_wick > total_range * 0.4:
            rejection_patterns.append({
                "type": "upper_rejection",
                "signal": "SELL",
                "strength": float(min(upper_wick / body / 2, 1.0)),
                "rejection_level": float(h),
                "candle_index": int(i)
            })
        
        # Lower rejection (bullish)
        if lower_wick > body * 1.5 and lower_wick > total_range * 0.4:
            rejection_patterns.append({
                "type": "lower_rejection",
                "signal": "BUY",
                "strength": float(min(lower_wick / body / 2, 1.0)),
                "rejection_level": float(l),
                "candle_index": int(i)
            })
    
    return {"patterns": rejection_patterns}

def get_chart_patterns(api, timeframe: int = 60, ticker: str = "EURUSD_otc", num_candles: int = 100) -> Dict:
    """Get chart pattern analysis for a trading pair"""
    try:
        df = _fetch_candles(api, ticker, timeframe, num_candles)
        if df.empty:
            return {"error": "No candle data available"}
        
        patterns = detect_chart_patterns(df)
        
        # Add overall pattern signal
        detected_patterns = []
        buy_signals = 0
        sell_signals = 0
        
        for pattern_name, pattern_data in patterns.items():
            if isinstance(pattern_data, dict) and pattern_data.get('detected', False):
                detected_patterns.append({
                    "pattern": pattern_name,
                    "signal": pattern_data.get('signal', 'NEUTRAL'),
                    "confidence": pattern_data.get('confidence', 0),
                    "details": pattern_data
                })
                
                if pattern_data.get('signal') == 'BUY':
                    buy_signals += 1
                elif pattern_data.get('signal') == 'SELL':
                    sell_signals += 1
        
        # Determine overall signal
        if buy_signals > sell_signals:
            overall_signal = "BUY"
        elif sell_signals > buy_signals:
            overall_signal = "SELL"
        else:
            overall_signal = "NEUTRAL"
        
        return {
            "ticker": ticker,
            "timeframe": timeframe,
            "analysis_time": time.time(),
            "overall_signal": overall_signal,
            "detected_patterns": detected_patterns,
            "pattern_summary": {
                "total_patterns": len(detected_patterns),
                "buy_patterns": buy_signals,
                "sell_patterns": sell_signals
            },
            "all_patterns": patterns
        }
        
    except Exception as e:
        return {"error": f"Chart pattern analysis failed: {str(e)}"}

def get_price_action_analysis(api, timeframe: int = 60, ticker: str = "EURUSD_otc", num_candles: int = 100) -> Dict:
    """Get comprehensive price action analysis"""
    try:
        df = _fetch_candles(api, ticker, timeframe, num_candles)
        if df.empty:
            return {"error": "No candle data available"}
        
        price_action = detect_price_action(df)
        
        # Consolidate signals
        all_signals = []
        buy_count = 0
        sell_count = 0
        
        # Process candlestick patterns
        if 'candlestick_patterns' in price_action:
            for pattern_name, pattern_data in price_action['candlestick_patterns'].items():
                signal = pattern_data.get('signal', 'NEUTRAL')
                all_signals.append(f"Candlestick {pattern_data.get('pattern', pattern_name)}: {signal}")
                if signal == 'BUY':
                    buy_count += 1
                elif signal == 'SELL':
                    sell_count += 1
        
        # Process breakout signals
        if 'breakout_signals' in price_action and 'signals' in price_action['breakout_signals']:
            for breakout in price_action['breakout_signals']['signals']:
                signal = breakout.get('signal', 'NEUTRAL')
                all_signals.append(f"Breakout {breakout.get('type', 'unknown')}: {signal}")
                if signal == 'BUY':
                    buy_count += 1
                elif signal == 'SELL':
                    sell_count += 1
        
        # Process momentum signals
        if 'momentum_signals' in price_action and 'signals' in price_action['momentum_signals']:
            for momentum in price_action['momentum_signals']['signals']:
                signal = momentum.get('signal', 'NEUTRAL')
                all_signals.append(f"Momentum {momentum.get('type', 'unknown')}: {signal}")
                if signal == 'BUY':
                    buy_count += 1
                elif signal == 'SELL':
                    sell_count += 1
        
        # Process rejection patterns
        if 'rejection_patterns' in price_action and 'patterns' in price_action['rejection_patterns']:
            for rejection in price_action['rejection_patterns']['patterns']:
                signal = rejection.get('signal', 'NEUTRAL')
                all_signals.append(f"Rejection {rejection.get('type', 'unknown')}: {signal}")
                if signal == 'BUY':
                    buy_count += 1
                elif signal == 'SELL':
                    sell_count += 1
        
        # Determine overall signal
        total_signals = buy_count + sell_count
        if total_signals == 0:
            overall_signal = "NO_DATA"
        elif buy_count > sell_count * 1.5:
            overall_signal = "STRONG_BUY"
        elif buy_count > sell_count:
            overall_signal = "BUY"
        elif sell_count > buy_count * 1.5:
            overall_signal = "STRONG_SELL"
        elif sell_count > buy_count:
            overall_signal = "SELL"
        else:
            overall_signal = "NEUTRAL"
        
        return {
            "ticker": ticker,
            "timeframe": timeframe,
            "analysis_time": time.time(),
            "overall_signal": overall_signal,
            "signal_summary": {
                "buy_signals": buy_count,
                "sell_signals": sell_count,
                "total_signals": total_signals,
                "signal_strength": max(buy_count, sell_count) / total_signals if total_signals > 0 else 0
            },
            "individual_signals": all_signals,
            "price_action_details": price_action
        }
        
    except Exception as e:
        return {"error": f"Price action analysis failed: {str(e)}"}

def get_comprehensive_analysis(api, timeframe: int = 60, ticker: str = "EURUSD_otc", num_candles: int = 200) -> Dict:
    """Get comprehensive technical analysis including indicators, patterns, and price action"""
    try:
        # Get all individual analyses
        indicators = get_all_indicators(api, timeframe, ticker, num_candles)
        chart_patterns = get_chart_patterns(api, timeframe, ticker, num_candles)
        price_action = get_price_action_analysis(api, timeframe, ticker, num_candles)
        trading_signals = get_trading_signals(api, timeframe, ticker, num_candles)
        
        # Combine all signals
        all_buy_signals = 0
        all_sell_signals = 0
        all_individual_signals = []
        
        # Count signals from trading_signals (indicators)
        if 'buy_signals' in trading_signals:
            all_buy_signals += trading_signals['buy_signals']
        if 'sell_signals' in trading_signals:
            all_sell_signals += trading_signals['sell_signals']
        if 'individual_signals' in trading_signals:
            all_individual_signals.extend(trading_signals['individual_signals'])
        
        # Count signals from chart patterns
        if 'pattern_summary' in chart_patterns:
            all_buy_signals += chart_patterns['pattern_summary'].get('buy_patterns', 0)
            all_sell_signals += chart_patterns['pattern_summary'].get('sell_patterns', 0)
        
        # Count signals from price action
        if 'signal_summary' in price_action:
            all_buy_signals += price_action['signal_summary'].get('buy_signals', 0)
            all_sell_signals += price_action['signal_summary'].get('sell_signals', 0)
        if 'individual_signals' in price_action:
            all_individual_signals.extend(price_action['individual_signals'])
        
        # Determine final overall signal
        total_signals = all_buy_signals + all_sell_signals
        if total_signals == 0:
            final_signal = "NO_DATA"
        elif all_buy_signals > all_sell_signals * 2:
            final_signal = "VERY_STRONG_BUY"
        elif all_buy_signals > all_sell_signals * 1.5:
            final_signal = "STRONG_BUY"
        elif all_buy_signals > all_sell_signals:
            final_signal = "BUY"
        elif all_sell_signals > all_buy_signals * 2:
            final_signal = "VERY_STRONG_SELL"
        elif all_sell_signals > all_buy_signals * 1.5:
            final_signal = "STRONG_SELL"
        elif all_sell_signals > all_buy_signals:
            final_signal = "SELL"
        else:
            final_signal = "NEUTRAL"
        
        return {
            "ticker": ticker,
            "timeframe": timeframe,
            "analysis_time": time.time(),
            "final_signal": final_signal,
            "comprehensive_summary": {
                "total_buy_signals": all_buy_signals,
                "total_sell_signals": all_sell_signals,
                "total_signals": total_signals,
                "signal_confidence": max(all_buy_signals, all_sell_signals) / total_signals if total_signals > 0 else 0
            },
            "all_individual_signals": all_individual_signals,
            "detailed_analysis": {
                "technical_indicators": indicators,
                "chart_patterns": chart_patterns,
                "price_action": price_action,
                "trading_signals": trading_signals
            }
        }
        
    except Exception as e:
        return {"error": f"Comprehensive analysis failed: {str(e)}"}
