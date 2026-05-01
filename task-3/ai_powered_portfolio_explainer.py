"""
Task 03 — AI-Powered Portfolio Explainer
=========================================
Timecell Intern Assessment

Uses an LLM (Google Gemini or OpenAI) to generate plain-English portfolio
risk explanations with structured outputs:
  - Risk summary (3-4 sentences)
  - What the investor is doing well
  - What the investor should consider changing
  - Verdict (Aggressive / Balanced / Conservative)

Bonuses included:
  - Configurable tone (--tone beginner/experienced/expert)
  - Second LLM call that critiques the first explanation (--critique)

This script was written with AI assistance (Claude).

Dependencies:
    pip install python-dotenv google-genai openai

.env file should contain:
    GEMINI_API_KEY=your_google_gemini_key_here
    OPENAI_API_KEY=your_openai_key_here   # optional fallback

Usage:
    python portfolio_explainer.py
    python portfolio_explainer.py --tone experienced
    python portfolio_explainer.py --tone expert --critique
"""

import argparse
import os
import re
import sys
import io
import json
import sys
import io
from dataclasses import dataclass

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

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

try:
    from dotenv import load_dotenv
except ImportError:
    sys.exit("Missing: python-dotenv  →  pip install python-dotenv")

load_dotenv()


# ═══════════════════════════════════════════════════════════════════════════════
#                                DATA STRUCTURES
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class Asset:
    """Represents a single asset in the portfolio."""
    name: str
    allocation_pct: float
    expected_crash_pct: float


@dataclass
class Portfolio:
    """Complete portfolio definition."""
    total_value_inr: float
    monthly_expenses_inr: float
    assets: list[Asset]


@dataclass
class RiskMetrics:
    """Computed risk metrics."""
    post_crash_value: float
    runway_months: int
    ruin_test: str
    largest_risk_asset: str
    largest_risk_score: float
    concentration_warning: bool


@dataclass
class ParsedExplanation:
    """Structured LLM explanation with four required parts."""
    summary: str
    doing_well: str
    consider_changing: str
    verdict: str


# ═══════════════════════════════════════════════════════════════════════════════
#             SECTION 1 — RISK METRIC COMPUTATION (same as Task 1)
# ═══════════════════════════════════════════════════════════════════════════════

