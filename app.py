import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# Page Configuration
st.set_page_config(page_title="I-REC Asset Management", layout="wide")

# --- APP LOGIC ---
st.title("🛡️ I-REC Asset Management & Revenue Dashboard")
st.sidebar.header("1. Project Configuration")
proj_name = st.sidebar.text_input("Project Name", "Hybrid Project Alpha")
solar_mw = st.sidebar.number_input("Solar (MW)", value=10.0)
wind_mw = st.sidebar.number_input("Wind (MW)", value=15.0)

st.sidebar.header("2. Market Assumptions (INR)")
sol_p = st.sidebar.slider("Solar I-REC Sale Price", 30, 100, 65)
win_p = st.sidebar.slider("Wind I-REC Sale Price", 30, 100, 55)

st.sidebar.header("3. ICX Fee Parameters")
# Standard ICX Rate for Grid Injection is approx. 2.25 INR
icx_issuance_rate = st.sidebar.number_input("ICX Issuance Fee (INR/MWh)", value=2.25)
fee_pct = st.sidebar.slider("Your Success Fee (%)", 0, 20, 10)

# --- CALCULATIONS (ICX STANDARDS) ---
# Generation Assumptions: Solar 20% CUF, Wind 35% CUF
s_gen = solar_mw * 8760 * 0.20 
w_gen = wind_mw * 8760 * 0.35  
total_recs = s_gen + w_gen

# Revenue Calculation
gross_rev = (s_gen * sol_p) + (w_gen * win_p)

# ICX Tiered Registration Fee (One-time for 5 years)
# < 3MW = ~44.5k | > 3MW = ~89k
one_time_reg = 89000 if (solar_mw + wind_mw) > 3 else 44500
annual_reg_amortized = one_time_reg / 5

# Annual Maintenance (I-TRACK Standard)
annual_maintenance = 180000 

# Issuance Cost based on ICX Rate
total_issuance_cost = total_recs * icx_issuance_rate

total_reg_costs_annual = annual_maintenance + annual_reg_amortized + total_issuance_cost

# Final Profit Logic
net_before_consultancy = gross_rev - total_reg_costs_annual
my_fee = net_before_consultancy * (fee_pct / 100)
client_final = net_before_consultancy - my_fee

# --- DASHBOARD DISPLAY ---
col_m1, col_m2, col_m3, col_m4 = st.columns(4)
col_m1.metric("Annual I-RECs", f"{int(total_recs):,}")
col_m2.metric("Gross Revenue", f"₹{int(gross_rev):,}")
col_m3.metric("ICX & Registry Costs", f"₹{int(total_reg_costs_annual):,}")
col_m4.metric("Net Client Profit", f"₹{int(client_final):,}")

st.markdown("---")

# --- DETAILED COST BREAKDOWN ---
st.subheader("📊 ICX Fee Schedule & Compliance Costs")
c1, c2 = st.columns(2)

with c1:
    st.info("**Regulatory Expenditure (Annualized)**")
    cost_data = {
        "Cost Item": ["Project Registration (ICX)", "Annual Registry Maintenance", "Variable Issuance Fee"],
        "Rate": [f"₹{int(one_time_reg):,} (5yr)", "₹1,80,000", f"₹{icx_issuance_rate}/MWh"],
        "Annual Impact": [f"₹{int(annual_reg_amortized):,}", f"₹{int(annual_maintenance):,}", f"₹{int(total_issuance_cost):,}"]
    }
    st.table(pd.DataFrame(cost_data))

with c2:
    st.info("**Consultancy Management**")
    st.write(f"Management of the full lifecycle at a {fee_pct}% Success Fee.")
    st.write(f"**Professional Fee:** ₹{int(my_fee):,}")
    st.write("---")
    st.write("**Final Annualized Project Upside:**")
    st.title(f"₹{int(client_final):,}")

# Revenue Mix Chart
fig = px.pie(
    values=[s_gen * sol_p, w_gen * win_p], 
    names=['Solar I-RECs', 'Wind I-RECs'], 
    hole=0.4, 
    title="Revenue Contribution by Asset Class",
    color_discrete_sequence=['#f9d71c', '#87ceeb']
)
st.plotly_chart(fig, use_container_width=True)

# --- PDF GENERATION ---
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 15, f"I-REC Commercial Summary: {proj_name}", ln=True, align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Total Capacity: {solar_mw + wind_mw} MW (Hybrid)", ln=True)
    pdf.cell(0, 10, f"Annual Issuance Estimate: {int(total_recs):,} I-RECs", ln=True)
    pdf.cell(0
