import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

import requests
import time

# --- 1. THE UPDATED LIVE FETCH ENGINE ---
def get_verified_rates():
    try:
        # We add a unique timestamp to the URL to force the API to give us 
        # the absolute freshest data in its current cache.
        url = f"https://open.er-api.com/v6/latest/EUR?t={int(time.time())}"
        response = requests.get(url, timeout=5)
        data = response.json()
        
        # Fresh live data
        live_eur = data['rates']['INR']
        live_usd = live_eur / data['rates']['USD']
        return live_eur, live_usd
    except:
        # Fallback to your agreed-upon hardcoded rates
        return 106.17, 90.95

# Fetch on every run to ensure "Live" actually means live
LIVE_EUR_RATE, LIVE_USD_RATE = get_verified_rates()

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
solar_mw = st.sidebar.number_input("Solar Capacity (MW)", value=435.0)
wind_mw = st.sidebar.number_input("Wind Capacity (MW)", value=551.25)

# ADDED SIDEBARS FOR CUF
st.sidebar.header("⚙️ Capacity Utilization Factor")
solar_cuf = st.sidebar.slider("Solar CUF (%)", 15.0, 30.0, 22.9, 0.1) / 100
wind_cuf = st.sidebar.slider("Wind CUF (%)", 25.0, 45.0, 37.0, 0.5) / 100

# ADDED SIDEBAR FOR PROJECTION YEARS
st.sidebar.header("⏳ Projection Horizon")
projection_years = st.sidebar.slider("Number of Years", 1, 5, 1)

# --- 2. THE SIDEBAR OVERRIDE (Add this in your Sidebar section) ---
st.sidebar.header("💱 Currency Exchange")

# Toggle between Live and Manual for the meeting
mode = st.sidebar.radio("Rate Source", ["Live API", "Manual Override"], horizontal=True)

if mode == "Live API":
    EUR_TO_INR = LIVE_EUR_RATE
    USD_TO_INR = LIVE_USD_RATE
    st.sidebar.caption(f"Last API Sync: {time.strftime('%H:%M:%S')} IST")
else:
    EUR_TO_INR = st.sidebar.number_input("Set EUR/INR", value=106.17, step=0.01)
    USD_TO_INR = st.sidebar.number_input("Set USD/INR", value=90.95, step=0.01)

# Use these variables in your cost calculations
st.sidebar.info(f"Using Rate: €1 = ₹{EUR_TO_INR:.2f}")


st.sidebar.header("💹 Market Dynamics")
irec_price_usd = st.sidebar.slider("I-REC Sale Price (USD)", 0.20, 1.20, 0.50, 0.05)
irec_price_inr = irec_price_usd * USD_TO_INR

st.sidebar.header("💼 Service Parameters")
fee_pct = st.sidebar.slider("Triara CAP's Success Fee (%)", 2, 20, 15)

# --- 3. THE COMPLETE COST & REVENUE ENGINE ---
# Updated to use dynamic CUF and years
s_gen = solar_mw * 8760 * solar_cuf 
w_gen = wind_mw * 8760 * wind_cuf  
total_irecs_annual = s_gen + w_gen
total_irecs_period = total_irecs_annual * projection_years

# A. Regulatory Costs (INR)
# Account Opening and Registration are one-time (Year 1)
one_time_costs = (ACC_OPENING_EUR * EUR_TO_INR) + (REGISTRATION_FEE_INR * 2)
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
    "Project Registration (5-Year Validity + GST)", 
    "Registry Maintenance (Recurring)", 
    "Issuance Fee (ICX + GST)",  
    "Independent Verification Audit (+ GST)", 
    "Triara CAP's Success Fee (+GST)"
]

# Calculating period costs for the table
costs_inr = [
    (ACC_OPENING_EUR * EUR_TO_INR),
    (REGISTRATION_FEE_INR * 2),
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
        # Using Slate Grey for Costs and Deep Corporate Blue for Profit
        color_discrete_sequence=['#D1D8E0', '#003366'] 
    )
    # Removing the legend to keep it clean, as the colors are distinct
    fig_pie.update_layout(showlegend=True, margin=dict(t=0, b=0, l=0, r=0))
    st.plotly_chart(fig_pie, use_container_width=True)