def compute_risk_metrics(portfolio: Portfolio) -> RiskMetrics:
    """
    Compute portfolio risk metrics to provide context to the LLM.

    Returns
    -------
    RiskMetrics dataclass with:
      - post_crash_value
      - runway_months
      - ruin_test (PASS / FAIL)
      - largest_risk_asset
      - largest_risk_score
      - concentration_warning
    """
    # Post-crash value
    post_crash_value = sum(
        (asset.allocation_pct / 100) * portfolio.total_value_inr *
        (1 + asset.expected_crash_pct / 100)
        for asset in portfolio.assets
    )

    # Runway months
    if portfolio.monthly_expenses_inr == 0:
        runway_months = -1  # infinite
    else:
        runway_months = int(post_crash_value // portfolio.monthly_expenses_inr)

    # Ruin test
    ruin_test = "PASS" if runway_months > 12 else "FAIL"

    # Largest risk asset
    risk_scores = [
        (asset.name, asset.allocation_pct * abs(asset.expected_crash_pct))
        for asset in portfolio.assets
    ]
    largest_risk_asset, largest_risk_score = max(risk_scores, key=lambda x: x[1])

    # Concentration warning
    concentration_warning = any(a.allocation_pct > 40 for a in portfolio.assets)

    return RiskMetrics(
        post_crash_value=post_crash_value,
        runway_months=runway_months,
        ruin_test=ruin_test,
        largest_risk_asset=largest_risk_asset,
        largest_risk_score=largest_risk_score,
        concentration_warning=concentration_warning,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#                          SECTION 2 — LLM HELPER
# ═══════════════════════════════════════════════════════════════════════════════

def _strip_markdown(text: str) -> str:
    """Remove markdown symbols for clean terminal output."""
    text = re.sub(r'\*{1,2}|_{1,2}', '', text)
    text = re.sub(r'`+', '', text)
    text = re.sub(r'^#{1,6}\s*', '', text, flags=re.MULTILINE)
    text = re.sub(r'^\s*[\*\+]\s+', '- ', text, flags=re.MULTILINE)
    text = re.sub(r'  +', ' ', text)
    return text.strip()


def call_llm(prompt: str) -> str:
    """
    Single reusable LLM helper.

    Detection order:
      1. GEMINI_API_KEY (preferred — generous free tier)
      2. OPENAI_API_KEY (fallback)

    Parameters
    ----------
    prompt : fully engineered prompt string

    Returns
    -------
    str : cleaned plain-text response from the LLM

    Raises
    ------
    RuntimeError : if no API key is found or all calls fail
    """
    gemini_key = os.getenv("GEMINI_API_KEY", "").strip()
    openai_key = os.getenv("OPENAI_API_KEY", "").strip()

    if not gemini_key and not openai_key:
        raise RuntimeError(
            "No LLM API key found.\n"
            "Set GEMINI_API_KEY or OPENAI_API_KEY in your .env file."
        )

    # ── Try Gemini first ──────────────────────────────────────────────────────

    if gemini_key:
        try:
            from google import genai as google_genai
            client   = google_genai.Client(api_key=gemini_key)
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
            )
            return _strip_markdown(response.text.strip())
        except Exception as exc:
            print(f"[!] Gemini call failed: {exc}")
            if openai_key:
                print("    Falling back to OpenAI...")

    # ── Fall back to OpenAI ───────────────────────────────────────────────────

    if openai_key:
        try:
            from openai import OpenAI
            client     = OpenAI(api_key=openai_key)
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=400,
                temperature=0.7,
            )
            return _strip_markdown(completion.choices[0].message.content.strip())
        except Exception as exc:
            raise RuntimeError(f"OpenAI call failed: {exc}")

    raise RuntimeError("All LLM API calls failed.")


# ═══════════════════════════════════════════════════════════════════════════════
#                         SECTION 3 — PROMPT ENGINEERING
# ═══════════════════════════════════════════════════════════════════════════════

