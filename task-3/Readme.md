# Task 3: AI-Powered Portfolio Explainer

## Overview
The **AI-Powered Portfolio Explainer** bridges the gap between raw mathematical risk (from Task 1) and human comprehension. It feeds the calculated risk metrics into an LLM and forces the AI to output a highly structured, 4-part summary of the portfolio's health, tailored to specific user knowledge levels.

## Workflow
1. **Data Loading & Computation**: Loads the shared `demo_portfolio.json` file from the project root and calculates the exact deterministic risk metrics (runway, ruin test, concentration) using the same logic as Task 1.
2. **Tone-Adjusted Prompting**: Builds a dynamic prompt containing the raw numbers and specific tone instructions (`beginner`, `experienced`, or `expert`), strictly forbidding the use of markdown.
3. **LLM Execution**: Sends the prompt to Google Gemini (or falls back to OpenAI) and retrieves the raw text.
4. **Parsing Engine**: Uses custom string parsing to break the raw LLM text into four distinct variables: `Summary`, `Doing Well`, `Consider Changing`, and `Verdict`.
5. **Critique Mode (Bonus)**: If enabled, passes the first explanation back to the LLM, asking it to act as a "Senior Risk Officer" to find flaws or missed risks in the original assessment.

## How to Run
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

## Expected Output
The terminal will display a colorful, formatted ASCII interface:
1. **Loading Status**: `[OK] Loaded portfolio from: demo_portfolio.json`
2. **Raw API Response**: A block showing exactly what the LLM returned before processing.
3. **Extracted Structured Output**: The parsed sections heavily color-coded for readability:
   - **Risk Summary** (Cyan)
   - **Doing Well** (Green)
   - **Consider Changing** (Yellow)
   - **Verdict** (Red/Green/Yellow depending on Aggressive/Conservative/Balanced)
4. **Critique Review** *(If --critique is used)*: A secondary red-bordered box detailing the Risk Officer's evaluation of the primary advice.
