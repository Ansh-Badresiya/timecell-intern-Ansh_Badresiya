import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

"""
market_prices.py
================
Fetches current prices for three assets, prints a formatted table,
and optionally generates AI market commentary via a free LLM API.

Required libraries (install via pip):
    pip install yfinance requests tabulate python-dotenv google-genai openai

.env file should contain:
    GEMINI_API_KEY=your_google_gemini_key_here
    OPENAI_API_KEY=your_openai_key_here   # optional fallback

Assets fetched:
    1. NIFTY 50          Indian stock index  (via yfinance, symbol ^NSEI)
    2. Bitcoin (BTC)     Cryptocurrency      (via CoinGecko free API)
    3. Gold (XAU/USD)    Commodity           (via yfinance, symbol GC=F)
"""

import os
import re
import logging
import textwrap
from datetime import datetime, timezone, timedelta

# ═══════════════════════════════════════════════════════════════════════════════
#                               Third-party imports
# ═══════════════════════════════════════════════════════════════════════════════

try:
    import requests
except ImportError:
    sys.exit("Missing library: requests  →  pip install requests")

try:
    import yfinance as yf
except ImportError:
    sys.exit("Missing library: yfinance  →  pip install yfinance")

try:
    from tabulate import tabulate
except ImportError:
    sys.exit("Missing library: tabulate  →  pip install tabulate")

try:
    from dotenv import load_dotenv
except ImportError:
    sys.exit("Missing library: python-dotenv  →  pip install python-dotenv")

# ═══════════════════════════════════════════════════════════════════════════════
#                            Logging configuration
# ═══════════════════════════════════════════════════════════════════════════════

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)


load_dotenv()

# ═══════════════════════════════════════════════════════════════════════════════
#                              ANSI color codes
# ═══════════════════════════════════════════════════════════════════════════════

class Colors:
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RESET   = "\033[0m"

# ═══════════════════════════════════════════════════════════════════════════════
#                                IST timezone helper
# ═══════════════════════════════════════════════════════════════════════════════

IST = timezone(timedelta(hours=5, minutes=30))


def now_ist() -> str:
    """Return the current date-time as a formatted IST string."""
    return datetime.now(IST).strftime("%Y-%m-%d %H:%M:%S IST")


# ═════════════════════════════════════════════════════════════════════════════
#                        SECTION 1 – Asset-fetching functions
# ═════════════════════════════════════════════════════════════════════════════