def build_prompt(
    portfolio: Portfolio,
    metrics: RiskMetrics,
    tone: str = "beginner",
) -> str:
    """
    Build the engineered prompt for the LLM.

    The prompt includes:
      - Portfolio composition
      - Computed risk metrics
      - Clear instructions for 4-part structured output
      - Tone-specific language guidance (Bonus 1)

    Parameters
    ----------
    portfolio : Portfolio object
    metrics   : RiskMetrics computed from the portfolio
    tone      : one of "beginner", "experienced", "expert"

    Returns
    -------
    str : complete prompt ready to send to the LLM
    """
    # ── Format portfolio for prompt ───────────────────────────────────────────

    asset_lines = "\n".join(
        f"  - {asset.name}: {asset.allocation_pct:.0f}% (crash: {asset.expected_crash_pct:.0f}%)"
        for asset in portfolio.assets
    )

    total_cr  = portfolio.total_value_inr / 1e7
    crash_cr  = metrics.post_crash_value / 1e7
    expenses  = portfolio.monthly_expenses_inr / 1e5

    # ── Tone-specific instructions ──────────────────────────────────

    tone_guide = {
        "beginner": (
            "Use very simple language. Avoid jargon. Use everyday analogies.\n"
            "For example, say 'your portfolio could drop by X%' instead of 'drawdown'."
        ),
        "experienced": (
            "You can use standard investment terms like volatility, correlation, diversification.\n"
            "The reader understands basic finance but isn't a professional."
        ),
        "expert": (
            "Use technical finance terminology freely: tail risk, factor exposure, "
            "Sharpe ratio, left-tail events, asset correlation.\n"
            "The reader is a sophisticated investor or finance professional."
        ),
    }

    tone_instruction = tone_guide.get(tone, tone_guide["beginner"])

    # ── Build the full prompt ─────────────────────────────────────────────────

    return f"""
You are a friendly but honest financial advisor. Your client has asked you to
explain the risk in their portfolio in plain English.

CLIENT PORTFOLIO:
Total value: ₹{total_cr:.2f} Crore
Monthly expenses: ₹{expenses:.2f} Lakh
Assets:
{asset_lines}

RISK METRICS YOU COMPUTED:
- Post-crash value (if all assets hit expected crash): ₹{crash_cr:.2f} Crore
- Runway (months portfolio can sustain expenses): {metrics.runway_months} months
- Ruin test (can survive 12+ months?): {metrics.ruin_test}
- Largest risk contributor: {metrics.largest_risk_asset} (score: {metrics.largest_risk_score:.0f})
- Concentration warning (any asset > 40%): {"YES" if metrics.concentration_warning else "NO"}

TONE GUIDANCE:
{tone_instruction}

OUTPUT FORMAT — CRITICAL — follow this exactly:
You must return EXACTLY four sections with these labels. Do NOT use markdown.

SUMMARY:
[Write 3-4 sentences explaining the portfolio's risk level. Mention the crash loss percentage,
runway months, and whether that's comfortable or risky. Be direct and specific.]

DOING WELL:
[One specific thing the investor is doing right with this portfolio. Be concrete — name an asset
or strategy.]

CONSIDER CHANGING:
[One specific thing the investor should change, and WHY. Name exact assets and percentages
if possible. Example: "Reduce BTC from 30% to 15% because it crashes 80% and dominates your risk."]

VERDICT:
[One word only: Aggressive, Balanced, or Conservative]

STRICT RULES:
- Plain text only. No asterisks, hashes, backticks, or markdown.
- Each section must start with its label exactly as shown above (SUMMARY:, DOING WELL:, etc.).
- Keep SUMMARY to 3-4 sentences. DOING WELL and CONSIDER CHANGING should each be 1-2 sentences.
- VERDICT must be exactly one of these three words: Aggressive, Balanced, Conservative.
""".strip()


# ═══════════════════════════════════════════════════════════════════════════════
#                      SECTION 4 — PARSING LLM RESPONSE
# ═══════════════════════════════════════════════════════════════════════════════

def parse_llm_response(raw_text: str) -> ParsedExplanation:
    """
    Extract the 4 required sections from the LLM response using delimiters.

    Parameters
    ----------
    raw_text : full text response from the LLM

    Returns
    -------
    ParsedExplanation dataclass with summary, doing_well, consider_changing, verdict

    Raises
    ------
    ValueError : if any required section is missing
    """
    # Case-insensitive search for section headers
    upper = raw_text.upper()

    # Find section positions
    summary_pos  = upper.find("SUMMARY:")
    doing_pos    = upper.find("DOING WELL:")
    consider_pos = upper.find("CONSIDER CHANGING:")
    verdict_pos  = upper.find("VERDICT:")

    if summary_pos == -1:
        raise ValueError("Missing SUMMARY: section in LLM response.")
    if doing_pos == -1:
        raise ValueError("Missing DOING WELL: section in LLM response.")
    if consider_pos == -1:
        raise ValueError("Missing CONSIDER CHANGING: section in LLM response.")
    if verdict_pos == -1:
        raise ValueError("Missing VERDICT: section in LLM response.")

    # Extract text between headers
    summary_text = raw_text[
        summary_pos + len("SUMMARY:"):doing_pos
    ].strip()

    doing_text = raw_text[
        doing_pos + len("DOING WELL:"):consider_pos
    ].strip()

    consider_text = raw_text[
        consider_pos + len("CONSIDER CHANGING:"):verdict_pos
    ].strip()

    verdict_text = raw_text[
        verdict_pos + len("VERDICT:"):
    ].strip()

    # Clean verdict to just the word
    verdict_clean = verdict_text.split()[0] if verdict_text else "Unknown"

    return ParsedExplanation(
        summary=summary_text,
        doing_well=doing_text,
        consider_changing=consider_text,
        verdict=verdict_clean,
    )


