import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# Page Configuration
st.set_page_config(page_title="Triara CAP | ABR I-REC Valuation", layout="wide")

# --- 1. CONFIGURATION & 2026 v2 CONSTANTS ---
USD_TO_INR = 90.95 
GST_RATE = 0.18

# I-TRACK Foundation (Global Registry - USD)
ACC_OPENING_USD = 588.50      
ANNUAL_TRADE_ACC_USD = 2354.00 
REDEMPTION_LEVY_USD = 0.08     

# ICX (Local Issuer - India - INR)
ICX_REG_BASE = 104110.00      
ICX_ISSUANCE_BASE = 2.60       
ICX_AUDIT_BASE = 10000.00

# --- 2. HEADER & BRANDING ---
col_logo, col_title = st.columns([1, 5])
with col_logo:
    # Replace the URL with your actual local logo path if available: e.g., st.image("logo.png")
    st.image("https://via.placeholder.com/200x60.png?text=TRIARA+CAP", use_container_width=True)

with col_title:
    st.title("🚀 I-REC 5-Year Strategic Valuation: Aditya Birla Renewables")

# --- 3. INPUTS ---
st.sidebar.header("📊 Project Configuration")
proj_name = st.sidebar.text_input("Project Name", "ABR Hybrid 150MW")
solar_mw = st.sidebar.number_input("Solar Capacity (MW)", value=100.0)
wind_mw = st.sidebar.number_input("Wind Capacity (MW)", value=50.0)

st.sidebar.header("💹 Market Dynamics")
# Added Slider for Price Scenarios as requested
irec_price_usd = st.sidebar.slider("I-REC Sale Price (USD)", 0.20, 1.20, 0.50, 0.05)
irec_price_inr = irec_price_usd * USD_TO_INR

st.sidebar.header("💼 Success Fee")
fee_pct = st.sidebar.slider("Triara CAP's Fee (%)", 15, 25, 17)

# --- 4. 5-YEAR CALCULATION ENGINE ---
total_irecs_annual = (solar_mw * 8760 * 0.20) + (wind_mw * 8760 * 0.35)
years = [1, 2, 3, 4, 5]
summary_data = []

cum_rev, cum_cost, cum_profit = 0, 0, 0

for year in years:
    # A. Global Fees (Registry)
    setup_cost = (ACC_OPENING_USD * USD_TO_INR) if year == 1 else 0
    maint_cost = ANNUAL_TRADE_ACC_USD * USD_TO_INR
    redemption_cost = total_irecs_annual * REDEMPTION_LEVY_USD * USD_TO_INR
    
    # B. Local Fees (Issuer + 18% GST)
    reg_cost = (ICX_REG_BASE * (1 + GST_RATE)) if year == 1 else 0
    issuance_cost = (total_irecs_annual * ICX_ISSUANCE_BASE) * (1 + GST_RATE)
    audit_cost = (ICX_AUDIT_BASE * (1 + GST_RATE))
    
    # C. Financials
    y_rev = total_irecs_annual * irec_price_inr
    y_op_exp = setup_cost + maint_cost + redemption_cost + reg_cost + issuance_cost + audit_cost
    
    net_pre_fee = y_rev - y_op_exp
    y_success_fee = net_pre_fee * (fee_pct / 100)
    y_profit = net_pre_fee - y_success_fee
    y_total_exp = y_op_exp + y_success_fee

    # Cumulatives
    cum_rev += y_rev
    cum_cost += y_total_exp
    cum_profit += y_profit
    
    summary_data.append({
        "Year": f"Year {year}",
        "Revenue": y_rev,
        "Total Expenses": y_total_exp,
        "Net Profit": y_profit
    })

# Add 5-Year Totals
summary_data.append({
    "Year": "5-Year Cumulative",
    "Revenue": cum_rev,
    "Total Expenses": cum_cost,
    "Net Profit": cum_profit
})

df_summary = pd.DataFrame(summary_data)

# --- 5. DASHBOARD UI ---
st.info(f"**Market Assumption:** Price ${irec_price_usd:.2f} | Exch Rate ₹{USD_TO_INR} | **GST 18% applied to local fees**")

# Top Metrics (Current Year 1 Focus)
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total I-RECs / Year", f"{int(total_irecs_annual):,}")
m2.metric("Gross Revenue (Year 1)", f"₹{int(summary_data[0]['Revenue']):,}")
m3.metric("Total Expenses (Year 1)", f"₹{int(summary_data[0]['Total Expenses']):,}")
m4.metric("Net Profit (Year 1)", f"₹{int(summary_data[0]['Net Profit']):,}")

st.markdown("---")
st.subheader("📋 5-Year Financial Performance Matrix")
st.table(df_summary.set_index("Year").style.format("₹{:,.0f}"))

# --- 6. VISUALIZATIONS ---
st.markdown("---")
c_left, c_right = st.columns(2)

with c_left:
    st.subheader("Profit vs. Expense (Year 1)")
    fig_pie = px.pie(
        values=[float(summary_data[0]['Total Expenses']), float(summary_data[0]['Net Profit'])], 
        names=['Total Expenses & Fees', 'Net Client Profit'],
        hole=0.4, color_discrete_sequence=['#E74C3C', '#2ECC71']
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with c_right:
    st.subheader("5-Year Cumulative Growth")
    df_plot = df_summary[df_summary["Year"] != "5-Year Cumulative"]
    fig_bar = px.bar(
        df_plot, x="Year", y=["Revenue", "Net Profit"],
        barmode="group", color_discrete_sequence=['#3498DB', '#2ECC71']
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# --- 7. PDF EXPORT ---
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(w=0, h=15, txt="
