import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# Page Configuration
st.set_page_config(page_title="I-REC Hybrid Asset Model", layout="wide")

# --- 1. CONFIGURATION & CURRENCY ---
# Using Jan 2026 Live Exchange Rate: 1 USD = 90.95 INR
USD_TO_INR = 90.95 

# --- 2. SIDEBAR INPUTS ---
st.sidebar.header("📊 Project Configuration")
proj_name = st.sidebar.text_input("Project Name", "Hybrid Wind-Solar Project")
solar_mw = st.sidebar.number_input("Solar Capacity (MW)", value=10.0)
wind_mw = st.sidebar.number_input("Wind Capacity (MW)", value=15.0)

st.sidebar.header("💹 Market Dynamics")
# Variable I-REC Price (USD) to show variations
irec_price_usd = st.sidebar.slider("I-REC Sale Price (USD)", 0.20, 1.50, 0.50, 0.05)
irec_price_inr = irec_price_usd * USD_TO_INR

st.sidebar.header("💼 Service Parameters")
fee_pct = st.sidebar.slider("Consultancy Success Fee (%)", 0, 20, 10)

# --- 3. THE COMPLETE COST & REVENUE ENGINE ---
# Generation (MWh)
s_gen = solar_mw * 8760 * 0.20 # Solar 20% CUF
w_gen = wind_mw * 8760 * 0.35  # Wind 35% CUF
total_irecs = s_gen + w_gen

# A. Fixed & Variable Regulatory Costs (INR)
reg_fee_total = 89000 if (solar_mw + wind_mw) > 3 else 44500
annual_reg_cost = reg_fee_total / 5
annual_maint_fee = 180000        
icx_issuance_fee = total_irecs * 2.25 # ICX Standard Rate
redemption_fee = total_irecs * 7.00   # 2026 Retirement Fee
verification_audit = 50000      

# B. Totals
gross_revenue = total_irecs * irec_price_inr
total_reg_op_costs = annual_reg_cost + annual_maint_fee + icx_issuance_fee + redemption_fee + verification_audit

# C. Professional Fees & Final Profit
net_pre_fee = gross_revenue - total_reg_op_costs
my_fee = net_pre_fee * (fee_pct / 100)
total_annual_expenses = total_reg_op_costs + my_fee
client_net_profit = gross_revenue - total_annual_expenses

# --- 4. DASHBOARD UI ---
st.title(f"🚀 I-REC Valuation Dashboard: {proj_name}")
st.write(f"Current Market View: **${irec_price_usd:.2f} per I-REC** (≈ ₹{irec_price_inr:.2f})")

# Top Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Project Capacity", f"{solar_mw + wind_mw} MW")
m2.metric("Annual I-RECs", f"{int(total_irecs):,}")
m3.metric("Total Annual Expenses", f"₹{int(total_annual_expenses):,}")
m4.metric("Net Client Profit", f"₹{int(client_net_profit):,}")

# --- 5. COMPREHENSIVE COST TABLE ---
st.subheader("📋 Detailed Expenditure & Fee Schedule")

cost_items = ["Registry Registration", "Registry Maintenance", "ICX Issuance Fee", "Redemption Fee", "Audit Fee", "Professional Fee"]
costs_inr = [annual_reg_cost, annual_maint_fee, icx_issuance_fee, redemption_fee, verification_audit, my_fee]
per_irec = [c / total_irecs for c in costs_inr]

df_data = pd.DataFrame({
    "Cost Component": cost_items,
    "Annual Expense (INR)": [f"₹{int(c):,}" for c in costs_inr],
    "Cost per I-REC (INR)": [f"₹{c:.2f}" for c in per_irec]
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
    st.subheader("Profit vs. Expense Ratio")
    fig_pie = px.pie(
        values=[total_annual_expenses, client_net_profit], 
        names=['
