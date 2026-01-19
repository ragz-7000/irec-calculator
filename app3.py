import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# Page Configuration
st.set_page_config(page_title="I-REC Hybrid Asset Model", layout="wide")

# --- 1. CONFIGURATION & CURRENCY (JAN 2026) ---
USD_TO_INR = 90.95 
REDEMPTION_FEE_USD = 0.07  
ISSUANCE_FEE_INR = 2.25    

# --- 2. SIDEBAR INPUTS ---
st.sidebar.header("📊 Project Configuration")
proj_name = st.sidebar.text_input("Project Name", "Hybrid Wind-Solar Project")
solar_mw = st.sidebar.number_input("Solar Capacity (MW)", value=10.0)
wind_mw = st.sidebar.number_input("Wind Capacity (MW)", value=15.0)

st.sidebar.header("💹 Market Dynamics")
irec_price_usd = st.sidebar.slider("I-REC Sale Price (USD)", 0.20, 1.50, 0.50, 0.05)
irec_price_inr = irec_price_usd * USD_TO_INR

st.sidebar.header("💼 Service Parameters")
fee_pct = st.sidebar.slider("Consultancy Success Fee (%)", 0, 20, 10)

# --- 3. THE COMPLETE COST & REVENUE ENGINE ---
s_gen = solar_mw * 8760 * 0.20 
w_gen = wind_mw * 8760 * 0.35  
total_irecs = s_gen + w_gen

# A. Regulatory Costs (INR)
reg_fee_total = 89000 if (solar_mw + wind_mw) > 3 else 44500
annual_reg_cost = reg_fee_total / 5
annual_maint_fee = 180000        
icx_issuance_fee = total_irecs * ISSUANCE_FEE_INR
redemption_fee_total = total_irecs * (REDEMPTION_FEE_USD * USD_TO_INR)
verification_audit = 50000      

# B. Totals
gross_revenue = total_irecs * irec_price_inr
total_op_costs = annual_reg_cost + annual_maint_fee + icx_issuance_fee + redemption_fee_total + verification_audit

# C. Consultancy Success Fee Calculation
net_pre_fee = gross_revenue - total_op_costs
my_fee = net_pre_fee * (fee_pct / 100)
total_annual_expenses = total_op_costs + my_fee
client_net_profit = gross_revenue - total_annual_expenses

# --- 4. DASHBOARD UI ---
st.title(f"🚀 I-REC Valuation Dashboard: {proj_name}")

# CLEANED ASSUMPTION HEADER
st.info(f"Assumptions: Sale Price ${irec_price_usd:.2f}  |  Redemption Fee ${REDEMPTION_FEE_USD:.2f}  |  Exch Rate ₹{USD_TO_INR}")

# Top Metrics (5 Columns to include Total Expenses)
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
    "Registry Registration (Amortized)", 
    "Registry Maintenance (Annual)", 
    "Issuance Fee (ICX)", 
    "Redemption Fee (Registry)", 
    "Independent Verification Audit", 
    "Consultancy Success Fee"
]
costs_inr = [annual_reg_cost, annual_maint_fee, icx_issuance_fee, redemption_fee_total, verification_audit, my_fee]
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

# --- 7. PDF EXPORT ---
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(w=0, h=15, txt=f"I-REC Commercial Valuation: {proj_name}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", "", 12)
    pdf.cell(w=0, h=10, txt=f"I-REC Sale Price: ${irec_price_usd:.2f} (INR {irec_price_inr:.2f})", ln=True)
    pdf.cell(w=0, h=10, txt=f"Total I-REC Volume: {int(total_irecs):,} Units", ln=True)
    pdf.cell(w=0, h=10, txt=f"Total Revenue: INR {int(gross_revenue):,}", ln=True)
    pdf.cell(w=0, h=10, txt=f"Total Expenses & Fees: INR {int(total_annual_expenses):,}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(w=0, h=10, txt=f"ESTIMATED NET ANNUAL PROFIT: INR {int(client_net_profit):,}", ln=True)
    return bytes(pdf.output())

st.sidebar.markdown("---")
if st.sidebar.button("Export Professional Proposal"):
    try:
        pdf_bytes = create_pdf()
        st.sidebar.download_button(
            label="Download PDF Report",
            data=pdf_bytes,
            file_name=f"IREC_Proposal_{proj_name}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.sidebar.error(f"Error: {e}")
