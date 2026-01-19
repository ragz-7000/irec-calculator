import streamlit as st

st.set_page_config(page_title="I-REC Revenue Model", layout="centered")

st.title("🔋 I-REC Revenue Calculator")
st.subheader("Wind-Solar Hybrid Project Model (India)")

# Sidebar Inputs for the "Meeting Interaction"
st.sidebar.header("Project Specifications")
solar_mw = st.sidebar.number_input("Solar Capacity (MW)", value=10.0)
wind_mw = st.sidebar.number_input("Wind Capacity (MW)", value=10.0)

st.sidebar.header("Market Assumptions")
solar_price = st.sidebar.slider("Solar I-REC Price (INR)", 30, 100, 65)
wind_price = st.sidebar.slider("Wind I-REC Price (INR)", 30, 100, 55)

# Calculations
solar_gen = solar_mw * 8760 * 0.20 # 20% CUF
wind_gen = wind_mw * 8760 * 0.35  # 35% CUF
total_recs = solar_gen + wind_gen

gross_rev = (solar_gen * solar_price) + (wind_gen * wind_price)
fees = (total_recs * 4) + 17800 # Issuance + annualized reg fee

# UI Display
col1, col2 = st.columns(2)
col1.metric("Annual I-RECs", f"{int(total_recs):,}")
col2.metric("Net Annual Revenue", f"₹{int(gross_rev - fees):,}")

st.info("Note: Calculations assume standard Indian CUF (Solar: 20%, Wind: 35%) and 2026 Registry Fees.")
