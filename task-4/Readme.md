# Devil's Advocate — Assumption Challenger
### Task 04: The Open Problem

---

## What This Is

Timecell's homepage says:

> *"Show me the assumption you'd have to be wrong about for this to be the wrong call."*

That's not a feature. That's a **philosophy**. This tool is that philosophy, in code.

Most portfolio tools show you outcomes: *"Your runway is 18 months."*  
Devil's Advocate asks: *"Which belief are you betting your financial safety on — and what happens if it's wrong?"*

---

## How It Works

```
1. You provide a portfolio + a decision you want to make
2. The tool computes baseline risk metrics (crash survival, runway, ruin test)
3. Gemini extracts the 4 hidden assumptions behind your decision
4. The math engine stress-tests each assumption independently
5. Gemini explains what broke, what held, and which assumption is your weakest link
```

**Two AI calls, deterministic math in between.** The AI finds beliefs; the math measures consequences.


---

## Usage

### Demo mode (built-in portfolio)
```bash
python main.py --demo
```

### Custom portfolio from JSON file
```bash
python main.py --portfolio demo_portfolio.json
```

### Custom portfolio + custom decision
```bash
python main.py --portfolio my_portfolio.json --decision "I want to increase BTC to 50%"
```

### Portfolio JSON format
```json
{
  "portfolio": {
    "total_value_inr": 10000000,
    "monthly_expenses_inr": 80000,
    "assets": [
      {"name": "BTC",     "allocation_pct": 30, "expected_crash_pct": -80},
      {"name": "NIFTY50", "allocation_pct": 40, "expected_crash_pct": -40},
      {"name": "GOLD",    "allocation_pct": 20, "expected_crash_pct": -15},
      {"name": "CASH",    "allocation_pct": 10, "expected_crash_pct":  0}
    ]
  },
  "decision": "I want to hold through any crash."
}
```

---

## Example Output

```
+================================================================================+
|                    DEVIL'S ADVOCATE -- Assumption Challenger                  |
|               "Show me the assumption you'd have to be wrong                  |
|                      about for this to be the wrong call."                    |
|                                                   -- Timecell.ai              |
+================================================================================+

PORTFOLIO OVERVIEW
  Total Value     : Rs. 1.00 Cr
  Monthly Expenses: Rs. 80,000

  Asset        Allocation  Expected Crash  Bar
  ------------ ---------- ---------------  --------------------
  BTC                 30%            -80%  ██████
  NIFTY50             40%            -40%  ████████
  GOLD                20%            -15%  ████
  CASH                10%              0%  ██

----------------------------------------------------------------------------------------------------


[ STEP 1 ] Computing baseline risk metrics...

BASELINE RISK METRICS (full crash scenario)
  Post-Crash Value  : Rs. 57.00 L
  Runway            : 71.2 months
  Ruin Test (>12mo) : PASS
  Largest Risk Asset: BTC

  Asset          Before Crash    After Crash           Loss
  ------------ -------------- -------------- --------------
  BTC             Rs. 30.00 L     Rs. 6.00 L -  Rs. 24.00 L
  NIFTY50         Rs. 40.00 L    Rs. 24.00 L -  Rs. 16.00 L
  GOLD            Rs. 20.00 L    Rs. 17.00 L -   Rs. 3.00 L
  CASH            Rs. 10.00 L    Rs. 10.00 L -        Rs. 0

[ STEP 2 ] Connecting to Gemini AI...
  [OK] Gemini 2.5 Flash ready

[ STEP 3 ] Extracting hidden assumptions...
  Decision: "I want to keep 30% in BTC and hold through any crash -- it always recovers."
  Asking Gemini to find what you're implicitly betting on...

  #1 [[REC] Recovery Risk]
     Assumption  : Bitcoin will recover from an 80% crash within a timeframe that does
                   not significantly impact the client's financial stability.
     If wrong    : If Bitcoin's recovery is significantly slower (5+ years) or incomplete,
                   the portfolio value will remain depressed for an extended period.

  #2 [[COR] Correlation Risk]
     Assumption  : The expected crashes for BTC, NIFTY50, and GOLD are largely independent.
     If wrong    : A systemic event causing all assets to crash simultaneously could make
                   it impossible to cover expenses without liquidating at extreme losses.

  #3 [[LIQ] Liquidity Risk]
     Assumption  : No urgent, large unforeseen cash needs beyond regular monthly expenses.
     If wrong    : A significant unexpected expense during a crash would force selling
                   depressed assets, locking in permanent capital impairment.

  #4 [[INF] Inflation Risk]
     Assumption  : Monthly expenses remain stable in real terms over the long term.
     If wrong    : 8% annual inflation quickly makes Rs. 80,000/month insufficient,
                   forcing larger portfolio withdrawals before recovery.

----------------------------------------------------------------------------------------------------


[ STEP 4 ] Stress-testing each assumption...
  (What happens to your runway if each belief is WRONG?)

  [ OK ] Assumption #1: Bitcoin will recover from an 80% crash within a time...
     Runway: 71.2mo -> 63.8mo (-7.5mo, -11%)  Ruin test: PASS

  [FAIL] Assumption #2: The expected crashes for BTC, NIFTY50, and GOLD are ...
     Runway: 71.2mo -> 8.0mo (-63.2mo, -89%)  Ruin test: FAIL

  [ OK ] Assumption #3: The client will not have any urgent, large, and unfo...
     Runway: 71.2mo -> 67.7mo (-3.6mo, -5%)   Ruin test: PASS

  [ OK ] Assumption #4: The client's monthly expenses will remain stable in ...
     Runway: 71.2mo -> 56.6mo (-14.7mo, -21%) Ruin test: PASS

----------------------------------------------------------------------------------------------------


[ STEP 5 ] Generating Devil's Advocate analysis...
  Asking Gemini to explain what the numbers mean...

+===============================================================================+
|                             DEVIL'S ADVOCATE VERDICT                          |
+===============================================================================+

  >> SUMMARY
  Overall, your portfolio shows good resilience under most individual stress scenarios.
  However, our stress tests revealed a critical vulnerability when multiple market
  downturns -- especially involving Bitcoin -- occur simultaneously.

  >> WHAT YOU'RE DOING WELL
  Your decision to hold through market volatility, particularly with Bitcoin, is
  commendable as it aligns with a long-term investment philosophy and avoids panic selling.

  >> WEAKEST ASSUMPTION
  The most damaging assumption is that Bitcoin, NIFTY50, and Gold will crash independently.
  If these assets experience a simultaneous downturn, your runway plummets from 71 months
  to just 8 months. This correlation risk is particularly plausible in India, where global
  market shocks can impact all asset classes including crypto and domestic equities.

  >> VERDICT: Aggressive
  Your current allocation, particularly the 30% in Bitcoin, introduces a significant
  risk of ruin if multiple market downturns coincide.

----------------------------------------------------------------------------------------------------

```


