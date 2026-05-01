import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

import argparse
import json
import os
from dataclasses import dataclass
from typing import Optional

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
#                             DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass
class Asset:
    """Represents a single asset in the portfolio."""
    name: str                      # asset name (eg. "BTC", "NIFTY50")
    allocation_pct: float          # percentage of portfolio (0-100)
    expected_crash_pct: float      # expected drop in crash (negative, eg. -40)


@dataclass
class Portfolio:
    """Complete portfolio definition."""
    total_value_inr: float         # total portfolio value in INR
    monthly_expenses_inr: float    # monthly living expenses in INR
    assets: list[Asset]            # list of assets


@dataclass
class RiskMetrics:
    """Computed risk metrics for a crash scenario."""
    post_crash_value: float        # portfolio value after crash
    runway_months: int             # months the portfolio can cover expenses
    ruin_test: str                 # "PASS" or "FAIL" (runway > 12?)
    largest_risk_asset: str        # name of highest-risk asset
    largest_risk_score: float      # risk score of that asset
    concentration_warning: bool    # True if any asset > 40%


# ═══════════════════════════════════════════════════════════════════════════════
#                        SECTION 1 — INPUT VALIDATION
# ═══════════════════════════════════════════════════════════════════════════════

def validate_portfolio(portfolio: Portfolio) -> None:
    """
    Validate portfolio structure and values.
    Raises exceptions on critical errors.

    Checks:
      - Asset allocation sums to ~100% (with tolerance for rounding)
      - All allocations are non-negative
      - All crash percentages are <= 0 (losses are negative)
      - At least 1 asset exists
      - Monthly expenses is non-negative
    """
    if not portfolio.assets:
        raise ValueError("Portfolio must contain at least one asset.")

    if portfolio.total_value_inr <= 0:
        raise ValueError("Portfolio value must be positive.")

    if portfolio.monthly_expenses_inr < 0:
        raise ValueError("Monthly expenses cannot be negative.")

    total_allocation = sum(a.allocation_pct for a in portfolio.assets)

    # Allow 0.1% rounding error
    if not (99.9 <= total_allocation <= 100.1):
        print(f"[!] WARNING: Asset allocations sum to {total_allocation:.1f}%, not 100%.")
        print("    Proceeding anyway, but results may be off.")

    for asset in portfolio.assets:
        if asset.allocation_pct < 0:
            raise ValueError(f"Asset '{asset.name}' has negative allocation: {asset.allocation_pct}%")
        if asset.expected_crash_pct > 0:
            raise ValueError(
                f"Asset '{asset.name}' has positive crash pct: {asset.expected_crash_pct}%. "
                "Crashes should be negative (e.g. -40 for -40%)."
            )


# ═══════════════════════════════════════════════════════════════════════════════
#                     SECTION 2 — CORE METRIC COMPUTATION
# ═══════════════════════════════════════════════════════════════════════════════

def _asset_value_after_crash(
    asset: Asset,
    total_value: float,
    crash_magnitude: float,  # eg. 1.0 for 100% of expected crash, 0.5 for 50%
) -> float:
    """
    Computing the value of a single asset after a crash.

    Parameters:

    asset              : the Asset object
    total_value        : total portfolio value in INR
    crash_magnitude    : multiplier applied to expected crash
                        (1.0 = full crash, 0.5 = moderate crash at 50%)

    Returns:

    float : asset value after crash
    
    Formula:
      asset_initial_value = (allocation_pct / 100) * total_value
      crash_pct_applied   = expected_crash_pct * crash_magnitude
      asset_post_crash    = asset_initial_value * (1 + crash_pct_applied / 100)
    """
    initial_value = (asset.allocation_pct / 100) * total_value
    crash_applied = asset.expected_crash_pct * crash_magnitude
    post_crash    = initial_value * (1 + crash_applied / 100)
    return post_crash


