import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import base64

# Page Configuration
st.set_page_config(page_title="I-REC Hybrid Dashboard", layout="wide")

# --- APP LOGIC ---
st.title("🔋 I-REC Revenue & Asset Dashboard")
st.sidebar.header("Project Config")
proj_name = st.sidebar.text_input("Project Name", "Hybrid Project Alpha")
solar_mw = st.sidebar.number_input("Solar (MW)", value=10.0)
wind_mw = st.sidebar.number_input("Wind (MW)", value=15.0)
sol_p = st.sidebar.slider("Solar Price (INR)", 30, 100, 65)
win_p = st.sidebar.slider("Wind Price (INR)", 30, 100, 55)
fee_pct = st.sidebar.slider("Consultancy Fee (%)", 0, 20, 10)

# Calculations
s_gen = solar_mw * 8760 * 0.20
w_gen = wind_mw * 8760 * 0.35
total_recs = s_gen + w_gen
gross_rev = (s_gen * sol_p) + (w_gen * win_p)
net_rev = gross_rev - (total_recs * 4.5) # Subtracting registry fees
my_fee = net_rev * (fee_pct/100)
client_final = net_rev - my_fee

# Visual Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Annual I-RECs", f"{int(total_recs):,}")
col2.metric("Gross Revenue", f"₹{int(gross_rev):,}")
col3.metric("Client Net Profit", f"₹{int(client_final):,}")

# Charts
fig = px.pie(values=[s_gen * sol_p, w_gen * win_p], names=['Solar Revenue', 'Wind Revenue'], hole=0.4, title="Revenue Composition")
st.plotly_chart(fig, use_container_width=True)

# --- PDF GENERATION FUNCTION ---
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, f"I-REC Valuation Report: {proj_name}", ln=True, align="C")
    pdf.set_font("Helvetica", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Total Capacity: {solar_mw + wind_mw} MW", ln=True)
    pdf.cell(0, 10, f"Annual Renewable Certificates: {int(total_recs):,} MWh", ln=True)
    pdf.cell(0, 10, f"Estimated Gross Revenue: INR {int(gross_rev):,}", ln=True)
    pdf.cell(0, 10, f"Net Revenue to Client: INR {int(client_final):,}", ln=True)
    pdf.ln(10)
    pdf.set_font("Helvetica", "I", 10)
    pdf.multi_cell(0, 10, "Disclaimer: These values are estimates based on standard Indian CUF data and current 2026 market prices for I-RECs.")
    return pdf.output()

# Download Button
if st.button("Generate Executive PDF Report"):
    pdf_data = create_pdf()
    st.download_button(label="Download PDF", data=pdf_data, file_name="IREC_Report.pdf", mime="application/pdf")
