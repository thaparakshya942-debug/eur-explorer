"""
Euro Exchange Rate Explorer — Group Assignment: From Data to App
BDS M1 · Session 4 & 5

Data source: Frankfurter API (https://api.frankfurter.dev) — free, no key required.

Run it with:   streamlit run app.py
"""

from datetime import date, timedelta

import requests
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Euro Exchange Rate Explorer", layout="wide")
st.title("💶 Euro Exchange Rate Explorer")
st.caption("How has the Euro moved against other currencies over time?")

# ---------------------------------------------------------------------------
# 1. Available comparison currencies
# ---------------------------------------------------------------------------
CURRENCIES = {
    "US Dollar (USD)": "USD",
    "British Pound (GBP)": "GBP",
    "Japanese Yen (JPY)": "JPY",
    "Danish Krone (DKK)": "DKK",
    "Swiss Franc (CHF)": "CHF",
    "Swedish Krona (SEK)": "SEK",
    "Norwegian Krone (NOK)": "NOK",
    "Chinese Yuan (CNY)": "CNY",
}

# ---------------------------------------------------------------------------
# 2. Cache the API call
# ---------------------------------------------------------------------------
@st.cache_data(ttl=3600)
def fetch_rates(start: date, end: date, target: str) -> pd.DataFrame:
    """
    Fetch daily EUR -> target exchange rates from the Frankfurter API
    for the given date range. Returns a DataFrame with columns [date, rate].
    Raises RuntimeError with a human-readable message if anything goes wrong.
    """
    url = f"https://api.frankfurter.dev/v1/{start.isoformat()}..{end.isoformat()}"
    params = {"base": "EUR", "symbols": target}

    try:
        r = requests.get(url, params=params, timeout=10)
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Could not reach the exchange rate service: {e}")

    if r.status_code != 200:
        raise RuntimeError(f"The exchange rate service returned an error (status {r.status_code}).")

    payload = r.json()
    rates = payload.get("rates")
    if not rates:
        raise RuntimeError("No exchange rate data was returned for this selection.")

    df = pd.DataFrame(
        [{"date": d, "rate": values[target]} for d, values in rates.items() if target in values]
    )
    if df.empty:
        raise RuntimeError(f"No data available for EUR/{target} in this date range.")

    df["date"] = pd.to_datetime(df["date"])
    return df.sort_values("date")


# ---------------------------------------------------------------------------
# 3. Sidebar controls — the interactive part
# ---------------------------------------------------------------------------
today = date.today()
default_start = today - timedelta(days=365)

with st.sidebar:
    st.header("Controls")
    currency_name = st.selectbox(
        "Compare EUR against",
        options=list(CURRENCIES.keys()),
        index=0,  # defaults to USD
    )
    start_date, end_date = st.slider(
        "Date range",
        min_value=today - timedelta(days=365 * 5),
        max_value=today,
        value=(default_start, today),
    )

target = CURRENCIES[currency_name]

if start_date >= end_date:
    st.error("The start date must be before the end date. Please adjust the range in the sidebar.")
    st.stop()

# ---------------------------------------------------------------------------
# 4. Fetch data — with a clear message if the API fails
# ---------------------------------------------------------------------------
with st.spinner("Fetching live exchange rate data..."):
    try:
        df = fetch_rates(start_date, end_date, target)
    except RuntimeError as e:
        st.error(f"⚠️ We couldn't load exchange rate data right now. {e} Please try again shortly.")
        st.stop()
    except Exception:
        st.error("⚠️ The exchange rate service is temporarily unavailable. Please try again shortly.")
        st.stop()

# ---------------------------------------------------------------------------
# 5. Visualization — one clear comparison chart
# ---------------------------------------------------------------------------
pct_change = (df["rate"].iloc[-1] / df["rate"].iloc[0] - 1) * 100
direction = "strengthened" if pct_change > 0 else "weakened"

fig = px.line(
    df,
    x="date",
    y="rate",
    labels={"date": "", "rate": f"EUR/{target}"},
    title=f"EUR vs {target}: {start_date} to {end_date}",
)
fig.update_layout(height=440, margin=dict(t=50, b=0))
st.plotly_chart(fig, use_container_width=True)

c1, c2, c3 = st.columns(3)
c1.metric(f"Start rate ({start_date})", f"{df['rate'].iloc[0]:.4f}")
c2.metric(f"End rate ({end_date})", f"{df['rate'].iloc[-1]:.4f}")
c3.metric("Change", f"{pct_change:+.2f}%")

st.markdown(
    f"### 📊 The Euro has **{direction}** against the {currency_name.split(' (')[0]} "
    f"by **{abs(pct_change):.2f}%** over this period."
)

# ---------------------------------------------------------------------------
# 6. Explanation + data limitation (required by the assignment)
# ---------------------------------------------------------------------------
st.markdown("### What this shows")
st.write(
    f"This chart tracks the exchange rate of 1 Euro to **{currency_name}** "
    f"from **{start_date}** to **{end_date}**, using daily reference rates "
    "published by the European Central Bank via the Frankfurter API. Use the "
    "sidebar to compare a different currency or change the date range."
)

st.markdown("### ⚠️ Data limitation")
st.write(
    "These are official daily reference rates set once per business day by the "
    "European Central Bank, not live, second-by-second trading rates. Rates "
    "are also not published on weekends or ECB holidays, so the chart may show "
    "small gaps on those dates. Actual rates you'd get from a bank or currency "
    "exchange service will typically include an additional margin or fee."
)

# ---------------------------------------------------------------------------
# 7. Let the user take the data home
# ---------------------------------------------------------------------------
st.download_button(
    "📥 Download this data (CSV)",
    data=df.to_csv(index=False).encode("utf-8"),
    file_name=f"eur_{target.lower()}_rates.csv",
    mime="text/csv",
)
