# Timecell Internship Project — Portfolio Risk & AI Assessment

## 📌 Project Overview & Structure

The repository is divided into four distinct tasks, each building upon the concepts of the previous one. A unified aesthetic—featuring rich ANSI colors, clear ASCII tables, and cross-platform terminal compatibility—has been applied across all tasks.

A central `demo_portfolio.json` file is shared across Tasks 1, 3, and 4 to maintain consistency during testing.

| Task | Name | Primary Skill | Marks |
|------|------|---------------|-------|
| 01 | Portfolio Risk Calculator | Python · Quantitative thinking | 30 |
| 02 | Live Market Data Fetch | APIs · Error handling · Clean code | 20 |
| 03 | AI-Powered Portfolio Explainer | LLM prompting · AI integration | 30 |
| 04 | Devil's Advocate (Open Problem) | Initiative · Judgment · Curiosity | 20 |

---

## 🚀 Setup & Execution

### Prerequisites
- Python 3.10+
- Install required dependencies from `requirements.txt`:

```bash
pip install -r requirements.txt
```

### API Keys
Tasks 2, 3, and 4 require access to LLM APIs. Create a `.env` file in the root directory (or inside the specific task folders) containing:
```env
GEMINI_API_KEY=your_google_gemini_key_here
OPENAI_API_KEY=your_openai_key_here  # Optional fallback
```

### Running the Tasks
Navigate to the respective task directories to execute the scripts:

```bash
# Task 1
cd task-1
python portfolio_risk_calculator.py
python portfolio_risk_calculator.py --moderate

# Task 2
cd task-2
python live_market_data_fetch.py

# Task 3
cd task-3
python ai_powered_portfolio_explainer.py
python ai_powered_portfolio_explainer.py --tone expert --critique

# Task 4
cd task-4
python main.py --demo
```

---

## 📁 Task 1: Portfolio Risk Calculator

### Overview
This task consists of a highly deterministic, math-driven **Portfolio Risk Calculator**. It evaluates a portfolio's resilience against expected market crashes by computing post-crash values, runway months (how long the portfolio can sustain monthly expenses), and identifying the largest risk contributor.

### Workflow
1. **Input Loading**: The script automatically loads portfolio data (asset names, allocation percentages, expected crash percentages) and financial context (total value, monthly expenses) from a shared `demo_portfolio.json` file in the project root.
2. **Metrics Computation**: It calculates the absolute post-crash value for each asset based on its expected drawdown, and aggregates these to find the total post-crash portfolio value.
3. **Runway Analysis**: It divides the post-crash value by the monthly expenses to determine the runway in months.
4. **Ruin Test**: If the post-crash runway is greater than 12 months, the portfolio "PASSES" the ruin test. Otherwise, it "FAILS".
5. **Concentration Warning**: It flags any asset that makes up more than 40% of the portfolio.

### How to Run
Run the script via the command line:
```bash
python portfolio_risk_calculator.py
```
To run a side-by-side comparison with a moderate crash (50% of the expected crash magnitude):
```bash
python portfolio_risk_calculator.py --moderate
```

### Expected Output
The terminal will display a colorful, formatted ASCII interface:
- **Confirmation**: `[OK] Loaded portfolio from: demo_portfolio.json`
- **Portfolio Summary**: Total value, expenses, and asset count.
- **Allocation Bar Chart**: A visual representation of how the portfolio is distributed, color-coded by the severity of the expected crash for each asset.
- **Scenario Metrics / Comparison Table**: A clean breakdown of the post-crash value, runway months, ruin test result, and the most dangerous asset.
- **Final Verdict**: A clear `[PASS]` or `[FAIL]` status indicating if the portfolio survives 12 months post-crash.

---

## 📁 Task 2: Live Market Data Fetcher

### Overview
This script is a **Live Market Data Fetcher** that retrieves real-time pricing for a set of diverse assets (equities, crypto, commodities) and uses a generative AI model (Google Gemini or OpenAI) to provide a plain-English, jargon-free summary of the current market mood.

