Async API: Getting Started & Best Practices
============================================

.. note::
   This guide covers how to set up and use the async API, best practices, troubleshooting, and security tips.

Getting Started
---------------

1. **Install dependencies**
   - Make sure you have `pandas` and `asyncio` installed.
   - Install the package: `pip install .`

2. **Import and connect**

   .. code-block:: python

      from BinaryOptionsToolsAsync.pocketoption import PocketOptionAsync
      import asyncio

      async def main():
          api = PocketOptionAsync(ssid, demo=True)
          ...

3. **Fetch data and trade**
   - Use `await api.get_candles(...)`, `await api.buy(...)`, etc.

4. **Close the connection**
   - Always call `await api.close()` when done.

.. important::
   Always use `asyncio.sleep()` for timing, not `time.sleep()`.

Best Practices
--------------
- Handle exceptions with try/except to avoid crashes.
- Never hardcode your SSID or credentials in scripts.
- Test with demo accounts before real trading.
- Log all actions for debugging and audit.

Troubleshooting
---------------
- **Connection errors**: Check your SSID and internet connection.
- **API changes**: Update the package if PocketOption changes their API.
- **Rate limits**: Avoid rapid repeated requests; use delays.

.. warning::
   Keep your SSID secret. Use environment variables or config files for sensitive data.

Security & Real Trading
-----------------------
- Monitor your bot and set limits to avoid large losses.

See also: :doc:`async_examples` and :doc:`BinaryOptionsToolsAsync` for more details.
