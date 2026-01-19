import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# Page Configuration
st.set_page_config(page_title="I-REC Hybrid Asset Model", layout="wide")

# --- 1. CONFIGURATION & CURRENCY ---
USD_TO_INR = 90.95 

# --- 2. SIDEBAR INPUTS ---
st.sidebar.header("📊 Project Configuration")
proj_name = st.sidebar.text_input("Project Name", "Hybrid Wind-Solar Project")
solar_mw = st.sidebar.number_input("Solar Capacity (MW)", value=10.0)
wind_mw = st.sidebar.number_input("Wind Capacity (MW)", value=15.0)

st.sidebar.header("💹 Market Dynamics")
# Variable I-REC Price (USD) to see variations
irec_price_usd = st.sidebar.slider("I-REC Sale Price (USD)", 0.20, 1.50, 0.50, 0.05)
irec_price_inr = irec_price_usd * USD_TO_INR

st.sidebar.header("💼 Service Parameters")
fee_pct = st.sidebar.slider("Consultancy Success Fee (%)", 0, 20, 10)

# --- 3. THE COMPLETE COST & REVENUE ENGINE ---
s_gen = solar_mw * 8760 * 0.20 
w_gen = wind_mw * 8760 * 0.35  
total_irecs = s_gen + w_gen

# A. Fixed & Variable Regulatory Costs (INR)
reg_fee_total = 89000 if (solar_mw + wind_mw) > 3 else 44500
annual_reg_cost = reg_fee_total / 5
annual_maint_fee = 180000        
icx_issuance_fee = total_irecs * 2.25 
redemption_fee = total_irecs * 7.00   
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

st.markdown("---")

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
    # Fixed Pie Chart Logic
    pie_values = [float(total_annual_expenses), float(client_net_profit)]
    pie_names = ['Total Expenses', 'Net Client Profit']
    fig_pie = px.pie(
        values=pie_values, 
        names=pie_names,
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
    pdf.cell(0, 15, f"I-REC Commercial Valuation: {proj_name}", ln=True, align='C')
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Assumption: I-REC Price at ${irec_price_usd:.2f} (INR {irec_price_inr:.2f})", ln=True)
    pdf.cell(0, 10, f"Annual I-REC Volume: {int(total_irecs):,} Units", ln=True)
    pdf.cell(0, 10, f"Net Annual Profit: INR {int(client_net_profit):,}", ln=True)
    return bytes(pdf.output())

st.sidebar.markdown("---")
if st.sidebar.button("Export Professional Proposal"):
    pdf_data = create_pdf()
    st.sidebar.download_button(
        label="Download PDF Now",
        data=pdf_data,
        file_name=f"IREC_Proposal_{proj_name}.pdf",
        mime="application/pdf"
    )