### Workflow
1. **API Integration**:
   - Uses `yfinance` to fetch the NIFTY 50 Indian stock index (`^NSEI`).
   - Uses the public CoinGecko API to fetch Bitcoin (`BTC`) prices in USD.
   - Uses `yfinance` to fetch COMEX Gold Futures (`GC=F`) in USD.
2. **Graceful Error Handling**: Each asset is fetched independently. If one API fails or times out, the others will still complete successfully.
3. **Fallback Chain**: Twelve Data → Alpha Vantage → yfinance (ensures a price is returned even when one or two sources are down).
4. **Prompt Engineering**: The script strips the raw prices into a heavily structured prompt, instructing the LLM to output exactly 1 sentence of mood, followed by 2-3 bullet points without any Markdown or special formatting.
5. **LLM Fallback System**: It attempts to call Google Gemini first. If the quota is exceeded or it fails, it gracefully falls back to OpenAI GPT-3.5-Turbo.

### How to Run
First, ensure you have a `.env` file in the `task-2` directory with your API keys. Then run:
```bash
python live_market_data_fetch.py
```

### Expected Output
The terminal will display:
- **Live Fetch Status**: Real-time `[OK]` or `[!]` lines as it contacts the APIs.
- **Asset Price Table**: A cleanly formatted table showing the Asset Name, comma-separated Price, and Currency.
- **AI Market Insight**: A color-coded box showing which LLM provider was used, followed by a dynamically wrapped, plain-text summary of the current market conditions formatted as clean bullet points.

---

## 📁 Task 3: AI-Powered Portfolio Explainer

### Overview
The **AI-Powered Portfolio Explainer** bridges the gap between raw mathematical risk (from Task 1) and human comprehension. It feeds the calculated risk metrics into an LLM and forces the AI to output a highly structured, 4-part summary of the portfolio's health, tailored to specific user knowledge levels.

### Workflow
1. **Data Loading & Computation**: Loads the shared `demo_portfolio.json` file and calculates the exact deterministic risk metrics (runway, ruin test, concentration) using the same logic as Task 1.
2. **Tone-Adjusted Prompting**: Builds a dynamic prompt containing the raw numbers and specific tone instructions (`beginner`, `experienced`, or `expert`), strictly forbidding the use of markdown.
3. **LLM Execution**: Sends the prompt to Google Gemini (or falls back to OpenAI) and retrieves the raw text.
4. **Parsing Engine**: Uses custom string parsing to break the raw LLM text into four distinct variables: `Summary`, `Doing Well`, `Consider Changing`, and `Verdict`.
5. **LangGraph Validation Loop** (Bonus): A second LLM call acts as a "Senior Risk Officer" that checks the first explanation for accuracy and consistency. If rejected, the system iterates up to 3 times to improve the output.
6. **LangSmith Observability**: Every LLM call is traced with `@traceable` decorator, logging token usage, latency, and cost per run.

### How to Run
First, ensure your API keys are in a `.env` file in the `task-3` directory.

Run with the default beginner tone:
```bash
python ai_powered_portfolio_explainer.py
```
Change the tone of the explanation:
```bash
python ai_powered_portfolio_explainer.py --tone expert
```
Enable the Risk Officer critique layer:
```bash
python ai_powered_portfolio_explainer.py --critique
```

### Expected Output
The terminal will display:
- **Loading Status**: `[OK] Loaded portfolio from: demo_portfolio.json`
- **Raw API Response**: Exactly what the LLM returned before processing.
- **Extracted Structured Output**: Color-coded sections:
  - **Risk Summary** (Cyan)
  - **Doing Well** (Green)
  - **Consider Changing** (Yellow)
  - **Verdict** (Red/Green/Yellow depending on Aggressive/Conservative/Balanced)
