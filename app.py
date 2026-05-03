import streamlit as st
import pandas as pd
import os
from datetime import datetime

# 1. Page Configuration & Modern Minimalist Styling
st.set_page_config(page_title="Trading Alpha POC", layout="wide")

st.markdown("""
    <style>
    /* Deep Navy Background */
    .stApp, [data-testid="stAppViewContainer"] { background-color: #0A1128 !important; }
    [data-testid="stSidebar"] { background-color: #070D1F !important; } 
    
    /* Force ALL regular text, labels, and table cells to be White */
    html, body, p, span, div, label, li, td, th { 
        color: #FFFFFF !important; 
    }
    
    /* Keep Headers Electric Blue */
    h1, h2, h3, h4, h5, h6 { 
        color: #5BC0BE !important; 
    }
    
    /* Metrics numbers styling */
    div[data-testid="stMetricValue"] > div { 
        color: #5BC0BE !important; 
    }
    
    /* Input box text color fix */
    input, .stSelectbox div[data-baseweb="select"] { 
        color: #FFFFFF !important; 
    }
    
    /* Button Styling */
    .stButton>button {
        background-color: #1C2541 !important;
        color: #FFFFFF !important;
        border-radius: 4px;
        border: 1px solid #5BC0BE !important;
    }
    .stButton>button:hover { 
        background-color: #5BC0BE !important; 
        color: #0A1128 !important; 
    }
    </style>
""", unsafe_allow_html=True)

# 2. Layout: Sidebar for Daily Inputs
with st.sidebar:
    st.header("0. Asset Selection")
    ticker = st.text_input("Ticker Code", value="ORWE").upper()
    
    st.header("1. Previous Day Data")
    high = st.number_input("High", value=12.99, step=0.01)
    low = st.number_input("Low", value=11.49, step=0.01)
    close = st.number_input("Close", value=12.40, step=0.01)
    
    st.header("2. Today's Opening Data")
    open_price = st.number_input("Open Price", value=11.36, step=0.01)
    or_high = st.number_input("OR High (Opening Range)", value=12.40, step=0.01)
    or_low = st.number_input("OR Low (Opening Range)", value=12.00, step=0.01)

    st.header("3. Live Market Data")
    current_price = st.number_input("Current Price", value=12.30, step=0.01)
    vwap = st.number_input("VWAP", value=12.40, step=0.01)
    rsi = st.number_input("RSI", value=60.0, step=1.0)
    current_volume = st.number_input("Current Volume", value=56700000, step=100000)
    avg_volume = st.number_input("30D Avg Volume", value=28100000, step=100000)

st.title(f"⚡ Trading Alpha - Execution POC | {ticker}")
st.markdown("---")

# 3. Core Calculations
pivot = (high + low + close) / 3
r1 = (2 * pivot) - low
s1 = (2 * pivot) - high

vol_strength = "Strong" if current_volume > (avg_volume * 1.2) else "Weak"

# 4. Strategy Engine & Condition Tracking
def evaluate_strategy_with_conditions(strategy_name, price, vwap, rsi, vol_status, r1, s1):
    decision = "Don't Enter"
    conditions = {}
    
    # RSI Safety Cap 
    overbought = rsi > 75
    conditions["Not Overbought (RSI <= 75)"] = not overbought

    if strategy_name == "Breakout":
        conditions["Price > R1"] = price > r1
        conditions["Price > VWAP"] = price > vwap
        conditions["RSI >= 55"] = rsi >= 55
        conditions["Strong Volume"] = vol_status == "Strong"
        
        if all(conditions.values()) and not overbought:
            decision = "Enter"
            
    elif strategy_name == "Pullback":
        # Simplified Pullback Logic based on the sheet
        conditions["Price > VWAP"] = price > vwap
        conditions["RSI >= 55"] = rsi >= 55
        conditions["Strong Volume"] = vol_status == "Strong"
        
        if all(conditions.values()) and not overbought:
            decision = "Enter"
            
    elif strategy_name == "Bounce":
        conditions["Price > S1"] = price > s1
        conditions["RSI > 50"] = rsi > 50
        conditions["Strong Volume"] = vol_status == "Strong"
        
        if all(conditions.values()) and not overbought:
            decision = "Enter"
            
    return decision, conditions

