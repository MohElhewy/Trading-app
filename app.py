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
    
    /* Base Text Color for paragraphs and labels */
    p, label, li, td, th { 
        color: #FFFFFF !important; 
    }
    
    /* Force Headers to be Electric Blue (Including Streamlit inner spans) */
    h1, h2, h3, h4, h5, h6,
    h1 span, h2 span, h3 span, h4 span, h5 span, h6 span { 
        color: #5BC0BE !important; 
    }
    
    /* Metrics numbers styling */
    div[data-testid="stMetricValue"] > div { 
        color: #5BC0BE !important; 
    }
    
    /* FIX: Input Boxes (Dark Background, White Text) */
    input[type="text"], input[type="number"] { 
        background-color: #1C2541 !important; 
        color: #FFFFFF !important; 
        border: 1px solid #5BC0BE !important;
        border-radius: 4px;
    }
    
    /* FIX: Dropdown/Selectbox */
    div[data-baseweb="select"] > div {
        background-color: #1C2541 !important;
        color: #FFFFFF !important;
        border: 1px solid #5BC0BE !important;
    }
    
    /* Button Styling */
    .stButton>button {
        background-color: #1C2541 !important;
        color: #FFFFFF !important;
        border-radius: 4px;
        border: 1px solid #5BC0BE !important;
    }
    .stButton>button:hover { 
        background-color: #1C2541 !important; 
        color: #0A1128 !important; 
    }
    </style>
""", unsafe_allow_html=True)

# 2. Layout: Sidebar for Daily Inputs (NO HARDCODED VALUES)
with st.sidebar:
    st.header("0. Asset Selection")
    ticker = st.text_input("Ticker Code", placeholder="e.g., ORWE").upper()
    
    st.header("1. Previous Day Data")
    high = st.number_input("High", value=0.0, step=0.01, format="%.2f")
    low = st.number_input("Low", value=0.0, step=0.01, format="%.2f")
    close = st.number_input("Close", value=0.0, step=0.01, format="%.2f")
    
    st.header("2. Today's Opening Data")
    open_price = st.number_input("Open Price", value=0.0, step=0.01, format="%.2f")
    or_high = st.number_input("OR High (Opening Range)", value=0.0, step=0.01, format="%.2f")
    or_low = st.number_input("OR Low (Opening Range)", value=0.0, step=0.01, format="%.2f")

    st.header("3. Live Market Data")
    current_price = st.number_input("Current Price", value=0.0, step=0.01, format="%.2f")
    vwap = st.number_input("VWAP", value=0.0, step=0.01, format="%.2f")
    rsi = st.number_input("RSI", value=0.0, step=1.0)
    current_volume = st.number_input("Current Volume", value=0, step=1000)
    avg_volume = st.number_input("30D Avg Volume", value=0, step=1000)

title_text = f"⚡ Trading Alpha - Execution POC | {ticker}" if ticker else "⚡ Trading Alpha - Execution POC"
st.title(title_text)
st.markdown("---")

# 3. Core Calculations & Validation
if high > 0 and low > 0 and close > 0:
    pivot = (high + low + close) / 3
    r1 = (2 * pivot) - low
    s1 = (2 * pivot) - high
    data_ready = True
else:
    pivot, r1, s1 = 0.0, 0.0, 0.0
    data_ready = False

# Volume Strength Calculation
vol_strength = "Weak"
if avg_volume > 0:
    vol_strength = "Strong" if current_volume > (avg_volume * 1.2) else "Weak"

# 4. Strategy Engine & Condition Tracking
def evaluate_strategy_with_conditions(strategy_name, price, vwap, rsi, vol_status, r1, s1):
    decision = "Don't Enter"
    conditions = {}
    
    overbought = rsi > 75
    conditions["Not Overbought (RSI <= 75)"] = not overbought

    if strategy_name == "Breakout":
        conditions["Price > R1"] = price > r1 if r1 > 0 else False
        conditions["Price > VWAP"] = price > vwap if vwap > 0 else False
        conditions["RSI >= 55"] = rsi >= 55
        conditions["Strong Volume"] = vol_status == "Strong"
        
        if all(conditions.values()) and not overbought and price > 0:
            decision = "Enter"
            
    elif strategy_name == "Pullback":
        conditions["Price > VWAP"] = price > vwap if vwap > 0 else False
        conditions["RSI >= 55"] = rsi >= 55
        conditions["Strong Volume"] = vol_status == "Strong"
        
        if all(conditions.values()) and not overbought and price > 0:
            decision = "Enter"
            
    elif strategy_name == "Bounce":
        conditions["Price > S1"] = price > s1 if s1 > 0 else False
        conditions["RSI > 50"] = rsi > 50
        conditions["Strong Volume"] = vol_status == "Strong"
        
        if all(conditions.values()) and not overbought and price > 0:
            decision = "Enter"
            
    return decision, conditions

breakout_dec, breakout_conds = evaluate_strategy_with_conditions("Breakout", current_price, vwap, rsi, vol_strength, r1, s1)
pullback_dec, pullback_conds = evaluate_strategy_with_conditions("Pullback", current_price, vwap, rsi, vol_strength, r1, s1)
bounce_dec, bounce_conds = evaluate_strategy_with_conditions("Bounce", current_price, vwap, rsi, vol_strength, r1, s1)

# 5. Dashboard Display
if not data_ready:
    st.info("⚠️ Please enter 'Previous Day Data' in the sidebar to calculate Pivot points and enable strategies.")

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
    if dec == "Enter" and data_ready:
        stop_loss = current_price * 0.99
        target = current_price * 1.03
        results.append({"Strategy": strat, "Signal": "🟢 ENTER", "Entry": current_price, "Stop Loss (-1%)": round(stop_loss, 2), "Target (+3%)": round(target, 2)})
    else:
        signal_text = "🔴 Don't Enter" if data_ready else "⏳ Waiting for Data"
        results.append({"Strategy": strat, "Signal": signal_text, "Entry": "-", "Stop Loss (-1%)": "-", "Target (+3%)": "-"})

st.table(pd.DataFrame(results))

# --- Conditions Breakdown ---
st.markdown("### 🔍 Conditions Breakdown")
cond_col1, cond_col2, cond_col3 = st.columns(3)

def render_conditions(column, strategy_name, conditions):
    with column:
        st.markdown(f"**{strategy_name}**")
        for cond, is_met in conditions.items():
            icon = "✅" if is_met and data_ready else "❌"
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
