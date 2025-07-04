"""
Async wrapper for BinaryOptionsTools V1 PocketOption API
This module provides an async interface compatible with the BinaryOptionsToolsV2 usage
"""
import asyncio
import time
import logging
from concurrent.futures import ThreadPoolExecutor
from BinaryOptionsToolsAsync.platforms.pocketoption.stable_api import PocketOption


class PocketOptionAsync:
    """Async wrapper for PocketOption V1 API"""
    
    def __init__(self, ssid: str, demo: bool = True):
        self.ssid = ssid
        self.demo = demo
        self._api = None
        self._executor = ThreadPoolExecutor(max_workers=1)
        self.logger = logging.getLogger("PocketOptionAsync")
        
    async def _ensure_connected(self):
        """Ensure the API is connected"""
        if self._api is None:
            self._api = PocketOption(self.ssid, self.demo)
            # Run connection in executor to avoid blocking
            await asyncio.get_event_loop().run_in_executor(
                self._executor, self._api.connect
            )
            # Wait a bit for connection to stabilize
            await asyncio.sleep(2)
    
    async def balance(self):
        """Get account balance"""
        await self._ensure_connected()
        return await asyncio.get_event_loop().run_in_executor(
            self._executor, self._api.get_balance
        )
    
    async def get_candles(self, asset: str, period: int, duration: int):
        """Get historical candles
        
        Args:
            asset: Trading asset (e.g., "EURUSD_otc")
            period: Timeframe in seconds
            duration: Duration in seconds to fetch history
        """
        await self._ensure_connected()
        
        # Calculate count based on duration and period
        count = max(10, duration // period)
        
        def _get_candles():
            return self._api.get_candles(asset, period, None, count, 1)
        
        return await asyncio.get_event_loop().run_in_executor(
            self._executor, _get_candles
        )
    
    async def buy(self, asset: str, amount: float, time: int, check_win: bool = False):
        """Open a buy (call) trade
        
        Args:
            asset: Trading asset
            amount: Trade amount
            time: Expiration time in seconds
            check_win: Whether to check win status immediately
            
        Returns:
            Tuple of (trade_id, success_status)
        """
        await self._ensure_connected()
        
        def _buy():
            try:
                result = self._api.buy(amount, asset, "call", time)
                if isinstance(result, tuple) and len(result) >= 2:
                    success = result[0]
                    trade_id = result[1]
                    return trade_id, success
                else:
                    return None, False
            except Exception as e:
                self.logger.error(f"Buy error: {e}")
                return None, False
        
        return await asyncio.get_event_loop().run_in_executor(
            self._executor, _buy
        )
    
    async def sell(self, asset: str, amount: float, time: int, check_win: bool = False):
        """Open a sell (put) trade
        
        Args:
            asset: Trading asset
            amount: Trade amount
            time: Expiration time in seconds
            check_win: Whether to check win status immediately
            
        Returns:
            Tuple of (trade_id, success_status)
        """
        await self._ensure_connected()
        
        def _sell():
            try:
                result = self._api.buy(amount, asset, "put", time)
                if isinstance(result, tuple) and len(result) >= 2:
                    success = result[0]
                    trade_id = result[1]
                    return trade_id, success
                else:
                    return None, False
            except Exception as e:
                self.logger.error(f"Sell error: {e}")
                return None, False
        
        return await asyncio.get_event_loop().run_in_executor(
            self._executor, _sell
        )
    
    async def check_win(self, trade_id: str):
        """Check trade result
        
        Args:
            trade_id: Trade ID to check
            
        Returns:
            Dictionary with trade result information
        """
        await self._ensure_connected()
        
        def _check_win():
            try:
                result = self._api.check_win(trade_id)
                if isinstance(result, tuple) and len(result) >= 2:
                    profit = result[0]
                    status = result[1]
                    return {
                        "result": status,
                        "trade_id": trade_id,
                        "profit": profit,
                        "amount": profit if profit else 0
                    }
                elif isinstance(result, dict):
                    return result
                else:
                    # Convert to expected format
                    return {
                        "result": "win" if result else "loss",
                        "trade_id": trade_id,
                        "amount": 0,
                        "profit": 0
                    }
            except Exception as e:
                self.logger.error(f"Check win error: {e}")
                return {
                    "result": "error",
                    "message": str(e),
                    "trade_id": trade_id
                }
        
        return await asyncio.get_event_loop().run_in_executor(
            self._executor, _check_win
        )
    
    async def get_payout(self, asset: str):
        """Get payout percentage for an asset
        
        Args:
            asset: Trading asset
            
        Returns:
            Payout percentage
        """
        await self._ensure_connected()
        
        def _get_payout():
            try:
                return self._api.GetPayout(asset)
            except Exception as e:
                self.logger.error(f"Get payout error: {e}")
                return 0
        
        return await asyncio.get_event_loop().run_in_executor(
            self._executor, _get_payout
        )
    
    async def close(self):
        """Close the API connection"""
        if self._executor:
            self._executor.shutdown(wait=True)
