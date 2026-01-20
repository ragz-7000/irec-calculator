import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# Page Configuration
st.set_page_config(page_title="Triara CAP | ABR I-REC Projection", layout="wide")

# --- 1. 2026 v2 FEE CONSTANTS ---
USD_TO_INR = 90.95 
GST_RATE = 0.18

ACC_OPENING_USD = 588.50      
ANNUAL_TRADE_ACC_USD = 2354.00 
REDEMPTION_LEVY_USD = 0.08     
ICX_REG_BASE = 104110.00      
ICX_ISSUANCE_BASE = 2.60       
ICX_AUDIT_BASE = 10000.00

# --- 2. HEADER & LOGO ---
col_logo, col_title = st.columns([1, 4])
with col_logo:
    # Placeholder for Triara CAP Logo - You can replace the URL with your actual logo path
    st.image("https://via.placeholder.com/150x50.png?text=TRIARA+CAP", width=150)

with col_title:
    st.title("🚀 I-REC 5-Year Strategic Valuation: Aditya Birla Renewables")

# --- 3. INPUTS & CONSTANTS ---
solar_mw = 100.0
wind_mw = 50.0
total_irecs_annual = (solar_mw * 8760 * 0.20) + (wind_mw * 8760 * 0.35)
fee_pct = 17.0

# --- 4. SCENARIO CALCULATION ENGINE ---
scenarios = [0.40, 0.50, 1.00]
years = [1, 2, 3, 4, 5]
data_list = []

for price in scenarios:
    price_inr = price * USD_TO_INR
    cum_rev = 0
    cum_exp = 0
    cum_profit = 0
    
    for year in years:
        # Global Fees
        setup_cost = (ACC_OPENING_USD * USD_TO_INR) if year == 1 else 0
        maint_cost = ANNUAL_TRADE_ACC_USD * USD_TO_INR
        redemption_cost = total_irecs_annual * REDEMPTION_LEVY_USD * USD_TO_INR
        
        # Local Fees (Incl. 18% GST)
        reg_cost = (ICX_REG_BASE * (1 + GST_RATE)) if year == 1 else 0
        issuance_cost = (total_irecs_annual * ICX_ISSUANCE_BASE) * (1 + GST_RATE)
        audit_cost = (ICX_AUDIT_BASE * (1 + GST_RATE))
        
        # Yearly Financials
        y_rev = total_irecs_annual * price_inr
        y_exp = setup_cost + maint_cost + redemption_cost + reg_cost + issuance_cost + audit_cost
        
        net_pre_fee = y_rev - y_exp
        y_success_fee = net_pre_fee * (fee_pct / 100)
        y_profit = net_pre_fee - y_success_fee
        
        # Track Totals
        cum_rev += y_rev
        cum_exp += (y_exp + y_success_fee)
        cum_profit += y_profit
        
        data_list.append({
            "Year": f"Year {year}",
            "Scenario": f"${price} / I-REC",
            "Profit": y_profit,
            "Revenue": y_rev,
            "Total Cost": y_exp + y_success_fee
        })
    
    # Add the 5-Year Aggregate Row
    data_list.append({
        "Year": "5-Year Total",
        "Scenario": f"${price} / I-REC",
        "Profit": cum_profit,
        "Revenue": cum_rev,
        "Total Cost": cum_exp
    })

df_master = pd.DataFrame(data_list)

# --- 5. VISUALIZATIONS ---
st.subheader("📊 5-Year Net Profit Curve")
df_plot = df_master[df_master["Year"] != "5-Year Total"]
fig_line = px.line(df_plot, x="Year", y="Profit", color="Scenario", markers=True,
                  title="Annual Net Profit Trend (Excl. Aggregates)")
st.plotly_chart(fig_line, use_container_width=True)

# --- 6. SUMMARY TABLES ---
st.markdown("---")
st.subheader("📋 Financial Performance Matrix (Detailed)")

# Separate Tables for clarity
for sc in [f"${p} / I-REC" for p in scenarios]:
    st.write(f"### Scenario: {sc}")
    temp_df = df_master[df_master["Scenario"] == sc][["Year", "Revenue", "Total Cost", "Profit"]]
    st.table(temp_df.set_index("Year").style.format("₹{:,.0f}"))

# --- 7. PDF EXPORT ---
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 15, "Triara CAP: 5-Year I-REC Valuation for ABR", ln=True, align='C')
    pdf.set_font("Arial", "", 12)
    pdf.ln(5)
    pdf.cell(0, 10, f"Annual Volume: {int(total_irecs_annual):,}", ln=True)
    pdf.cell(0, 10, "Summary: Includes all I-TRACK 2026 v2 global and local ICX fees (18% GST).", ln=True)
    return bytes(pdf.output())

if st.sidebar.button("Download Executive Proposal"):
    st.sidebar.download_button("Download PDF", data=create_pdf(), file_name="Triara_ABR_5Year_Proposal.pdf")
