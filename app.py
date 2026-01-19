import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# Page Configuration
st.set_page_config(page_title="I-REC Hybrid Dashboard", layout="wide")

# --- APP LOGIC ---
st.title("🛡️ I-REC Asset Management & Revenue Dashboard")
st.sidebar.header("1. Project Configuration")
proj_name = st.sidebar.text_input("Project Name", "Hybrid Project Alpha")
solar_mw = st.sidebar.number_input("Solar (MW)", value=10.0)
wind_mw = st.sidebar.number_input("Wind (MW)", value=15.0)

st.sidebar.header("2. Market Assumptions (INR)")
sol_p = st.sidebar.slider("Solar Price (per MWh)", 30, 100, 65)
win_p = st.sidebar.slider("Wind Price (per MWh)", 30, 100, 55)

st.sidebar.header("3. Service Structure")
fee_pct = st.sidebar.slider("Your Success Fee (%)", 0, 20, 10)

# --- CALCULATIONS ---
# 1. Generation
s_gen = solar_mw * 8760 * 0.20 
w_gen = wind_mw * 8760 * 0.35  
total_recs = s_gen + w_gen

# 2. Revenue
gross_rev = (s_gen * sol_p) + (w_gen * win_p)

# 3. 2026 REGULATORY COSTS (I-TRACK / GCC / ICX)
# One-time Project Registration (Valid for 5 years)
one_time_reg_fee = 89000 if (solar_mw + wind_mw) > 3 else 44500
annual_amortized_reg = one_time_reg_fee / 5

# Annual Maintenance Fee (Registry level)
annual_maintenance = 180000 

# Issuance Fee (Variable based on MWh)
issuance_rate = 3.50 
total_issuance_cost = total_recs * issuance_rate

total_reg_costs_annual = annual_maintenance + annual_amortized_reg + total_issuance_cost

# 4. Final Profits
net_before_consultancy = gross_rev - total_reg_costs_annual
my_fee = net_before_consultancy * (fee_pct / 100)
client_final = net_before_consultancy - my_fee

# --- DASHBOARD DISPLAY ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Annual I-RECs", f"{int(total_recs):,}")
m2.metric("Gross Revenue", f"₹{int(gross_rev):,}")
m3.metric("Annual Regulatory Cost", f"₹{int(total_reg_costs_annual):,}")
m4.metric("Net Client Profit", f"₹{int(client_final):,}")

st.markdown("---")

# --- COST BREAKDOWN ---
st.subheader("📊 Detailed Expenditure Analysis")
c1, c2 = st.columns(2)

with c1:
    st.info("**Regulatory & Registry Charges**")
    cost_breakdown = {
        "Cost Item": ["One-time Project Registration", "Annual Maintenance Fee", "Issuance Fee (per MWh)"],
        "Amount (INR)": [f"₹{int(one_time_reg_fee):,}", f"₹{int(annual_maintenance):,}", f"₹{issuance_rate}/MWh"],
        "Frequency": ["Every 5 Years", "Annual", "Monthly"]
    }
    st.table(pd.DataFrame(cost_breakdown))

with c2:
    st.info("**Consultancy & Success Fee**")
    st.write(f"Based on your {fee_pct}% performance structure:")
    st.write(f"**Your Management Fee:** ₹{int(my_fee):,}")
    st.write("---")
    st.write("**Total Annualized Overhead:**")
    st.title(f"₹{int(total_reg_costs_annual + my_fee):,}")

# Charts
fig = px.pie(values=[s_gen * sol_p, w_gen * win_p], names=['Solar Revenue', 'Wind Revenue'], 
             hole=0.4, title