---

## Project Structure

```
devil_advocate/
├── main.py                  ← CLI entry point, orchestrates the flow
├── risk_engine.py           ← Pure deterministic math (no AI)
├── gemini_client.py         ← Both Gemini API calls
├── display.py               ← All terminal formatting / colors
├── demo_portfolio.json      ← Example portfolio for testing
├── requirements.txt
└── README.md
```

---

## My Approach & Design Decisions

### Why this for Task 04?
Timecell's homepage has one standout quote: *"Show me the assumption you'd have to be wrong about."* Every other Task (01–03) builds tools that compute outcomes. None of them ask *why* those outcomes might be wrong. This is the gap I chose to fill — not because it was the easiest thing to build, but because it's the most philosophically aligned with what Timecell actually believes.

### Prompt Engineering (what worked)
- **First attempt**: Asked Gemini to return assumptions as free text. Problem: inconsistent format, hard to parse.
- **Second attempt**: Specified a strict JSON schema with a fixed set of `stress_type` values. This made the output machine-readable while keeping it semantically rich.
- **Key decision**: Map each assumption to a `stress_type` that the deterministic math engine knows how to handle. This creates a closed loop: AI → math → AI. Neither layer is doing more than it should.

### What the AI does vs what the math does
- **AI**: Extract beliefs, explain consequences in plain English. Subjective, contextual, narrative.
- **Math**: Compute runway, ruin test, crash losses. Deterministic, auditable, exact.
- This separation is intentional. A language model should not be trusted to multiply numbers. It should be trusted to understand context.

### AI Usage
- Used Gemini 2.5 Flash (free tier via Google AI Studio)
- Two calls per run: assumption extraction + explanation
- Chose Gemini because it has a generous free tier, fast inference, and strong JSON output when prompted carefully

---

## What I'd Add With More Time
- Historical correlation data (pull actual BTC/NIFTY correlation coefficients from yfinance)
- Monte Carlo simulation mode — run 10,000 random crash scenarios and show probability distribution
- Save/compare assumption reports across portfolio versions
- Interactive mode: let the user challenge the AI's assumptions in a back-and-forth conversation
