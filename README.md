# Euro Exchange Rate Explorer

An interactive Streamlit app that tracks how the Euro has moved against other
major currencies over time, using live daily reference rates from the
European Central Bank.

## Target audience
Business owners and investors who trade internationally or hold assets in
USD/EUR, and want to understand how currency movements affect their costs,
pricing, or investment returns.

## The question
Has the Euro strengthened or weakened against the US Dollar over the last
12 months — and by how much?

## Data source
[Frankfurter API](https://api.frankfurter.dev) — free, no API key required.
Provides official daily EUR reference rates published by the European
Central Bank.

## Live app
[Paste your deployed Streamlit Cloud URL here]

## Running locally
```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

## Limitations
These are official daily reference rates, not live trading rates, and are
not published on weekends or ECB holidays. Actual bank/exchange rates will
typically include an additional margin or fee.

## AI tools used
[Fill in honestly, e.g.:
"We used Claude (Anthropic) to help us understand the Frankfurter API,
build and debug the Streamlit app's error handling, and draft this README.
All code was reviewed and tested by the group before submission."]

## Group members
[Fill in names]
