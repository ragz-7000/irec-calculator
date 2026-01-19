import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# Page Configuration
st.set_font_size = 14
st.set_page_config(page_title="I-REC 5-Year Projection", layout="wide")

# --- 1. 2026 v2 FEE CONSTANTS ---
USD_TO_INR = 90.95 
GST_RATE = 0.18

# Registry & Issuer Constants
ACC_OPENING_USD = 588.50      
ANNUAL_TRADE_ACC_USD = 2354.00 
REDEMPTION_LEVY_USD = 0.08     
ICX_REG_BASE = 104110.00      
ICX_ISSUANCE_BASE = 2.60       
ICX_AUDIT_BASE = 10000.00

# --- 2. INPUTS ---
st.title("🚀 I-REC 5-Year Strategic Valuation: Aditya Birla Renewables")
solar_mw = 100.0
wind_mw = 50.0
total_irecs_annual = (solar_mw * 8760 * 0.20) + (wind_mw * 8760 * 0.35)
fee_pct = 17.0

# --- 3. SCENARIO CALCULATION LOGIC ---
scenarios = [0.40, 0.50, 1.00]
years = [1, 2, 3, 4, 5]
data_list = []

for price in scenarios:
    price_inr = price * USD_TO_INR
    for year in years:
        # 1. Global Fees
        # Opening fee only in Year 1
        setup_cost = (ACC_OPENING_USD * USD_TO_INR) if year == 1 else 0
        maint_cost = ANNUAL_TRADE_ACC_USD * USD_TO_INR
        redemption_cost = total_irecs_annual * REDEMPTION_LEVY_USD * USD_TO_INR
        
        # 2. Local Fees (Incl. 18% GST)
        # Registration only in Year 1 (Valid for 5 years)
        reg_cost = (ICX_REG_BASE * (1 + GST_RATE)) if year == 1 else 0
        issuance_cost = (total_irecs_annual * ICX_ISSUANCE_BASE) * (1 + GST_RATE)
        audit_cost = (ICX_AUDIT_BASE * (1 + GST_RATE))
        
        # 3. Financials
        gross_rev = total_irecs_annual * price_inr
        total_exp = setup_cost + maint_cost + redemption_cost + reg_cost + issuance_cost + audit_cost
        
        net_pre_fee = gross_rev - total_exp
        success_fee = net_pre_fee * (fee_pct / 100)
        net_profit = net_pre_fee - success_fee
        
        data_list.append({
            "Year": f"Year {year}",
            "Scenario": f"${price} / I-REC",
            "Net Profit (INR)": net_profit,
            "Gross Revenue": gross_rev
        })

df_scenarios = pd.DataFrame(data_list)

# --- 4. VISUALIZATIONS ---
st.subheader("📊 5-Year Net Profit Projection")
fig_line = px.line(
    df_scenarios, 
    x="Year", 
    y="Net Profit (INR)", 
    color="Scenario",
    markers=True,
    title="Cumulative Annual Net Profit Comparison",
    labels={"Net Profit (INR)": "Annual Net Profit (₹)"}
)
fig_line.update_layout(hovermode="x unified")
st.plotly_chart(fig_line, use_container_width=True)

# --- 5. DETAILED DATA TABLE ---
st.markdown("---")
st.subheader("📋 Scenario Summary Table (Annualized)")

pivot_df = df_scenarios.pivot(index="Scenario", columns="Year", values="Net Profit (INR)")
st.table(pivot_df.style.format("₹{:,.0f}"))

# --- 6. SIDE-BY-SIDE ANALYSIS ---
c1, c2 = st.columns(2)
with c1:
    st.info("**Year 1 Impact:** Includes Account Opening ($588) and 5-Year Asset Registration (₹1.04L + GST).")
with c2:
    st.success(f"**Annual Volume:** {int(total_irecs_annual):,} I-RECs generated from 150MW Hybrid Asset.")

# --- 7. PDF EXPORT ---
def create_scenario_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 15, "5-YEAR I-REC SCENARIO ANALYSIS: ABR", ln=True, align='C')
    pdf.set_font("Arial", "", 11)
    pdf.ln(5)
    pdf.multi_cell(0, 7, f"Based on 150MW Hybrid Capacity. Projections include 18% GST on local fees and 17% Triara Success Fee. Registration fee (v2) amortized over 5 years validity.")
    return bytes(pdf.output())

if st.button("Export 5-Year Strategic Proposal"):
    st.download_button("Download PDF", data=create_scenario_pdf(), file_name="ABR_5Year_Scenarios.pdf")
