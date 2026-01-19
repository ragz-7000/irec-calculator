import streamlit as st
import pandas as pd
import plotly.express as px

# Page Config
st.set_page_config(page_title="I-REC Asset Dashboard", layout="wide")

st.title("🛡️ I-REC Asset Management & Revenue Dashboard")
st.markdown("---")

# --- SIDEBAR: INPUTS ---
st.sidebar.header("📍 Project Configuration")
project_name = st.sidebar.text_input("Project Name", "Hybrid Project Alpha")
solar_mw = st.sidebar.number_input("Solar Capacity (MW)", min_value=0.0, value=10.0, step=0.5)
wind_mw = st.sidebar.number_input("Wind Capacity (MW)", min_value=0.0, value=15.0, step=0.5)

st.sidebar.header("📈 Market Assumptions (INR)")
solar_price = st.sidebar.slider("Solar I-REC Price", 30, 100, 65)
wind_price = st.sidebar.slider("Wind I-REC Price", 30, 100, 55)

st.sidebar.header("💼 Service Structure")
consultancy_pct = st.sidebar.slider("Consultancy Success Fee (%)", 0, 20, 10)

# --- CALCULATIONS ---
# Standard Indian CUF: Solar 20%, Wind 35%
solar_ann_gen = solar_mw * 8760 * 0.20
wind_ann_gen = wind_mw * 8760 * 0.35
total_recs = solar_ann_gen + wind_ann_gen

solar_rev = solar_ann_gen * solar_price
wind_rev = wind_ann_gen * wind_price
gross_total = solar_rev + wind_rev

# Registry & Issuance Fees (Estimated for 2026)
issuance_costs = total_recs * 4.5  # Avg issuance fee
reg_fee_annual = 17800             # Amortized project reg fee
total_registry_fees = issuance_costs + reg_fee_annual

# Consultancy Fee Calculation
my_fee = (gross_total - total_registry_fees) * (consultancy_pct / 100)
net_to_client = gross_total - total_registry_fees - my_fee

# --- DASHBOARD LAYOUT ---

# Row 1: Key Metrics
m1, m2, m3, m4 = st.columns(4)
m1.metric("Annual I-RECs (MWh)", f"{int(total_recs):,}")
m2.metric("Gross Revenue", f"₹{int(gross_total):,}")
m3.metric("Your Management Fee", f"₹{int(my_fee):,}")
m4.metric("Net Client Profit", f"₹{int(net_to_client):,}", delta="After All Costs")

st.markdown("---")

# Row 2: Charts
c1, c2 = st.columns([1, 1])

with c1:
    st.subheader("Revenue Breakdown: Solar vs Wind")
    df_pie = pd.DataFrame({
        "Source": ["Solar I-RECs", "Wind I-RECs"],
        "Revenue": [solar_rev, wind_rev]
    })
    fig_pie = px.pie(df_pie, values='Revenue', names='Source', hole=0.4, 
                     color_discrete_sequence=['#FFD700', '#00BFFF'])
    st.plotly_chart(fig_pie, use_container_width=True)

with c2:
    st.subheader("5-Year Cumulative Profit Projection")
    years = [1, 2, 3, 4, 5]
    cumulative_profit = [int(net_to_client * y) for y in years]
    df_line = pd.DataFrame({"Year": years, "Net Profit (INR)": cumulative_profit})
    fig_line = px.line(df_line, x="Year", y="Net Profit (INR)", markers=True)
    st.plotly_chart(fig_line, use_container_width=True)

# Row 3: Process Map Reference
st.markdown("### 🛠️ Execution Roadmap")
st.info("The dashboard assumes a 5-year registration cycle. Market prices are updated based on current I-TRACK secondary market trends in India.")



# Row 4: Data Table for Transparency
with st.expander("View Detailed Financial Table"):
    st.table(pd.DataFrame({
        "Description": ["Gross Solar Revenue", "Gross Wind Revenue", "Registry/Issuance Costs", "Consultancy Fee", "Final Client Take-home"],
        "Amount (INR)": [f"₹{int(solar_rev):,}", f"₹{int(wind_rev):,}", f"₹{int(total_registry_fees):,}", f"₹{int(my_fee):,}", f"₹{int(net_to_client):,}"]
    }))
