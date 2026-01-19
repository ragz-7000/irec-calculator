import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# Page Configuration
st.set_page_config(page_title="I-REC Hybrid Valuation v2", layout="wide")

# --- 1. 2026 v2 FEE CONSTANTS ---
USD_TO_INR = 90.95 
GST_RATE = 0.18

# A. Global Registry Fees (I-TRACK Foundation - USD)
# These are typically exempt from local GST but subject to RCM by the client.
ACC_OPENING_USD = 588.50      # One-time
ANNUAL_TRADE_ACC_USD = 2354.00 # Yearly Maintenance
REDEMPTION_LEVY_USD = 0.08     # Global Platform Operator Fee (v2)

# B. Local Issuer Fees (ICX India - INR) - Subject to 18% GST
ICX_REG_BASE = 104110.00      # Registration for >3MW (5-year validity)
ICX_ISSUANCE_BASE = 2.60       # Standard Issuance per MWh
ICX_AUDIT_BASE = 10000.00      # Independent Verification Provision

# --- 2. SIDEBAR INPUTS ---
st.sidebar.header("📊 Asset Configuration")
proj_name = st.sidebar.text_input("Project Name", "ABR Hybrid 150MW")
solar_mw = st.sidebar.number_input("Solar Capacity (MW)", value=100.0)
wind_mw = st.sidebar.number_input("Wind Capacity (MW)", value=50.0)

st.sidebar.header("💹 Market Assumptions")
irec_price_usd = st.sidebar.slider("Sale Price (USD)", 0.20, 1.20, 0.50, 0.05)
irec_price_inr = irec_price_usd * USD_TO_INR

st.sidebar.header("💼 Triara CAP Commercials")
fee_pct = st.sidebar.slider("Success Fee (%)", 15, 25, 17)

# --- 3. THE CALCULATION ENGINE ---
total_irecs = (solar_mw * 8760 * 0.20) + (wind_mw * 8760 * 0.35)

# 3.1 Global Registry Costs (INR)
global_setup = ACC_OPENING_USD * USD_TO_INR
global_maint = ANNUAL_TRADE_ACC_USD * USD_TO_INR
global_redemption = total_irecs * REDEMPTION_LEVY_USD * USD_TO_INR

# 3.2 Local ICX Costs (INR + 18% GST)
local_reg_annual = (ICX_REG_BASE / 5) * (1 + GST_RATE) # Amortized
local_issuance = (total_irecs * ICX_ISSUANCE_BASE) * (1 + GST_RATE)
local_audit = ICX_AUDIT_BASE * (1 + GST_RATE)

# 3.3 Summary Metrics
gross_revenue = total_irecs * irec_price_inr
total_compliance_costs = global_maint + global_redemption + local_reg_annual + local_issuance + local_audit
net_pre_fee = gross_revenue - total_compliance_costs
triara_success_fee = net_pre_fee * (fee_pct / 100)
client_final_net = net_pre_fee - triara_success_fee

# --- 4. DASHBOARD UI ---
st.title(f"🚀 I-REC Commercial Strategy for Aditya Birla Renewables")
st.info(f"Market Benchmarks: Sale Price ${irec_price_usd:.2f} | Global Redemption ${REDEMPTION_LEVY_USD} | Local GST 18%")

# Top Row Metrics
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Annual I-RECs", f"{int(total_irecs):,}")
c2.metric("Gross Revenue", f"₹{int(gross_revenue):,}")
c3.metric("Total Expenses", f"₹{int(total_compliance_costs + triara_success_fee):,}")
c4.metric("Triara Fee", f"₹{int(triara_success_fee):,}")
c5.metric("Net Client Profit", f"₹{int(client_final_net):,}")

st.markdown("---")

# --- 5. DETAILED COST TABLE ---
st.subheader("📋 Exhaustive 2026 v2 Compliance & Service Fee Schedule")
cost_breakdown = pd.DataFrame({
    "Category": ["Global Setup", "Global Maintenance", "Global Operational", "Local Setup", "Local Operational", "Local Compliance", "Service"],
    "Cost Component": [
        "Account Opening Fee (One-time)", 
        "Annual Trade Account Fee", 
        "Platform Operator Redemption Fee", 
        "Asset Registration (Amortized + GST)", 
        "Issuance Fees (ICX + GST)", 
        "Independent Verification (+ GST)", 
        "Triara CAP Success Fee"
    ],
    "Annual INR": [
        global_setup, 
        global_maint, 
        global_redemption, 
        local_reg_annual, 
        local_issuance, 
        local_audit, 
        triara_success_fee
    ]
})
cost_breakdown["Per I-REC"] = cost_breakdown["Annual INR"] / total_irecs
st.table(cost_breakdown.style.format({"Annual INR": "₹{:,.0f}", "Per I-REC": "₹{:,.2f}"}))

# --- 6. VISUAL ANALYSIS ---
col_l, col_r = st.columns(2)
with col_l:
    fig_p = px.pie(values=[total_compliance_costs, triara_success_fee, client_final_net], 
                   names=['Regulatory Costs', 'Triara Fee', 'Net Profit'],
                   hole=0.4, color_discrete_sequence=['#ff4b4b', '#0066cc', '#00cc96'])
    st.plotly_chart(fig_p, use_container_width=True)
with col_r:
    fig_b = px.bar(x=["Revenue", "Expenses", "Net Profit"], 
                   y=[gross_revenue, (total_compliance_costs + triara_success_fee), client_final_net],
                   color=["Revenue", "Expense", "Profit"], text_auto='.3s')
    st.plotly_chart(fig_b, use_container_width=True)

# --- 7. PDF EXPORT ---
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.cell(0, 15, "ADITYA BIRLA RENEWABLES: I-REC VALUATION", ln=True, align='C')
    pdf.set_font("Arial", "", 12)
    pdf.ln(10)
    pdf.cell(0, 10, f"Annual Volume Projection: {int(total_irecs):,} MWh", ln=True)
    pdf.cell(0, 10, f"Net Annualized Revenue: INR {int(client_final_net):,}", ln=True)
    pdf.ln(5)
    pdf.set_font("Arial", "I", 10)
    pdf.multi_cell(0, 7, "Calculated based on I-TRACK Foundation Fee Structure 2026 v2. Local ICX fees include 18% GST.")
    return bytes(pdf.output())

if st.sidebar.button("Export Board Proposal"):
    st.sidebar.download_button("Download PDF", data=create_pdf(), file_name="ABR_IREC_Full_Proposal.pdf")
