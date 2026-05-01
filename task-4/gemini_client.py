"""
gemini_client.py — All Gemini API interactions via raw HTTP.
Two calls: extract assumptions, then explain stress test results.
"""

import json
import os
import re
import requests
from dotenv import load_dotenv


GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"


def init_gemini() -> str:
    """Load .env, validate GEMINI_API_KEY, return it."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "GEMINI_API_KEY not found.\n"
            "  1. Copy .env.example to .env\n"
            "  2. Add your key: GEMINI_API_KEY=your_key_here\n"
            "  Get a free key at: https://aistudio.google.com"
        )
    return api_key


def _call_gemini(api_key: str, prompt: str) -> str:
    headers = {"Content-Type": "application/json"}
    params = {"key": api_key}
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.3,
            "maxOutputTokens": 20000,
        },
    }
    response = requests.post(
        GEMINI_API_URL,
        headers=headers,
        params=params,
        json=payload,
        timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"Gemini API error {response.status_code}: {response.text[:300]}"
        )
    data = response.json()
    return data["candidates"][0]["content"]["parts"][0]["text"]


def extract_assumptions(api_key: str, portfolio: dict, decision: str) -> list:
    assets_summary = "\n".join(
        f"  - {a['name']}: {a['allocation_pct']}% allocation, expected crash: {a['expected_crash_pct']}%"
        for a in portfolio["assets"]
    )

    prompt = f"""You are a senior risk analyst at a family office. A client has presented the following portfolio and decision.

PORTFOLIO:
- Total Value: Rs {portfolio['total_value_inr']:,}
- Monthly Expenses: Rs {portfolio['monthly_expenses_inr']:,}
- Assets:
{assets_summary}

CLIENT DECISION: "{decision}"

Your job: Identify the 4 hidden assumptions this investor is making — beliefs that must be TRUE for this decision to be safe.

Each assumption must be:
1. Specific and falsifiable
2. Financially consequential if wrong
3. Mapped to one of these stress test types:
   - "expense_shock" -> assumes expenses stay constant
   - "correlated_crash" -> assumes asset crashes are independent
   - "liquidity_need" -> assumes no urgent cash need in near term
   - "slower_recovery" -> assumes a specific asset recovers quickly
   - "inflation_expense" -> assumes expenses won't inflate

Respond ONLY with a valid JSON array. No explanation, no markdown, no backticks.

Format:
[
  {{
    "id": 1,
    "assumption": "One clear sentence stating the belief",
    "consequence_if_wrong": "What financially happens if this is false",
    "stress_type": "one of the 5 types above",
    "stress_params": {{}}
  }}
]

For stress_params:
- expense_shock: {{"multiplier": 1.5}}
- correlated_crash: {{"multiplier": 1.4}}
- liquidity_need: {{"withdrawal_inr": 500000}}
- slower_recovery: {{"extra_decay_pct": 20, "target_asset": "ASSET_NAME"}}
- inflation_expense: {{"annual_inflation_pct": 8, "years": 3}}

For slower_recovery, set target_asset to the riskiest asset in this portfolio.
Use ONLY the 5 stress_type values listed. Return exactly 4 assumptions covering different risk types.
"""

    raw_text = _call_gemini(api_key, prompt).strip()
    raw_text = re.sub(r"^```json\s*", "", raw_text)
    raw_text = re.sub(r"\s*```$", "", raw_text)
    raw_text = raw_text.strip()
    return json.loads(raw_text)


def explain_stress_results(api_key: str, baseline_metrics, stress_results: list, decision: str) -> str:
    results_text = ""
    for r in stress_results:
        status = "FAIL" if r["stressed_ruin_test"] == "FAIL" else "PASS"
        results_text += (
            f"\nAssumption #{r['id']}: \"{r['assumption']}\"\n"
            f"  Baseline: {baseline_metrics.runway_months:.1f}mo -> Stressed: {r['stressed_runway']:.1f}mo | {status}\n"
            f"  Change: {r['runway_change']:+.1f} months\n"
        )

    prompt = f"""You are a CIO at a family office. You just stress-tested a client's portfolio.

CLIENT DECISION: "{decision}"
BASELINE RUNWAY: {baseline_metrics.runway_months:.1f} months | RUIN TEST: {baseline_metrics.ruin_test}

STRESS TEST RESULTS:
{results_text}

Write a plain-English explanation for a non-expert HNI client. Direct, honest, like a trusted advisor.

Use exactly these 4 section headers:

SUMMARY:
[2-3 sentences on overall health and what stress tests revealed]

WHAT YOU'RE DOING WELL:
[1 specific genuinely good thing]

WEAKEST ASSUMPTION:
[Which assumption causes most damage if wrong, and why it's plausible in India's market]

VERDICT: [Aggressive / Balanced / Conservative]
[One sentence explaining]

Under 220 words total. Prose only, no bullet points.
"""
    return _call_gemini(api_key, prompt).strip()