def fetch_indian_index(symbol: str = "^NSEI", display_name: str = "NIFTY 50") -> dict | None:
    """
    Fetch the latest price of an Indian stock / index via yfinance.
    Returns dict {"asset", "price", "currency"} or None on failure.
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        price = info.last_price

        if price is None or price != price:   # NaN guard
            hist = ticker.history(period="1d")
            if hist.empty:
                raise ValueError(f"No price data returned for symbol '{symbol}'.")
            price = float(hist["Close"].iloc[-1])

        currency = getattr(info, "currency", "INR") or "INR"
        return {"asset": display_name, "price": float(price), "currency": currency}

    except Exception as exc:
        logger.error("Failed to fetch Indian index (%s): %s", symbol, exc)
        return None


def fetch_crypto_coingecko(coin_id: str = "bitcoin", display_name: str = "Bitcoin (BTC)") -> dict | None:
    """
    Fetch the current USD price of a cryptocurrency from CoinGecko.
    Free public API — no key required.
    Returns dict {"asset", "price", "currency"} or None on failure.
    """
    url = "https://api.coingecko.com/api/v3/simple/price"
    params = {"ids": coin_id, "vs_currencies": "usd"}

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if coin_id not in data or "usd" not in data[coin_id]:
            raise ValueError(f"Unexpected CoinGecko response for '{coin_id}': {data}")

        return {"asset": display_name, "price": float(data[coin_id]["usd"]), "currency": "USD"}

    except Exception as exc:
        logger.error("Failed to fetch crypto '%s' from CoinGecko: %s", coin_id, exc)
        return None


def fetch_commodity_yfinance(symbol: str = "GC=F", display_name: str = "Gold (XAU/USD)") -> dict | None:
    """
    Fetch the price of a commodity via yfinance.
    Default 'GC=F' is COMEX Gold Futures — a standard gold price proxy.
    Returns dict {"asset", "price", "currency"} or None on failure.
    """
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.fast_info
        price = info.last_price

        if price is None or price != price:
            hist = ticker.history(period="1d")
            if hist.empty:
                raise ValueError(f"No price data returned for symbol '{symbol}'.")
            price = float(hist["Close"].iloc[-1])

        currency = getattr(info, "currency", "USD") or "USD"
        return {"asset": display_name, "price": float(price), "currency": currency}

    except Exception as exc:
        logger.error("Failed to fetch commodity (%s): %s", symbol, exc)
        return None


# ═════════════════════════════════════════════════════════════════════════════
#                             SECTION 2 – Table formatting
# ═════════════════════════════════════════════════════════════════════════════


def print_banner():
    print()
    print(f"{Colors.BOLD}{Colors.CYAN}+================================================================================+{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}|                                                                                |{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}|                              LIVE MARKET PRICES                                |{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}|                  NIFTY 50  |  Bitcoin (BTC)  |  Gold (XAU/USD)                 |{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}|                                                                                |{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}+================================================================================+{Colors.RESET}")
    print()


def format_price(price: float) -> str:
    """Format price with comma-separated thousands and 2 decimal places."""
    return f"{price:,.2f}"


def print_price_table(results: list[dict], fetch_time: str) -> None:
    """Print a colored ASCII table of asset prices."""
    rows = []
    for item in results:
        if item is None:
            continue
        rows.append([item["asset"], format_price(item["price"]), item["currency"]])

    if not rows:
        print(f"\n{Colors.RED}[!] No asset prices could be fetched. Check your internet connection.{Colors.RESET}")
        return

    print(f"\n{Colors.BOLD}+{'=' * 60}+{Colors.RESET}")
    print(f"{Colors.BOLD}|  {Colors.CYAN}Asset Prices{Colors.RESET}{Colors.BOLD} -- fetched at {Colors.DIM}{fetch_time}{Colors.RESET}{Colors.BOLD}{'':>3}|{Colors.RESET}")
    print(f"{Colors.BOLD}+{'=' * 60}+{Colors.RESET}")
    print(
        tabulate(
            rows,
            headers=["Asset", "Price", "Currency"],
            tablefmt="pretty",
            colalign=("left", "right", "left"),
        )
    )
    print(f"{Colors.BOLD}+{'=' * 60}+{Colors.RESET}\n")


# ═════════════════════════════════════════════════════════════════════════════
#                           SECTION 3 – AI market commentary
# ═════════════════════════════════════════════════════════════════════════════


def strip_markdown(text: str) -> str:
    """
    Remove common markdown symbols from a string so it prints cleanly
    in a plain terminal.

    Handles: **bold**, *italic*, __underline__, `code`,
             ### headings, and leading markdown bullet markers (* or -).
    """
    # Remove bold/italic markers: ** or * or __ or _
    text = re.sub(r'\*{1,2}|_{1,2}', '', text)
    # Remove inline code backticks
    text = re.sub(r'`+', '', text)
    # Remove heading markers like ##, ###
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    # Replace markdown bullet (lines starting with * or + ) with a plain dash
    text = re.sub(r'^\s*[\*\+]\s+', '- ', text, flags=re.MULTILINE)
    # Collapse any leftover multiple spaces
    text = re.sub(r'  +', ' ', text)
    return text.strip()


def build_prompt(results: list[dict]) -> str:
    """
    Build the LLM prompt asking for a plain-text, jargon-free market insight.
    The prompt explicitly forbids markdown so the output is terminal-friendly.
    """
    lines = []
    for item in results:
        if item:
            lines.append(f"  - {item['asset']}: {format_price(item['price'])} {item['currency']}")

    prices_text = "\n".join(lines) if lines else "  (no price data available)"

    prompt = (
        "You are a helpful financial analyst talking to everyday people with no finance background.\n"
        "Based on the current market prices below, give a short, friendly market insight.\n\n"
        f"Current prices:\n{prices_text}\n\n"
        "STRICT FORMATTING RULES - follow these exactly or your response will be rejected:\n"
        "  1. Plain text ONLY. Absolutely no markdown.\n"
        "  2. Do NOT use asterisks (*), hashes (#), underscores (_), backticks, or any special symbols.\n"
        "  3. Use a simple dash (-) for bullet points, nothing else.\n"
        "  4. Start with one short sentence summarising the overall market mood.\n"
        "  5. Follow with 2-3 bullet points, each beginning with a plain dash (-).\n"
        "  6. Keep the entire response under 80 words.\n"
        "  7. Use plain everyday language - no jargon.\n\n"
        "Correct format example:\n"
        "Markets are showing mixed signals today.\n"
        "- Indian stocks are holding steady near recent highs.\n"
        "- Bitcoin is climbing, showing strong investor confidence in crypto.\n"
        "- Gold is rising slightly, hinting at some caution among investors.\n"
    )
    return prompt


def call_gemini(prompt: str) -> str:
    """
    Call Google Gemini using the new google-genai SDK.
    Install: pip install google-genai
    Requires GEMINI_API_KEY in .env
    """
    try:
        from google import genai as google_genai
    except ImportError:
        raise RuntimeError("google-genai not installed. Run: pip install google-genai")

    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY not set in .env")

    client = google_genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model="gemini-2.5-flash",   # 1500 req/day on free tier
        contents=prompt,
    )
    return response.text.strip()


def call_openai(prompt: str) -> str:
    """
    Call OpenAI (gpt-3.5-turbo) as a fallback.
    Requires OPENAI_API_KEY in .env
    """
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("openai not installed. Run: pip install openai")

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY not set in .env")

    client = OpenAI(api_key=api_key)
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=120,
        temperature=0.7,
    )
    return completion.choices[0].message.content.strip()


def get_ai_insight(results: list[dict]) -> None:
    """
    Detect which LLM API key is available, call it, clean the output,
    and print a plain-text market insight. Never raises — degrades gracefully.
    """
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not gemini_key and not openai_key:
        print(
            "[!] AI Market Insight skipped - no LLM API key found.\n"
            "    Set GEMINI_API_KEY or OPENAI_API_KEY in your .env file."
        )
        return

    prompt = build_prompt(results)
    insight_text = None
    provider = None

    # Prefer Gemini (generous free tier); fall back to OpenAI
    if gemini_key:
        try:
            insight_text = call_gemini(prompt)
            provider = "Google Gemini 2.5 Flash"
        except Exception as exc:
            print(f"    [!] Gemini call failed: {exc}")
            print("        Trying OpenAI fallback...")

    if insight_text is None and openai_key:
        try:
            insight_text = call_openai(prompt)
            provider = "OpenAI GPT-3.5-Turbo"
        except Exception as exc:
            print(f"    [!] OpenAI call failed: {exc}")

    # Prefer OpenAI (generous free tier); fall back to Gemini
    # if openai_key:
    #     try:
    #         insight_text = call_openai(prompt)
    #         provider = "OpenAI GPT-3.5-Turbo"
    #     except Exception as exc:
    #         print(f"    [!] OpenAI call failed: {exc}")
    #         print("        Trying Gemini fallback...")

    # if insight_text is None and gemini_key:
    #     try:
    #         insight_text = call_gemini(prompt)
    #         provider = "Google Gemini 2.5 Flash"
    #     except Exception as exc:
    #         print(f"    [!] Gemini call failed: {exc}")


    if insight_text:
        insight_text = strip_markdown(insight_text)

        print(f"\n{Colors.BOLD}+{'=' * 60}+{Colors.RESET}")
        print(f"{Colors.BOLD}|  {Colors.MAGENTA}[AI] Market Insight{Colors.RESET}{Colors.BOLD}  [{Colors.DIM}{provider}{Colors.RESET}{Colors.BOLD}]{Colors.RESET}")
        print(f"{Colors.BOLD}+{'=' * 60}+{Colors.RESET}")
        for line in insight_text.split('\n'):
            if line.strip():
                if line.strip().startswith('-'):
                    print(f"  {Colors.CYAN}" + textwrap.fill(line.strip(), width=56, subsequent_indent="    ") + Colors.RESET)
                else:
                    print(f"  {Colors.WHITE}" + textwrap.fill(line.strip(), width=58) + Colors.RESET)
            else:
                print()
        print(f"{Colors.BOLD}+{'=' * 60}+{Colors.RESET}\n")
    else:
        print(
            f"{Colors.RED}[!] AI Market Insight unavailable - all LLM API calls failed.\n"
            f"    Check your API key, quota, and internet connection.{Colors.RESET}"
        )


# ═════════════════════════════════════════════════════════════════════════════
#                           SECTION 4 – Main orchestration
# ═════════════════════════════════════════════════════════════════════════════


def fetch_all_assets() -> list[dict | None]:
    """
    Run all asset fetches independently.
    A failure in one never prevents the others from running.
    """
    print(f"\n{Colors.BOLD}[ ... ]{Colors.RESET} Fetching live asset prices...\n")

    nifty = fetch_indian_index(symbol="^NSEI", display_name="NIFTY 50")
    if nifty is None:
        print(f"    {Colors.RED}[!] NIFTY 50 fetch failed.{Colors.RESET}")
    else:
        print(f"    {Colors.GREEN}[OK]{Colors.RESET} NIFTY 50          -> {Colors.YELLOW}{format_price(nifty['price'])} {nifty['currency']}{Colors.RESET}")

    btc = fetch_crypto_coingecko(coin_id="bitcoin", display_name="Bitcoin (BTC)")
    if btc is None:
        print(f"    {Colors.RED}[!] Bitcoin fetch failed.{Colors.RESET}")
    else:
        print(f"    {Colors.GREEN}[OK]{Colors.RESET} Bitcoin (BTC)     -> {Colors.YELLOW}{format_price(btc['price'])} {btc['currency']}{Colors.RESET}")

    gold = fetch_commodity_yfinance(symbol="GC=F", display_name="Gold (XAU/USD)")
    if gold is None:
        print(f"    {Colors.RED}[!] Gold fetch failed.{Colors.RESET}")
    else:
        print(f"    {Colors.GREEN}[OK]{Colors.RESET} Gold (XAU/USD)    -> {Colors.YELLOW}{format_price(gold['price'])} {gold['currency']}{Colors.RESET}")

    return [nifty, btc, gold]


def main() -> None:
    """Entry point -- fetch prices, print table, then request AI insight."""
    print_banner()
    fetch_time = now_ist()
    results = fetch_all_assets()
    print_price_table(results, fetch_time)
    get_ai_insight(results)


if __name__ == "__main__":
    main()