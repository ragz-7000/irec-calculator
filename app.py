import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# Page Configuration
st.set_page_config(page_title="I-REC Hybrid Asset Manager", layout="wide")

# --- INPUTS ---
st.sidebar.header("1. Project Details")
proj_name = st.sidebar.text_input("Project Name", "Hybrid Wind-Solar India")
solar_mw = st.sidebar.number_input("Solar Capacity (MW)", value=10.0)
wind_mw = st.sidebar.number_input("Wind Capacity (MW)", value=15.0)

st.sidebar.header("2. Revenue Assumptions")
rec_price = st.sidebar.slider("Expected I-REC Price (INR/MWh)", 30, 100, 60)

st.sidebar.header("3. Service & Success Fee")
fee_pct = st.sidebar.slider("Consultancy Fee (%)", 0, 20, 10)

# --- THE EXHAUSTIVE COST ENGINE (2026 RATES) ---
# Generation (MWh)
s_gen = solar_mw * 8760 * 0.20 
w_gen = wind_mw * 8760 * 0.35  
total_mwh = s_gen + w_gen

# A. One-Time Setup Costs (Amortized over 5 years)
reg_fee_total = 89000 if (solar_mw + wind_mw) > 3 else 44500
annual_reg_cost = reg_fee_total / 5

# B. Recurring Fixed Costs
annual_maint_fee = 180000 # Paid to I-TRACK (Registry)
verification_audit = 50000 # Independent audit of meters/COD

# C. Recurring Variable Costs
icx_issuance_fee = total_mwh * 2.25 # Paid to ICX (Issuer)
redemption_fee = total_mwh * 0.50 # Standard retirement fee estimate

total_operating_costs = annual_reg_cost + annual_maint_fee + verification_audit + icx_issuance_fee + redemption_fee

# D. Professional Fees
gross_revenue = total_mwh * rec_price
net_pre_fee = gross_revenue - total_operating_costs
consultancy_fee = net_pre_fee * (fee_pct / 100)
client_final_profit = net_pre_fee - consultancy_fee

# --- DASHBOARD UI ---
st.title(f"💼 I-REC Full-Cycle Commercial Model: {proj_name}")
st.markdown("---")

# Metrics
c1, c2, c3, c4 = st.columns(4)
c1.metric("Annual Generation", f"{int(total_mwh):,} MWh")
c2.metric("Gross Annual Revenue", f"₹{int(gross_revenue):,}")
c3.metric("Total Compliance Costs", f"₹{int(total_operating_costs):,}")
c4.metric("Net Client Profit", f"₹{int(client_final_profit):,}")

# Cost Breakdown Table
st.subheader("📋 Comprehensive Cost Breakdown (Annualized)")
detailed_costs = {
    "Expense Category": ["Registry Registration (Amortized)", "Annual Registry Maintenance", "Independent Audit/Verification", "ICX Issuance Fees (Variable)", "Redemption/Retirement Fees", "Professional Management Fee"],
    "Entity Paid": ["I-TRACK", "I-TRACK", "Verifier", "ICX (Local Issuer)", "Registry", "Consultant"],
    "Amount (INR)": [f"₹{int(annual_reg_cost):,}", f"₹{int(annual_maint_fee):,}", f"₹{int(verification_audit):,}", f"₹{int(icx_issuance_fee):,}", f"₹{int(redemption_fee):,}", f"₹{int(consultancy_fee):,}"]
}
st.table(pd.DataFrame(detailed_costs))

# PDF EXPORT
def create_full_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, f"Full Commercial Proposal: {proj_name}", ln=True, align='C')
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    for i in range(len(detailed_costs["Expense Category"])):
        pdf.cell(100, 10, detailed_costs["Expense Category"][i], border=1)
        pdf.cell(80, 10, detailed_costs["Amount (INR)"][i], border=1, ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"ESTIMATED NET ANNUAL PROFIT: INR {int(client_final_profit):,}", ln=True)
    return bytes(pdf.output())

if st.button("Download Complete Cost-Revenue Report"):
    pdf_bytes = create_full_pdf()
    st.download_button("Download PDF", data=pdf_bytes, file_name="Full_IREC_Model.pdf")
