import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# Page Configuration
st.set_page_config(page_title="I-REC Hybrid Asset Model", layout="wide")

# --- CUSTOM CSS FOR TEXT SIZES ---
st.markdown("""
    <style>
    /* Shrink the main title */
    h1 {
        font-size: 1.8rem !important;
        font-weight: 700;
        padding-bottom: 0rem;
    }
    /* Shrink the metric labels and values */
    [data-testid="stMetricValue"] {
        font-size: 1rem !important;
    }
    [data-testid="stMetricLabel"] {
        font-size: 1.2rem !important;
    }
    /* Reduce padding between elements for a tighter look */
    .block-container {
        padding-top: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 1. CONFIGURATION & CURRENCY (REVISED 2026 EUR v2) ---
EUR_TO_INR = 106.17  
USD_TO_INR = 90.95  
GST_RATE = 1.18    

# Fees from v2 Document
ACC_OPENING_EUR = 500.00      
ANNUAL_TRADE_ACC_EUR = 2000.00     
ISSUANCE_FEE_INR = 2.60 * GST_RATE 
REGISTRATION_FEE_INR = 104110 * GST_RATE

# --- 2. SIDEBAR INPUTS ---
# This creates 3 columns: [Small Space, Your Logo, Large Space]
# The middle number (2) controls the logo size. Decrease it to make it even smaller.
left_co, cent_co, last_co = st.sidebar.columns([1, 1.25, 1])

with cent_co:
    st.sidebar.image("Triara_Logo.png") 

st.sidebar.header("📊 Project Configuration")
proj_name = st.sidebar.text_input("Project Name", "Wind-Solar Hybrid Project")
solar_mw = st.sidebar.number_input("Solar Capacity (MW)", value=100.0)
wind_mw = st.sidebar.number_input("Wind Capacity (MW)", value=50.0)

# ADDED SIDEBARS FOR CUF
st.sidebar.header("⚙️ Capacity Utilization Factor")
solar_cuf = st.sidebar.slider("Solar CUF (%)", 15.0, 30.0, 20.0, 0.5) / 100
wind_cuf = st.sidebar.slider("Wind CUF (%)", 25.0, 45.0, 35.0, 0.5) / 100

# ADDED SIDEBAR FOR PROJECTION YEARS
st.sidebar.header("⏳ Projection Horizon")
projection_years = st.sidebar.slider("Number of Years", 1, 5, 1)

st.sidebar.header("💹 Market Dynamics")
irec_price_usd = st.sidebar.slider("I-REC Sale Price (USD)", 0.20, 1.20, 0.50, 0.05)
irec_price_inr = irec_price_usd * USD_TO_INR

st.sidebar.header("💼 Service Parameters")
fee_pct = st.sidebar.slider("Triara CAP's Success Fee (%)", 15, 25, 17)

# --- 3. THE COMPLETE COST & REVENUE ENGINE ---
# Updated to use dynamic CUF and years
s_gen = solar_mw * 8760 * solar_cuf 
w_gen = wind_mw * 8760 * wind_cuf  
total_irecs_annual = s_gen + w_gen
total_irecs_period = total_irecs_annual * projection_years

# A. Regulatory Costs (INR)
# Account Opening and Registration are one-time (Year 1)
one_time_costs = (ACC_OPENING_EUR * EUR_TO_INR) + REGISTRATION_FEE_INR
# Maintenance, Issuance, and Audit are recurring
annual_recurring = (ANNUAL_TRADE_ACC_EUR * EUR_TO_INR) + \
                   (total_irecs_annual * ISSUANCE_FEE_INR) + \
                   (10000 * GST_RATE)

total_op_costs = one_time_costs + (annual_recurring * projection_years)

# B. Totals
gross_revenue = total_irecs_period * irec_price_inr

# C. Triara CAP Success Fee Calculation
net_pre_fee = gross_revenue - total_op_costs
my_fee = net_pre_fee * (fee_pct / 100) * GST_RATE
total_period_expenses = total_op_costs + my_fee
client_net_profit = gross_revenue - total_period_expenses

# --- 4. DASHBOARD UI ---
st.title(f"🚀 I-REC Valuation Dashboard for Aditya Birla Renewables")

# CLEANED ASSUMPTION HEADER
st.info(f"Assumptions: Sale Price USD {irec_price_usd:0.2f} | Period: {projection_years} Year(s) | Solar CUF: {solar_cuf*100}% | Wind CUF: {wind_cuf*100}% | EUR/INR: {EUR_TO_INR} | USD/INR: {USD_TO_INR}")

# Top Metrics
m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Project Capacity", f"{solar_mw + wind_mw} MW")
m2.metric("Total I-RECs", f"{int(total_irecs_period):,}")
m3.metric("Total Revenue", f"₹{int(gross_revenue):,}")
m4.metric("Total Expenses", f"₹{int(total_period_expenses):,}")
m5.metric("Net Client Profit", f"₹{int(client_net_profit):,}")

st.markdown("---")

# --- 5. COMPREHENSIVE COST TABLE ---
st.subheader(f"📋 Detailed Expenditure & Fee Schedule ({projection_years} Year Period)")

cost_items = [
    "Registry Account Opening (One-time)",
    "Registry Registration (5-Year Validity + GST)", 
    "Registry Maintenance (Recurring)", 
    "Issuance Fee (ICX + GST)",  
    "Independent Verification Audit (+ GST)", 
    "Triara CAP's Success Fee (+GST)"
]

# Calculating period costs for the table
costs_inr = [
    (ACC_OPENING_EUR * EUR_TO_INR),
    REGISTRATION_FEE_INR,
    (ANNUAL_TRADE_ACC_EUR * EUR_TO_INR) * projection_years,
    (total_irecs_annual * ISSUANCE_FEE_INR) * projection_years,
    (10000 * GST_RATE) * projection_years,
    my_fee
]

df_data = pd.DataFrame({
    "Cost Component": cost_items,
    "Period Total (INR)": [f"₹{int(c):,}" for c in costs_inr],
    "Avg. Cost per I-REC": [f"₹{c/total_irecs_period:.2f}" for c in costs_inr]
})

total_row = pd.DataFrame({
    "Cost Component": [f"**TOTAL {projection_years}-YEAR EXPENSES**"],
    "Period Total (INR)": [f"**₹{int(total_period_expenses):,}**"],
    "Avg. Cost per I-REC": [f"**₹{total_period_expenses/total_irecs_period:.2f}**"]
})
st.table(pd.concat([df_data, total_row], ignore_index=True))

# --- 6. VISUALIZATIONS ---
st.markdown("---")
c_left, c_right = st.columns(2)

with c_left:
    st.subheader("Financial Distribution")
    fig_pie = px.pie(
        values=[float(total_period_expenses), float(client_net_profit)], 
        names=['Total Costs & Fees', 'Net Client Profit'],
        hole=0.4,
        color_discrete_sequence=['#E74C3C', '#2ECC71']
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with c_right:
    st.subheader("Revenue Benchmarking (INR)")
    fig_bar = px.bar(
        x=["Gross Revenue", "Total Expenses", "Net Profit"],
        y=[gross_revenue, total_period_expenses, client_net_profit],
        color=["Revenue", "Expense", "Profit"],
        text_auto='.2s'
    )
    st.plotly_chart(fig_bar, use_container_width=True)
