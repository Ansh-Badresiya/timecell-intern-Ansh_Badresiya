# Task 1: Portfolio Risk Calculator

## Overview
This task consists of a highly deterministic, math-driven **Portfolio Risk Calculator**. It evaluates a portfolio's resilience against expected market crashes by computing post-crash values, runway months (how long the portfolio can sustain monthly expenses), and identifying the largest risk contributor.

## Workflow
1. **Input Loading**: The script automatically loads portfolio data (asset names, allocation percentages, expected crash percentages) and financial context (total value, monthly expenses) from a shared `demo_portfolio.json` file in the project root.
2. **Metrics Computation**: It calculates the absolute post-crash value for each asset based on its expected drawdown, and aggregates these to find the total post-crash portfolio value.
3. **Runway Analysis**: It divides the post-crash value by the monthly expenses to determine the runway in months.
4. **Ruin Test**: If the post-crash runway is greater than 12 months, the portfolio "PASSES" the ruin test. Otherwise, it "FAILS".
5. **Concentration Warning**: It flags any asset that makes up more than 40% of the portfolio.

## How to Run
Run the script via the command line:
```bash
python portfolio_risk_calculator.py
```
To run a side-by-side comparison with a moderate crash (50% of the expected crash magnitude):
```bash
python portfolio_risk_calculator.py --moderate
```

## Expected Output
The terminal will display a colorful, formatted ASCII interface:
1. **Confirmation**: `[OK] Loaded portfolio from: demo_portfolio.json`
2. **Portfolio Summary**: Total value, expenses, and asset count.
3. **Allocation Bar Chart**: A visual representation of how the portfolio is distributed, color-coded by the severity of the expected crash for each asset.
4. **Scenario Metrics / Comparison Table**: A clean breakdown of the post-crash value, runway months, ruin test result, and the most dangerous asset.
5. **Final Verdict**: A clear `[PASS]` or `[FAIL]` status indicating if the portfolio survives 12 months post-crash.
