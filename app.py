import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF

# Page Configuration
st.set_page_config(page_title="Triara CAP | ABR I-REC Strategy", layout="wide")

# --- 1. 2026 v2 AUDITED CONSTANTS ---
USD_TO_INR = 90.95 
GST_RATE = 0.18

# A. Global Registry (I-TRACK Foundation / Evident)
# Typically invoiced in USD; RCM (Reverse Charge) applies for GST in India.
ACC_OPENING_USD = 588.50       # One-time Account Setup
ANNUAL_TRADE_ACC_USD = 2354.00  # Yearly Trade Account Maintenance
PLATFORM_REDEMPTION_USD = 0.08  # Global Platform Operator (Redemption) Fee

# B. Local Issuer (ICX India) - Mandatory 18% GST
ICX_REG_BASE = 104110.00       # 5-Year Asset Registration (>3MW)
ICX_ISSUANCE_BASE = 2.60        # Standard Issuance Fee / MWh
ICX_VERIFICATION_BASE = 10000.00 # Independent Audit Provision

# --- 2. DYNAMIC INPUTS ---
col_logo, col_title = st.columns([1, 4])
with col_logo:
    st.image("https://via.placeholder.com/200x60.png?text=TRIARA+CAP", use_container_width=True)
with col_title:
    st.title("🚀 I-REC 5-Year Strategic Valuation: Aditya Birla Renewables")

solar_mw = 100.0
wind_mw = 50.0
total_irecs_annual = (solar_mw * 8760 * 0.20) + (wind_mw * 8760 * 0.35)
fee_pct = 17.0
scenarios = [0.40, 0.50, 1.00]

# --- 3. THE 5-YEAR COMPREHENSIVE ENGINE ---
years = [1, 2, 3, 4, 5]
all_results = []

for price_usd in scenarios:
    price_inr = price_usd * USD_TO_INR
    c_rev, c_cost, c_profit = 0, 0, 0
    
    for year in years:
        # 3.1 Global Costs (INR)
        setup = (ACC_OPENING_USD * USD_TO_INR) if year == 1 else 0
        maint = ANNUAL_TRADE_ACC_USD * USD_TO_INR
        # Platform Operator Fee (No GST on Global Invoice, usually RCM handled by client)
        platform_redemption = total_irecs_annual * PLATFORM_REDEMPTION_USD * USD_TO_INR
        
        # 3.2 Local ICX Costs (INR + 18% GST)
        # Registration valid for 5 years, charged only in Year 1
        reg = (ICX_REG_BASE * (1 + GST_RATE)) if year == 1 else 0
        issu = (total_irecs_annual * ICX_ISSUANCE_BASE) * (1 + GST_RATE)
        audi = (ICX_VERIFICATION_BASE * (1 + GST_RATE))
        
        # 3.3 Yearly P&L
        y_rev = total_irecs_annual * price_inr
        y_op_exp = setup + maint + platform_redemption + reg + issu + audi
        
        y_net_pre_fee = y_rev - y_op_exp
        y_triara_fee = y_net_pre_fee * (fee_pct / 100)
        y_profit = y_net_pre_fee - y_triara_fee
        y_total_exp = y_op_exp + y_triara_fee

        c_rev += y_rev
        c_cost += y_total_exp
        cum_p = c_rev - c_cost
        
        all_results.append({
            "Scenario": f"${price_usd:.2f}",
            "Year": f"Year {year}",
            "Revenue": y_rev,
            "Expenses": y_total_exp,
            "Annual Profit": y_profit,
            "Cumulative Profit": cum_p
        })
    
    # Add Aggregate Data
    all_results.append({
        "Scenario": f"${price_usd:.2f}",
        "Year": "5-Year Total",
        "Revenue": c_rev,
        "Expenses": c_cost,
        "Annual Profit": cum_p,
        "Cumulative Profit": cum_p
    })

df_master = pd.DataFrame(all_results)

# --- 4. DASHBOARD VISUALS ---
st.info(f"Financial Integrity Check: Global Redemption ${PLATFORM_REDEMPTION_USD} | Local GST 18% | Registration valid 5yrs")

# Scenario Comparison Graph
st.subheader("📊 5-Year Cumulative Profitability Analysis")
df_plot = df_master[df_master["Year"] != "5-Year Total"]
fig = px.line(df_plot, x="Year", y="Cumulative Profit", color="Scenario", markers=True,
             title="Cumulative Client Net Profit (INR) Across Price Tiers")
st.plotly_chart(fig, use_container_width=True)

# Full Financial Table
st.subheader("📋 Exhaustive Multi-Year Financial Matrix")
pivot_df = df_master.pivot(index="Scenario", columns="Year", values="Annual Profit")
st.table(pivot_df.style.format("₹{:,.0f}"))

# --- 5. DETAILED EXPENSE BREAKDOWN (YEAR 1) ---
with st.expander("🔍 View Year 1 Mandatory Outflows (Breakdown)"):
    y1_costs = {
        "Global Account Opening (One-time)": ACC_OPENING_USD * USD_TO_INR,
        "Annual Trade Account (Foundation)": ANNUAL_TRADE_ACC_USD * USD_TO_INR,
        "5-Year Asset Registration (ICX + GST)": ICX_REG_BASE * (1 + GST_RATE),
        "Issuance Fees (ICX + GST)": (total_irecs_annual * ICX_ISSUANCE_BASE) * (1 + GST_RATE),
        "Platform Redemption Levy (Global)": total_irecs_annual * PLATFORM_REDEMPTION_USD * USD_TO_INR,
        "Success Fee (Triara CAP)": all_results[0]['Expenses'] - (y_op_exp - y_triara_fee) # Approx
    }
    st.json(y1_costs)

# --- 6. PDF EXPORT ---
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 15, "STRATEGIC PROPOSAL: ADITYA BIRLA RENEWABLES", ln=True, align='C')
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Subject: 150MW Hybrid Asset I-REC Monetization", ln=True)
    pdf.cell(0, 10, f"5-Year Projected
