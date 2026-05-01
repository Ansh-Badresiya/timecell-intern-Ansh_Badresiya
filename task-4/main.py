import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

"""
main.py - CLI entry point for Devil's Advocate: Assumption Challenger
Usage:
  python main.py                          # demo mode
  python main.py --demo                   # demo mode explicit
  python main.py --portfolio myport.json  # custom portfolio file
  python main.py --decision "I want 50% BTC"  # custom decision with demo portfolio
"""

import argparse
import json
import time

from risk_engine import compute_risk_metrics, stress_test_assumption, format_inr
from gemini_client import init_gemini, extract_assumptions, explain_stress_results
from display import (
    print_banner,
    print_portfolio_summary,
    print_baseline_metrics,
    print_assumption,
    print_stress_result,
    print_final_explanation,
    print_separator,
    Colors,
)

DEMO_PORTFOLIO = {
    "total_value_inr": 10_000_000,
    "monthly_expenses_inr": 80_000,
    "assets": [
        {"name": "BTC",     "allocation_pct": 30, "expected_crash_pct": -80},
        {"name": "NIFTY50", "allocation_pct": 40, "expected_crash_pct": -40},
        {"name": "GOLD",    "allocation_pct": 20, "expected_crash_pct": -15},
        {"name": "CASH",    "allocation_pct": 10, "expected_crash_pct":   0},
    ],
}
DEMO_DECISION = "I want to keep 30% in BTC and hold through any crash — it always recovers."


def run(portfolio: dict, decision: str):
    print_banner()

    # Step 1: Show portfolio
    print_portfolio_summary(portfolio)
    print_separator()

    # Step 2: Baseline risk metrics
    print(f"\n{Colors.BOLD}[ STEP 1 ] Computing baseline risk metrics...{Colors.RESET}")
    baseline = compute_risk_metrics(portfolio)
    print_baseline_metrics(baseline, portfolio)

    # Step 3: Init Gemini (just validates API key)
    print(f"\n{Colors.BOLD}[ STEP 2 ] Connecting to Gemini AI...{Colors.RESET}")
    try:
        api_key = init_gemini()
        print("  [OK] Gemini 2.5 Flash ready")
    except EnvironmentError as e:
        print(f"  [ERROR] {e}")
        sys.exit(1)

    # Step 4: Extract assumptions
    print(f"\n{Colors.BOLD}[ STEP 3 ] Extracting hidden assumptions...{Colors.RESET}")
    print(f"  Decision: \"{Colors.YELLOW}{decision}{Colors.RESET}\"")
    print("  Asking Gemini to find what you're implicitly betting on...\n")

    try:
        assumptions = extract_assumptions(api_key, portfolio, decision)
    except Exception as e:
        print(f"  [ERROR] Failed to extract assumptions: {e}")
        sys.exit(1)

    for i, assumption in enumerate(assumptions, 1):
        print_assumption(i, assumption)
        time.sleep(0.2)

    print_separator()

    # Step 5: Stress test each assumption
    print(f"\n{Colors.BOLD}[ STEP 4 ] Stress-testing each assumption...{Colors.RESET}")
    print("  (What happens to your runway if each belief is WRONG?)\n")

    stress_results = []
    for assumption in assumptions:
        stress_params = dict(assumption.get("stress_params", {}))
        stress_params["stress_type"] = assumption["stress_type"]

        try:
            stressed = stress_test_assumption(portfolio, stress_params)
            runway_change = stressed.runway_months - baseline.runway_months
            result = {
                "id": assumption["id"],
                "assumption": assumption["assumption"],
                "stressed_runway": stressed.runway_months,
                "stressed_post_crash_value": stressed.post_crash_value,
                "stressed_ruin_test": stressed.ruin_test,
                "runway_change": runway_change,
            }
            stress_results.append(result)
            print_stress_result(result, baseline.runway_months)
        except Exception as e:
            print(f"  [!] Could not stress-test assumption #{assumption['id']}: {e}")

        time.sleep(0.15)

    print_separator()

    # Step 6: AI explanation
    print(f"\n{Colors.BOLD}[ STEP 5 ] Generating Devil's Advocate analysis...{Colors.RESET}")
    print("  Asking Gemini to explain what the numbers mean...\n")

    try:
        explanation = explain_stress_results(api_key, baseline, stress_results, decision)
        print_final_explanation(explanation)
    except Exception as e:
        print(f"  [ERROR] Failed to generate explanation: {e}")

    print_separator()
    print("  Timecell Devil's Advocate - Task 04 | Built with Gemini 2.5 Flash\n")


def main():
    parser = argparse.ArgumentParser(
        description="Devil's Advocate: Stress-test the hidden assumptions in your portfolio decision"
    )
    parser.add_argument("--portfolio", type=str, help="Path to portfolio JSON file")
    parser.add_argument("--decision", type=str, help="The portfolio decision to challenge")
    parser.add_argument("--demo", action="store_true", help="Run with built-in demo portfolio")
    args = parser.parse_args()

    if args.demo or (not args.portfolio and not args.decision):
        run(DEMO_PORTFOLIO, DEMO_DECISION)
        return

    portfolio = DEMO_PORTFOLIO
    decision = DEMO_DECISION

    if args.portfolio:
        try:
            with open(args.portfolio) as f:
                data = json.load(f)
            portfolio = data.get("portfolio", data)
            decision = args.decision or data.get("decision", DEMO_DECISION)
        except FileNotFoundError:
            print(f"Error: File '{args.portfolio}' not found.")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON: {e}")
            sys.exit(1)
    elif args.decision:
        decision = args.decision

    run(portfolio, decision)


if __name__ == "__main__":
    main()