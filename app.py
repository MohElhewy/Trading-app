import streamlit as st
import pandas as pd

# 1. Page Configuration & Modern Minimalist Styling
st.set_page_config(page_title="Trading Alpha POC", layout="wide")

st.markdown("""
    <style>
    /* Deep Navy & Electric Blue Theme */
    .stApp { background-color: #0A1128; color: #F1F5F9; }
    h1, h2, h3 { color: #5BC0BE !important; }
    div[data-testid="stMetricValue"] { color: #5BC0BE; }
    .stButton>button {
        background-color: #1C2541;
        color: white;
        border-radius: 4px;
        border: 1px solid #5BC0BE;
    }
    .stButton>button:hover { background-color: #5BC0BE; color: #0A1128; }
    </style>
""", unsafe_allow_html=True)

st.title("⚡ Trading Alpha - Execution POC")
st.markdown("---")

# 2. Layout: Sidebar for Daily Inputs
with st.sidebar:
    st.header("1. Previous Day Data")
    high = st.number_input("High", value=12.99, step=0.01)
    low = st.number_input("Low", value=11.49, step=0.01)
    close = st.number_input("Close", value=12.40, step=0.01)
    
    st.header("2. Live Market Data")
    current_price = st.number_input("Current Price", value=12.50, step=0.01)
    vwap = st.number_input("VWAP", value=12.40, step=0.01)
    rsi = st.number_input("RSI", value=60.0, step=1.0)
    current_volume = st.number_input("Current Volume", value=50000000, step=100000)
    avg_volume = st.number_input("30D Avg Volume", value=28000000, step=100000)

# 3. Core Calculations
pivot = (high + low + close) / 3
r1 = (2 * pivot) - low
s1 = (2 * pivot) - high

vol_strength = "Strong" if current_volume > (avg_volume * 1.2) else "Weak"

# 4. Strategy Engine
def evaluate_strategy(strategy_name, price, vwap, rsi, vol_status, r1, s1):
    decision = "Don't Enter"
    
    # RSI Safety Cap (Avoid Overbought)
    if rsi > 75:
        return "Don't Enter (RSI Overbought)"

    if strategy_name == "Breakout":
        if price > r1 and price > vwap and rsi >= 55 and vol_status == "Strong":
            decision = "Enter"
    elif strategy_name == "Pullback":
        if price > vwap and rsi >= 55 and vol_status == "Strong": # Simplified logic
            decision = "Enter"
    elif strategy_name == "Bounce":
        if price > s1 and rsi > 50 and vol_status == "Strong":
            decision = "Enter"
            
    return decision

# Evaluate all three
breakout_dec = evaluate_strategy("Breakout", current_price, vwap, rsi, vol_strength, r1, s1)
pullback_dec = evaluate_strategy("Pullback", current_price, vwap, rsi, vol_strength, r1, s1)
bounce_dec = evaluate_strategy("Bounce", current_price, vwap, rsi, vol_strength, r1, s1)

# 5. Dashboard Display
col1, col2, col3, col4 = st.columns(4)
col1.metric("Pivot", f"{pivot:.2f}")
col2.metric("R1 (Resistance)", f"{r1:.2f}")
col3.metric("S1 (Support)", f"{s1:.2f}")
col4.metric("Volume Status", vol_strength)

st.markdown("### Strategy Signals")

# Display Results neatly
results = []
strategies = ["Breakout", "Pullback", "Bounce"]
decisions = [breakout_dec, pullback_dec, bounce_dec]

for strat, dec in zip(strategies, decisions):
    if dec == "Enter":
        stop_loss = current_price * 0.99  # 1% strict stop loss
        target = current_price * 1.03     # 3% target for short swings
        results.append({"Strategy": strat, "Signal": "🟢 ENTER", "Entry": current_price, "Stop Loss (-1%)": round(stop_loss, 2), "Target (+3%)": round(target, 2)})
    else:
        results.append({"Strategy": strat, "Signal": f"🔴 {dec}", "Entry": "-", "Stop Loss (-1%)": "-", "Target (+3%)": "-"})

st.table(pd.DataFrame(results))