with c_right:
    st.subheader("Revenue Benchmarking (INR)")
    fig_bar = px.bar(
        x=["Gross Revenue", "Total Expenses", "Net Profit"],
        y=[gross_revenue, total_period_expenses, client_net_profit],
        color=["Revenue", "Expense", "Profit"],
        # Mapping specific corporate shades to each bar
        color_discrete_map={
            "Revenue": "#003366",   # Deep Corporate Blue
            "Expense": "#4A90E2",   # Steel Blue
            "Profit": "#A3C1AD"     # Muted Sage (Professional Green)
        },
        text_auto='.2s'
    )
    # Refining the bar layout for a cleaner look
    fig_bar.update_layout(
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title=None,
        yaxis_title=None
    )
    st.plotly_chart(fig_bar, use_container_width=True)

import streamlit.components.v1 as components

# Add this button where you want it to appear
if st.button("🖨️ Prepare Print-Ready View"):
    components.html(
        """
        <script>
            window.parent.print();
        </script>
        """,
        height=0,
    )

# --- 7. OPERATIONAL ROADMAP & DOCUMENTATION ---
st.markdown("---")
st.subheader("📋 Operational Roadmap & Compliance Requirements")

col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown("### **Execution Timelines**")
    timeline_data = {
        "Phase": ["Registration & Validation", "Verification & Issuance", "Monetization"],
        "Expected Timeline": ["3 - 4 Months", "1 - 2 Months", "Post-Issuance (as per contract)"],
        "Dependency": ["Complete documentation dossier", "Accurate generation data", "Market execution"]
    }
    st.table(pd.DataFrame(timeline_data))

with col2:
    st.markdown("### **Key Documentation Required**")
    with st.expander("🔍 View Checklist for Aditya Birla Renewables"):
        st.markdown("""
        **Project Technicals**
        * Single Line Diagram (SLD) & Project Geo Co-ordinates
        * Commissioning Certificate & Project Photographs
        
        **Compliance & Ownership**
        * No Double Accounting Declaration 
        * Owner's Declaration Letter (if registrant is not the legal owner)
        * No RPO (Renewable Purchase Obligation) Declaration
        * Issuance is contingent upon a formal declaration from the off-taker or captive consumer confirming that the environmental attributes are not being utilized for any internal sustainability claims or third-party contractual obligations.")
        
        **Generation Data**
        * Generation Statements (Last 6 Months)
        * Photographs of Trivector Meters with clear timestamps
        * Wheeling Banking Agreement / Power Purchase Agreement (PPA)
        """)

# Subtle note on the "No Double Accounting" requirement
st.caption("Note: All documentation must confirm the device is not registered in any other mechanism or claiming additional government tariffs.")

# --- 8. SERVICE SCOPE & FEE STRUCTURE ---
st.markdown("---")
st.subheader("🤝 Triara CAP Engagement Framework")

# Refined Professional Language
st.write("""
Triara CAP acts as your end-to-end technical partner for the I-REC lifecycle. 
Our scope of work includes expert advisory on market strategy, managing the complete 
registration of your projects, handling the periodic verification for issuance, 
and executing the final sale of certificates in global markets.
""")

col_left, col_right = st.columns(2)

with col_left:
    st.info("💡 **Standard Success Fee**")
    st.write(f"""
    For all sales and monetization efforts managed by Triara CAP, 
     the success fee is set at **{fee_pct}%** of the net revenue. 
    This covers the full cost of counterparty sourcing and contract execution.
    """)

with col_right:
    st.success("🏢 **Direct Sale Provision**")
    st.write("""
    We recognize that Aditya Birla may occasionally sell I-RECs directly to internal 
    entities or existing partners. In these cases, our fee is reduced to **2%**. 
    This ensures you only pay for the technical compliance and registry management 
    we provide, without the full monetization charge.
    """)

# Operational Compliance Footer
st.markdown("---")
st.markdown("""
<div style="background-color: #f8f9fa; padding: 15px; border-radius: 5px; border-left: 5px solid #003366;">
    <strong>Compliance Note:</strong> Issuance is subject to a formal declaration 
    confirming that these environmental attributes are not being used for RPO 
    compliance by any third-party or captive consumer.
</div>
""", unsafe_allow_html=True)
