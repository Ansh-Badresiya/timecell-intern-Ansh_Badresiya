# Task 2: Live Market Data Fetcher

## Overview
This script is a **Live Market Data Fetcher** that retrieves real-time pricing for a set of diverse assets (equities, crypto, commodities) and uses a generative AI model (Google Gemini or OpenAI) to provide a plain-English, jargon-free summary of the current market mood.

## Workflow
1. **API Integration**: 
   - Uses `yfinance` to fetch the NIFTY 50 Indian stock index (`^NSEI`).
   - Uses the public CoinGecko API to fetch Bitcoin (`BTC`) prices in USD.
   - Uses `yfinance` to fetch COMEX Gold Futures (`GC=F`) in USD.
2. **Graceful Error Handling**: Each asset is fetched independently. If one API fails or times out, the others will still complete successfully.
3. **Prompt Engineering**: The script strips the raw prices into a heavily structured prompt, instructing the LLM to output exactly 1 sentence of mood, followed by 2-3 bullet points without any Markdown or special formatting.
4. **LLM Fallback System**: It attempts to call Google Gemini first. If the quota is exceeded or it fails, it gracefully falls back to OpenAI GPT-3.5-Turbo.

## How to Run
First, ensure you have a `.env` file in the `task-2` directory with your API keys:
```env
GEMINI_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
```
Then run the script:
```bash
python live_market_data_fetch.py
```

## Expected Output
The terminal will display a colorful, formatted ASCII interface:
1. **Live Fetch Status**: Real-time `[OK]` or `[!]` lines as it contacts the APIs to retrieve prices.
2. **Asset Price Table**: A cleanly formatted table showing the Asset Name, comma-separated Price, and Currency.
3. **AI Market Insight**: A color-coded box showing which LLM provider was used, followed by a dynamically wrapped, plain-text summary of the current market conditions formatted as clean bullet points.
