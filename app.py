import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# Page Configuration
st.set_page_config(page_title="Triara CAP | I-REC Strategy", layout="wide")

# --- 1. 2026 v2 GLOBAL & LOCAL CONSTANTS ---
USD_TO_INR = 90.95 
GST_RATE = 0.18

# I-TRACK Foundation (Global Registry - USD)
ACC_OPENING_USD = 588.50       # One-time Setup
ANNUAL_TRADE_ACC_USD = 2354.00  # Yearly Maintenance
REDEMPTION_LEVY_USD = 0.08      # Global Platform Operator Rate

# ICX India (Local Issuer - INR) - Subject to 18% GST
ICX_REG_BASE = 104110.00       # Registration >3MW (5-Year Validity)
ICX_ISSUANCE_BASE = 2.60        # Standard Issuance Fee
ICX_AUDIT_BASE = 10000.00       # Independent Verification Provision

# --- 2. HEADER & BRANDING ---
col_logo, col_title = st.columns([1, 5])
with col_logo:
    # Triara CAP Branding
    st.image("https://via.placeholder.com/200x60.png?text=TRIARA+CAP", use_container_width=True)

with col_title:
    st.title("🚀 I-REC 5-Year Strategic Valuation: Aditya Birla Renewables")

# --- 3. INPUTS ---
st.sidebar.header("📊 Project Configuration")
solar_mw = 100.0
wind_mw = 50.0
total_irecs_annual = (solar_mw * 8760 * 0.20) + (wind_mw * 8760 * 0.35)
fee_pct = 17.0

st.sidebar.header("💹 Market Scenarios (USD/I-REC)")
scenarios = [0.40, 0.50, 1.00]

# --- 4. 5-YEAR CALCULATION ENGINE ---
years = [1, 2, 3, 4, 5]
all_data = []

for price in scenarios:
    price_inr = price * USD_TO_INR
    cum_rev, cum_exp, cum_profit = 0, 0, 0
    
    for year in years:
        # A. Global Fees
        setup = (ACC_OPENING_USD * USD_TO_INR) if year == 1 else 0
        maint = ANNUAL_TRADE_ACC_USD * USD_TO_INR
        redemp = total_irecs_annual * REDEMPTION_LEVY_USD * USD_TO_INR
        
        # B. Local Fees (Incl. 18% GST)
        reg = (ICX_REG_BASE * (1 + GST_RATE)) if year == 1 else 0
        issu = (total_irecs_annual * ICX_ISSUANCE_BASE) * (1 + GST_RATE)
        audi = (ICX_AUDIT_BASE * (1 + GST_RATE))
        
        # C. Yearly Financials
        y_rev = total_irecs_annual * price_inr
        y_op_exp = setup + maint + redemp + reg + issu + audi
        
        net_pre_fee = y_rev - y_op_exp
        y_success_fee = net_pre_fee * (fee_pct / 100)
        y_profit = net_pre_fee - y_success_fee
        y_total_exp = y_op_exp + y_success_fee

        cum_rev += y_rev
        cum_exp += y_total_exp
        cum_profit += y_profit
        
        all_data.append({
            "Scenario": f"${price:.2f}",
            "Year": f"Year {year}",
            "Revenue": y_rev,
            "Expenses": y_total_exp,
            "Net Profit": y_profit
        })
    
    # Add the Cumulative Column for the table
    all_data.append({
        "Scenario": f"${price:.2f}",
        "Year": "5-Year Total",
        "Revenue": cum_rev,
        "Expenses": cum_exp,
        "Net Profit": cum_profit
    })

df_master = pd.DataFrame(all_data)

# --- 5. DASHBOARD UI ---
st.info(f"Assumptions: Exch Rate ₹{USD_TO_INR} | Global Redemption ${REDEMPTION_LEVY_USD} | Local GST 18%")

# 5-Year Profit Graph
st.subheader("📈 5-Year Net Profit Projection")
df_plot = df_master[df_master["Year"] != "5-Year Total"]
fig_line = px.line(df_plot, x="Year", y="Net Profit", color="Scenario", markers=True, 
                  color_discrete_sequence=['#ff4b4b', '#0066cc', '#00cc96'])
st.plotly_chart(fig_line, use_container_width=True)

# 5-Year Summary Table
st.subheader("📋 Financial Performance Matrix (Cumulative & Annual)")
# Pivot for better board-level reading
pivot_df = df_master.pivot(index="Scenario", columns="Year", values="Net Profit")
st.table(pivot_df.style.format("₹{:,.0f}"))

# --- 6. PDF EXPORT ---
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 15, "Triara CAP: Aditya Birla Renewables Strategic Proposal", ln=True, align='C')
    pdf.set_font("Arial", "", 11)
    pdf.ln(5)
    pdf.multi_cell(0, 7, f"This proposal covers the 150MW Hybrid Asset (100MW Solar / 50MW Wind). "
                         f"All calculations are based on I-TRACK Foundation Fee Structure 2026 v2.")
    return bytes(pdf.output())

st.sidebar.markdown("---")
if st.sidebar.button("Export Board Presentation (PDF)"):
    st.sidebar.download_button("Download Now", data=create_pdf(), file_name="Triara_ABR_Full_Proposal.pdf")
