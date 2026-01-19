import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# Page Configuration
st.set_page_config(page_title="I-REC Hybrid Asset Model", layout="wide")

# --- 1. CONFIGURATION & CURRENCY ---
USD_TO_INR = 90.95 
REDEMPTION_FEE_USD = 0.07  
ISSUANCE_FEE_INR = 2.23    

# --- 2. SIDEBAR INPUTS ---
st.sidebar.header("📊 Project Configuration")
proj_name = st.sidebar.text_input("Project Name", "Wind-Solar Hybrid Project")
solar_mw = st.sidebar.number_input("Solar Capacity (MW)", value=100.0)
wind_mw = st.sidebar.number_input("Wind Capacity (MW)", value=50.0)

st.sidebar.header("💹 Market Dynamics")
irec_price_usd = st.sidebar.slider("I-REC Sale Price (USD)", 0.20, 1.20, 0.50, 0.05)
irec_price_inr = irec_price_usd * USD_TO_INR

st.sidebar.header("💼 Service Parameters")
fee_pct = st.sidebar.slider("Triara CAP's Success Fee (%)", 15, 25, 17)

# --- 3. THE COMPLETE COST & REVENUE ENGINE ---
s_gen = solar_mw * 8760 * 0.20 
w_gen = wind_mw * 8760 * 0.35  
total_irecs = s_gen + w_gen

# Regulatory Costs (INR)
reg_fee_total = 89000 if (solar_mw + wind_mw) > 3 else 44500
annual_reg_cost = reg_fee_total / 5
annual_maint_fee = 180000        
icx_issuance_fee = total_irecs * ISSUANCE_FEE_INR
redemption_fee_total = total_irecs * (REDEMPTION_FEE_USD * USD_TO_INR)
verification_audit = 10000      

# Totals
gross_revenue = total_irecs * irec_price_inr
total_op_costs = annual_reg_cost + annual_maint_fee + icx_issuance_fee + redemption_fee_total + verification_audit

# Triara CAP Success Fee Calculation
net_pre_fee = gross_revenue - total_op_costs
my_fee = net_pre_fee * (fee_pct / 100)
total_annual_expenses = total_op_costs + my_fee
client_net_profit = gross_revenue - total_annual_expenses

# --- 4. DASHBOARD UI ---
st.title(f"🚀 I-REC Valuation Dashboard for Aditya Birla Renewables")
st.info(f"Assumptions: Sale Price USD {irec_price_usd:.2f}  |  Redemption Fee USD {REDEMPTION_FEE_USD}  |  Exch Rate ₹{USD_TO_INR}")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("Project Capacity", f"{solar_mw + wind_mw} MW")
m2.metric("Total I-RECs", f"{int(total_irecs):,}")
m3.metric("Total Revenue", f"₹{int(gross_revenue):,}")
m4.metric("Total Expenses", f"₹{int(total_annual_expenses):,}")
m5.metric("Net Client Profit", f"₹{int(client_net_profit):,}")

st.markdown("---")
st.subheader("📋 Detailed Expenditure & Fee Schedule")

cost_items = ["Registry Registration", "Registry Maintenance", "Issuance Fee (ICX)", "Redemption Fee", "Audit Fee", "Triara CAP Success Fee"]
costs_inr = [annual_reg_cost, annual_maint_fee, icx_issuance_fee, redemption_fee_total, verification_audit, my_fee]

df_data = pd.DataFrame({
    "Cost Component": cost_items,
    "Annual Expense (INR)": [f"Rs. {int(c):,}" for c in costs_inr],
    "Cost per I-REC (INR)": [f"Rs. {c/total_irecs:.2f}" for c in costs_inr]
})
st.table(df_data)

# --- 7. EXECUTIVE PDF EXPORT ---
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Header Banner
    pdf.set_fill_color(0, 102, 204) 
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 20)
    pdf.cell(0, 20, "ADITYA BIRLA RENEWABLES - I-REC VALUATION", ln=True, align='C')
    pdf.ln(20)
    
    pdf.set_text_color(0, 0, 0)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Summary of Asset Monetization", ln=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(100, 8, f"Total Capacity: {solar_mw + wind_mw} MW")
    pdf.cell(100, 8, f"Annual I-RECs: {int(total_irecs):,}", ln=True)
    pdf.cell(100, 8, f"Revenue: Rs. {int(gross_revenue):,}")
    pdf.cell(100, 8, f"Success Fee: {fee_pct}%", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.set_fill_color(46, 204, 113)
    pdf.cell(0, 12, f"  ESTIMATED NET ANNUAL PROFIT: Rs. {int(client_net_profit):,}", border=1, fill=True, ln=True)
    
    return bytes(pdf.output())

if st.sidebar.button("Export Proposal"):
    st.sidebar.download_button("Download PDF", data=create_pdf(), file_name="Triara_AdityaBirla_Proposal.pdf")