# Evaluate all three and get conditions
breakout_dec, breakout_conds = evaluate_strategy_with_conditions("Breakout", current_price, vwap, rsi, vol_strength, r1, s1)
pullback_dec, pullback_conds = evaluate_strategy_with_conditions("Pullback", current_price, vwap, rsi, vol_strength, r1, s1)
bounce_dec, bounce_conds = evaluate_strategy_with_conditions("Bounce", current_price, vwap, rsi, vol_strength, r1, s1)

# 5. Dashboard Display
col1, col2, col3, col4 = st.columns(4)
col1.metric("Pivot", f"{pivot:.2f}")
col2.metric("R1 (Resistance)", f"{r1:.2f}")
col3.metric("S1 (Support)", f"{s1:.2f}")
col4.metric("Volume Status", vol_strength)

st.markdown("### 🎯 Strategy Signals")

# Display Results Table
results = []
strategies = ["Breakout", "Pullback", "Bounce"]
decisions = [breakout_dec, pullback_dec, bounce_dec]

for strat, dec in zip(strategies, decisions):
    if dec == "Enter":
        stop_loss = current_price * 0.99
        target = current_price * 1.03
        results.append({"Strategy": strat, "Signal": "🟢 ENTER", "Entry": current_price, "Stop Loss (-1%)": round(stop_loss, 2), "Target (+3%)": round(target, 2)})
    else:
        results.append({"Strategy": strat, "Signal": f"🔴 {dec}", "Entry": "-", "Stop Loss (-1%)": "-", "Target (+3%)": "-"})

st.table(pd.DataFrame(results))

# --- NEW SECTION: Display Conditions ---
st.markdown("### 🔍 Conditions Breakdown")
cond_col1, cond_col2, cond_col3 = st.columns(3)

def render_conditions(column, strategy_name, conditions):
    with column:
        st.markdown(f"**{strategy_name}**")
        for cond, is_met in conditions.items():
            icon = "✅" if is_met else "❌"
            st.write(f"{icon} {cond}")

render_conditions(cond_col1, "Breakout", breakout_conds)
render_conditions(cond_col2, "Pullback", pullback_conds)
render_conditions(cond_col3, "Bounce", bounce_conds)
# ---------------------------------------

# 6. Trade Log (Track & Trace)
st.markdown("---")
st.header("📋 Operations Log")

LOG_FILE = "trade_log.csv"

with st.form("log_form"):
    col_log1, col_log2, col_log3 = st.columns(3)
    log_ticker = col_log1.text_input("Ticker", value=ticker)
    log_strategy = col_log2.selectbox("Strategy", strategies)
    log_status = col_log3.selectbox("Result", ["Win", "Loss", "Breakeven"])
    
    log_profit = st.number_input("Net P/L % (After Comm.)", value=0.0, step=0.1)
    submitted = st.form_submit_button("Log Operation")
    
    if submitted and log_ticker:
        new_data = pd.DataFrame({
            "Date": [datetime.now().strftime("%Y-%m-%d %H:%M")],
            "Ticker": [log_ticker.upper()],
            "Strategy": [log_strategy],
            "Result": [log_status],
            "P/L %": [log_profit]
        })
        
        if os.path.exists(LOG_FILE):
            log_df = pd.read_csv(LOG_FILE)
            log_df = pd.concat([log_df, new_data], ignore_index=True)
        else:
            log_df = new_data
            
        log_df.to_csv(LOG_FILE, index=False)
        st.success("Operation logged successfully!")

# Display Historical Log
if os.path.exists(LOG_FILE):
    st.markdown("#### Historical Data")
    st.dataframe(pd.read_csv(LOG_FILE), use_container_width=True)