- **Critique Review** *(if `--critique` is used)*: A secondary red-bordered box detailing the Risk Officer's evaluation.

---

## 📁 Task 4: Devil's Advocate — Assumption Challenger (The Open Problem)

### What This Is

Timecell's homepage says:

> *"Show me the assumption you'd have to be wrong about for this to be the wrong call."*

That's not a feature. That's a **philosophy**. This tool is that philosophy, in code.

Most portfolio tools show you outcomes: *"Your runway is 18 months."*  
Devil's Advocate asks: *"Which belief are you betting your financial safety on — and what happens if it's wrong?"*

### How It Works

```
1. You provide a portfolio + a decision you want to make
2. The tool computes baseline risk metrics (crash survival, runway, ruin test)
3. Gemini extracts the 4 hidden assumptions behind your decision
4. The math engine stress-tests each assumption independently
5. Gemini explains what broke, what held, and which assumption is your weakest link
```

**Two AI calls, deterministic math in between.** The AI finds beliefs; the math measures consequences.

### Usage

- **Demo mode (built-in portfolio)**
  ```bash
  python main.py --demo
  ```
- **Custom portfolio from JSON file**
  ```bash
  python main.py --portfolio demo_portfolio.json
  ```
- **Custom portfolio + custom decision**
  ```bash
  python main.py --portfolio my_portfolio.json --decision "I want to increase BTC to 50%"
  ```

### Example Output (abridged)

The terminal will display a full interactive report:
- Portfolio overview with allocation bar chart
- Baseline risk metrics (post-crash value, runway, ruin test, largest risk asset)
- Hidden assumptions extracted by Gemini (e.g., Recovery Risk, Correlation Risk, Liquidity Risk, Inflation Risk)
- Stress-test results: how each assumption affects runway (with delta and percentage change)
- Devil's Advocate verdict: summary, what you're doing well, weakest assumption, and final risk label

*(Full example in the `task-4/README.md`)*

### Project Structure (Task 4)

```
devil_advocate/
├── main.py                  # CLI entry point, orchestrates the flow
├── risk_engine.py           # Pure deterministic math (no AI)
├── gemini_client.py         # Both Gemini API calls
├── display.py               # All terminal formatting / colors
├── demo_portfolio.json      # Example portfolio for testing
├── requirements.txt
└── README.md
```

### My Approach & Design Decisions

**Why this for Task 04?**  
Timecell's standout quote is *"Show me the assumption you'd have to be wrong about."* Tasks 1–3 compute outcomes. None of them ask *why* those outcomes might be wrong. This is the gap I chose to fill — because it's philosophically aligned with what Timecell believes.

**AI vs. Math separation:**  
- AI extracts beliefs and explains consequences (subjective, contextual).  
- Math computes runway, ruin test, crash losses (deterministic, auditable).  
A language model should not be trusted to multiply numbers. It should be trusted to understand context.

**Prompt engineering evolution:**  
- First attempt: free-text assumptions → inconsistent format.  
- Second attempt: strict JSON schema with `stress_type` values → machine-readable, semantically rich.  
- Key decision: Map each assumption to a `stress_type` the math engine knows. This creates a closed loop: AI → math → AI.

---

## 🧠 My Development Journey

### Task 1 – Portfolio Risk Calculator

#### Step 1: Understanding the problem
**Prompt to ChatGPT:**
> *“I have uploaded the PDF. From this, explain the problem statement very clearly in simple English. What do we need to solve so that we can get the best marks according to the evaluation schema? Give me a general idea of how to implement this problem.”*

**Output received:**
ChatGPT explained the task as: *“You are given a portfolio dictionary with total value, monthly expenses, and assets (each with allocation % and expected crash %). Compute post-crash value, runway months, ruin test (PASS if runway > 12 months), largest risk asset, and concentration warning.”* It also suggested breaking the solution into validation, computation, and output formatting.

