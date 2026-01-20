import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# Page Configuration
st.set_page_config(page_title="I-REC Hybrid Asset Model | EUR Edition", layout="wide")

# --- 1. CONFIGURATION & CURRENCY (UPDATED JAN 2026 v2 - EUR) ---
EUR_TO_INR = 98.45  # Updated EUR/INR Exchange Rate
USD_TO_INR = 90.95  
GST_RATE = 1.18    # 18% GST Multiplier

# Revised Global Fees in EUR (v2 Standards)
ACC_OPENING_EUR = 500.00      
ANNUAL_TRADE_ACC_EUR = 2000.00 
REDEMPTION_FEE_EUR = 0.06     # Global Platform Operator Rate

# Revised Local Fees (ICX India - INR)
ISSUANCE_FEE_INR = 2.60 * GST_RATE 
REGISTRATION_FEE_INR = 104110 * GST_RATE

# --- 2. SIDEBAR INPUTS ---
st.sidebar.header("📊 Project Configuration")
proj_name = st.sidebar.text_input("Project Name", "Wind-Solar Hybrid Project")
solar_mw = st.sidebar.number_input("Solar Capacity (MW)", value=100.0)
wind_mw = st.sidebar.number_input("Wind Capacity (MW)", value=50.0)

st.sidebar.header("⚙️ Capacity Utilization Factor (CUF)")
solar_cuf = st.sidebar.slider("Solar CUF (%)", 15.0, 30.0, 20.0, 0.5) / 100
wind_cuf = st.sidebar.slider("Wind CUF (%)", 25.0, 45.0, 35.0, 0.5) / 100

st.sidebar.header("💹 Market Dynamics")
# Market price is still typically quoted in USD for global trading
irec_price_usd = st.sidebar.slider("I-REC Sale Price (USD)", 0.20, 1.20, 0.50, 0.05)
irec_price_inr = irec_price_usd * USD_TO_INR

st.sidebar.header("💼 Service Parameters")
fee_pct = st.sidebar.slider("Triara CAP's Success Fee (%)", 15, 25, 17)

# --- 3. THE COMPLETE COST & REVENUE ENGINE ---
s_gen = solar_mw * 8760 * solar_cuf 
w_gen = wind_mw * 8760 * wind_cuf  
total_irecs = s_gen + w_gen

# A. Regulatory Costs (INR) - Calculated via EUR Base
acc_opening_annual = (ACC_OPENING_EUR * EUR_TO_INR) / 5 
annual_reg_cost = REGISTRATION_FEE_INR / 5
annual_maint_fee = ANNUAL_TRADE_ACC_EUR * EUR_TO_INR        
icx_issuance_fee = total_irecs * ISSUANCE_FEE_INR
redemption_fee_total = total_irecs * (REDEMPTION_FEE_EUR * EUR_TO_INR)
verification_audit = 10000 * GST_RATE     

# B. Totals
gross_revenue = total_irecs * irec_price_inr
total_op_costs = acc_opening_annual + annual_reg_cost + annual_maint_fee + icx_issuance_fee + redemption_fee_total + verification_audit

# C. Triara CAP Success Fee Calculation
net_pre_fee = gross_revenue - total_op_costs
my_fee = net_pre_fee * (fee_pct / 100)
total_annual_expenses = total_op_costs + my_fee
client_net_profit = gross_revenue - total_annual_expenses

# --- 4. DASHBOARD UI ---
st.title(f"🚀 I-REC Valuation Dashboard for Aditya Birla Renewables")

st.info(f"Assumptions: Sale Price USD {irec_price_usd:0.2f} | EUR/INR: {EUR_TO_INR} | USD/INR: {USD_TO_INR} | Incl. 18% GST on Local Fees")

# Top Metrics
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Project Capacity", f"{solar_mw + wind_mw} MW")
m2.metric("Total I-RECs", f"{int(total_irecs):,}")
m3.metric("Total Revenue", f"₹{int(gross_revenue):,}")
m4.metric("Total Expenses", f"₹{int(total_annual_expenses):,}")
m5.metric("Net Client Profit", f"₹{int(client_net_profit):,}")

st.markdown("---")

# --- 5. COMPREHENSIVE COST TABLE ---
st.subheader("📋 Detailed Expenditure & Fee Schedule")

cost_items = [
    f"Registry Account Opening (Amortized €{ACC_OPENING_EUR/5})",
    "Registry Registration (Amortized + GST)", 
    f"Registry Maintenance (Annual €{ANNUAL_TRADE_ACC_EUR})", 
    "Issuance Fee (ICX + GST)", 
    f"Redemption Fee (Registry €{REDEMPTION_FEE_EUR}/unit)", 
    "Independent Verification Audit (+ GST)", 
    "Triara CAP's Success Fee"
]
costs_inr = [acc_opening_annual, annual_reg_cost, annual_maint_fee, icx_issuance_fee, redemption_fee_total, verification_audit, my_fee]

df_data = pd.DataFrame({
    "Cost Component": cost_items,
    "Annual Expense (INR)": [f"₹{int(c):,}" for c in costs_inr],
    "Cost per I-REC (INR)": [f"₹{c/total_irecs:.2f}" for c in costs_inr]
})

total_row = pd.DataFrame({
    "Cost Component": ["**TOTAL ANNUAL EXPENSES**"],
    "Annual Expense (INR)": [f"**₹{int(total_annual_expenses):,}**"],
    "Cost per I-REC (INR)": [f"**₹{total_annual_expenses/total_irecs:.2f}**"]
})
st.table(pd.concat([df_data, total_row], ignore_index=True))

# --- 6. VISUALIZATIONS ---
st.markdown("---")
c_left, c_right = st.columns(2)

with c_left:
    st.subheader("Financial Distribution")
    fig_pie = px.pie(
        values=[float(total_annual_expenses), float(client_net_profit)], 
        names=['Total Costs & Fees', 'Net Client Profit'],
        hole=0.4,
        color_discrete_sequence=['#E74C3C', '#2ECC71']
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with c_right:
    st.subheader("Revenue Benchmarking (INR)")
    fig_bar = px.bar(
        x=["Gross Revenue", "Total Expenses", "Net Profit"],
        y=[gross_revenue, total_annual_expenses, client_net_profit],
        color=["Revenue", "Expense", "Profit"],
        text_auto='.2s'
    )
    st.plotly_chart(fig_bar, use_container_width=True)