# ═══════════════════════════════════════════════════════════════════════════════
#                        SECTION 5 — OUTPUT FORMATTING
# ═══════════════════════════════════════════════════════════════════════════════

def print_banner():
    print()
    print(f"{Colors.BOLD}{Colors.CYAN}+================================================================================+{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}|                                                                                |{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}|                              AI PORTFOLIO EXPLAINER                            |{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}|                                                                                |{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}+================================================================================+{Colors.RESET}")
    print()


def print_report(parsed: ParsedExplanation, raw_response: str) -> None:
    """
    Print both the raw API response and the extracted structured output.
    """
    # ── Raw API Response ──────────────────────────────────────────────────────
    
    print(f"\n{Colors.BOLD}+{'=' * 78}+{Colors.RESET}")
    print(f"{Colors.BOLD}|  {Colors.DIM}Raw API Response{Colors.RESET}{Colors.BOLD}{'':>61}|{Colors.RESET}")
    print(f"{Colors.BOLD}+{'=' * 78}+{Colors.RESET}")
    print(f"{Colors.DIM}{raw_response}{Colors.RESET}")
    print(f"{Colors.BOLD}+{'=' * 78}+{Colors.RESET}\n")

    # ── Extracted Structured Output ───────────────────────────────────────────

    print(f"{Colors.BOLD}+{'=' * 78}+{Colors.RESET}")
    print(f"{Colors.BOLD}|  {Colors.GREEN}Extracted Output{Colors.RESET}{Colors.BOLD}{'':>61}|{Colors.RESET}")
    print(f"{Colors.BOLD}+{'=' * 78}+{Colors.RESET}")
    print(f"\n{Colors.CYAN}{Colors.BOLD}Risk Summary:{Colors.RESET}\n{parsed.summary}\n")
    print(f"{Colors.GREEN}{Colors.BOLD}Doing Well:{Colors.RESET}\n{parsed.doing_well}\n")
    print(f"{Colors.YELLOW}{Colors.BOLD}Consider Changing:{Colors.RESET}\n{parsed.consider_changing}\n")
    
    verdict_color = Colors.RED if "Aggressive" in parsed.verdict else (Colors.GREEN if "Conservative" in parsed.verdict else Colors.YELLOW)
    print(f"{Colors.MAGENTA}{Colors.BOLD}Verdict: {verdict_color}{parsed.verdict}{Colors.RESET}\n")
    print(f"{Colors.BOLD}+{'=' * 78}+{Colors.RESET}\n")


# ═══════════════════════════════════════════════════════════════════════════════
#                        SECTION 6 — [BONUS 2] CRITIQUE
# ═══════════════════════════════════════════════════════════════════════════════

def critique_first(
    portfolio: Portfolio,
    metrics: RiskMetrics,
    first_response: str,
) -> str:
    """
    BONUS 2 — Make a second LLM call acting as a "risk officer" who critiques
    the first explanation.

    The critique should:
      - Identify any missing risks or over-optimism
      - Suggest one improvement to the original advice

    Parameters
    ----------
    portfolio       : Portfolio object
    metrics         : RiskMetrics computed from portfolio
    first_response  : the full text of the first LLM explanation

    Returns
    -------
    str : critique text from the LLM
    """
    asset_lines = "\n".join(
        f"  - {a.name}: {a.allocation_pct:.0f}% (crash: {a.expected_crash_pct:.0f}%)"
        for a in portfolio.assets
    )

    prompt = f"""
You are a senior risk officer reviewing a junior analyst's portfolio risk explanation.

PORTFOLIO:
{asset_lines}

METRICS:
- Post-crash value: ₹{metrics.post_crash_value / 1e7:.2f} Cr
- Runway: {metrics.runway_months} months
- Largest risk: {metrics.largest_risk_asset}

ANALYST'S EXPLANATION:
{first_response}

YOUR TASK:
Act as a critical risk officer. In 2-3 sentences:
1. Identify ONE risk or concern the analyst missed or understated.
2. Suggest ONE concrete improvement to their advice.

Keep it constructive but direct. Use plain text — no markdown.
""".strip()

    return call_llm(prompt)