#### Step 2: Getting a detailed step‑by‑step prompt
**Prompt to ChatGPT:**
> *“Based on the provided PDF, give me a detailed prompt that will help me build this project step by step in an easy manner, covering each topic in detail, including inputs, outputs, and bonus questions. Write a strict prompt by stating that you have expertise in wealth management, the AI domain, and portfolio risk analysis. In the prompt, also mention which tech stack I should use for this project and why that specific stack should be used, with proper reasons.”*

**Output received:**
A long, structured prompt that became the blueprint for Task 1. It specified:
- Use pure Python (no numpy/pandas) for simplicity and auditability.
- Functions: `validate_portfolio()`, `compute_risk_metrics()`, `print_metrics_table()`.
- Edge cases: zero expenses, 100% cash, mis‑allocations, negative crash percentages.
- Bonuses: `--moderate` flag for second scenario, ASCII bar chart for allocation.

#### Step 3: Claude for tech stack and project structure
I fed that prompt + PDF to Claude (with extended thinking). Claude returned:
- A recommended project structure (`portfolio_risk_calculator.py`, `demo_portfolio.json`).
- Explanation why CLI‑first is better for this test (rich output, scripting friendly).
- Initial skeleton code for Task 1.

#### Step 4: Verifying formulas and logic
I manually tested formulas using multiple AI tools and sources. Example check:

**Prompt to DeepSeek:**
> *“Given a portfolio with total_value_inr=10,000,000, asset BTC allocation 30%, expected_crash_pct=-80. What is the post-crash value of BTC?”*

**Answer:** `0.3 * 10,000,000 * (1 - 0.8) = 600,000` – matched my code.

I decided to stay with pure Python; if asset count grows to 10,000+, numpy/pandas can be added later.

#### Step 5: Adding edge cases and fixing errors
**Prompt to DeepSeek:**
> *“Add all possible edge cases – especially for every if-else condition used inside the risk calculator – and provide example cases for each condition.”*

DeepSeek returned updated code with:
- Empty assets list → raise `ValueError`.
- Monthly expenses = 0 → runway = `float('inf')` → ruin test `PASS`.
- Allocation sum not 100% → warning but continue.
- Positive crash percentage → raise error (crashes must be negative).

After running, I found a bug in the “no assets” edge case – the code still tried to compute max on an empty list. I manually fixed it myself.

#### Step 6: Cleaning variable names and adding comments
**Prompt to ChatGPT:**
> *“Improve code readability – converting variable names into meaningful names such as total_allocation, post_crash_asset_value, and similar descriptive variable names and compute_risk_metrics similar descriptive function name. Also add simple English comments and improve the output structure overall code structure so that the project would look professional, understandable.”*

**Output:** The final `portfolio_risk_calculator.py` you see – with clear dataclasses, color‑coded terminal output, and side‑by‑side comparison table.

---

### Task 2 – Live Market Data Fetch

#### Step 1: Finding APIs and tech stack
**Prompt to Claude (with web search enabled):**
> *“You are an expert in API integrations and financial data pipelines. Recommend free, public APIs for fetching NIFTY 50, Bitcoin, and Gold. Provide a tech stack and initial code structure for Task 2 of the Timecell test.”*

**Claude’s output:** Suggested `yfinance` for NIFTY 50 and Gold (free, reliable, though delayed ~15 minutes for NSE stocks) and CoinGecko for Bitcoin (public API, no key required). Provided initial skeleton with `fetch_indian_index()`, `fetch_crypto_coingecko()`, `fetch_commodity_yfinance()`.

#### Step 2: Implementing the three fetchers
I implemented three separate functions:
- `fetch_indian_index()` – uses `yf.Ticker("^NSEI")` to get NIFTY 50 price.
- `fetch_crypto_coingecko()` – calls `https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd`.
- `fetch_commodity_yfinance()` – uses `yf.Ticker("GC=F")` for Gold Futures.

Each function has its own exception handling – if one fails, the others continue.

