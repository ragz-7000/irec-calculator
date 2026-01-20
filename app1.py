import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# Page Configuration
st.set_page_config(page_title="I-REC Multi-Year Valuation", layout="wide")

# --- 1. CONFIGURATION & CURRENCY (EUR BASE) ---
EUR_TO_INR = 98.45  
USD_TO_INR = 90.95  
GST_RATE = 1.18    

# 2026 v2 Fees in EUR
ACC_OPENING_EUR = 500.00      
ANNUAL_TRADE_ACC_EUR = 2000.00 
REDEMPTION_FEE_EUR = 0.06     

# Local ICX Fees (INR)
ISSUANCE_FEE_INR = 2.60 * GST_RATE 
REGISTRATION_FEE_INR = 104110 * GST_RATE

# --- 2. SIDEBAR INPUTS ---
st.sidebar.header("📊 Project Configuration")
proj_name = st.sidebar.text_input("Project Name", "ABR Hybrid Project")
solar_mw = st.sidebar.number_input("Solar Capacity (MW)", value=100.0)
wind_mw = st.sidebar.number_input("Wind Capacity (MW)", value=50.0)

st.sidebar.header("⏳ Investment Horizon")
projection_years = st.sidebar.slider("Projection Period (Years)", 1, 5, 5)

st.sidebar.header("⚙️ CUF & Market")
solar_cuf = st.sidebar.slider("Solar CUF (%)", 15.0, 30.0, 20.0) / 100
wind_cuf = st.sidebar.slider("Wind CUF (%)", 25.0, 45.0, 35.0) / 100
irec_price_usd = st.sidebar.slider("Sale Price (USD)", 0.20, 1.20, 0.50, 0.05)
irec_price_inr = irec_price_usd * USD_TO_INR

st.sidebar.header("💼 Success Fee")
fee_pct = st.sidebar.slider("Triara CAP's Fee (%)", 15, 25, 17)

# --- 3. MULTI-YEAR CALCULATION ENGINE ---
s_gen = solar_mw * 8760 * solar_cuf 
w_gen = wind_mw * 8760 * wind_cuf  
total_irecs_annual = s_gen + w_gen

# A. Fixed & One-Time Costs (Paid in Year 1)
one_time_setup = (ACC_OPENING_EUR * EUR_TO_INR) + REGISTRATION_FEE_INR

# B. Recurring Annual Costs (Registry + Issuance + Redemption + Audit)
annual_recurring = (ANNUAL_TRADE_ACC_EUR * EUR_TO_INR) + \
                   (total_irecs_annual * ISSUANCE_FEE_INR) + \
                   (total_irecs_annual * REDEMPTION_FEE_EUR * EUR_TO_INR) + \
                   (10000 * GST_RATE)

# C. Multi-Year Totals
total_revenue = (total_irecs_annual * irec_price_inr) * projection_years
total_op_costs = one_time_setup + (annual_recurring * projection_years)

# Success Fee on Net
net_pre_fee = total_revenue - total_op_costs
total_success_fee = net_pre_fee * (fee_pct / 100)
net_client_profit = net_pre_fee - total_success_fee

# --- 4. DASHBOARD UI ---
st.title(f"🚀 {projection_years}-Year I-REC Valuation for Aditya Birla Renewables")

st.info(f"Summary for {projection_years} Years: Year 1 absorbs one-time setup of ₹{int(one_time_setup):,} | Annual recurring ₹{int(annual_recurring):,}")

# Top Metrics for the selected horizon
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Selected Period", f"{projection_years} Years")
m2.metric("Total I-RECs", f"{int(total_irecs_annual * projection_years):,}")
m3.metric("Gross Revenue", f"₹{int(total_revenue):,}")
m4.metric("Total Expenses", f"₹{int(total_op_costs + total_success_fee):,}")
m5.metric("Net Client Profit", f"₹{int(net_client_profit):,}")

st.markdown("---")

# --- 5. CASH FLOW TABLE ---
st.subheader(f"📋 Projected Cash Flow Table ({projection_years} Years)")

# Generate row-by-row data
years_data = []
for y in range(1, projection_years + 1):
    y_rev = total_irecs_annual * irec_price_inr
    y_costs = annual_recurring + (one_time_setup if y == 1 else 0)
    y_net_pre = y_rev - y_costs
    y_fee = y_net_pre * (fee_pct / 100)
    y_profit = y_net_pre - y_fee
    years_data.append([f"Year {y}", f"₹{int(y_rev):,}", f"₹{int(y_costs):,}", f"₹{int(y_profit):,}"])

df_cashflow = pd.DataFrame(years_data, columns=["Period", "Revenue", "Compliance Costs", "Net Profit"])
st.table(df_cashflow)

# --- 6. VISUALIZATION ---
st.markdown("---")
st.subheader("📈 Cumulative Profit Growth")

# Prepare cumulative data for graph
cumulative_profit = []
curr_p = 0
for y in range(1, projection_years + 1):
    y_rev = total_irecs_annual * irec_price_inr
    y_costs = annual_recurring + (one_time_setup if y == 1 else 0)
    y_profit = (y_rev - y_costs) * (1 - fee_pct/100)
    curr_p += y_profit
    cumulative_profit.append({"Year": f"Year {y}", "Cumulative Profit": curr_p})

fig_line = px.line(cumulative_profit, x="Year", y="Cumulative Profit", markers=True, 
                   title=f"Cumulative Net Profit over {projection_years} Years")
st.plotly_chart(fig_line, use_container_width=True)