def compute_risk_metrics(
    portfolio: Portfolio,
    crash_magnitude: float = 1.0,  # 1.0 = full crash, 0.5 = moderate (50%)
) -> RiskMetrics:
    """
    Compute all portfolio risk metrics for a given crash scenario.

    Parameters:

    portfolio        : Portfolio object with assets and totals
    crash_magnitude  : multiplier for expected crash percentages
                      (1.0 = severe crash, 0.5 = moderate crash)

    Returns:

    RiskMetrics : dataclass with all computed values
    """
    validate_portfolio(portfolio)

    # ── Compute post-crash value ──────────────────────────────────────────────

    post_crash_value = sum(
        _asset_value_after_crash(asset, portfolio.total_value_inr, crash_magnitude)
        for asset in portfolio.assets
    )

    # ── Compute runway months ─────────────────────────────────────────────────

    if portfolio.monthly_expenses_inr == 0:
        # No expenses — infinite runway
        runway_months = float('inf')
    else:
        runway_months = int(post_crash_value // portfolio.monthly_expenses_inr)

    # ── Ruin test ─────────────────────────────────────────────────────────────

    ruin_test = "PASS" if runway_months > 12 else "FAIL"

    # ── Largest risk asset ────────────────────────────────────────────────────

    # Risk contribution = allocation_pct * abs(expected_crash_pct)
    # (we use abs because a -40% crash means 40% magnitude)
    risk_scores = [
        (asset.name, asset.allocation_pct * abs(asset.expected_crash_pct))
        for asset in portfolio.assets
    ]
    largest_risk_asset, largest_risk_score = max(risk_scores, key=lambda x: x[1])

    # ── Concentration warning ─────────────────────────────────────────────────

    concentration_warning = any(a.allocation_pct > 40 for a in portfolio.assets)

    return RiskMetrics(
        post_crash_value=post_crash_value,
        runway_months=int(runway_months) if runway_months != float('inf') else -1,
        ruin_test=ruin_test,
        largest_risk_asset=largest_risk_asset,
        largest_risk_score=largest_risk_score,
        concentration_warning=concentration_warning,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#                       SECTION 3 — OUTPUT FORMATTING
# ═══════════════════════════════════════════════════════════════════════════════

def print_banner():
    print()
    print(f"{Colors.BOLD}{Colors.CYAN}+=============================================================================+{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}|                                                                             |{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}|                          PORTFOLIO RISK CALCULATOR                          |{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}|                                                                             |{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}+=============================================================================+{Colors.RESET}")
    print()

def _format_currency(value: float) -> str:
    """Format a value as INR currency with commas and two decimals."""
    if value >= 1e7:
        return f"Rs. {value / 1e7:.2f} Cr"
    elif value >= 1e5:
        return f"Rs. {value / 1e5:.2f} L"
    else:
        return f"Rs. {value:,.2f}"


def _format_runway(months: int) -> str:
    """Format runway months as a readable string."""
    if months == -1:
        return "inf (no expenses)"
    years = months // 12
    remaining_months = months % 12
    if years > 0:
        return f"{months} months ({years}y {remaining_months}m)"
    return f"{months} months"


def print_metrics_table(metrics: RiskMetrics, scenario_name: str = "SEVERE CRASH") -> None:
    """
    Print a colored, readable table of risk metrics.

    Parameters:

    metrics       : RiskMetrics dataclass
    scenario_name : label for the scenario
    """
    ruin_color   = Colors.GREEN if metrics.ruin_test == "PASS" else Colors.RED
    runway_color = Colors.GREEN if metrics.runway_months > 18 else (
        Colors.YELLOW if metrics.runway_months > 12 else Colors.RED
    )

    print(f"\n{Colors.BOLD}+{'=' * 68}+{Colors.RESET}")
    print(f"{Colors.BOLD}|  Scenario: {Colors.YELLOW}{scenario_name:<56}{Colors.RESET}{Colors.BOLD}|{Colors.RESET}")
    print(f"{Colors.BOLD}+{'=' * 68}+{Colors.RESET}")

    print(f"  {'Post-crash value':<35} {Colors.CYAN}{_format_currency(metrics.post_crash_value)}{Colors.RESET}")
    print(f"  {'Runway months':<35} {runway_color}{_format_runway(metrics.runway_months)}{Colors.RESET}")
    print(f"  {'Ruin test (runway > 12mo)?':<35} {ruin_color}{metrics.ruin_test}{Colors.RESET}")
    print(f"  {'Largest risk asset':<35} {Colors.YELLOW}{metrics.largest_risk_asset} (score: {metrics.largest_risk_score:.0f}){Colors.RESET}")

    if metrics.concentration_warning:
        print(f"  {'Concentration warning':<35} {Colors.RED}[!] YES -- one or more assets exceed 40%{Colors.RESET}")
    else:
        print(f"  {'Concentration warning':<35} {Colors.GREEN}[ OK ] No concentration risk{Colors.RESET}")

    print(f"{Colors.BOLD}+{'=' * 68}+{Colors.RESET}\n")


def print_comparison_table(
    severe: RiskMetrics,
    moderate: RiskMetrics,
    portfolio: Portfolio,
) -> None:
    """
    Print a colored side-by-side comparison of severe and moderate crash scenarios.
    """
    print(f"\n{Colors.BOLD}+{'=' * 98}+{Colors.RESET}")
    print(f"{Colors.BOLD}|  {'CRASH SCENARIO COMPARISON':<96}|{Colors.RESET}")
    print(f"{Colors.BOLD}+{'=' * 98}+{Colors.RESET}")

    header = (
        f"  {Colors.BOLD}{'Metric':<30}{Colors.RESET} | "
        f"{Colors.RED}{'Severe Crash (100%)':<30}{Colors.RESET} | "
        f"{Colors.YELLOW}{'Moderate Crash (50%)':<30}{Colors.RESET}"
    )
    print(header)
    print(f"  {'-' * 96}")

    def ruin_colored(val):
        return f"{Colors.GREEN}{val}{Colors.RESET}" if val == "PASS" else f"{Colors.RED}{val}{Colors.RESET}"

    rows = [
        (
            "Post-crash value",
            f"{Colors.CYAN}{_format_currency(severe.post_crash_value)}{Colors.RESET}",
            f"{Colors.CYAN}{_format_currency(moderate.post_crash_value)}{Colors.RESET}",
        ),
        (
            "Runway months",
            f"{Colors.YELLOW}{_format_runway(severe.runway_months)}{Colors.RESET}",
            f"{Colors.GREEN}{_format_runway(moderate.runway_months)}{Colors.RESET}",
        ),
        (
            "Ruin test",
            ruin_colored(severe.ruin_test),
            ruin_colored(moderate.ruin_test),
        ),
        (
            "Largest risk asset",
            f"{Colors.YELLOW}{severe.largest_risk_asset} ({severe.largest_risk_score:.0f}){Colors.RESET}",
            f"{Colors.YELLOW}{moderate.largest_risk_asset} ({moderate.largest_risk_score:.0f}){Colors.RESET}",
        ),
    ]

    for label, severe_val, moderate_val in rows:
        print(f"  {label:<30} | {severe_val:<30} | {moderate_val:<30}")

    print(f"{Colors.BOLD}+{'=' * 98}+{Colors.RESET}\n")


# ═══════════════════════════════════════════════════════════════════════════════
#                     SECTION 4 — CLI BAR CHART
# ═══════════════════════════════════════════════════════════════════════════════

def print_allocation_chart(portfolio: Portfolio) -> None:
    """
    Print a colored text-based bar chart of asset allocations.
    """
    print(f"\n{Colors.BOLD}+{'=' * 68}+{Colors.RESET}")
    print(f"{Colors.BOLD}|  {'Asset Allocation (Bar Chart)':<66}|{Colors.RESET}")
    print(f"{Colors.BOLD}+{'=' * 68}+{Colors.RESET}")

    max_name_len = max(len(a.name) for a in portfolio.assets) if portfolio.assets else 0

    for asset in portfolio.assets:
        num_blocks = max(1, int(asset.allocation_pct // 2))
        bar = "█" * num_blocks

        # Color by crash severity
        if asset.expected_crash_pct <= -60:
            bar_color = Colors.RED
        elif asset.expected_crash_pct <= -30:
            bar_color = Colors.YELLOW
        else:
            bar_color = Colors.GREEN

        print(
            f"  {Colors.WHITE}{asset.name:<{max_name_len}}{Colors.RESET} | "
            f"{bar_color}{bar}{Colors.RESET} "
            f"{Colors.BOLD}{asset.allocation_pct:.0f}%{Colors.RESET}  "
            f"{Colors.DIM}(crash: {asset.expected_crash_pct:.0f}%){Colors.RESET}"
        )

    print(f"{Colors.BOLD}+{'=' * 68}+{Colors.RESET}\n")


# ═══════════════════════════════════════════════════════════════════════════════
#                          SECTION 5 — MAIN ORCHESTRATION
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    """
    Entry point — parse arguments, compute metrics, and print reports.
    """
    # ── Argument parsing ──────────────────────────────────────────────────────

    parser = argparse.ArgumentParser(
        description="Portfolio Risk Calculator — analyze portfolio resilience under crash scenarios."
    )
    parser.add_argument(
        "--moderate",
        action="store_true",
        help="Also compute and display moderate crash scenario (50% of expected crash).",
    )
    args = parser.parse_args()

    # ── Print banner + load demo portfolio ───────────────────────────────────

    print_banner()

    portfolio_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demo_portfolio.json")
    try:
        with open(portfolio_path, "r") as f:
            data = json.load(f)
        portfolio = Portfolio(
            total_value_inr=data["total_value_inr"],
            monthly_expenses_inr=data["monthly_expenses_inr"],
            assets=[Asset(**a) for a in data["assets"]]
        )
        print(f"  {Colors.GREEN}[OK]{Colors.RESET} Loaded portfolio from: {Colors.CYAN}{os.path.basename(portfolio_path)}{Colors.RESET}\n")
    except Exception as e:
        sys.exit(f"{Colors.RED}[ERROR] Failed to load portfolio: {e}{Colors.RESET}")

    print(f"{Colors.BOLD}+{'=' * 68}+{Colors.RESET}")
    print(f"{Colors.BOLD}|  {'Portfolio Summary':<66}|{Colors.RESET}")
    print(f"{Colors.BOLD}+{'=' * 68}+{Colors.RESET}")
    print(f"  Total Value        : {Colors.GREEN}{_format_currency(portfolio.total_value_inr)}{Colors.RESET}")
    print(f"  Monthly Expenses   : {Colors.YELLOW}{_format_currency(portfolio.monthly_expenses_inr)}{Colors.RESET}")
    print(f"  Number of Assets   : {Colors.CYAN}{len(portfolio.assets)}{Colors.RESET}")
    print(f"{Colors.BOLD}+{'=' * 68}+{Colors.RESET}\n")

    # ── Print allocation chart ────────────────────────────────────────────────

    print_allocation_chart(portfolio)

    # ── Compute severe crash metrics ──────────────────────────────────────────

    try:
        severe_metrics = compute_risk_metrics(portfolio, crash_magnitude=1.0)
    except (ValueError, RuntimeError) as exc:
        sys.exit(f"[ERROR] {exc}")

    # ── Compute moderate crash metrics if --moderate flag is set ──────────────

    if args.moderate:
        moderate_metrics = compute_risk_metrics(portfolio, crash_magnitude=0.5)
        print_comparison_table(severe_metrics, moderate_metrics, portfolio)
    else:
        print_metrics_table(severe_metrics, scenario_name="SEVERE CRASH")

    # ── Summary line ──────────────────────────────────────────────────────────

    print(f"\n{Colors.BOLD}+{'=' * 68}+{Colors.RESET}")
    if severe_metrics.ruin_test == "PASS":
        print(f"  {Colors.GREEN}[PASS]{Colors.RESET} Your portfolio can survive 12+ months without additional income.")
    else:
        print(f"  {Colors.RED}[FAIL]{Colors.RESET} Your portfolio FAILS the ruin test -- less than 12 months of runway.")
    print(f"{Colors.BOLD}+{'=' * 68}+{Colors.RESET}\n")


if __name__ == "__main__":
    main()