#### Step 3: Adding graceful error handling
I realised that an API might fail due to network issues or rate limits. I added:
- `try/except` blocks around each fetch.
- If an asset fails, it returns `None` and the script logs a warning but continues.
- At the end, if **all three assets fail**, the script exits with a critical error. If at least one succeeds, the table shows prices for successes and `N/A` for failures.

#### Step 4: AI market insight with fallback LLMs
I integrated an LLM to generate a plain‑English market summary. The script:
- Builds a prompt with the fetched prices and strict formatting rules (no markdown, only dash bullet points).
- Tries Google Gemini first (free tier, using `gemini-2.5-flash`).
- If Gemini fails (quota, key missing, etc.), falls back to OpenAI GPT-3.5-Turbo.
- If both fail, prints a message and continues without AI insight.

#### Step 5: Environment variables and code polish
I added a `.env` file to store API keys (`GEMINI_API_KEY`, `OPENAI_API_KEY`).  
I then used GPT to clean the code:

**Prompt to GPT:**
> *“Make the code clean, has a proper structure, and outputs a well‑formatted table. Add simple English comments so that by reading the function names, variable names, and comments, even a non‑technical person can understand what is going on.”*

**Output:** The final `live_market_data_fetch.py` – with color‑coded fetch status, a neatly tabulated price table, and an AI insight that strips markdown and wraps text cleanly.

#### Step 6: Testing the final script
I ran the script multiple times to ensure:
- Prices update correctly (NIFTY in INR, Bitcoin in USD, Gold in USD).
- If CoinGecko is slow, the other two still show.
- The AI insight always follows the bullet‑point format without markdown.

**Example terminal output after a successful run:**
```
+================================================================================+
|                              LIVE MARKET PRICES                                |
|                  NIFTY 50  |  Bitcoin (BTC)  |  Gold (XAU/USD)                 |
+================================================================================+

[ ... ] Fetching live asset prices...

    [OK] NIFTY 50          -> 22,541.80 INR
    [OK] Bitcoin (BTC)     -> 62,341.20 USD
    [OK] Gold (XAU/USD)    -> 2,350.00 USD

+============================================================+
|  Asset Prices -- fetched at 2025-05-02 10:32:15 IST       |
+============================================================+
+----------+-------------+----------+
| Asset    |       Price | Currency |
+----------+-------------+----------+
| NIFTY 50 |   22,541.80 | INR      |
| Bitcoin  |   62,341.20 | USD      |
| Gold     |    2,350.00 | USD      |
+----------+-------------+----------+

+============================================================+
|  [AI] Market Insight  [Google Gemini 2.5 Flash]            |
+============================================================+
Markets are showing mixed signals today.
- Indian stocks are holding steady near recent highs.
- Bitcoin is climbing, showing strong investor confidence.
- Gold is rising slightly, hinting at some caution.
+============================================================+
```

---


### Task 3 – AI-Powered Portfolio Explainer

#### Step 1: Initial generation
Used earlier prompt (same as Task 1) with Task 3 description. Claude gave a basic script using Gemini with the old model `gemini-1.5-flash`.

#### Step 2: Model error
**Error output:**
```json
{
  "error": {
    "code": 404,
    "message": "models/gemini-1.5-flash is not found for API version v1beta...",
    "status": "NOT_FOUND"
  }
}
```

**Fix:** I visited Google AI Studio docs, found the correct SDK usage:
```python
from google import genai
client = genai.Client(api_key="...")
response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
```
I pasted this into GitCopilot with the prompt: *“Use the provided code structure and the same model as in this code, because this code is from the official docs of Gemini.”* The error was resolved.

#### Step 3: Output inconsistency – missing verdict
The LLM sometimes omitted the one‑line verdict. I decided to enforce structure using **Pydantic BaseModel** (still with Gemini SDK, not LangChain). I also added `HumanMessage`/`SystemMessage` for clear message context (using simple string templates, not LangChain classes).

