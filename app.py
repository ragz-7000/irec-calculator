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
s_gen = solar_mw * 8760 * 0.20  # Solar Generation
w_gen = wind_mw * 8760 * 0.35   # Wind Generation
total_recs = s_gen + w_gen

# Revenue
gross_rev = (s_gen * sol_p) + (w_gen * win_p)

# Detailed Regulatory Costs (2026 Estimates)
annual_acct_fee = 180000        # Approx €2,000 Annual Maintenance
reg_fee_amortized = 17800       # Registration fee (89k / 5 years)
issuance_costs = total_recs * 3 # Avg ₹3 per REC
total_reg_costs = annual_acct_fee + reg_fee_amortized + issuance_costs

# Consultancy Fee
my_fee = (gross_rev - total_reg_costs) * (fee_pct / 100)
client_final = gross_rev - total_reg_costs - my_fee

# --- DASHBOARD DISPLAY ---
m1, m2, m3, m4 = st.columns(4)
m1.metric("Annual I-RECs", f"{int(total_recs):,}")
m2.metric("Gross Revenue", f"₹{int(gross_rev):,}")
m3.metric("Total Fees/Costs", f"₹{int(total_reg_costs + my_fee):,}")
m4.metric("Net Client Profit", f"₹{int(client_final):,}")

st.markdown("---")

# --- COST BREAKDOWN SECTION ---
st.subheader("📊 Transparency: Where do the costs go?")
col_a, col_b = st.columns(2)

with col_a:
    st.write("**Mandatory Registry Charges (Fixed & Variable)**")
    cost_data = {
        "Item": ["Annual Maintenance (I-TRACK)", "Project Registration (Amortized)", "Issuance Fees (per MWh)"],
        "Amount (INR)": [f"₹{int(annual_acct_fee):,}", f"₹{int(reg_fee_amortized):,}", f"₹{int(issuance_costs):,}"]
    }
    st.table(pd.DataFrame(cost_data))

with col_b:
    st.write("**Professional Service Fees**")
    st.info(f"Your project's compliance and monetization are managed for a success fee of {fee_pct}%.")
    st.write(f"**Management Fee:** ₹{int(my_fee):,}")
    st.write("**Net Take-Home for Client:**")
    st.title(f"₹{int(client_final):,}")

# Charts
fig = px.pie(values=[s_gen * sol_p, w_gen * win_p], names=['Solar Revenue', 'Wind Revenue'], 
             hole=0.4, title="Revenue Composition", color_discrete_sequence=['#f9d71c', '#87ceeb'])
st.plotly_chart(fig, use_container_width=True)

# --- PDF GENERATION ---
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"I-REC Valuation: {proj_name}", ln=True, align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Total I-RECs: {int(total_recs):,} MWh", ln=True)
    pdf.cell(0, 10, f"Total Regulatory Costs: INR {int(total_reg_costs):,}", ln=True)
    pdf.cell(0, 10, f"Your Management Fee: INR {int(my_fee):,}", ln=True)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 15, f"NET ANNUAL PROFIT: INR {int(client_final):,}", ln=True)
    return bytes(pdf.output())

if st.button("Download Executive Summary PDF"):
    pdf_bytes = create_pdf()
    st.download_button("Download Now", data=pdf_bytes, file_name="Report.pdf", mime="application/pdf")
