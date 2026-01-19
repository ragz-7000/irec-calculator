import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# Page Configuration
st.set_page_config(page_title="I-REC Hybrid Dashboard", layout="wide")

# --- SIDEBAR: INPUTS ---
st.sidebar.header("1. Project Config")
proj_name = st.sidebar.text_input("Project Name", "Hybrid Project Alpha")
solar_mw = st.sidebar.number_input("Solar (MW)", value=10.0)
wind_mw = st.sidebar.number_input("Wind (MW)", value=15.0)

st.sidebar.header("2. ICX & Registry Costs")
icx_issuance_rate = st.sidebar.number_input("ICX Issuance Fee (INR/MWh)", value=2.25)
fee_pct = st.sidebar.slider("Your Success Fee (%)", 0, 20, 10)

# --- CALCULATIONS ---
s_gen = solar_mw * 8760 * 0.20 
w_gen = wind_mw * 8760 * 0.35  
total_recs = s_gen + w_gen

# Revenue Assumptions
gross_rev = (s_gen * 65) + (w_gen * 55) # Hardcoded avg prices for clarity

# Registration Fees
one_time_reg = 89000 if (solar_mw + wind_mw) > 3 else 44500
annual_maintenance = 180000 
issuance_cost = total_recs * icx_issuance_rate
total_costs = annual_maintenance + (one_time_reg / 5) + issuance_cost

# Final Net
net_revenue = gross_rev - total_costs
my_fee = net_revenue * (fee_pct / 100)
client_final = net_revenue - my_fee

# --- DASHBOARD LAYOUT ---
st.title(f"📊 I-REC Strategy: {proj_name}")
m1, m2, m3 = st.columns(3)
m1.metric("Annual Certificates", f"{int(total_recs):,} MWh")
m2.metric("Est. Gross Revenue", f"₹{int(gross_rev):,}")
m3.metric("Net Client Profit", f"₹{int(client_final):,}")

# --- REVENUE CHART ---
st.markdown("---")
fig = px.pie(
    values=[s_gen * 65, w_gen * 55], 
    names=['Solar Revenue', 'Wind Revenue'], 
    hole=0.4, 
    title="Annual Revenue Composition",
    color_discrete_sequence=['#f9d71c', '#87ceeb']
)
st.plotly_chart(fig, use_container_width=True)

# --- PDF GENERATION FUNCTION ---
def generate_custom_pdf():
    pdf = FPDF()
    # PAGE 1: Financial Summary
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 15, "I-REC COMMERCIAL VALUATION", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(100, 10, "Description", border=1)
    pdf.cell(80, 10, "Value (Annualized)", border=1, ln=True)
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(100, 10, "Total I-RECs (MWh)", border=1)
    pdf.cell(80, 10, f"{int(total_recs):,}", border=1, ln=True)
    pdf.cell(100, 10, "ICX Issuance Fees", border=1)
    pdf.cell(80, 10, f"INR {int(issuance_cost):,}", border=1, ln=True)
    pdf.cell(100, 10, "Registry Maintenance", border=1)
    pdf.cell(80, 10, "INR 1,80,000", border=1, ln=True)
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, f"FINAL CLIENT NET REVENUE: INR {int(client_final):,}", ln=True)
    
    # PAGE 2: Strategic Board Note
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 15, "EXECUTIVE BOARD NOTE", ln=True, align="L")
    pdf.set_font("Helvetica", "", 11)
    note_text = (
        "Project Objective: To monetize the environmental attributes of the Hybrid Energy asset. "
        "Key Advantage: I-RECs allow the project to realize a higher 'Green Premium' beyond simple power sales. "
        "Global Standards: By registering under I-TRACK, the project gains eligibility to supply power "
        "to global multinational corporations (MNCs) seeking Scope 2 carbon compliance in India."
    )
    pdf.multi_cell(0, 10, note_text)
    return bytes(pdf.output())

# --- EXPORT BUTTON ---
st.sidebar.markdown("---")
if st.sidebar.button("Export Professional Proposal"):
    try:
        pdf_data = generate_custom_pdf()
        st.sidebar.success("✅ Proposal Ready!")
        st.sidebar.download_button(
            label="📥 Download PDF",
            data=pdf_data,
            file_name=f"IREC_Proposal_{proj_name}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Error: {e}")
