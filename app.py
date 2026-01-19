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

# --- FIXED PDF GENERATION FUNCTION ---
def create_pdf(proj_name, solar_mw, wind_mw, total_recs, gross_rev, client_final):
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(0, 15, "I-REC VALUATION REPORT", ln=True, align="C")
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 10, f"Project: {proj_name}", ln=True, align="C")
    pdf.ln(10)
    
    # Financial Table Headers
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_fill_color(240, 240, 240)
    pdf.cell(90, 10, "Description", border=1, fill=True)
    pdf.cell(90, 10, "Value", border=1, fill=True, ln=True)
    
    # Table Data
    pdf.set_font("Helvetica", "", 12)
    data = [
        ("Solar Capacity", f"{solar_mw} MW"),
        ("Wind Capacity", f"{wind_mw} MW"),
        ("Estimated Annual I-RECs", f"{int(total_recs):,} MWh"),
        ("Gross Annual Revenue", f"INR {int(gross_rev):,}"),
        ("Net Client Profit (Annual)", f"INR {int(client_final):,}")
    ]
    
    for desc, val in data:
        pdf.cell(90, 10, desc, border=1)
        pdf.cell(90, 10, val, border=1, ln=True)
    
    pdf.ln(15)
    pdf.set_font("Helvetica", "I", 10)
    pdf.multi_cell(0, 8, "Disclaimer: This report is a preliminary valuation based on standard industry CUF and 2026 market estimates. Actual issuance depends on grid injection and verification.")
    
    # Return as bytes
    return bytes(pdf.output())

# --- UPDATED BUTTON LOGIC ---
st.markdown("---")
st.subheader("📄 Export Executive Summary")
if st.button("Prepare PDF Report"):
    try:
        pdf_bytes = create_pdf(proj_name, solar_mw, wind_mw, total_recs, gross_rev, client_final)
        st.success("✅ Report Generated Successfully!")
        st.download_button(
            label="💾 Download PDF Report",
            data=pdf_bytes,
            file_name=f"IREC_Valuation_{proj_name.replace(' ', '_')}.pdf",
            mime="application/pdf"
        )
    except Exception as e:
        st.error(f"Error generating PDF: {e}")
