import streamlit as st
import pandas as pd
import numpy as np
import requests
import plotly.graph_objects as go
import ta   # technical indicators

st.set_page_config(page_title="V75 Signal Tool", layout="wide")
st.title("📊 V75 Scalping Signal Tool")

# Replace with your Deriv API endpoint and token
API_ENDPOINT = "https://api.deriv.com/api/exchange/v1/marketdata/volatility_75/ohlc"
API_TOKEN = "YOUR_API_TOKEN"

def get_candles():
    # Example placeholder for live data
    # Replace with websocket or official REST call when you have credentials
    url = f"{API_ENDPOINT}?granularity=60&count=100"
    try:
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            raw = r.json()
            df = pd.DataFrame(raw.get("candles", []))
            df = df.rename(columns={"o":"open","h":"high","l":"low","c":"close","t":"time"})
            df["time"] = pd.to_datetime(df["time"], unit="s")
            df.set_index("time", inplace=True)
            return df
        else:
            return pd.DataFrame()
    except:
        return pd.DataFrame()

def compute_signals(df):
    df["EMA20"] = ta.trend.ema_indicator(df["close"], window=20)
    df["EMA50"] = ta.trend.ema_indicator(df["close"], window=50)
    df["RSI"] = ta.momentum.rsi(df["close"], window=14)
    df["ATR"] = ta.volatility.average_true_range(df["high"], df["low"], df["close"], window=14)
    last = df.iloc[-1]
    if last.EMA20 > last.EMA50 and last.RSI > 50:
        return "✅ BUY", df
    elif last.EMA20 < last.EMA50 and last.RSI < 50:
        return "🔻 SELL", df
    else:
        return "⚪ No Signal", df

data = get_candles()
if not data.empty:
    signal, data = compute_signals(data)
    st.subheader(f"Current Signal: {signal}")

    fig = go.Figure(data=[go.Candlestick(
        x=data.index,
        open=data["open"],
        high=data["high"],
        low=data["low"],
        close=data["close"]
    )])
    fig.add_trace(go.Scatter(x=data.index, y=data["EMA20"], line=dict(color="blue"), name="EMA20"))
    fig.add_trace(go.Scatter(x=data.index, y=data["EMA50"], line=dict(color="red"), name="EMA50"))
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("Waiting for live candle data or invalid API settings...")
