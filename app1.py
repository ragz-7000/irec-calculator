import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# Page Configuration
st.set_page_config(page_title="I-REC Hybrid Asset Manager", layout="wide")

# --- 1. CONFIGURATION & CONSTANTS ---
# Using Jan 2026 Exchange Rate: 1 USD = 90.95 INR
USD_TO_INR = 90.95 
irec_price_usd = 0.50
irec_price_inr = irec_price_usd * USD_TO_INR

# --- 2. SIDEBAR INPUTS ---
st.sidebar.header("📊 Project Configuration")
proj_name = st.sidebar.text_input("Project Name", "Hybrid Wind-Solar Project")
solar_mw = st.sidebar.number_input("Solar Capacity (MW)", value=10.0)
wind_mw = st.sidebar.number_input("Wind Capacity (MW)", value=15.0)

st.sidebar.header("💼 Service Parameters")
fee_pct = st.sidebar.slider("Your Success Fee (%)", 0, 20, 10)

# --- 3. THE COMPLETE COST & REVENUE ENGINE ---
# Generation (MWh)
s_gen = solar_mw * 8760 * 0.20 
w_gen = wind_mw * 8760 * 0.35  
total_irecs = s_gen + w_gen

# A. Regulatory & Issuance Costs (INR)
reg_fee_total = 89000 if (solar_mw + wind_mw) > 3 else 44500
annual_reg_cost = reg_fee_total / 5
annual_maint_fee = 180000        # Paid to I-TRACK Registry
icx_issuance_fee = total_irecs * 2.25 # Paid to ICX (Issuer)
redemption_fee = total_irecs * 7.00   # UPDATED: Current 2026 Retirement Fee

# B. Operational & Professional Costs
verification_audit = 50000      
gross_revenue = total_irecs * irec_price_inr

# Subtotal of Regulatory/Op Costs
total_op_costs = annual_reg_cost + annual_maint_fee + icx_issuance_fee + redemption_fee + verification_audit

# C. Success Fee (Calculated on Net Revenue)
net_pre_fee = gross_revenue - total_op_costs
my_fee = net_pre_fee * (fee_pct / 100)
total_annual_expenses = total_op_costs + my_fee
client_net_profit = gross_revenue - total_annual_expenses

# --- 4. DASHBOARD UI ---
st.title(f"🔋 Commercial Dashboard: {proj_name}")
st.info(f"Market Assumption: I-REC Price = ${irec_price_usd} (₹{irec_price_inr:.2f}) | Exch Rate: ₹{USD_TO_INR}")

# Top Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Project Capacity", f"{int(solar_mw + wind_mw)} MW")
m2.metric("Total I-RECs", f"{int(total_irecs):,}")
m3.metric("Total Annual Expenses", f"₹{int(total_annual_expenses):,}")
m4.metric("Net Client Profit", f"₹{int(client_net_profit):,}")

# --- 5. COMPREHENSIVE COST TABLE ---
st.subheader("📋 Exhaustive Expenditure & Fee Schedule")

cost_items = [
    "Registry Registration (Amortized)",
    "Annual Registry Maintenance (I-TRACK)",
    "ICX Issuance Fee (Variable)",
    "Redemption/Retirement Fee",
    "Independent Verification Audit",
    "Professional Management Fee"
]
costs_inr = [annual_reg_cost, annual_maint_fee, icx_issuance_fee, redemption_fee, verification_audit, my_fee]
per_irec = [c / total_irecs for c in costs_inr]

df = pd.DataFrame({
    "Cost Component": cost_items,
    "Annual Expense (INR)": [f"₹{int(c):,}" for c in costs_inr],
    "Cost per I-REC (INR)": [f"₹{c:.2f}" for c in per_irec]
})

# Add Total Row
total_row = pd.DataFrame({
    "Cost Component": ["**TOTAL ANNUAL EXPENSES**"],
    "Annual Expense (INR)": [f"**₹{int(total_annual_expenses):,}**"],
    "Cost per I-REC (INR)": [f"**₹{total_annual_expenses/total_irecs:.2f}**"]
})
final_df = pd.concat([df, total_row], ignore_index=True)

st.table(final_df)

# --- 6. VISUALIZATIONS ---
st.markdown("---")
c_left, c_right = st.columns(2)

with c_left:
    st.subheader("Financial Distribution")
    fig_pie = px.pie(
        values=[total_annual_expenses, client_net_profit], 
        names=['Total Expenses', 'Net Client Profit'],
        hole=0.4,
        color_discrete_sequence=['#E74C3C', '#2ECC71']
    )
    st.plotly_chart(fig_pie, use_container_width=True)

with c_right:
    st.subheader("Revenue vs Expenses")
    fig_bar = px.bar(
        x=["Gross Revenue", "Total Expenses", "Net Profit"],
        y=[gross_revenue, total_annual_expenses, client_net_profit],
        color=["Revenue", "Expense", "Profit"],
        text_auto='.2s'
    )
    st.plotly_chart(fig_bar, use_container_width=True)

# --- 7. PDF EXPORT ---
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 15, f"I-REC Commercial Proposal: {proj_name}", ln=True, align='C')
    pdf.set_font("Arial", "", 11)
    pdf.ln(10)
    pdf.cell(0, 10, f"Annual I-REC Volume: {int(total_irecs):,} Units", ln=True)
    pdf.cell(0, 10, f"Total Annual Expenses (incl. Fees): INR {int(total_annual_expenses):,}", ln=True)
    pdf.cell(0, 10, f"Estimated Net Annual Profit: INR {int(client_net_profit):,}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(0, 8, "This report includes the updated ₹7.00/unit Redemption Fee as per 2026 I-TRACK standards.")
    return bytes(pdf.output())

if st.button("Download Executive Summary Report"):
    st.download_button("Download PDF", data=create_pdf(), file_name="IREC_Valuation_Report.pdf")
