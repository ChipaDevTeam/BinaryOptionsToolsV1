# Made by © Vigo Walker and © Alexandre Portner at Chipa

import asyncio
import threading
import sys
from tzlocal import get_localzone
import json
from BinaryOptionsTools.platforms.pocketoption.api import PocketOptionAPI
# import pocketoptionapi.country_id as Country
# import threading
import time
import logging
import BinaryOptionsTools.platforms.pocketoption.global_value as global_value
from collections import defaultdict
# from pocketoptionapi.expiration import get_expiration_time, get_remaning_time
import pandas as pd

# Obtener la zona horaria local del sistema como una cadena en el formato IANA
local_zone_name = get_localzone()


def nested_dict(n, type):
    if n == 1:
        return defaultdict(type)
    else:
        return defaultdict(lambda: nested_dict(n - 1, type))


def get_balance():
    # balances_raw = self.get_balances()
    return global_value.balance


class PocketOption:
    __version__ = "1.0.0"

    def __init__(self, ssid,demo):
        self.size = [1, 5, 10, 15, 30, 60, 120, 300, 600, 900, 1800,
                     3600, 7200, 14400, 28800, 43200, 86400, 604800, 2592000]
        global_value.SSID = ssid
        global_value.DEMO = demo
        global_value.IS_DEMO = demo
        print(demo)
        self.suspend = 0.5
        self.thread = None
        self.subscribe_candle = []
        self.subscribe_candle_all_size = []
        self.subscribe_mood = []
        # for digit
        self.get_digital_spot_profit_after_sale_data = nested_dict(2, int)
        self.get_realtime_strike_list_temp_data = {}
        self.get_realtime_strike_list_temp_expiration = 0
        self.SESSION_HEADER = {
            "User-Agent": r"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                          r"Chrome/66.0.3359.139 Safari/537.36"}
        self.SESSION_COOKIE = {}
        self.api = PocketOptionAPI()
        self.loop = asyncio.get_event_loop()
        self.logger = logging.getLogger("PocketOption")

        # Initialize OHLC aggregation system
        from .ohlc_aggregator import SubscriptionManager
        self.ohlc_manager = SubscriptionManager()
        self.ohlc_subscriptions = {}  # Track OHLC subscriptions

        #

        # --start
        # self.connect()
        # this auto function delay too long

    # --------------------------------------------------------------------------

    def get_server_timestamp(self):
        return self.api.time_sync.server_timestamp
    def Stop(self):
        sys.exit()

    def get_server_datetime(self):
        return self.api.time_sync.server_datetime

    def set_session(self, header, cookie):
        self.SESSION_HEADER = header
        self.SESSION_COOKIE = cookie

    def get_async_order(self, buy_order_id):
        # name': 'position-changed', 'microserviceName': "portfolio"/"digital-options"
        if self.api.order_async["deals"][0]["id"] == buy_order_id:
            return self.api.order_async["deals"][0]
        else:
            return None

    def get_async_order_id(self, buy_order_id):
        return self.api.order_async["deals"][0][buy_order_id]

    def start_async(self):
        asyncio.run(self.api.connect())
    def disconnect(self):
        """Gracefully close the WebSocket connection and clean up."""
        try:
            # Close the WebSocket connection
            if global_value.websocket_is_connected:
                asyncio.run(self.api.close())  # Use the close method from the PocketOptionAPI class
                print("WebSocket connection closed successfully.")
            else:
                print("WebSocket was not connected.")

            # Cancel any running asyncio tasks
            if self.loop is not None:
                for task in asyncio.all_tasks(self.loop):
                    task.cancel()

                # If you were using a custom event loop, stop and close it
                if not self.loop.is_closed():
                    self.loop.stop()
                    self.loop.close()
                    print("Event loop stopped and closed successfully.")

            # Clean up the WebSocket thread if it's still running
            if self.api.websocket_thread is not None and self.api.websocket_thread.is_alive():
                self.api.websocket_thread.join()
                print("WebSocket thread joined successfully.")

        except Exception as e:
            self.logger.warning(f"Error during disconnect: {e}")
            print(f"Error during disconnect: {e}")

    def connect(self):
        """
        Método síncrono para establecer la conexión.
        Utiliza internamente el bucle de eventos de asyncio para ejecutar la coroutine de conexión.
        """
        try:
            # Iniciar el hilo que manejará la conexión WebSocket
            websocket_thread = threading.Thread(target=self.api.connect, daemon=True)
            websocket_thread.start()

        except Exception as e:
            self.logger.warning(f"Error to connect: {e}")
            print(f"Error al conectar: {e}")
            return False
        return True
    
    def GetPayout(self, pair):
        try:
            data = self.api.GetPayoutData()
            data = json.loads(data)
            self.logger.debug(f"PayoutData: {data}")
            data2 = None
            for i in data:
                #print(f"Checking for: {i[1]}")
                if i[1] == pair:
                    data2 = i

            #print(f"Data2: {data2}")
            #print(f"Target: {pair}")
            return data2[5]
        except Exception as e:
            self.logger.warning(f"Error getting payout {e}")
            return None

    @staticmethod
    def check_connect():
        # True/False
        if global_value.websocket_is_connected == 0:
            return False
        elif global_value.websocket_is_connected is None:
            return False
        else:
            return True

        # wait for timestamp getting

    # self.update_ACTIVES_OPCODE()
    @staticmethod
    def get_balance():
        if global_value.balance_updated:
            return global_value.balance
        else:
            return None
    @staticmethod
    def check_open():
        #print(global_value.order_open)
        return global_value.order_open
    @staticmethod
    def check_order_closed(ido):
        
        while ido not in global_value.order_closed :
            time.sleep(0.1)

        for pack in global_value.stat :
            if pack[0] == ido :
               print('Order Closed',pack[1])

        #print(global_value.order_closed)
        return pack[0]
    
    
    def buy(self, amount, active, action, expirations):
        self.api.buy_multi_option = {}
        self.api.buy_successful = None
        req_id = "buy"

        try:
            if req_id not in self.api.buy_multi_option:
                self.api.buy_multi_option[req_id] = {"id": None}
            else:
                self.api.buy_multi_option[req_id]["id"] = None
        except Exception as e:
            logging.error(f"Error initializing buy_multi_option: {e}")
            return False, None

        global_value.order_data = None
        global_value.result = None

        

        self.api.buyv3(amount, active, action, expirations, req_id)

        start_t = time.time()
        while True:
            if global_value.result is not None and global_value.order_data is not None:
                break
            if time.time() - start_t >= 5:
                if isinstance(global_value.order_data, dict) and "error" in global_value.order_data:
                    logging.error(global_value.order_data["error"])
                else:
                    logging.error("Unknown error occurred during buy operation")
                return False, None
            time.sleep(0.1)  # Sleep for a short period to prevent busy-waiting

        return global_value.result, global_value.order_data.get("id", None)

    def check_win(self, id_number):
        """Return amount of deals and win/lose status."""

        start_t = time.time()
        order_info = None

        while True:
            try:
                order_info = self.get_async_order(id_number)
                if order_info and "id" in order_info and order_info["id"] is not None:
                    break
            except Exception as e:
                self.logger.debug(f"CheckWin: error: {e}")
                pass
            # except Exception as e:
            #    logging.error(f"Error retrieving order info: {e}")

            if time.time() - start_t >= 120:
                logging.error("Timeout: Could not retrieve order info in time.")
                return None, "unknown"

            time.sleep(0.1)  # Sleep for a short period to prevent busy-waiting

        if order_info and "profit" in order_info:
            status = "win" if order_info["profit"] > 0 else "lose"
            if order_info["profit"] > 0:
                status = "win"
            elif order_info["profit"] == 0:
                status == "draw"
            else:
                status == "loss"
            return order_info["profit"], status
        else:
            logging.error("Invalid order info retrieved.")
            return None, "unknown"

    @staticmethod
    def last_time(timestamp, period):
        # Divide por 60 para convertir a minutos, usa int() para truncar al entero más cercano (redondear hacia abajo),
        # y luego multiplica por 60 para volver a convertir a segundos.
        timestamp_redondeado = (timestamp // period) * period
        return int(timestamp_redondeado)

    def get_candles(self, active, period, start_time=None, count=6000, count_request=1):
        """
        Obtiene datos históricos de velas usando suscripción a candles y peticiones históricas.
        Devuelve un DataFrame ordenado de menor a mayor por la columna 'time'.

        :param active: El activo para el cual obtener las velas.
        :param period: El intervalo de tiempo de cada vela en segundos.
        :param count: El número de segundos a obtener en cada petición, max: 9000 = 150 datos de 1 min.
        :param start_time: El tiempo final para la última vela.
        :param count_request: El número de peticiones para obtener más datos históricos.
        """
        try:
            # Subscribe to candles for real-time data first
            self.subscribe_candles(active)
            
            if start_time is None:
                time_sync = self.get_server_timestamp()
                time_red = self.last_time(time_sync, period)
            else:
                time_red = start_time
                time_sync = self.get_server_timestamp()

            all_candles = []
            max_retries = 3
            retry_delay = 0.5

            for request_num in range(count_request):
                self.api.history_data = None
                retries = 0
                
                while retries < max_retries:
                    try:
                        # Send candle request
                        self.api.getcandles(active, period, count, time_red)
                        
                        # Wait for history_data with improved timeout handling
                        timeout_counter = 0
                        max_timeout = 150  # Increased timeout for better reliability
                        
                        while self.api.history_data is None and timeout_counter < max_timeout:
                            time.sleep(0.1)
                            timeout_counter += 1
                            
                            # Check if we have real-time candle data available
                            if (hasattr(self.api, 'real_time_candles') and
                                active in self.api.real_time_candles and 
                                period in self.api.real_time_candles[active] and
                                len(self.api.real_time_candles[active][period]) > 0):
                                
                                # Use real-time candle data as fallback
                                print(f"Using real-time candle data for {active}")
                                real_time_data = list(self.api.real_time_candles[active][period].values())
                                if real_time_data:
                                    # Convert real-time data to the expected format
                                    formatted_data = []
                                    for candle in real_time_data[-min(len(real_time_data), count//period):]:
                                        if isinstance(candle, dict):
                                            formatted_data.append({
                                                'time': candle.get('time', 0),
                                                'open': candle.get('open', 0),
                                                'close': candle.get('close', 0),
                                                'high': candle.get('high', 0),
                                                'low': candle.get('low', 0),
                                                'volume': candle.get('volume', 0)
                                            })
                                    
                                    if formatted_data:
                                        all_candles.extend(formatted_data)
                                        break

                        if self.api.history_data is not None:
                            all_candles.extend(self.api.history_data)
                            break
                        elif timeout_counter >= max_timeout:
                            print(f"Timeout waiting for history data, attempt {retries + 1}/{max_retries}")
                            retries += 1
                            if retries < max_retries:
                                time.sleep(retry_delay)
                            else:
                                print(f"Failed to get candles after {max_retries} attempts")
                                break

                    except Exception as e:
                        print(f"Error in get_candles request {request_num + 1}: {e}")
                        retries += 1
                        if retries < max_retries:
                            time.sleep(retry_delay)
                        else:
                            break

                # Sort candles and update time_red for next request
                if all_candles:
                    all_candles = sorted(all_candles, key=lambda x: x.get("time", 0))
                    # Use the earliest time for the next request
                    time_red = all_candles[0]["time"]

            # Unsubscribe from candles to clean up
            try:
                self.unsubscribe_candles(active)
            except:
                pass

            if not all_candles:
                print(f"No candles received for {active}")
                return pd.DataFrame()

            # Remove duplicates based on time
            unique_candles = []
            seen_times = set()
            for candle in all_candles:
                candle_time = candle.get("time", 0)
                if candle_time not in seen_times:
                    seen_times.add(candle_time)
                    unique_candles.append(candle)

            # Create DataFrame with all obtained candles
            df_candles = pd.DataFrame(unique_candles)

            if df_candles.empty:
                print(f"DataFrame is empty for {active}")
                return df_candles

            # Ensure all required columns exist
            required_columns = ['time', 'open', 'high', 'low', 'close']
            for col in required_columns:
                if col not in df_candles.columns:
                    df_candles[col] = 0

            # Sort by time column (ascending order)
            df_candles = df_candles.sort_values(by='time').reset_index(drop=True)
            df_candles['time'] = pd.to_datetime(df_candles['time'], unit='s')
            df_candles.set_index('time', inplace=True)
            df_candles.index = df_candles.index.floor('1s')
            
            return df_candles
            
        except Exception as e:
            print(f"Error in get_candles: {e}")
            # Ensure cleanup
            try:
                self.unsubscribe_candles(active)
            except:
                pass
            return pd.DataFrame()

    @staticmethod
    def process_data_history(data, period):
        """
        Este método toma datos históricos, los convierte en un DataFrame de pandas, redondea los tiempos al minuto más cercano,
        y calcula los valores OHLC (Open, High, Low, Close) para cada minuto. Luego, convierte el resultado en un diccionario
        y lo devuelve.

        :param dict data: Datos históricos que incluyen marcas de tiempo y precios.
        :param int period: Periodo en minutos
        :return: Un diccionario que contiene los valores OHLC agrupados por minutos redondeados.
        """
        # Crear DataFrame
        df = pd.DataFrame(data['history'], columns=['timestamp', 'price'])
        # Convertir a datetime y redondear al minuto
        df['datetime'] = pd.to_datetime(df['timestamp'], unit='s', utc=True)
        # df['datetime'] = df['datetime'].dt.tz_convert(str(local_zone_name))
        df['minute_rounded'] = df['datetime'].dt.floor(f'{period / 60}min')

        # Calcular OHLC
        ohlcv = df.groupby('minute_rounded').agg(
            open=('price', 'first'),
            high=('price', 'max'),
            low=('price', 'min'),
            close=('price', 'last')
        ).reset_index()

        ohlcv['time'] = ohlcv['minute_rounded'].apply(lambda x: int(x.timestamp()))
        ohlcv = ohlcv.drop(columns='minute_rounded')

        ohlcv = ohlcv.iloc[:-1]

        ohlcv_dict = ohlcv.to_dict(orient='records')

        return ohlcv_dict

    @staticmethod
    def process_candle(candle_data, period):
        """
        Resumen: Este método estático de Python, denominado `process_candle`, toma datos de velas financieras y un período de tiempo específico como entrada.
        Realiza varias operaciones de limpieza y organización de datos utilizando pandas, incluyendo la ordenación por tiempo, eliminación de duplicados,
        y reindexación. Además, verifica si las diferencias de tiempo entre las entradas consecutivas son iguales al período especificado y retorna tanto el DataFrame procesado
        como un booleano indicando si todas las diferencias son iguales al período dado. Este método es útil para preparar y verificar la consistencia de los datos de velas financieras
        para análisis posteriores.

        Procesa los datos de las velas recibidos como entrada.
        Convierte los datos de entrada en un DataFrame de pandas, los ordena por tiempo de forma ascendente,
        elimina duplicados basados en la columna 'time', y reinicia el índice del DataFrame.
        Adicionalmente, verifica si las diferencias de tiempo entre las filas consecutivas son iguales al período especificado,
        asumiendo que el período está dado en segundos, e imprime si todas las diferencias son de 60 segundos.
        :param list candle_data: Datos de las velas a procesar.
        :param int period: El período de tiempo entre las velas, usado para la verificación de diferencias de tiempo.
        :return: DataFrame procesado con los datos de las velas.
        """
        # Convierte los datos en un DataFrame y los añade al DataFrame final
        data_df = pd.DataFrame(candle_data)
        # datos_completos = pd.concat([datos_completos, data_df], ignore_index=True)
        # Procesa los datos obtenidos
        data_df.sort_values(by='time', ascending=True, inplace=True)
        data_df.drop_duplicates(subset='time', keep="first", inplace=True)
        data_df.reset_index(drop=True, inplace=True)
        data_df.ffill(inplace=True)
        #data_df.drop(columns='symbol_id', inplace=True)
        # Verificación opcional: Comprueba si las diferencias son todas de 60 segundos (excepto el primer valor NaN)
        diferencias = data_df['time'].diff()
        diff = (diferencias[1:] == period).all()
        return data_df, diff

    def change_symbol(self, active, period):
        return self.api.change_symbol(active, period)

    def sync_datetime(self):
        return self.api.synced_datetime

    def subscribe_candles(self, active, create_ohlc=False, timeframe_seconds=60, max_candles=1000, on_candle_complete=None):
        """
        Subscribe to candle data for a trading pair.
        
        Args:
            active: Trading pair (e.g., "AEDCNY_otc")
            create_ohlc: If True, aggregates tick data into OHLC candles
            timeframe_seconds: Timeframe for OHLC candles in seconds (default: 60)
            max_candles: Maximum number of OHLC candles to keep in memory
            on_candle_complete: Callback function called when an OHLC candle is completed
            
        Returns:
            Result of candle subscription request
        """
        try:
            # Subscribe to raw tick data
            result = self.api.subscribe_candles(active)
            
            # If OHLC aggregation is requested, set it up
            if create_ohlc:
                success = self.ohlc_manager.subscribe_candles_ohlc(
                    asset=active,
                    timeframe_seconds=timeframe_seconds,
                    max_candles=max_candles,
                    on_candle_complete=on_candle_complete
                )
                
                if success:
                    # Track this subscription
                    self.ohlc_subscriptions[active] = {
                        'timeframe': timeframe_seconds,
                        'max_candles': max_candles,
                        'callback': on_candle_complete
                    }
                    self.logger.info(f"OHLC aggregation enabled for {active} with {timeframe_seconds}s timeframe")
                else:
                    self.logger.warning(f"Failed to enable OHLC aggregation for {active}")
            
            return result
            
        except Exception as e:
            self.logger.warning(f"Error subscribing to candles for {active}: {e}")
            return None

    def unsubscribe_candles(self, active):
        """
        Unsubscribe from candle data for a trading pair.
        
        Args:
            active: Trading pair (e.g., "AEDCNY_otc")
            
        Returns:
            Result of candle unsubscription request
        """
        try:
            # Unsubscribe from OHLC aggregation if active
            if active in self.ohlc_subscriptions:
                timeframe = self.ohlc_subscriptions[active]['timeframe']
                self.ohlc_manager.unsubscribe_candles_ohlc(active, timeframe)
                del self.ohlc_subscriptions[active]
                self.logger.info(f"OHLC aggregation disabled for {active}")
            
            # Unsubscribe from raw tick data
            result = self.api.unsubscribe_candles(active)
            return result
            
        except Exception as e:
            self.logger.warning(f"Error unsubscribing from candles for {active}: {e}")
            return None
    
    def get_ohlc_candles(self, active, timeframe_seconds=60, count=None):
        """
        Get aggregated OHLC candles for a trading pair.
        
        Args:
            active: Trading pair (e.g., "AEDCNY_otc")
            timeframe_seconds: Timeframe in seconds
            count: Number of candles to return (None for all)
            
        Returns:
            List of OHLC candles in dictionary format
        """
        try:
            return self.ohlc_manager.get_candles(active, timeframe_seconds, count)
        except Exception as e:
            self.logger.warning(f"Error getting OHLC candles for {active}: {e}")
            return []
    
    def get_current_ohlc_candle(self, active, timeframe_seconds=60):
        """
        Get the current incomplete OHLC candle for a trading pair.
        
        Args:
            active: Trading pair (e.g., "AEDCNY_otc")
            timeframe_seconds: Timeframe in seconds
            
        Returns:
            Current incomplete candle or None
        """
        try:
            return self.ohlc_manager.get_current_candle(active, timeframe_seconds)
        except Exception as e:
            self.logger.warning(f"Error getting current OHLC candle for {active}: {e}")
            return None
    
    def get_ohlc_stats(self):
        """
        Get statistics about OHLC aggregation.
        
        Returns:
            Dictionary with aggregation statistics
        """
        try:
            stats = {}
            for timeframe, aggregator in self.ohlc_manager.aggregators.items():
                stats[f"{timeframe}s"] = aggregator.get_stats()
            return stats
        except Exception as e:
            self.logger.warning(f"Error getting OHLC stats: {e}")
            return {}
    
    # Technical Analysis Methods
    
    def get_technical_indicators(self, active="EURUSD_otc", timeframe=60, num_candles=200):
        """Get all technical indicators for a trading pair"""
        try:
            from BinaryOptionsTools.indicators.technical_analysis import get_all_indicators
            return get_all_indicators(self, timeframe, active, num_candles)
        except ImportError:
            return {"error": "Technical analysis module not available"}
        except Exception as e:
            return {"error": f"Technical indicators analysis failed: {str(e)}"}
    
    def get_trading_signals(self, active="EURUSD_otc", timeframe=60, num_candles=200):
        """Get consolidated trading signals from all indicators"""
        try:
            from BinaryOptionsTools.indicators.technical_analysis import get_trading_signals
            return get_trading_signals(self, timeframe, active, num_candles)
        except ImportError:
            return {"error": "Technical analysis module not available"}
        except Exception as e:
            return {"error": f"Trading signals analysis failed: {str(e)}"}
    
    def get_chart_patterns(self, active="EURUSD_otc", timeframe=60, num_candles=100):
        """Get chart pattern analysis for a trading pair"""
        try:
            from BinaryOptionsTools.indicators.technical_analysis import get_chart_patterns
            return get_chart_patterns(self, timeframe, active, num_candles)
        except ImportError:
            return {"error": "Technical analysis module not available"}
        except Exception as e:
            return {"error": f"Chart pattern analysis failed: {str(e)}"}
    
    def get_price_action_analysis(self, active="EURUSD_otc", timeframe=60, num_candles=100):
        """Get comprehensive price action analysis"""
        try:
            from BinaryOptionsTools.indicators.technical_analysis import get_price_action_analysis
            return get_price_action_analysis(self, timeframe, active, num_candles)
        except ImportError:
            return {"error": "Technical analysis module not available"}
        except Exception as e:
            return {"error": f"Price action analysis failed: {str(e)}"}
    
    def get_comprehensive_analysis(self, active="EURUSD_otc", timeframe=60, num_candles=200):
        """Get comprehensive technical analysis including indicators, patterns, and price action"""
        try:
            from BinaryOptionsTools.indicators.technical_analysis import get_comprehensive_analysis
            return get_comprehensive_analysis(self, timeframe, active, num_candles)
        except ImportError:
            return {"error": "Technical analysis module not available"}
        except Exception as e:
            return {"error": f"Comprehensive analysis failed: {str(e)}"}
    
    # Individual Indicator Methods
    
    def get_sma(self, active="EURUSD_otc", timeframe=60, period=20, num_candles=50):
        """Get Simple Moving Average"""
        try:
            from BinaryOptionsTools.indicators.technical_analysis import get_sma
            return get_sma(self, timeframe, active, period, num_candles)
        except ImportError:
            return {"error": "Technical analysis module not available"}
        except Exception as e:
            return {"error": f"SMA calculation failed: {str(e)}"}
    
    def get_ema(self, active="EURUSD_otc", timeframe=60, period=20, num_candles=50):
        """Get Exponential Moving Average"""
        try:
            from BinaryOptionsTools.indicators.technical_analysis import get_ema
            return get_ema(self, timeframe, active, period, num_candles)
        except ImportError:
            return {"error": "Technical analysis module not available"}
        except Exception as e:
            return {"error": f"EMA calculation failed: {str(e)}"}
    
    def get_rsi(self, active="EURUSD_otc", timeframe=60, period=14, num_candles=50):
        """Get Relative Strength Index"""
        try:
            from BinaryOptionsTools.indicators.technical_analysis import get_rsi
            return get_rsi(self, timeframe, active, period, num_candles)
        except ImportError:
            return {"error": "Technical analysis module not available"}
        except Exception as e:
            return {"error": f"RSI calculation failed: {str(e)}"}
    
    def get_macd(self, active="EURUSD_otc", timeframe=60, fast_period=12, slow_period=26, signal_period=9, num_candles=100):
        """Get MACD (Moving Average Convergence Divergence)"""
        try:
            from BinaryOptionsTools.indicators.technical_analysis import get_macd
            return get_macd(self, timeframe, active, fast_period, slow_period, signal_period, num_candles)
        except ImportError:
            return {"error": "Technical analysis module not available"}
        except Exception as e:
            return {"error": f"MACD calculation failed: {str(e)}"}
    
    def get_bollinger_bands(self, active="EURUSD_otc", timeframe=60, period=20, num_candles=50):
        """Get Bollinger Bands"""
        try:
            from BinaryOptionsTools.indicators.technical_analysis import get_bollinger_bands
            return get_bollinger_bands(self, timeframe, active, period, num_candles)
        except ImportError:
            return {"error": "Technical analysis module not available"}
        except Exception as e:
            return {"error": f"Bollinger Bands calculation failed: {str(e)}"}
    
    def get_stochastic(self, active="EURUSD_otc", timeframe=60, k_period=14, d_period=3, num_candles=50):
        """Get Stochastic Oscillator"""
        try:
            from BinaryOptionsTools.indicators.technical_analysis import get_stochastic
            return get_stochastic(self, timeframe, active, k_period, d_period, num_candles)
        except ImportError:
            return {"error": "Technical analysis module not available"}
        except Exception as e:
            return {"error": f"Stochastic calculation failed: {str(e)}"}
    
    def get_williams_r(self, active="EURUSD_otc", timeframe=60, period=14, num_candles=50):
        """Get Williams %R"""
        try:
            from BinaryOptionsTools.indicators.technical_analysis import get_williams_r
            return get_williams_r(self, timeframe, active, period, num_candles)
        except ImportError:
            return {"error": "Technical analysis module not available"}
        except Exception as e:
            return {"error": f"Williams %R calculation failed: {str(e)}"}
    
    def get_atr(self, active="EURUSD_otc", timeframe=60, period=14, num_candles=50):
        """Get Average True Range"""
        try:
            from BinaryOptionsTools.indicators.technical_analysis import get_atr
            return get_atr(self, timeframe, active, period, num_candles)
        except ImportError:
            return {"error": "Technical analysis module not available"}
        except Exception as e:
            return {"error": f"ATR calculation failed: {str(e)}"}
    
    def get_support_resistance(self, active="EURUSD_otc", timeframe=60, num_candles=100):
        """Get Support and Resistance levels"""
        try:
            from BinaryOptionsTools.indicators.technical_analysis import get_support_resistance
            return get_support_resistance(self, timeframe, active, num_candles)
        except ImportError:
            return {"error": "Technical analysis module not available"}
        except Exception as e:
            return {"error": f"Support/Resistance calculation failed: {str(e)}"}