**Partial prompt to GitCopilot:**
> *“Modify the code to use Pydantic to parse the LLM output into a fixed schema with fields: summary, doing_well, consider_changing, verdict.”*

#### Step 4: Prompt engineering journey (4 versions)
- **V1 (initial)** – Generic “You are a financial advisor…” – output was free‑text, often missed the verdict.
- **V2** – Added few‑shot example and requested JSON – better but still sometimes hallucinated extra fields.
- **V3** – Added `--tone` config, raw/structured separation, and self‑critique instructions. However, the JSON was not always valid.
- **V4 (final)** – Strict production prompt with:
  - Chain‑of‑thought: “First compute risk perception, then write summary…”
  - Enum validation: “Verdict must be exactly one of: Aggressive, Balanced, Conservative.”
  - No‑extra‑text rule: “Return only the four sections with exact labels, no markdown.”

**Prompt to DeepSeek (to help craft V4):**
> *“Search the web for best prompt engineering examples (Hugging Face, Google AI Studio). Merge techniques like role prompting, few‑shot, chain‑of‑thought, and output constraints. Produce a detailed prompt that forces the LLM to return exactly SUMMARY:, DOING WELL:, CONSIDER CHANGING:, VERDICT: sections in plain text.”*

DeepSeek returned a 40‑line prompt that became the `build_prompt()` function.

#### Step 5: Bonus 2 – Validation loop without LangGraph
The original plan was to use LangGraph, but I realised I could implement a plain Python loop.

**Prompt to GitCopilot:**
> *“Make a second LLM2 (Gemini) that gives two things: 'accepted' or 'rejected' and a summary of feedback if rejected. Send LLM1’s output to LLM2 for validation. If rejected, send it back to LLM1 with the feedback to improve. Max 3 iterations. Use only the Gemini SDK, no external frameworks.”*

The resulting code (`critique_first()` function) runs a loop up to 3 times, each time passing the critique back to the first LLM. This works perfectly and is entirely native Python.

#### Step 6: Observability
I added manual logging of token usage and latency using Gemini’s response metadata (no LangSmith). Each `call_llm()` prints a line like `[TRACE] Gemini - tokens: 342, latency: 1.2s` to the console.

**Final output example from Task 3:**
```
+--------------------------------------------------------------------------------+
|                                 Raw API Response                               |
+--------------------------------------------------------------------------------+
SUMMARY: Your portfolio loses 37% in a severe crash, leaving ₹6.3Cr. With monthly expenses of ₹80k, you have 78 months of runway – that's safe...
DOING WELL: You keep 10% in cash, which protects against immediate emergencies.
CONSIDER CHANGING: Reduce BTC from 30% to 15%; it crashes 80% and dominates your risk.
VERDICT: Aggressive

+--------------------------------------------------------------------------------+
|                                Extracted Output                                |
+--------------------------------------------------------------------------------+

Risk Summary: Your portfolio loses 37% in a severe crash, leaving ₹6.3Cr. With monthly expenses of ₹80k, you have 78 months of runway – that's safe...

Doing Well: You keep 10% in cash, which protects against immediate emergencies.

Consider Changing: Reduce BTC from 30% to 15%; it crashes 80% and dominates your risk.

Verdict: Aggressive
```

---

### Task 4 – The Open Problem (Devil's Advocate)

*(The journey for Task 4 is already detailed in the `task-4/README.md`. It follows a similar pattern: prompt to Gemini for assumption extraction, deterministic math stress‑test, then a final AI explanation. I used the same iterative prompt engineering – starting with free‑text, evolving to strict JSON schema – to achieve reliable output.)*

---


## 🙏 Acknowledgements

- **Google Gemini** for generous free tier and fast inference.
- **Claude** for helping structure the project and debug tricky API integrations.
- **DeepSeek & ChatGPT** for rapid prototyping and edge‑case discovery.
- **Timecell** for a thoughtfully designed assessment that mirrors real startup engineering.