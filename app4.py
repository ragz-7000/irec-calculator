# --- 7. UPGRADED EXECUTIVE PDF EXPORT ---
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    
    # Header Banner
    pdf.set_fill_color(30, 144, 255)  # Dodger Blue
    pdf.rect(0, 0, 210, 40, 'F')
    pdf.set_text_color(255, 255, 255)
    pdf.set_font("Arial", "B", 24)
    pdf.cell(0, 20, "EXECUTIVE PROPOSAL", ln=True, align='C')
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"I-REC Commercial Valuation: {proj_name}", ln=True, align='C')
    
    pdf.ln(20)
    pdf.set_text_color(0, 0, 0)
    
    # Project Summary Section
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, "  PROJECT SUMMARY", ln=True, fill=True)
    pdf.set_font("Arial", "", 11)
    pdf.ln(2)
    pdf.cell(95, 8, f"Project Name: {proj_name}")
    pdf.cell(95, 8, f"Total Capacity: {solar_mw + wind_mw} MW", ln=True)
    pdf.cell(95, 8, f"Annual I-REC Volume: {int(total_irecs):,} Units")
    pdf.cell(95, 8, f"Sale Price: USD {irec_price_usd:.2f} (INR {irec_price_inr:.2f})", ln=True)
    
    pdf.ln(10)
    
    # Financial Breakdown Table
    pdf.set_font("Arial", "B", 12)
    pdf.set_fill_color(230, 230, 230)
    pdf.cell(0, 10, "  FINANCIAL BREAKDOWN (ANNUAL)", ln=True, fill=True)
    pdf.set_font("Arial", "B", 10)
    
    # Table Headers
    pdf.cell(130, 10, "Description", border=1)
    pdf.cell(60, 10, "Amount (INR)", border=1, ln=True, align='C')
    
    # Table Rows
    pdf.set_font("Arial", "", 10)
    pdf.cell(130, 10, "Estimated Gross Revenue", border=1)
    pdf.cell(60, 10, f"Rs. {int(gross_revenue):,}", border=1, ln=True, align='R')
    
    pdf.cell(130, 10, "Total Regulatory & Operating Costs", border=1)
    pdf.cell(60, 10, f"Rs. {int(total_op_costs):,}", border=1, ln=True, align='R')
    
    pdf.cell(130, 10, f"Triara CAP Success Fee ({fee_pct}%)", border=1)
    pdf.cell(60, 10, f"Rs. {int(my_fee):,}", border=1, ln=True, align='R')
    
    # Total Highlight
    pdf.set_font("Arial", "B", 11)
    pdf.set_fill_color(46, 204, 113) # Success Green
    pdf.cell(130, 12, "NET ANNUAL PROFIT TO CLIENT", border=1, fill=True)
    pdf.cell(60, 12, f"Rs. {int(client_net_profit):,}", border=1, fill=True, ln=True, align='R')
    
    pdf.ln(15)
    
    # Strategic Note
    pdf.set_font("Arial", "I", 9)
    pdf.set_text_color(100, 100, 100)
    note = (f"This valuation is prepared for Aditya Birla Renewables. It assumes an exchange rate of 1 USD = {USD_TO_INR} INR. "
            "All registry fees are based on I-TRACK/ICX 2026 standards.")
    pdf.multi_cell(0, 5, note)
    
    return bytes(pdf.output())
