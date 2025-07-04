"""
OHLC Candle Aggregator for real-time tick data.
This module aggregates streaming tick data into time-based OHLC candles.
"""

import time
from collections import defaultdict, deque
from datetime import datetime, timezone
import threading
import logging
from typing import Dict, List, Optional, Callable, Any


class OHLCCandle:
    """Represents a single OHLC candle."""
    
    def __init__(self, timestamp: int, open_price: float):
        self.timestamp = timestamp
        self.open = open_price
        self.high = open_price
        self.low = open_price
        self.close = open_price
        self.volume = 0
        self.tick_count = 1
        
    def update(self, price: float):
        """Update the candle with a new price tick."""
        self.high = max(self.high, price)
        self.low = min(self.low, price)
        self.close = price
        self.tick_count += 1
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert candle to dictionary format."""
        return {
            "time": self.timestamp,
            "open": self.open,
            "high": self.high,
            "low": self.low,
            "close": self.close,
            "volume": self.volume,
            "tick_count": self.tick_count
        }
        
    def __repr__(self):
        return f"OHLCCandle(time={self.timestamp}, O={self.open}, H={self.high}, L={self.low}, C={self.close})"


class CandleAggregator:
    """Aggregates real-time tick data into OHLC candles."""
    
    def __init__(self, timeframe_seconds: int = 60, max_candles: int = 1000, 
                 on_candle_complete: Optional[Callable] = None):
        """
        Initialize the candle aggregator.
        
        Args:
            timeframe_seconds: Timeframe for candles in seconds (default: 60 = 1 minute)
            max_candles: Maximum number of candles to keep in memory
            on_candle_complete: Callback function called when a candle is completed
        """
        self.timeframe = timeframe_seconds
        self.max_candles = max_candles
        self.on_candle_complete = on_candle_complete
        
        # Store candles per asset
        self.candles: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_candles))
        self.current_candles: Dict[str, OHLCCandle] = {}
        
        # Threading for thread-safe operations
        self.lock = threading.RLock()
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
    def _get_candle_timestamp(self, timestamp: float) -> int:
        """Get the candle timestamp for a given tick timestamp."""
        # Round down to the nearest timeframe boundary
        return int(timestamp // self.timeframe) * self.timeframe
        
    def add_tick(self, asset: str, timestamp: float, price: float) -> Optional[OHLCCandle]:
        """
        Add a new price tick and return completed candle if any.
        
        Args:
            asset: Asset symbol (e.g., "EURUSD_otc")
            timestamp: Tick timestamp (Unix timestamp)
            price: Tick price
            
        Returns:
            Completed candle if a candle boundary was crossed, None otherwise
        """
        with self.lock:
            candle_timestamp = self._get_candle_timestamp(timestamp)
            completed_candle = None
            
            # Check if we need to start a new candle
            if asset not in self.current_candles:
                # First tick for this asset
                self.current_candles[asset] = OHLCCandle(candle_timestamp, price)
                self.logger.debug(f"Started new candle for {asset} at {candle_timestamp}")
                
            elif self.current_candles[asset].timestamp != candle_timestamp:
                # New candle period - close current and start new
                completed_candle = self.current_candles[asset]
                self.candles[asset].append(completed_candle)
                
                self.logger.debug(f"Completed candle for {asset}: {completed_candle}")
                
                # Start new candle
                self.current_candles[asset] = OHLCCandle(candle_timestamp, price)
                
                # Call completion callback if provided
                if self.on_candle_complete:
                    try:
                        self.on_candle_complete(asset, completed_candle)
                    except Exception as e:
                        self.logger.error(f"Error in candle completion callback: {e}")
                        
            else:
                # Update current candle
                self.current_candles[asset].update(price)
                
            return completed_candle
            
    def get_candles(self, asset: str, count: int = None) -> List[Dict[str, Any]]:
        """
        Get completed candles for an asset.
        
        Args:
            asset: Asset symbol
            count: Number of candles to return (None for all)
            
        Returns:
            List of candles in dictionary format
        """
        with self.lock:
            if asset not in self.candles:
                return []
                
            candles_list = list(self.candles[asset])
            
            if count is not None:
                candles_list = candles_list[-count:]
                
            return [candle.to_dict() for candle in candles_list]
            
    def get_current_candle(self, asset: str) -> Optional[Dict[str, Any]]:
        """Get the current incomplete candle for an asset."""
        with self.lock:
            if asset in self.current_candles:
                return self.current_candles[asset].to_dict()
            return None
            
    def get_latest_candle(self, asset: str, include_current: bool = False) -> Optional[Dict[str, Any]]:
        """
        Get the latest candle for an asset.
        
        Args:
            asset: Asset symbol
            include_current: If True, return current incomplete candle if no completed candles exist
            
        Returns:
            Latest candle or None
        """
        with self.lock:
            # Try to get the latest completed candle
            if asset in self.candles and len(self.candles[asset]) > 0:
                return self.candles[asset][-1].to_dict()
                
            # If no completed candles and include_current is True, return current candle
            if include_current and asset in self.current_candles:
                return self.current_candles[asset].to_dict()
                
            return None
            
    def clear_asset_data(self, asset: str):
        """Clear all data for a specific asset."""
        with self.lock:
            if asset in self.candles:
                del self.candles[asset]
            if asset in self.current_candles:
                del self.current_candles[asset]
            self.logger.debug(f"Cleared all data for {asset}")
            
    def get_assets(self) -> List[str]:
        """Get list of assets with data."""
        with self.lock:
            assets = set(self.candles.keys())
            assets.update(self.current_candles.keys())
            return list(assets)
            
    def get_stats(self) -> Dict[str, Any]:
        """Get aggregator statistics."""
        with self.lock:
            stats = {
                "timeframe_seconds": self.timeframe,
                "max_candles": self.max_candles,
                "assets_count": len(self.get_assets()),
                "assets": {}
            }
            
            for asset in self.get_assets():
                completed_count = len(self.candles.get(asset, []))
                has_current = asset in self.current_candles
                current_ticks = self.current_candles[asset].tick_count if has_current else 0
                
                stats["assets"][asset] = {
                    "completed_candles": completed_count,
                    "has_current_candle": has_current,
                    "current_candle_ticks": current_ticks
                }
                
            return stats


class SubscriptionManager:
    """Manages multiple candle aggregators for different timeframes."""
    
    def __init__(self):
        self.aggregators: Dict[int, CandleAggregator] = {}
        self.subscriptions: Dict[str, List[int]] = defaultdict(list)  # asset -> [timeframes]
        self.lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
        
    def subscribe_candles_ohlc(self, asset: str, timeframe_seconds: int, 
                              max_candles: int = 1000, 
                              on_candle_complete: Optional[Callable] = None) -> bool:
        """
        Subscribe to OHLC candles for an asset with specific timeframe.
        
        Args:
            asset: Asset symbol
            timeframe_seconds: Candle timeframe in seconds
            max_candles: Maximum candles to keep
            on_candle_complete: Callback for completed candles
            
        Returns:
            True if subscription successful
        """
        with self.lock:
            try:
                # Create aggregator if it doesn't exist
                if timeframe_seconds not in self.aggregators:
                    self.aggregators[timeframe_seconds] = CandleAggregator(
                        timeframe_seconds=timeframe_seconds,
                        max_candles=max_candles,
                        on_candle_complete=on_candle_complete
                    )
                    
                # Add to subscriptions
                if timeframe_seconds not in self.subscriptions[asset]:
                    self.subscriptions[asset].append(timeframe_seconds)
                    
                self.logger.info(f"Subscribed {asset} to {timeframe_seconds}s candles")
                return True
                
            except Exception as e:
                self.logger.error(f"Error subscribing {asset} to candles: {e}")
                return False
                
    def unsubscribe_candles_ohlc(self, asset: str, timeframe_seconds: int = None) -> bool:
        """
        Unsubscribe from OHLC candles.
        
        Args:
            asset: Asset symbol
            timeframe_seconds: Specific timeframe to unsubscribe from (None for all)
            
        Returns:
            True if unsubscription successful
        """
        with self.lock:
            try:
                if asset not in self.subscriptions:
                    return True
                    
                if timeframe_seconds is None:
                    # Unsubscribe from all timeframes
                    for tf in self.subscriptions[asset]:
                        if tf in self.aggregators:
                            self.aggregators[tf].clear_asset_data(asset)
                    del self.subscriptions[asset]
                    self.logger.info(f"Unsubscribed {asset} from all candle timeframes")
                else:
                    # Unsubscribe from specific timeframe
                    if timeframe_seconds in self.subscriptions[asset]:
                        self.subscriptions[asset].remove(timeframe_seconds)
                        if timeframe_seconds in self.aggregators:
                            self.aggregators[timeframe_seconds].clear_asset_data(asset)
                            
                    if not self.subscriptions[asset]:
                        del self.subscriptions[asset]
                        
                    self.logger.info(f"Unsubscribed {asset} from {timeframe_seconds}s candles")
                    
                return True
                
            except Exception as e:
                self.logger.error(f"Error unsubscribing {asset} from candles: {e}")
                return False
                
    def process_tick(self, asset: str, timestamp: float, price: float):
        """Process a price tick for all relevant aggregators."""
        with self.lock:
            if asset in self.subscriptions:
                for timeframe in self.subscriptions[asset]:
                    if timeframe in self.aggregators:
                        self.aggregators[timeframe].add_tick(asset, timestamp, price)
                        
    def get_candles(self, asset: str, timeframe_seconds: int, count: int = None) -> List[Dict[str, Any]]:
        """Get candles for asset and timeframe."""
        with self.lock:
            if timeframe_seconds in self.aggregators:
                return self.aggregators[timeframe_seconds].get_candles(asset, count)
            return []
            
    def get_current_candle(self, asset: str, timeframe_seconds: int) -> Optional[Dict[str, Any]]:
        """Get current incomplete candle."""
        with self.lock:
            if timeframe_seconds in self.aggregators:
                return self.aggregators[timeframe_seconds].get_current_candle(asset)
            return None
