import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# Page Configuration
st.set_page_config(page_title="I-REC Hybrid Asset Manager", layout="wide")

# --- 1. CONFIGURATION & CONSTANTS ---
USD_TO_INR = 90.95 
irec_price_usd = 0.50
irec_price_inr = irec_price_usd * USD_TO_INR

# --- 2. SIDEBAR INPUTS ---
st.sidebar.header("📊 Project Configuration")
proj_name = st.sidebar.text_input("Project Name", "Hybrid Wind-Solar Project")
solar_mw = st.sidebar.number_input("Solar Capacity (MW)", value=10.0)
wind_mw = st.sidebar.number_input("Wind Capacity (MW)", value=15.0)

st.sidebar.header("💼 Service Parameters")
fee_pct = st.sidebar.slider("Consultancy Fee (%)", 0, 20, 10)

# --- 3. THE COMPLETE COST ENGINE ---
# Generation (MWh)
s_gen = solar_mw * 8760 * 0.20 
w_gen = wind_mw * 8760 * 0.35  
total_irecs = s_gen + w_gen

# A. Regulatory Costs (INR) - Updated with ICX/REPA 2026 Standards
reg_fee_total = 89000 if (solar_mw + wind_mw) > 3 else 44500
annual_reg_cost = reg_fee_total / 5
annual_maint_fee = 180000        # Registry Maintenance
icx_issuance_fee = total_irecs * 3.00 # Standard Issuance Fee
redemption_fee = total_irecs * 7.00   # NEW: Official Redemption Fee

# B. Operational Costs
verification_audit = 50000      
gross_revenue = total_irecs * irec_price_inr

# Total Annual Overhead
total_op_costs = annual_reg_cost + annual_maint_fee + icx_issuance_fee + redemption_fee + verification_audit
net_pre_fee = gross_revenue - total_op_costs
my_fee = net_pre_fee * (fee_pct / 100)
total_annual_expenses = total_op_costs + my_fee
client_net_profit = gross_revenue - total_annual_expenses

# --- 4. DASHBOARD UI ---
st.title(f"🔋 Commercial Dashboard: {proj_name}")
st.info(f"Assumptions: $0.50/REC | Issuance: ₹3.00 | Redemption: ₹7.00 | Exch Rate: ₹{USD_TO_INR}")

# Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Total I-RECs", f"{int(total_irecs):,}")
m2.metric("Gross Revenue", f"₹{int(gross_revenue):,}")
m3.metric("Total Expenses", f"₹{int(total_annual_expenses):,}")
m4.metric("Net Client Profit", f"₹{int(client_net_profit):,}")

# --- 5. UPDATED COST TABLE ---
st.subheader("📋 Exhaustive Expenditure & Fee Schedule")

cost_items = ["Registry Registration", "Registry Maintenance", "Issuance Fee (ICX)", "Redemption Fee", "Audit Fee", "Management Fee"]
costs_inr = [annual_reg_cost, annual_maint_fee, icx_issuance_fee, redemption_fee, verification_audit, my_fee]

df = pd.DataFrame({
    "Cost Component": cost_items,
    "Annual Expense (INR)": [f"₹{int(c):,}" for c in costs_inr],
    "Cost per I-REC (INR)": [f"₹{c / total_irecs:.2f}" for c in costs_inr]
})

total_row = pd.DataFrame({
    "Cost Component": ["**TOTAL ANNUAL EXPENSES**"],
    "Annual Expense (INR)": [f"**₹{int(total_annual_expenses):,}**"],
    "Cost per I-REC (INR)": [f"**₹{total_annual_expenses/total_irecs:.2f}**"]
})
st.table(pd.concat([df, total_row], ignore_index=True))

# --- 6. VISUALS ---
st.subheader("Financial Breakdown")
fig = px.pie(
    values=[total_annual_expenses, client_net_profit], 
    names=['Total Expenses', 'Net Client Profit'],
    hole=0.4, color_discrete_sequence=['#E74C3C', '#2ECC71']
)
st.plotly_chart(fig, use_container_width=True)

# --- 7. PDF EXPORT ---
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 15, f"I-REC Commercial Proposal: {proj_name}", ln=True, align='C')
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Total I-RECs: {int(total_irecs):,} MWh", ln=True)
    pdf.cell(0, 10, f"Total Annual Expenses: INR {int(total_annual_expenses):,}", ln=True)
    pdf.cell(0, 10, f"Net Annual Profit: INR {int(client_net_profit):,}", ln=True)
    return bytes(pdf.output())

if st.button("Download Final Report"):
    st.download_button("Download PDF", data=create_pdf(), file_name="IREC_Final_Report.pdf")
