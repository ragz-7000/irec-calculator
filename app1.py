import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# Page Configuration
st.set_page_config(page_title="I-REC Hybrid Asset Model", layout="wide")

# --- 1. CONFIGURATION & CURRENCY (JAN 2026 v2) ---
USD_TO_INR = 90.95 
GST_RATE = 0.18  # 18% GST on local services

# I-TRACK Foundation Fees (USD)
ACCOUNT_OPENING_USD = 588.50
ANNUAL_ACCOUNT_USD = 2354.00
REDEMPTION_FEE_USD = 0.08  # v2 Global Rate

# ICX Local Fees (INR) - 2026 v2 Revised
REGISTRATION_FEE_INR = 104110.00 # For >3MW Projects
ISSUANCE_FEE_INR = 2.60         # Standard Grid-Connected

# --- 2. SIDEBAR INPUTS ---
st.sidebar.header("📊 Project Configuration")
proj_name = st.sidebar.text_input("Project Name", "ABR Hybrid Project")
solar_mw = st.sidebar.number_input("Solar Capacity (MW)", value=100.0)
wind_mw = st.sidebar.number_input("Wind Capacity (MW)", value=50.0)

st.sidebar.header("💹 Market Dynamics")
irec_price_usd = st.sidebar.slider("I-REC Sale Price (USD)", 0.20, 1.20, 0.50, 0.05)
irec_price_inr = irec_price_usd * USD_TO_INR

st.sidebar.header("💼 Service Parameters")
fee_pct = st.sidebar.slider("Triara CAP's Success Fee (%)", 15, 25, 17)

# --- 3. THE COMPLETE COST ENGINE ---
s_gen = solar_mw * 8760 * 0.20 
w_gen = wind_mw * 8760 * 0.35  
total_irecs = s_gen + w_gen

# A. Regulatory Costs (INR) + GST
annual_reg_cost = (REGISTRATION_FEE_INR / 5) * (1 + GST_RATE) # Amortized + GST
annual_maint_fee = (ANNUAL_ACCOUNT_USD * USD_TO_INR)          # Global (No GST usually)
icx_issuance_total = (total_irecs * ISSUANCE_FEE_INR) * (1 + GST_RATE) 
redemption_total = (total_irecs * REDEMPTION_FEE_USD * USD_TO_INR)
verification_audit = 10000 * (1 + GST_RATE)

# B. Totals
gross_revenue = total_irecs * irec_price_inr
total_op_costs = annual_reg_cost + annual_maint_fee + icx_issuance_total + redemption_total + verification_audit

# C. Success Fee
net_pre_fee = gross_revenue - total_op_costs
my_fee = net_pre_fee * (fee_pct / 100) # Triara Fee (GST applied on invoice separately)
total_annual_expenses = total_op_costs + my_fee
client_net_profit = gross_revenue - total_annual_expenses

# --- 4. DASHBOARD UI ---
st.title(f"🚀 I-REC Valuation Dashboard: Aditya Birla Renewables")
st.info(f"Assumptions: Sale Price ${irec_price_usd:.2f} | Exch Rate ₹{USD_TO_INR} | **GST 18% applied to ICX Fees**")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Capacity", f"{solar_mw + wind_mw} MW")
m2.metric("Total I-RECs", f"{int(total_irecs):,}")
m3.metric("Total Revenue", f"₹{int(gross_revenue):,}")
m4.metric("Total Expenses", f"₹{int(total_annual_expenses):,}")
m5.metric("Net Client Profit", f"₹{int(client_net_profit):,}")

st.markdown("---")
st.subheader("📋 Detailed Expenditure (Incl. 18% GST where applicable)")

cost_items = [
    "Registry Registration (Incl. GST)", 
    "Registry Maintenance (Annual)", 
    "Issuance Fees (Incl. GST)", 
    "Redemption Fees", 
    "Independent Audit (Incl. GST)", 
    "Triara CAP Success Fee"
]
costs_inr = [annual_reg_cost, annual_maint_fee, icx_issuance_total, redemption_total, verification_audit, my_fee]

df_data = pd.DataFrame({
    "Cost Component": cost_items,
    "Annual Expense (INR)": [f"₹{int(c):,}" for c in costs_inr],
    "Cost per I-REC (INR)": [f"₹{c/total_irecs:.2f}" for c in costs_inr]
})
st.table(df_data)

# --- 5. PDF EXPORT ---
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(w=0, h=15, txt=f"I-REC Commercial Valuation: {proj_name}", ln=True, align='C')
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(w=0, h=10, txt=f"Total I-REC Volume: {int(total_irecs):,} Units", ln=True)
    pdf.cell(w=0, h=10, txt=f"Net Annual Profit: INR {int(client_net_profit):,}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(0, 8, "Note: All local ICX payments include 18% GST as per 2026 v2 standards.")
    return bytes(pdf.output())

if st.sidebar.button("Export Proposal"):
    st.sidebar.download_button("Download PDF", data=create_pdf(), file_name="ABR_IREC_Proposal.pdf")
