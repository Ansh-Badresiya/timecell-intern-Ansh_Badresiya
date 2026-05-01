"""
risk_engine.py — Pure deterministic math.
Computes crash survival, runway, and portfolio risk metrics.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class RiskMetrics:
    post_crash_value: float
    runway_months: float
    ruin_test: str  # 'PASS' or 'FAIL'
    largest_risk_asset: str
    concentration_warning: bool
    crash_losses: dict  # per-asset loss breakdown


def compute_risk_metrics(portfolio: dict, crash_multiplier: float = 1.0) -> RiskMetrics:
    """
    Core risk calculator.
    crash_multiplier: 1.0 = full crash, 0.5 = moderate crash scenario
    """
    total_value = portfolio["total_value_inr"]
    monthly_expenses = portfolio["monthly_expenses_inr"]
    assets = portfolio["assets"]

    if total_value <= 0:
        raise ValueError("Portfolio value must be positive")
    if monthly_expenses <= 0:
        raise ValueError("Monthly expenses must be positive")

    total_allocation = sum(a["allocation_pct"] for a in assets)
    if abs(total_allocation - 100) > 0.01:
        raise ValueError(f"Allocations must sum to 100%, got {total_allocation}%")

    crash_losses = {}
    post_crash_value = 0.0
    largest_risk_score = 0.0
    largest_risk_asset = "NONE"

    for asset in assets:
        name = asset["name"]
        alloc_pct = asset["allocation_pct"]
        crash_pct = asset["expected_crash_pct"]  # negative number e.g. -80

        asset_value = total_value * (alloc_pct / 100)
        loss_pct = crash_pct * crash_multiplier  # apply multiplier for moderate scenario
        asset_post_crash = asset_value * (1 + loss_pct / 100)
        loss_amount = asset_value - asset_post_crash

        crash_losses[name] = {
            "initial_value": asset_value,
            "post_crash_value": asset_post_crash,
            "loss_amount": loss_amount,
            "loss_pct": loss_pct,
        }

        post_crash_value += asset_post_crash

        # Risk score = allocation × crash magnitude
        risk_score = alloc_pct * abs(crash_pct)
        if risk_score > largest_risk_score:
            largest_risk_score = risk_score
            largest_risk_asset = name

    runway_months = post_crash_value / monthly_expenses if monthly_expenses > 0 else float("inf")
    ruin_test = "PASS" if runway_months > 12 else "FAIL"
    concentration_warning = any(a["allocation_pct"] > 40 for a in assets)

    return RiskMetrics(
        post_crash_value=post_crash_value,
        runway_months=runway_months,
        ruin_test=ruin_test,
        largest_risk_asset=largest_risk_asset,
        concentration_warning=concentration_warning,
        crash_losses=crash_losses,
    )


def stress_test_assumption(portfolio: dict, assumption: dict) -> RiskMetrics:
    """
    Modify the portfolio based on an assumption being WRONG,
    then recompute risk metrics.
    """
    import copy
    stressed_portfolio = copy.deepcopy(portfolio)

    assumption_type = assumption.get("stress_type")

    if assumption_type == "expense_shock":
        # Assumption was: expenses stay constant. If wrong, they spike.
        multiplier = assumption.get("multiplier", 1.5)
        stressed_portfolio["monthly_expenses_inr"] *= multiplier

    elif assumption_type == "correlated_crash":
        # Assumption was: crashes are independent. If wrong, all risky assets crash together harder.
        multiplier = assumption.get("multiplier", 1.4)
        for asset in stressed_portfolio["assets"]:
            if asset["expected_crash_pct"] < -10:  # risky assets only
                asset["expected_crash_pct"] = min(asset["expected_crash_pct"] * multiplier, -100)

    elif assumption_type == "liquidity_need":
        # Assumption was: no urgent liquidity needed. If wrong, must withdraw a lump sum now.
        withdrawal = assumption.get("withdrawal_inr", 500_000)
        stressed_portfolio["total_value_inr"] = max(
            stressed_portfolio["total_value_inr"] - withdrawal, 1
        )
        # Allocations stay the same (percentages don't change, just total value drops)

    elif assumption_type == "slower_recovery":
        # Assumption was: assets recover in X years. If wrong, crash value is locked in.
        # Simulate by making the crash worse (value stays depressed)
        extra_decay = assumption.get("extra_decay_pct", 20)
        for asset in stressed_portfolio["assets"]:
            if asset["name"] == assumption.get("target_asset", "BTC"):
                asset["expected_crash_pct"] = min(
                    asset["expected_crash_pct"] - extra_decay, -100
                )

    elif assumption_type == "inflation_expense":
        # Assumption was: expenses won't inflate. If wrong, real expenses are higher.
        annual_inflation = assumption.get("annual_inflation_pct", 8)
        years = assumption.get("years", 3)
        inflation_factor = (1 + annual_inflation / 100) ** years
        stressed_portfolio["monthly_expenses_inr"] *= inflation_factor

    return compute_risk_metrics(stressed_portfolio)


def format_inr(amount: float) -> str:
    """Format a number as Indian Rupees with crore/lakh notation (plain ASCII)."""
    if amount >= 1_00_00_000:
        return f"Rs. {amount/1_00_00_000:.2f} Cr"
    elif amount >= 1_00_000:
        return f"Rs. {amount/1_00_000:.2f} L"
    else:
        return f"Rs. {amount:,.0f}"