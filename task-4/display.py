"""
display.py - All terminal output / formatting logic.
"""

from risk_engine import RiskMetrics, format_inr


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
#                                 Helpers
# ═══════════════════════════════════════════════════════════════════════════════

def print_separator(char="-", width=100):
    print(f"\n{Colors.DIM}{char * width}{Colors.RESET}\n")


def print_banner():
    print()
    print(f"{Colors.BOLD}{Colors.CYAN}+================================================================================+{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}|                    DEVIL'S ADVOCATE -- Assumption Challenger                  |{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}|               \"Show me the assumption you'd have to be wrong                  |{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}|                      about for this to be the wrong call.\"                    |{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}|                                                   -- Timecell.ai              |{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}+================================================================================+{Colors.RESET}")
    print()


def print_portfolio_summary(portfolio: dict):
    print(f"{Colors.BOLD}PORTFOLIO OVERVIEW{Colors.RESET}")
    print(f"  Total Value     : {Colors.GREEN}{format_inr(portfolio['total_value_inr'])}{Colors.RESET}")
    print(f"  Monthly Expenses: {Colors.YELLOW}{format_inr(portfolio['monthly_expenses_inr'])}{Colors.RESET}")
    print()
    print(f"  {'Asset':<12} {'Allocation':>10} {'Expected Crash':>15}  {'Bar'}")
    print(f"  {'─'*12} {'─'*10} {'─'*15}  {'─'*20}")

    for asset in portfolio["assets"]:
        name  = asset["name"]
        alloc = asset["allocation_pct"]
        crash = asset["expected_crash_pct"]

        # Color by crash severity
        if crash <= -60:
            crash_color = Colors.RED
        elif crash <= -30:
            crash_color = Colors.YELLOW
        else:
            crash_color = Colors.GREEN

        # Bar chart — plain '=' chars, no block chars
        bar = "█" * (alloc // 5)

        print(
            f"  {name:<12} {alloc:>9}%  "
            f"{crash_color}{crash:>13}%{Colors.RESET}  "
            f"{Colors.BLUE}{bar}{Colors.RESET}"
        )


def print_baseline_metrics(metrics: RiskMetrics, portfolio: dict):
    print(f"\n{Colors.BOLD}BASELINE RISK METRICS (full crash scenario){Colors.RESET}")

    ruin_color   = Colors.GREEN if metrics.ruin_test == "PASS" else Colors.RED
    runway_color = Colors.GREEN if metrics.runway_months > 18 else (
        Colors.YELLOW if metrics.runway_months > 12 else Colors.RED
    )

    print(f"  Post-Crash Value  : {Colors.CYAN}{format_inr(metrics.post_crash_value)}{Colors.RESET}")
    print(f"  Runway            : {runway_color}{metrics.runway_months:.1f} months{Colors.RESET}")
    print(f"  Ruin Test (>12mo) : {ruin_color}{metrics.ruin_test}{Colors.RESET}")
    print(f"  Largest Risk Asset: {Colors.YELLOW}{metrics.largest_risk_asset}{Colors.RESET}")

    if metrics.concentration_warning:
        print(f"  {Colors.RED}[!] Concentration Warning: One asset exceeds 40% of portfolio{Colors.RESET}")

    # Per-asset crash breakdown
    print(f"\n  {'Asset':<12} {'Before Crash':>14} {'After Crash':>14} {'Loss':>14}")
    print(f"  {'─'*12} {'─'*14} {'─'*14} {'─'*14}")
    for name, data in metrics.crash_losses.items():
        loss_color = Colors.RED if data["loss_amount"] > 0 else Colors.GREEN
        print(
            f"  {name:<12} "
            f"{format_inr(data['initial_value']):>14} "
            f"{format_inr(data['post_crash_value']):>14} "
            f"{loss_color}-{format_inr(data['loss_amount']):>13}{Colors.RESET}"
        )


def print_assumption(index: int, assumption: dict):
    # Plain ASCII labels replacing emoji
    type_labels = {
        "expense_shock":     "[EXP] Expense Risk",
        "correlated_crash":  "[COR] Correlation Risk",
        "liquidity_need":    "[LIQ] Liquidity Risk",
        "slower_recovery":   "[REC] Recovery Risk",
        "inflation_expense": "[INF] Inflation Risk",
    }
    label = type_labels.get(assumption.get("stress_type", ""), "[???] Unknown")

    print(f"  {Colors.BOLD}#{index}{Colors.RESET} [{Colors.YELLOW}{label}{Colors.RESET}]")
    print(f"     Assumption  : {Colors.WHITE}{assumption['assumption']}{Colors.RESET}")
    print(f"     If wrong    : {Colors.DIM}{assumption.get('consequence_if_wrong', 'See stress test')}{Colors.RESET}")
    print()


def print_stress_result(result: dict, baseline_runway: float):
    change     = result["runway_change"]
    pct_change = (change / baseline_runway * 100) if baseline_runway > 0 else 0

    # Plain ASCII status tags instead of emoji
    status_tag   = "[FAIL]" if result["stressed_ruin_test"] == "FAIL" else "[ OK ]"
    status_color = Colors.RED if result["stressed_ruin_test"] == "FAIL" else Colors.GREEN
    change_color = Colors.RED if change < -3 else (Colors.YELLOW if change < 0 else Colors.GREEN)

    assumption_text = result["assumption"]
    if len(assumption_text) > 55:
        assumption_text = assumption_text[:52] + "..."

    print(
        f"  {status_color}{status_tag}{Colors.RESET} "
        f"Assumption #{result['id']}: "
        f"{Colors.DIM}{assumption_text}{Colors.RESET}"
    )
    print(
        f"     Runway: {Colors.CYAN}{baseline_runway:.1f}mo{Colors.RESET} -> "
        f"{change_color}{result['stressed_runway']:.1f}mo{Colors.RESET} "
        f"({change_color}{change:+.1f}mo, {pct_change:+.0f}%{Colors.RESET})  "
        f"Ruin test: "
        f"{Colors.RED if result['stressed_ruin_test'] == 'FAIL' else Colors.GREEN}"
        f"{result['stressed_ruin_test']}{Colors.RESET}"
    )
    print()


def print_final_explanation(explanation: str):
    print(f"{Colors.BOLD}+===============================================================================+{Colors.RESET}")
    print(f"{Colors.BOLD}|                             DEVIL'S ADVOCATE VERDICT                          |{Colors.RESET}")
    print(f"{Colors.BOLD}+===============================================================================+{Colors.RESET}")
    print()

    lines = explanation.strip().split("\n")
    for line in lines:
        stripped = line.strip()
        if not stripped:
            print()
            continue

        upper = stripped.upper()

        # Section headers — colored, plain ASCII arrow instead of emoji
        if upper.startswith("SUMMARY"):
            print(f"  {Colors.BOLD}{Colors.CYAN}>> SUMMARY{Colors.RESET}")
        elif upper.startswith("WHAT YOU"):
            print(f"\n  {Colors.BOLD}{Colors.GREEN}>> WHAT YOU'RE DOING WELL{Colors.RESET}")
        elif upper.startswith("WEAKEST"):
            print(f"\n  {Colors.BOLD}{Colors.RED}>> WEAKEST ASSUMPTION{Colors.RESET}")
        elif upper.startswith("VERDICT"):
            print(f"\n  {Colors.BOLD}{Colors.YELLOW}>> {stripped}{Colors.RESET}")
        else:
            print(f"  {stripped}")