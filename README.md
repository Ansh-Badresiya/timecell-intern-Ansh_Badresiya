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

## 🧠 How I Used AI to Build These Projects

## Task 1 – Portfolio Risk Calculator

### Step 1: Figuring out what to build  
**I asked ChatGPT:**  
> *“I’ve uploaded the PDF. Can you explain the problem in simple words? What do I need to make so I get full marks? Just give me a rough idea.”*  

**It said:**  
You get a portfolio with total money, monthly spending, and a few assets (each has a percentage and a crash percentage). You must calculate:  
- How much money is left after a bad crash  
- How many months you can survive on that (runway)  
- Whether you pass the “ruin test” (runway > 12 months)  
- Which asset is the biggest risk  
- A warning if any asset is more than 25% of the portfolio  

Then break your code into: check the inputs → do the math → show the results nicely.

### Step 2: Getting a detailed plan  
**I then asked ChatGPT:**  
> *“Pretend you’re a wealth management expert. Based on the PDF, give me a step‑by‑step prompt that tells me exactly what to code – inputs, outputs, bonus stuff. Also suggest which tools to use and why.”*  

**The plan I got:**  
- Use plain Python (no fancy libraries like NumPy) – easier to read and check.  
- Write three functions: `validate_portfolio()`, `compute_risk_metrics()`, `print_metrics_table()`.  
- Handle weird cases: zero monthly expenses, 100% cash, wrong allocation sums, positive crash percentages (should be negative).  
- Bonuses: a `--moderate` flag for a second scenario, and a simple text bar chart for allocations.

### Step 3: Picking the tech stack with Claude  
I gave that plan + PDF to Claude (with longer thinking). Claude told me:  
- Use a simple project structure: `portfolio_risk_calculator.py` and a `demo_portfolio.json`.  
- Command‑line first is better for this test – easier to see output and automate.  
- Gave me starter code.

### Step 4: Double‑checking the math  
I tested the formulas with several online sources and AI tools. Example:  
**I asked DeepSeek:**  
> *“Portfolio total = ₹10,00,000, asset ‘Crypto’ has 30% allocation and crash = -80%. What’s the value after crash?”*  

**Answer:** 0.3 × 10,00,000 × (1 – 0.8) = ₹60,000. My code gave the same.  
I stuck with plain Python – if I ever have 10,000+ assets, I can switch to NumPy later.

### Step 5: Catching all edge cases and fixing a bug  
**I told DeepSeek:**  
> *“Add every possible edge case to my code – for each if‑else condition – and give me example inputs that trigger each one.”*  

DeepSeek gave me updated code that handles:  
- Empty asset list → error  
- Monthly expenses = 0 → runway is infinite → test passes  
- Allocations don’t add up to 100% → warning but still works  
- Crash percentage is positive → error (crashes must be negative)  

After running, I spotted a bug: when there are no assets, the code still tried to find the biggest risk asset. I fixed that myself.

### Step 6: Cleaning up names and adding comments  
**I asked ChatGPT:**  
> *“Make my code easier to read – rename variables to something obvious like `total_allocation`, `post_crash_value`. Add simple comments. Improve how the output looks so it’s professional.”*  

**Final result:** `portfolio_risk_calculator.py` with clear dataclasses, colours in the terminal, and a side‑by‑side table comparing the normal and moderate scenarios.

---

## Task 2 – Live Market Data Fetch

### Step 1: Finding free APIs  
**I asked Claude (with web search turned on):**  
> *“You’re an API expert. Tell me some free APIs to get live prices for NIFTY 50, Bitcoin, and Gold. Then give me a tech stack and starter code for Task 2.”*  

Claude suggested:  
- `yfinance` for NIFTY 50 and Gold (free but about 15 minutes delayed for Indian stocks)  
- CoinGecko for Bitcoin (no API key needed)  
- Provided starters: `fetch_nifty()`, `fetch_bitcoin()`, `fetch_gold()`

### Step 2: Writing the three fetchers  
I wrote three separate functions:  
- `fetch_nifty()` → uses `yf.Ticker("^NSEI")`  
- `fetch_bitcoin()` → calls `https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd`  
- `fetch_gold()` → uses `yf.Ticker("GC=F")`  

Each has its own try/except – if one fails, the others keep going.

### Step 3: Handling failures gracefully  
If an API fails, it returns `None` and prints a warning.  
At the end:  
- If at least one asset worked → show the table with “N/A” for the failed ones.  
- If all three failed → critical error and stop.

### Step 4: Adding AI market summary with fallback  
The script creates a prompt with the prices and strict rules (no markdown, just plain bullet points). It tries:  
1. Google Gemini (`gemini-2.5-flash`) – free  
2. If Gemini fails → OpenAI GPT-3.5-Turbo  
3. If both fail → just skip the AI part and show a message.

### Step 5: Using .env and cleaning the code  
I put API keys in a `.env` file (so I don’t hardcode them).  
Then I asked GPT:  
> *“Organise my code neatly, add comments so even a beginner can understand it, and format the output as a nice table.”*  

The final `live_market_data_fetch.py` has coloured statuses, a clean table, and AI insight that strips out markdown.

### Step 6: Testing it live  
I ran it several times. Here’s a sample output (changed the numbers and wording):