# ═══════════════════════════════════════════════════════════════════════════════
#                       SECTION 7 — MAIN ORCHESTRATION
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    """Entry point — parse args, compute metrics, call LLM, print output."""

    # ── Argument parsing ──────────────────────────────────────────────────────

    parser = argparse.ArgumentParser(
        description="AI-Powered Portfolio Explainer with structured LLM output."
    )
    parser.add_argument(
        "--tone",
        choices=["beginner", "experienced", "expert"],
        default="beginner",
        help="Tone of the explanation (default: beginner).",
    )
    parser.add_argument(
        "--critique",
        action="store_true",
        help="Run a second LLM call that critiques the first explanation (Bonus 2).",
    )
    args = parser.parse_args()

    print_banner()

    # ── Load demo portfolio ───────────────────────────────────────────────────

    portfolio_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "demo_portfolio.json")
    try:
        with open(portfolio_path, "r") as f:
            data = json.load(f)
        portfolio = Portfolio(
            total_value_inr=data["total_value_inr"],
            monthly_expenses_inr=data["monthly_expenses_inr"],
            assets=[Asset(**a) for a in data["assets"]]
        )
        print(f"{Colors.GREEN}[OK]{Colors.RESET} Loaded portfolio from: {Colors.CYAN}{os.path.basename(portfolio_path)}{Colors.RESET}\n")
    except Exception as e:
        sys.exit(f"{Colors.RED}[ERROR] Failed to load portfolio: {e}{Colors.RESET}")

    # ── Compute risk metrics ──────────────────────────────────────────────────

    print(f"{Colors.BOLD}[ ... ]{Colors.RESET} Computing portfolio risk metrics...")
    metrics = compute_risk_metrics(portfolio)

    # ── Build prompt with selected tone ───────────────────────────────────────

    print(f"{Colors.BOLD}[ ... ]{Colors.RESET} Generating explanation (tone: {Colors.CYAN}{args.tone}{Colors.RESET})...")
    prompt = build_prompt(portfolio, metrics, tone=args.tone)

    # ── Call LLM ──────────────────────────────────────────────────────────────

    try:
        raw_response = call_llm(prompt)
    except RuntimeError as exc:
        sys.exit(f"{Colors.RED}[ERROR] {exc}{Colors.RESET}")

    # ── Parse response ────────────────────────────────────────────────────────

    try:
        parsed = parse_llm_response(raw_response)
    except ValueError as exc:
        print(f"{Colors.RED}[!] WARNING: Failed to parse LLM response: {exc}{Colors.RESET}")
        print(f"\nRaw response was:\n{raw_response}\n")
        sys.exit(1)

    # ── Print report ──────────────────────────────────────────────────────────

    print_report(parsed, raw_response)

    # ── Bonus 2: Critique (if --critique flag is set) ────────────────────────

    if args.critique:
        print(f"{Colors.BOLD}[ ... ]{Colors.RESET} Generating critique (Bonus 2)...")
        try:
            critique_text = critique_first(portfolio, metrics, raw_response)
            print(f"{Colors.BOLD}+{'=' * 78}+{Colors.RESET}")
            print(f"{Colors.BOLD}|  {Colors.RED}Critique  [Risk Officer Review]{Colors.RESET}{Colors.BOLD}{'':>44}|{Colors.RESET}")
            print(f"{Colors.BOLD}+{'=' * 78}+{Colors.RESET}")
            print(f"{Colors.YELLOW}{critique_text}{Colors.RESET}")
            print(f"{Colors.BOLD}+{'=' * 78}+{Colors.RESET}\n")
        except Exception as exc:
            print(f"{Colors.RED}[!] Critique call failed: {exc}{Colors.RESET}\n")


if __name__ == "__main__":
    main()