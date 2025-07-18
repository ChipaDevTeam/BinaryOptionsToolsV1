# BinaryOptionsTools

![CodeRabbit Pull Request Reviews](https://img.shields.io/coderabbit/prs/github/ChipaDevTeam/BinaryOptionsToolsV1?utm_source=oss&utm_medium=github&utm_campaign=ChipaDevTeam%2FBinaryOptionsToolsV1&labelColor=171717&color=FF570A&link=https%3A%2F%2Fcoderabbit.ai&label=CodeRabbit+Reviews)

**BinaryOptionsTools** is a set of tools designed to make binary options trading easier. It helps with market analysis, strategy creation, and automatic trading. Use these tools to make smarter trading decisions.

👉 [Join us on Discord](https://discord.gg/H8er9mbF4V)

---

## Support us
join PocketOption with our affiliate link: [https://pocket-friends.com/r/u9klnwxgcc](https://pocket-friends.com/r/u9klnwxgcc) <br>
donate in paypal: [Paypal.me](https://paypal.me/ChipaCL?country.x=CL&locale.x=en_US) <br> 
help us in patreon: [Patreon](https://patreon.com/VigoDEV?utm_medium=unknown&utm_source=join_link&utm_campaign=creatorshare_creator&utm_content=copyLink) <br>

## Features

- 📊 **Live market data**: Get the latest market updates instantly.
- 🔎 **Analysis tools**: Use built-in indicators to study market trends.
- 🤖 **Strategy tools**: Create, test, and improve your trading strategies.
- 📈 **Automatic trading**: Let the tools trade for you based on your strategies.

## Join the Community

Meet other traders, share ideas, and get updates about new features.  
👉 [Join us on Discord](https://discord.gg/H8er9mbF4V)

---

<details>
  <summary>How do I set up and start using BinaryOptionsTools?</summary>

  ### Prerequisite: Create a Virtual Environment
  Setting up a virtual environment helps manage dependencies better:

  #### On Windows:
  ```bash
  python -m venv env
  .\env\Scripts\activate
  ```

  #### On macOS/Linux:
  ```bash
  python3 -m venv env
  source env/bin/activate
  ```

  ### Installation Steps
  1. **Clone the Repository**
      ```bash
      git clone https://github.com/theshadow76/BinaryOptionsTools.git
      ```
     ```bash
      cd BinaryOptionsTools
      ```

  2. **Install Dependencies**
      ```bash
      pip install .
      ```

  3. **Run the Application**
      ```bash
      python setup.py
      ```
</details>

<details>
  <summary>What is BinaryOptionsTools?</summary>

  BinaryOptionsTools is a collection of tools to help you trade binary options better. It offers live data, analysis tools, strategy development, and automatic trading features.

</details>

<details>
  <summary>How do I install BinaryOptionsTools?</summary>

  Follow these steps:

  1. **Clone the repository:**
      ```bash
      git clone https://github.com/theshadow76/BinaryOptionsTools.git
      ```

  2. **Go to the project folder:**
      ```bash
      cd BinaryOptionsTools
      ```

  3. **Install required files:**
      ```bash
      pip install .
      ```

</details>

<details>
  <summary>How can I contribute to BinaryOptionsTools?</summary>

  We welcome help from everyone! Whether you find bugs, suggest improvements, or add new features, we encourage you to contribute.

  ### How to Contribute
  1. Fork the project.
  2. Create a new branch for your changes.
  3. Write clear and detailed commit messages.
  4. Open a pull request and explain your changes.

</details>

<details>
  <summary>How do I retrieve the authentication key for Pocket Option?</summary>

  Follow these steps to get your auth key from Pocket Option:

  1. **Go to Pocket Option Website**
      Open [Pocket Option](https://u3.shortink.io/smart/SDIaxbeamcYYqB) in your browser.

  2. **Open Developer Tools**
      Press `CTRL + Shift + I` to open Developer Tools. Then, go to the **Network** tab.

  3. **Refresh the Network Activity**
      Press `CTRL + R` to refresh and see new network activity.

  4. **Find WebSocket Activity**
      Click on **WS** (WebSocket) in the **Network** tab.

  5. **Locate the Auth Key**
      Click on the last WebSocket line under **WS**, then go to **Messages** on the right panel. Look for `auth`. Right-click the WebSocket line and select **Copy Message** to save the auth key.

</details>

---

## Async API Usage (BinaryOptionsToolsAsync)

You can use the async version for non-blocking trading bots and data collection. Here is a minimal example:

```python
import asyncio
from BinaryOptionsToolsAsync.pocketoption import PocketOptionAsync

async def main():
    ssid = input("Enter your ssid: ")
    api = PocketOptionAsync(ssid, demo=True)
    balance = await api.balance()
    print(f"[ASYNC] GET BALANCE: {balance}")
    await api.close()

if __name__ == "__main__":
    asyncio.run(main())
```

See `examples/async_minimal.py` for a more complete example, including candle fetching.

---