```
+================================================================================+
|                           LIVE MARKET PRICES (Real‑time)                       |
|               NIFTY 50      |    Bitcoin (BTC)     |   Gold (XAU/USD)         |
+================================================================================+

Fetching prices...

   [OK] NIFTY 50          -> 22,891.45 INR
   [OK] Bitcoin (BTC)     -> 64,102.30 USD
   [OK] Gold (XAU/USD)    -> 2,367.80 USD

+============================================================+
|  Snapshot taken at 2025-05-02 14:20:10 IST                 |
+============================================================+
+------------+-------------+----------+
| Asset      |       Price | Currency |
+------------+-------------+----------+
| NIFTY 50   |   22,891.45 | INR      |
| Bitcoin    |   64,102.30 | USD      |
| Gold       |    2,367.80 | USD      |
+------------+-------------+----------+

+============================================================+
|  [AI] Market Pulse  (Google Gemini)                        |
+============================================================+
Markets show modest optimism today.
- NIFTY continues its gradual uptrend.
- Bitcoin broke past $64k, driven by ETF inflows.
- Gold flat, but geopolitical risks support safe‑haven demand.
+============================================================+
```

---

## Task 3 – AI‑Powered Portfolio Explainer

### Step 1: First script attempt  
I used the same kind of prompt as Task 1, but for Task 3. Claude gave me a basic Gemini script using the old `gemini-2.0-flash` model.

### Step 2: Fixing the “model not found” error  
The error said:  
```json
{ "error": { "code": 404, "message": "models/gemini-2.0-flash is not found..." } }
```
I went to Google AI Studio docs, found the correct way:  
```python
from google import genai
client = genai.Client(api_key="...")
response = client.models.generate_content(model="gemini-2.5-flash", contents=prompt)
```
I told GitCopilot to update my code using that official pattern. Error gone.

### Step 3: Making sure the verdict always appears  
Sometimes the AI forgot to give the one‑line verdict. So I forced a structure using **Pydantic** (still using Gemini, not LangChain). I also added clear system and user messages using simple strings.

**I asked GitCopilot:**  
> *“Change my code to parse the AI’s answer into a fixed format with fields: summary, doing_well, consider_changing, verdict.”*

### Step 4: Improving the prompt – four tries  
- **Try 1:** Just “act as an advisor” → random text, often missing the verdict.  
- **Try 2:** Added an example and asked for JSON → better but sometimes added extra stuff.  
- **Try 3:** Added a `--tone` option (beginner/experienced/expert) and separated raw from structured output – JSON still sometimes broken.  
- **Try 4 (final):** Very strict prompt: “Think step by step, then give exactly these four sections with these exact labels. No extra words. Verdict must be one of: Aggressive, Balanced, Conservative.”  

To build that final prompt, I asked DeepSeek:  
> *“Look up the best prompt engineering tips online (Hugging Face, Google AI Studio). Mix role‑playing, few‑shot examples, chain‑of‑thought, and output rules. Give me a prompt that forces the AI to output only SUMMARY:, DOING WELL:, CONSIDER CHANGING:, VERDICT: lines.”*  

DeepSeek gave me a ~40‑line prompt that became my `build_prompt()` function.

### Step 5: Bonus 2 – Validation loop without LangGraph  
I originally thought I’d need LangGraph, but I realised a simple Python loop works.  

**I told GitCopilot:**  
> *“Make a second AI (also Gemini) that only says ‘accepted’ or ‘rejected’ plus a short reason. Send the first AI’s answer to this second AI for checking. If rejected, send it back to the first AI with the feedback to improve. Try at most 3 times. Use only Gemini, no extra libraries.”*  

The resulting code (`critique_and_regenerate()`) runs up to 3 loops and works perfectly.

### Step 6: Adding simple tracking  
I added a little logging for token count and response time (using what Gemini gives me). Each AI call prints something like:  
`[TRACE] Gemini – tokens: 287, latency: 0.94s`

### Final output example (changed numbers and wording)

```
+--------------------------------------------------------------------------------+
|                                 Raw API Response                               |
+--------------------------------------------------------------------------------+
SUMMARY: In a severe downturn, your portfolio shrinks by 41% to ₹5.9Cr. With ₹85k monthly expenses, you have about 69 months of runway – safe.
DOING WELL: You hold 15% in cash, which covers emergencies without selling assets.
CONSIDER CHANGING: Your 40% in a single crypto asset (BTC) is too concentrated; consider trimming to 15–20%.
VERDICT: Aggressive

+--------------------------------------------------------------------------------+
|                                Extracted Output                                |
+--------------------------------------------------------------------------------+

Risk Summary: In a severe downturn, your portfolio shrinks by 41% to ₹5.9Cr. With ₹85k monthly expenses, you have about 69 months of runway – safe.

Doing Well: You hold 15% in cash, which covers emergencies without selling assets.

Consider Changing: Your 40% in a single crypto asset (BTC) is too concentrated; consider trimming to 15–20%.

Verdict: Aggressive

```

## Task 4 – The Open Problem (Devil's Advocate)

*(The journey for Task 4 is already detailed in the `task-4/README.md`. It follows a similar pattern: prompt to Gemini for assumption extraction, deterministic math stress‑test, then a final AI explanation. I used the same iterative prompt engineering – starting with free‑text, evolving to strict JSON schema – to achieve reliable output.)*

---


## 🙏 Acknowledgements

- **Google Gemini (AntiGravity Tool)** for generous free tier and fast inference.
- **Claude (AntiGravity Tool)** for helping structure the project and debug tricky API integrations.
- **DeepSeek & ChatGPT** for rapid prototyping and edge‑case discovery.
- **Timecell** for a thoughtfully designed assessment that mirrors real startup engineering.
