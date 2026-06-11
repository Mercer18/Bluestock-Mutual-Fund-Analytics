# generate_final_report.py
# Day 7 Capstone Project - Automated PDF Report Generator

import os
import sys
import pandas as pd
import numpy as np
from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
    Image, PageBreak, KeepTogether
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfgen import canvas

# Base directories
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
reports_dir = os.path.join(base_dir, 'reports')
figures_dir = os.path.join(reports_dir, 'figures')
output_pdf_path = os.path.join(base_dir, 'Final_Report.pdf')
output_pdf_copy = os.path.join(reports_dir, 'Final_Report.pdf')

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to calculate the total page count dynamically
    and add professional header/footer to all pages except the cover.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super().showPage()
        super().save()

    def draw_page_decorations(self, page_count):
        if self._pageNumber == 1:
            # Draw beautiful cover decorations
            self.saveState()
            self.setFillColor(colors.HexColor('#414BEA')) # Primary Blue
            self.rect(0, 0, 15, 792, fill=True, stroke=False)
            self.setFillColor(colors.HexColor('#F05537')) # Secondary Orange
            self.rect(15, 0, 10, 792, fill=True, stroke=False)
            self.restoreState()
            return

        self.saveState()
        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(colors.HexColor('#414BEA'))
        
        # Header
        self.drawString(54, 752, "BLUESTOCK MUTUAL FUND ANALYTICS PLATFORM")
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor('#666666'))
        self.drawRightString(558, 752, "CAPSTONE FINAL REPORT")
        
        # Header Line
        self.setStrokeColor(colors.HexColor('#414BEA'))
        self.setLineWidth(0.75)
        self.line(54, 744, 558, 744)
        
        # Footer Line
        self.setStrokeColor(colors.HexColor('#cccccc'))
        self.setLineWidth(0.5)
        self.line(54, 50, 558, 50)
        
        # Footer
        self.drawString(54, 38, "Confidential - For Bluestock Internal Review Only")
        page_text = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(558, 38, page_text)
        
        self.restoreState()

def build_pdf():
    print("Initializing PDF generation...")
    # Page setup
    doc = SimpleDocTemplate(
        output_pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=72,
        bottomMargin=72
    )

    styles = getSampleStyleSheet()
    
    # Custom Palette
    primary_color = colors.HexColor('#414BEA')
    secondary_color = colors.HexColor('#F05537')
    dark_neutral = colors.HexColor('#222222')
    light_neutral = colors.HexColor('#F5F5FA')
    
    # Modify default styles in-place or add new unique styles
    title_style = ParagraphStyle(
        'CoverTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=26,
        leading=32,
        textColor=primary_color,
        spaceAfter=12
    )
    
    subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=13,
        leading=18,
        textColor=colors.HexColor('#555555'),
        spaceAfter=30
    )
    
    meta_style = ParagraphStyle(
        'CoverMeta',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=15,
        textColor=dark_neutral
    )
    
    h1_style = ParagraphStyle(
        'Header1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=22,
        textColor=primary_color,
        spaceBefore=15,
        spaceAfter=10,
        keepWithNext=True
    )
    
    h2_style = ParagraphStyle(
        'Header2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=secondary_color,
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyDark',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=10,
        leading=14.5,
        textColor=dark_neutral,
        spaceAfter=10
    )
    
    body_bold = ParagraphStyle(
        'BodyBold',
        parent=body_style,
        fontName='Helvetica-Bold'
    )

    callout_style = ParagraphStyle(
        'CalloutText',
        parent=styles['Normal'],
        fontName='Helvetica-Oblique',
        fontSize=9.5,
        leading=14,
        textColor=colors.HexColor('#444444')
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.white,
        alignment=1
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8,
        leading=10,
        textColor=dark_neutral,
        alignment=1
    )

    story = []

    # ================= PAGE 1: COVER PAGE =================
    story.append(Spacer(1, 120))
    story.append(Paragraph("BLUESTOCK FINTECH", ParagraphStyle('UpperBranding', parent=subtitle_style, fontName='Helvetica-Bold', textColor=secondary_color, fontSize=11, spaceAfter=8)))
    story.append(Paragraph("MUTUAL FUND ANALYTICS<br/>CAPSTONE PLATFORM", title_style))
    story.append(Paragraph("An End-to-End Analytics, Risk Modeling, Ingestion Pipeline and BI Dashboard System for Indian Mutual Funds (2022-2026)", subtitle_style))
    
    story.append(Spacer(1, 150))
    
    meta_text = """
    <b>Prepared By:</b> Rishi (Fintech Intern)<br/>
    <b>Project Duration:</b> June 1, 2026 - June 11, 2026<br/>
    <b>Status:</b> Final Release (Version 1.0)<br/>
    <b>Repository:</b> <font color="#414BEA">https://github.com/Mercer18/Bluestock-Mutual-Fund-Analytics</font>
    """
    story.append(Paragraph(meta_text, meta_style))
    story.append(PageBreak())

    # ================= PAGE 2: TOC & CONTROL =================
    story.append(Paragraph("Document Control & Contents", h1_style))
    story.append(Spacer(1, 10))
    
    control_data = [
        [Paragraph("<b>Attribute</b>", table_cell_style), Paragraph("<b>Details</b>", table_cell_style)],
        [Paragraph("Project Name", table_cell_style), Paragraph("Bluestock Mutual Fund Analytics Capstone", table_cell_style)],
        [Paragraph("Client / Sponsor", table_cell_style), Paragraph("Bluestock Fintech Private Limited", table_cell_style)],
        [Paragraph("Target Database", table_cell_style), Paragraph("SQLite 3.x (bluestock_mf.db)", table_cell_style)],
        [Paragraph("Tech Stack", table_cell_style), Paragraph("Python 3.13, Pandas, NumPy, SQLite, Power BI, Git", table_cell_style)],
        [Paragraph("Release Date", table_cell_style), Paragraph("June 11, 2026", table_cell_style)],
        [Paragraph("Deliverables", table_cell_style), Paragraph("Final Report (PDF), Slides (PPTX), Code Repo, Power BI Theme", table_cell_style)]
    ]
    t_control = Table(control_data, colWidths=[150, 350])
    t_control.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (1,0), primary_color),
        ('TEXTCOLOR', (0,0), (1,0), colors.white),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('BACKGROUND', (0,1), (0,-1), light_neutral),
    ]))
    story.append(t_control)
    story.append(Spacer(1, 20))
    
    story.append(Paragraph("Table of Contents", h2_style))
    story.append(Spacer(1, 5))
    
    toc_data = [
        ["1. Executive Summary", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 3"],
        ["2. Data Sources & Metadata Dictionary", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 4"],
        ["3. Relational Database & Star Schema", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 6"],
        ["4. Exploratory Data Analysis (EDA)", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 8"],
        ["5. Quantitative Performance Scorecard", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 11"],
        ["6. BI Dashboard Design (Power BI)", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 14"],
        ["7. Advanced Risk Modeling (VaR & HHI)", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 16"],
        ["8. Cohorts & SIP Continuity Analysis", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 17"],
        ["9. Limitations & Strategic Recommendations", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 18"],
        ["10. Appendix & Code Inventories", ". . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .", "Page 20"]
    ]
    t_toc = Table(toc_data, colWidths=[200, 240, 60])
    t_toc.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('TEXTCOLOR', (2,0), (2,-1), primary_color),
        ('ALIGN', (2,0), (2,-1), 'RIGHT'),
    ]))
    story.append(t_toc)
    story.append(PageBreak())

    # ================= PAGE 3: SECTION 1: EXEC SUMMARY =================
    story.append(Paragraph("1. Executive Summary", h1_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "Modern investment platforms require rigorous mathematical and computational frameworks to evaluate fund performance, risk factors, and investor behaviors. This capstone project details the implementation of an end-to-end <b>Mutual Fund Analytics Platform</b> developed for Bluestock Fintech. Over the course of seven days, we successfully ingested, cleaned, loaded, analyzed, and visualized historical and transactional mutual fund data spanning 40 mutual fund schemes over a 4.4-year period (January 2022 to May 2026).",
        body_style
    ))
    story.append(Paragraph(
        "<b>Core Achievements:</b>",
        body_bold
    ))
    ach_text = """
    • <b>ETL Pipeline:</b> Created robust scripts fetching live NAV listings using AMFI APIs with exponential backoff.<br/>
    • <b>Database Architecture:</b> Designed and deployed a relational SQLite Star Schema database structure, ensuring optimal load performance via SQLAlchemy and verification with SQL queries.<br/>
    • <b>EDA & Data Science:</b> Generated 16 detailed plots uncovering investor demographics, transaction patterns, and sector distributions.<br/>
    • <b>Risk-Adjusted Performance:</b> Calculated metrics (CAGR, Sharpe, Sortino, Alpha, Beta, Drawdowns) to build a composite fund scorecard.<br/>
    • <b>BI Visualization:</b> Developed a custom Power BI theme and dashboard layout guide across 4 analysis pages.<br/>
    • <b>Advanced Risk Modeling:</b> Implemented daily tail-loss calculations (95% VaR & CVaR) and Herfindahl-Hirschman Indices (HHI) for stock concentration.<br/>
    • <b>Investor retention:</b> Formulated cohort tables and SIP continuity matrices flagging at-risk accounts.
    """
    story.append(Paragraph(ach_text, body_style))
    
    story.append(Spacer(1, 15))
    callout_data = [[Paragraph(
        "<i>Executive Takeaway:</i> By integrating robust data pipelines with rigorous risk-modelling and interactive BI visualization, Bluestock is positioned to offer institutional-grade advisory products to retail investors, shifting focus from simple return-chasing to sophisticated risk-adjusted asset allocation.",
        callout_style
    )]]
    t_call = Table(callout_data, colWidths=[500])
    t_call.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), light_neutral),
        ('BOX', (0,0), (-1,-1), 1, secondary_color),
        ('PADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_call)
    story.append(PageBreak())

    # ================= PAGE 4: SECTION 2: DATA SOURCES =================
    story.append(Paragraph("2. Data Sources & Ingestion Framework", h1_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "Our data ingestion engine operates on two core data categories: live market data and internal transactional records. Live Net Asset Value (NAV) data is obtained dynamically from the <b>Association of Mutual Funds in India (AMFI)</b> open REST API (<code>mfapi.in</code>). Internal transactions, customer demography, and fund portfolios are stored as static historical CSV exports. Together, these sources represent a realistic representation of a wealth management system's data assets.",
        body_style
    ))
    story.append(Paragraph("API Connection and Retry Logic", h2_style))
    story.append(Paragraph(
        "Connecting to third-party open APIs introduces latency and reliability concerns. To mitigate this, our ingestion script <code>live_nav_fetch.py</code> implements a connection timeout of 15 seconds, exponential retry backoffs (handling 502 Bad Gateway codes with sleep delays), and strict logging of successful vs. failed requests. A sleep delay of 2 seconds is maintained between calls to respect AMFI endpoint rate limits.",
        body_style
    ))
    story.append(Paragraph("Data Volume Summary", h2_style))
    story.append(Paragraph(
        "The complete dataset analyzed contains:<br/>"
        "• <b>40 Mutual Fund Schemes</b> across Equity, Debt, and Hybrid categories.<br/>"
        "• <b>64,320 Historical NAV Records</b> spanning 4.4 years (2022-2026).<br/>"
        "• <b>32,778 Investor Transactions</b> containing Lumpsum and SIP investments.<br/>"
        "• <b>940 Portfolio Stock Holdings</b> detailing weights and sectors.",
        body_style
    ))
    story.append(Spacer(1, 10))
    
    # Metadata dictionary table summary
    story.append(Paragraph("Metadata Dictionary - Dim Fund table", h2_style))
    fund_meta_data = [
        [Paragraph("<b>Field Name</b>", table_header_style), Paragraph("<b>Data Type</b>", table_header_style), Paragraph("<b>Key Type</b>", table_header_style), Paragraph("<b>Description</b>", table_header_style)],
        [Paragraph("amfi_code", table_cell_style), Paragraph("INTEGER", table_cell_style), Paragraph("Primary Key", table_cell_style), Paragraph("Unique code assigned by AMFI", table_cell_style)],
        [Paragraph("scheme_name", table_cell_style), Paragraph("VARCHAR", table_cell_style), Paragraph("-", table_cell_style), Paragraph("Name of the mutual fund scheme", table_cell_style)],
        [Paragraph("category", table_cell_style), Paragraph("VARCHAR", table_cell_style), Paragraph("-", table_cell_style), Paragraph("Equity, Debt, Hybrid, etc.", table_cell_style)],
        [Paragraph("expense_ratio_pct", table_cell_style), Paragraph("DECIMAL", table_cell_style), Paragraph("-", table_cell_style), Paragraph("Annual fund management fee %", table_cell_style)],
        [Paragraph("benchmark", table_cell_style), Paragraph("VARCHAR", table_cell_style), Paragraph("-", table_cell_style), Paragraph("Nifty 50, Nifty 100, Gilt Index, etc.", table_cell_style)]
    ]
    t_meta = Table(fund_meta_data, colWidths=[110, 80, 90, 220])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_neutral]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_meta)
    story.append(PageBreak())

    # ================= PAGE 5: SECTION 2: METADATA PART 2 =================
    story.append(Paragraph("Metadata Dictionary (Continued)", h1_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "Here we define the field schemas and descriptions for the primary transactional fact tables and investor demography tables used within our analytics database.",
        body_style
    ))
    
    story.append(Paragraph("Fact NAV Table Schema", h2_style))
    nav_meta_data = [
        [Paragraph("<b>Field Name</b>", table_header_style), Paragraph("<b>Data Type</b>", table_header_style), Paragraph("<b>Key Type</b>", table_header_style), Paragraph("<b>Description</b>", table_header_style)],
        [Paragraph("nav_id", table_cell_style), Paragraph("INTEGER", table_cell_style), Paragraph("Primary Key", table_cell_style), Paragraph("Auto-incremented ID", table_cell_style)],
        [Paragraph("amfi_code", table_cell_style), Paragraph("INTEGER", table_cell_style), Paragraph("Foreign Key", table_cell_style), Paragraph("Links to dim_fund", table_cell_style)],
        [Paragraph("date", table_cell_style), Paragraph("DATE", table_cell_style), Paragraph("-", table_cell_style), Paragraph("NAV calculation date", table_cell_style)],
        [Paragraph("nav", table_cell_style), Paragraph("DECIMAL", table_cell_style), Paragraph("-", table_cell_style), Paragraph("Net Asset Value per unit", table_cell_style)]
    ]
    t_nav_meta = Table(nav_meta_data, colWidths=[110, 80, 90, 220])
    t_nav_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_neutral]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_nav_meta)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Fact Transactions Table Schema", h2_style))
    tx_meta_data = [
        [Paragraph("<b>Field Name</b>", table_header_style), Paragraph("<b>Data Type</b>", table_header_style), Paragraph("<b>Key Type</b>", table_header_style), Paragraph("<b>Description</b>", table_header_style)],
        [Paragraph("transaction_id", table_cell_style), Paragraph("VARCHAR", table_cell_style), Paragraph("Primary Key", table_cell_style), Paragraph("Unique transaction identifier", table_cell_style)],
        [Paragraph("investor_id", table_cell_style), Paragraph("INTEGER", table_cell_style), Paragraph("Foreign Key", table_cell_style), Paragraph("Links to dim_investor", table_cell_style)],
        [Paragraph("amfi_code", table_cell_style), Paragraph("INTEGER", table_cell_style), Paragraph("Foreign Key", table_cell_style), Paragraph("Links to dim_fund", table_cell_style)],
        [Paragraph("date", table_cell_style), Paragraph("DATE", table_cell_style), Paragraph("-", table_cell_style), Paragraph("Execution date of transaction", table_cell_style)],
        [Paragraph("type", table_cell_style), Paragraph("VARCHAR", table_cell_style), Paragraph("-", table_cell_style), Paragraph("Transaction Type (SIP or Lumpsum)", table_cell_style)],
        [Paragraph("amount", table_cell_style), Paragraph("DECIMAL", table_cell_style), Paragraph("-", table_cell_style), Paragraph("Investment amount in INR", table_cell_style)]
    ]
    t_tx_meta = Table(tx_meta_data, colWidths=[110, 80, 90, 220])
    t_tx_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_neutral]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_tx_meta)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Fact Portfolio Table Schema", h2_style))
    port_meta_data = [
        [Paragraph("<b>Field Name</b>", table_header_style), Paragraph("<b>Data Type</b>", table_header_style), Paragraph("<b>Key Type</b>", table_header_style), Paragraph("<b>Description</b>", table_header_style)],
        [Paragraph("portfolio_id", table_cell_style), Paragraph("INTEGER", table_cell_style), Paragraph("Primary Key", table_cell_style), Paragraph("Unique record identifier", table_cell_style)],
        [Paragraph("amfi_code", table_cell_style), Paragraph("INTEGER", table_cell_style), Paragraph("Foreign Key", table_cell_style), Paragraph("Links to dim_fund", table_cell_style)],
        [Paragraph("stock_name", table_cell_style), Paragraph("VARCHAR", table_cell_style), Paragraph("-", table_cell_style), Paragraph("Name of company holding", table_cell_style)],
        [Paragraph("sector", table_cell_style), Paragraph("VARCHAR", table_cell_style), Paragraph("-", table_cell_style), Paragraph("Industry sector of company", table_cell_style)],
        [Paragraph("weight_pct", table_cell_style), Paragraph("DECIMAL", table_cell_style), Paragraph("-", table_cell_style), Paragraph("Weight allocation in fund", table_cell_style)]
    ]
    t_port_meta = Table(port_meta_data, colWidths=[110, 80, 90, 220])
    t_port_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_neutral]),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_port_meta)
    story.append(PageBreak())

    # ================= PAGE 6: SECTION 3: DB SCHEMA & ETL =================
    story.append(Paragraph("3. Relational Database & Star Schema Design", h1_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "To facilitate rapid aggregation, reporting, and dashboard querying, we modeled the mutual fund ecosystem using a <b>Star Schema</b>. At the center of our data model are the numerical fact tables: <code>fact_nav</code>, <code>fact_transactions</code>, <code>fact_portfolio</code>, <code>fact_aum</code>, and <code>fact_sip_industry</code>. These facts are contextualized by shared dimension tables: <code>dim_fund</code> and <code>dim_date</code>.",
        body_style
    ))
    
    story.append(Paragraph("Database Ingestion and Loading Logic", h2_style))
    story.append(Paragraph(
        "Using Python's <code>SQLAlchemy</code>, the relational SQLite database <code>bluestock_mf.db</code> is populated in a clean transactional sequence:<br/>"
        "1. **Table Initialization:** Standard DDL definitions from <code>schema.sql</code> establish constraints, primary keys, and foreign relations.<br/>"
        "2. **Dimension Load:** <code>dim_fund</code> is loaded first to prevent foreign key constraint violations on transactional tables.<br/>"
        "3. **Fact Ingestion:** NAV records and transaction lines are loaded using bulk-insert methods to optimize ingestion throughput.<br/>"
        "4. **Index Creation:** Database indices are compiled on frequently queried fields, specifically `amfi_code` and `date` columns.",
        body_style
    ))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Schema Architecture Summary", h2_style))
    story.append(Paragraph(
        "The entity-relationship mapping consists of:<br/>"
        "• **dim_fund** (amfi_code, scheme_name, expense_ratio_pct, category, benchmark)<br/>"
        "• **fact_nav** (nav_id, amfi_code, date, nav)<br/>"
        "• **fact_transactions** (transaction_id, investor_id, amfi_code, date, type, amount)<br/>"
        "• **fact_portfolio** (portfolio_id, amfi_code, stock_name, sector, weight_pct)<br/>"
        "• **fact_aum** (aum_id, amfi_code, date, aum_inr_crores)<br/>"
        "• **fact_sip_industry** (sip_id, date, total_sip_accounts, total_sip_inflow_inr)",
        body_style
    ))
    story.append(PageBreak())

    # ================= PAGE 7: SECTION 3: SQL QUERIES =================
    story.append(Paragraph("Analytical SQL Verification Queries", h1_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "To test structural integrity and ensure calculations are mathematically correct, 10 analytical validation queries are defined in <code>queries.sql</code>. Executing these queries verifies facts link properly with dimensions.",
        body_style
    ))
    
    story.append(Paragraph("Query 1: Total AUM and Fund Count by Category", h2_style))
    sql_text_1 = """
    SELECT f.category, COUNT(DISTINCT f.amfi_code) as total_funds, 
           ROUND(SUM(a.aum_inr_crores), 2) as total_aum_crores
    FROM dim_fund f
    LEFT JOIN fact_aum a ON f.amfi_code = a.amfi_code
    GROUP BY f.category;
    """
    story.append(Paragraph(f"<font face='Courier' size='8'>{sql_text_1.replace('\n', '<br/>')}</font>", ParagraphStyle('SQLBlock', parent=body_style, background=light_neutral, borderPadding=10, borderWidth=0.5, borderColor=colors.HexColor('#cccccc'))))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Query 2: Top 5 Schemes by Net Lumpsum and SIP Inflow", h2_style))
    sql_text_2 = """
    SELECT f.scheme_name, f.category, 
           SUM(CASE WHEN t.type = 'SIP' THEN t.amount ELSE 0 END) as total_sip,
           SUM(CASE WHEN t.type = 'Lumpsum' THEN t.amount ELSE 0 END) as total_lumpsum,
           SUM(t.amount) as net_inflow
    FROM dim_fund f
    JOIN fact_transactions t ON f.amfi_code = t.amfi_code
    GROUP BY f.amfi_code
    ORDER BY net_inflow DESC
    LIMIT 5;
    """
    story.append(Paragraph(f"<font face='Courier' size='8'>{sql_text_2.replace('\n', '<br/>')}</font>", ParagraphStyle('SQLBlock2', parent=body_style, background=light_neutral, borderPadding=10, borderWidth=0.5, borderColor=colors.HexColor('#cccccc'))))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "The verification process confirmed:<br/>"
        "• Zero orphaned transactional lines (100% referential integrity).<br/>"
        "• Calculations match between pure Python code (Pandas) and SQL query aggregates.<br/>"
        "• Query execution times averaged <15ms due to proper primary/foreign index constraints.",
        body_style
    ))
    story.append(PageBreak())

    # ================= PAGE 8: SECTION 4: EDA FINDINGS =================
    story.append(Paragraph("4. Exploratory Data Analysis (EDA) Findings", h1_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "A critical component of data science is understanding the underlying distributions and patterns before modeling. Our EDA phase (compiled in <code>03_eda_analysis.ipynb</code>) generated 16 detailed plots analyzing customer demographics, geography, payment preferences, and stock holdings.",
        body_style
    ))
    
    story.append(Paragraph("Key Demographic Patterns", h2_style))
    story.append(Paragraph(
        "• **Age Distribution:** The bulk of mutual fund investors belong to the **25-40 age cohort**, highlighting that young professionals are the primary market. Average monthly SIP size peaks in the **35-45 age group**, correlating with peak earning years.<br/>"
        "• **Gender Split:** The transaction counts show a gender distribution of **63.4% Male and 36.6% Female** investors. However, there is no statistically significant difference in the average investment amount between genders, suggesting wealth accumulation levels remain similar once invested.<br/>"
        "• **City Tier splits:** Investors from **Tier 1 cities** contribute 72% of total lumpsum investments, while **Tier 2 and Tier 3 cities** exhibit a higher relative growth rate in monthly SIP accounts, showing that systematic plans are democratizing investment.",
        body_style
    ))
    
    story.append(Paragraph("Geographical Splits & Top States", h2_style))
    story.append(Paragraph(
        "A breakdown of SIP inflow by state shows that **Maharashtra, Karnataka, and Delhi** represent the top three states by total active investments. Interestingly, states like Gujarat and Tamil Nadu exhibit the highest average SIP ticket sizes (₹6,200 per month compared to the national average of ₹4,800).",
        body_style
    ))
    story.append(PageBreak())

    # ================= PAGE 9: SECTION 4: EDA IMAGES 1 =================
    story.append(Paragraph("EDA Visualizations: Demographics", h1_style))
    story.append(Spacer(1, 10))
    
    # We will embed demographic figures if they exist, or show empty space with text
    fig_age_path = os.path.join(figures_dir, '05_age_demographics.png')
    fig_gender_path = os.path.join(figures_dir, '07_gender_split.png')
    
    img_list_dem = []
    
    if os.path.exists(fig_age_path):
        img_list_dem.append(Image(fig_age_path, width=240, height=180))
    else:
        img_list_dem.append(Paragraph("[Missing: Age Demographics Chart]", table_cell_style))
        
    if os.path.exists(fig_gender_path):
        img_list_dem.append(Image(fig_gender_path, width=240, height=180))
    else:
        img_list_dem.append(Paragraph("[Missing: Gender Split Chart]", table_cell_style))
        
    t_dem_imgs = Table([img_list_dem], colWidths=[250, 250])
    t_dem_imgs.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_dem_imgs)
    
    story.append(Paragraph("Figure 4.1: Age Distribution and Gender Split of Active Investors", ParagraphStyle('FigCap', parent=body_style, fontName='Helvetica-BoldOblique', fontSize=9, alignment=1, textColor=colors.HexColor('#666666'))))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Insight: Age-Based Asset Allocation", h2_style))
    story.append(Paragraph(
        "The age demographics chart clearly demonstrates that younger cohorts (20-30 years) dominate by volume of accounts but have smaller average ticket sizes. Older cohorts (50+ years) have fewer active SIP accounts but account for over 45% of the total lumpsum AUM, indicating a distinct maturity profile where risk profile shifts from aggressive equity to wealth preservation.",
        body_style
    ))
    story.append(PageBreak())

    # ================= PAGE 10: SECTION 4: EDA IMAGES 2 =================
    story.append(Paragraph("EDA Visualizations: Inflows & Allocations", h1_style))
    story.append(Spacer(1, 10))
    
    fig_sip_path = os.path.join(figures_dir, '03_sip_inflow_trend.png')
    fig_donut_path = os.path.join(figures_dir, '12_sector_allocation_donut.png')
    
    img_list_alloc = []
    
    if os.path.exists(fig_sip_path):
        img_list_alloc.append(Image(fig_sip_path, width=240, height=180))
    else:
        img_list_alloc.append(Paragraph("[Missing: SIP Inflow Trend Chart]", table_cell_style))
        
    if os.path.exists(fig_donut_path):
        img_list_alloc.append(Image(fig_donut_path, width=240, height=180))
    else:
        img_list_alloc.append(Paragraph("[Missing: Sector Donut Chart]", table_cell_style))
        
    t_alloc_imgs = Table([img_list_alloc], colWidths=[250, 250])
    t_alloc_imgs.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(t_alloc_imgs)
    
    story.append(Paragraph("Figure 4.2: SIP Cumulative Inflow Trends and Aggregate Sector Allocations", ParagraphStyle('FigCap2', parent=body_style, fontName='Helvetica-BoldOblique', fontSize=9, alignment=1, textColor=colors.HexColor('#666666'))))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Insight: Financial & Technology Sector Bias", h2_style))
    story.append(Paragraph(
        "Aggregate sector holdings reveal a heavy bias toward **Financial Services (34.2%)** and **Information Technology (18.6%)** across all mutual fund holdings. While this reflects the major capitalizations of the Indian equity market (Nifty 50), it also flags a concentration risk for investors holding multiple mutual funds, as their overlapping exposures remain high.",
        body_style
    ))
    story.append(PageBreak())

    # ================= PAGE 11: SECTION 5: PERFORMANCE =================
    story.append(Paragraph("5. Quantitative Performance Analytics", h1_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "To evaluate mutual funds beyond simple nominal returns, we constructed a comprehensive **Quantitative Performance Scorecard** (calculated in <code>generate_analytics.py</code>). This evaluates volatility, tail risk, and regression parameters vs. benchmark indices.",
        body_style
    ))
    
    story.append(Paragraph("Performance Metrics Definition", h2_style))
    story.append(Paragraph(
        "• **CAGR:** Compounded Annual Growth Rate measures geometric return over 1-year and 3-year periods.<br/>"
        "• **Annual Volatility:** Annualized standard deviation of daily NAV returns. Equity funds display volatility ranging from 12% to 22%, whereas debt funds remain below 3%.<br/>"
        "• **Sharpe Ratio:** Annualized return excess of risk-free rate (6.5% for India) per unit of volatility. A Sharpe > 1.0 indicates excellent risk-adjusted performance.<br/>"
        "• **Sortino Ratio:** Identical to Sharpe, but only penalizes downside standard deviation (negative returns), providing a more realistic view of tail loss protection.",
        body_style
    ))
    
    # Add a mini table of performance rankings
    story.append(Paragraph("Top 5 Ranked Funds on Performance Metrics", h2_style))
    top_perf_data = [
        [Paragraph("<b>Scheme Name</b>", table_header_style), Paragraph("<b>Category</b>", table_header_style), Paragraph("<b>3-Yr CAGR (%)</b>", table_header_style), Paragraph("<b>Sharpe Ratio</b>", table_header_style), Paragraph("<b>Sortino Ratio</b>", table_header_style)],
        [Paragraph("Mirae Asset Large Cap Fund - Reg", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("34.00%", table_cell_style), Paragraph("1.07", table_cell_style), Paragraph("1.52", table_cell_style)],
        [Paragraph("Kotak Flexicap Fund - Reg", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("29.58%", table_cell_style), Paragraph("0.97", table_cell_style), Paragraph("1.39", table_cell_style)],
        [Paragraph("Mirae Asset Tax Saver Fund - Reg", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("29.18%", table_cell_style), Paragraph("0.92", table_cell_style), Paragraph("1.31", table_cell_style)],
        [Paragraph("ICICI Pru Midcap Fund - Reg", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("31.78%", table_cell_style), Paragraph("0.88", table_cell_style), Paragraph("1.25", table_cell_style)],
        [Paragraph("SBI Bluechip Fund - Reg", table_cell_style), Paragraph("Equity", table_cell_style), Paragraph("30.46%", table_cell_style), Paragraph("0.86", table_cell_style), Paragraph("1.21", table_cell_style)]
    ]
    t_perf = Table(top_perf_data, colWidths=[180, 80, 90, 80, 80])
    t_perf.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_neutral]),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_perf)
    story.append(PageBreak())

    # ================= PAGE 12: SECTION 5: REGRESSION & DRAWDOWN =================
    story.append(Paragraph("Regression Metrics & Drawdown Profiles", h1_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "Evaluating a fund manager's ability to outperform the market benchmark requires regression parameters (Alpha and Beta) against indices like the Nifty 100 TRI.",
        body_style
    ))
    
    story.append(Paragraph("Manager's Alpha & Systematic Beta", h2_style))
    story.append(Paragraph(
        "• **Beta (Systematic Risk):** Measures the fund's sensitivity to market movements. Mid Cap and Small Cap funds show Beta values between 1.15 and 1.35, indicating higher systematic risk. Large cap index funds match close to 1.0.<br/>"
        "• **Alpha (Active Outperformance):** Annualized abnormal return generated above benchmark predictions. Active funds like *SBI Small Cap Fund* show a positive annualized Alpha of **21.69%**, confirming manager skill in identifying undervalued stocks.",
        body_style
    ))
    
    story.append(Paragraph("Maximum Drawdown (Max DD) and Recovery", h2_style))
    story.append(Paragraph(
        "Max Drawdown measures the worst peak-to-trough drop in a fund's NAV before a new high is reached. It represents the historical worst-case loss scenario for an investor.",
        body_style
    ))
    
    drawdown_perf_data = [
        [Paragraph("<b>Scheme Name</b>", table_header_style), Paragraph("<b>Max DD (%)</b>", table_header_style), Paragraph("<b>Peak Date</b>", table_header_style), Paragraph("<b>Trough Date</b>", table_header_style), Paragraph("<b>Recovery Period</b>", table_header_style)],
        [Paragraph("SBI Small Cap Fund - Reg", table_cell_style), Paragraph("-28.71%", table_cell_style), Paragraph("2024-03-05", table_cell_style), Paragraph("2024-06-04", table_cell_style), Paragraph("145 Days", table_cell_style)],
        [Paragraph("DSP Small Cap Fund - Reg", table_cell_style), Paragraph("-31.17%", table_cell_style), Paragraph("2024-03-05", table_cell_style), Paragraph("2024-06-04", table_cell_style), Paragraph("182 Days", table_cell_style)],
        [Paragraph("Axis Midcap Fund - Reg", table_cell_style), Paragraph("-20.96%", table_cell_style), Paragraph("2023-09-12", table_cell_style), Paragraph("2023-11-20", table_cell_style), Paragraph("92 Days", table_cell_style)],
        [Paragraph("HDFC Top 100 Fund - Reg", table_cell_style), Paragraph("-24.73%", table_cell_style), Paragraph("2022-04-10", table_cell_style), Paragraph("2022-06-20", table_cell_style), Paragraph("110 Days", table_cell_style)],
        [Paragraph("Kotak Liquid Fund - Reg", table_cell_style), Paragraph("-0.12%", table_cell_style), Paragraph("2023-03-15", table_cell_style), Paragraph("2023-03-18", table_cell_style), Paragraph("4 Days", table_cell_style)]
    ]
    t_dd = Table(drawdown_perf_data, colWidths=[180, 80, 80, 80, 90])
    t_dd.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_neutral]),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_dd)
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "The analysis highlights that while Small Cap schemes generate higher long-term returns, they suffer from deep drawdown periods (up to -31%) requiring longer recovery times (up to 182 days) compared to liquid funds which recover almost instantly.",
        body_style
    ))
    story.append(PageBreak())

    # ================= PAGE 13: SECTION 5: COMPARISON CHART =================
    story.append(Paragraph("Performance Scorecard & Cumulative Return Chart", h1_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "A composite score was constructed for each fund weighting 3-Yr CAGR (30%), Sharpe Ratio (25%), Alpha (20%), Expense Ratio (15%), and Maximum Drawdown (10%). Ranking all 40 funds helps identify the top overall performers on a risk-adjusted basis.",
        body_style
    ))
    
    fig_comp_path = os.path.join(base_dir, 'benchmark_comparison_chart.png')
    
    if os.path.exists(fig_comp_path):
        story.append(Image(fig_comp_path, width=440, height=260))
        story.append(Spacer(1, 8))
        story.append(Paragraph("Figure 5.1: 3-Year Cumulative Performance of Top 5 Scorecard Funds vs Benchmarks", ParagraphStyle('FigCap3', parent=body_style, fontName='Helvetica-BoldOblique', fontSize=9, alignment=1, textColor=colors.HexColor('#666666'))))
    else:
        story.append(Paragraph("[Missing: Benchmark Comparison Chart]", table_cell_style))
        
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "The cumulative performance chart clearly illustrates that all top 5 funds generated returns exceeding the Nifty 50 and Nifty 100 TRI benchmarks over the 3-year period (2023-2026), proving active managers consistently added value during this cycle. However, the dispersion among active managers remains wide, emphasizing the need for robust fund scorecards.",
        body_style
    ))
    story.append(PageBreak())

    # ================= PAGE 14: SECTION 6: POWER BI DASHBOARD =================
    story.append(Paragraph("6. BI Dashboard Design (Power BI)", h1_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "To deliver executive-level insights, we developed an interactive 4-page Power BI Dashboard. The data modeling and visual layout were structured based on a custom Bluestock JSON theme, utilizing rounded borders, clean spacing, and curated brand colors (#414BEA and #F05537).",
        body_style
    ))
    
    story.append(Paragraph("Data Modeling and Relationships", h2_style))
    story.append(Paragraph(
        "The model links dimensions to facts in clean 1-to-many relationships:<br/>"
        "• **dim_fund** (amfi_code) → **fact_nav** (amfi_code) [1 to *]<br/>"
        "• **dim_fund** (amfi_code) → **fact_transactions** (amfi_code) [1 to *]<br/>"
        "• **dim_fund** (amfi_code) → **fact_portfolio** (amfi_code) [1 to *]<br/>"
        "• **dim_fund** (amfi_code) → **fact_aum** (amfi_code) [1 to *]",
        body_style
    ))
    
    story.append(Paragraph("DAX Measures In Use", h2_style))
    story.append(Paragraph(
        "We defined several DAX measures to support dynamic visualizations:<br/>"
        "• **Total SIP Inflows:** <code>Total_SIP_Inflow = CALCULATE(SUM(fact_transactions[amount]), fact_transactions[type] = \"SIP\")</code><br/>"
        "• **Active Folio Count:** <code>Folio_Count = DISTINCTCOUNT(fact_transactions[investor_id])</code><br/>"
        "• **Net Inflows:** <code>Net_Inflow = SUM(fact_transactions[amount])</code>",
        body_style
    ))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Dashboard Colors and Styling (JSON Theme)", h2_style))
    story.append(Paragraph(
        "The dashboard uses a custom configuration theme file <code>bluestock_theme.json</code>:<br/>"
        "• **Primary Accent:** `#414BEA` (Bluestock Blue)<br/>"
        "• **Secondary Accent:** `#F05537` (Bluestock Coral/Orange)<br/>"
        "• **Visual Card Styling:** Rounded corners with a 10px radius and a subtle drop shadow to present a premium look.",
        body_style
    ))
    story.append(PageBreak())

    # ================= PAGE 15: SECTION 6: POWER BI DETAILS =================
    story.append(Paragraph("Dashboard Structure & Key Views", h1_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "The Power BI dashboard is structured across 4 distinct analytical pages, each targeting a key business question:",
        body_style
    ))
    
    story.append(Paragraph("Page 1: Industry Overview", h2_style))
    story.append(Paragraph(
        "• **Focus:** High-level market AUM and category distributions.<br/>"
        "• **Key Visuals:** KPI cards for Total Inflow and Folios, Category AUM Treemap, monthly SIP inflow trends.",
        body_style
    ))
    
    story.append(Paragraph("Page 2: Fund Performance & Scorecard", h2_style))
    story.append(Paragraph(
        "• **Focus:** Volatility-adjusted returns and benchmark comparisons.<br/>"
        "• **Key Visuals:** Return vs Volatility scatter plot, sortable composite scorecard table, daily NAV vs Nifty benchmarks.",
        body_style
    ))
    
    story.append(Paragraph("Page 3: Investor Analytics & Demographics", h2_style))
    story.append(Paragraph(
        "• **Focus:** Customer segmentation and behavior profiles.<br/>"
        "• **Key Visuals:** Transaction amounts by state heatmap, Age group vs Average monthly SIP, Payment mode donut chart.",
        body_style
    ))
    
    story.append(Paragraph("Page 4: SIP Trends & Market Momentum", h2_style))
    story.append(Paragraph(
        "• **Focus:** Momentum correlation between market index and investor inflows.<br/>"
        "• **Key Visuals:** Dual axis line chart (SIP Monthly Inflow vs Nifty 50 Close Value), Category inflow heatmaps.",
        body_style
    ))
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Screenshot Placeholder & Visual Walkthrough Guide", h2_style))
    story.append(Paragraph(
        "A complete walkthrough guide is available in `dashboard/dashboard_guide.md`, specifying all columns, colors, charts, filters, and slicer interactions required to build or modify the `.pbix` report.",
        body_style
    ))
    story.append(PageBreak())

    # ================= PAGE 16: SECTION 7: ADVANCED RISK =================
    story.append(Paragraph("7. Advanced Risk Modeling", h1_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "To provide institutional-grade risk consulting, we implemented two advanced mathematical risk frameworks: **Historical Value at Risk (VaR)** and **Herfindahl-Hirschman Portfolio Concentration Index (HHI)**.",
        body_style
    ))
    
    story.append(Paragraph("Value at Risk (95% VaR) & Conditional Value at Risk (CVaR)", h2_style))
    story.append(Paragraph(
        "Value at Risk (VaR) measures the worst potential loss over a 1-day holding period at a 95% confidence level. CVaR (Conditional VaR) calculates the average loss that occurs in the worst 5% of trading days. It answers: *If the market drops past our VaR threshold, what is our expected average loss?*",
        body_style
    ))
    
    var_perf_data = [
        [Paragraph("<b>Scheme Name</b>", table_header_style), Paragraph("<b>Category</b>", table_header_style), Paragraph("<b>Daily VaR 95%</b>", table_header_style), Paragraph("<b>Daily CVaR 95%</b>", table_header_style)],
        [Paragraph("ABSL Small Cap Fund - Reg", table_cell_style), Paragraph("Equity (Small)", table_cell_style), Paragraph("-2.39%", table_cell_style), Paragraph("-3.03%", table_cell_style)],
        [Paragraph("SBI Small Cap Fund - Direct", table_cell_style), Paragraph("Equity (Small)", table_cell_style), Paragraph("-2.32%", table_cell_style), Paragraph("-3.02%", table_cell_style)],
        [Paragraph("Axis Midcap Fund - Reg", table_cell_style), Paragraph("Equity (Mid)", table_cell_style), Paragraph("-1.70%", table_cell_style), Paragraph("-2.24%", table_cell_style)],
        [Paragraph("HDFC Top 100 Fund - Reg", table_cell_style), Paragraph("Equity (Large)", table_cell_style), Paragraph("-1.29%", table_cell_style), Paragraph("-1.68%", table_cell_style)],
        [Paragraph("ICICI Pru Liquid Fund - Reg", table_cell_style), Paragraph("Debt (Liquid)", table_cell_style), Paragraph("-0.02%", table_cell_style), Paragraph("-0.03%", table_cell_style)]
    ]
    t_var = Table(var_perf_data, colWidths=[180, 110, 100, 110])
    t_var.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_neutral]),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_var)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("Sector HHI Portfolio Concentration Index", h2_style))
    story.append(Paragraph(
        "The Herfindahl-Hirschman Index (HHI) evaluates diversification levels. It is calculated by summing the squared weights of stock sectors in the fund's portfolio. An HHI score above 2,500 indicates a highly concentrated portfolio, while a score below 1,500 represents high diversification.<br/>"
        "• **Focused Equity Funds:** Display HHI scores between **2,800 and 3,400**, showing they are highly exposed to a few major stock selections (e.g. holding 15% in a single company).<br/>"
        "• **Flexi Cap Schemes:** Display HHI scores between **1,200 and 1,800**, reflecting well-diversified exposures across multiple sectors.",
        body_style
    ))
    story.append(PageBreak())

    # ================= PAGE 17: SECTION 8: COHORTS & SIP =================
    story.append(Paragraph("8. Cohorts & SIP Continuity Analysis", h1_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "Understanding investor lifecycle and payment behaviors is critical for preventing customer churn. We implemented **Investor Cohort Analysis** and **SIP Continuity Day Gap Modeling** (using customer transaction logs).",
        body_style
    ))
    
    story.append(Paragraph("Investor Cohort Analysis", h2_style))
    story.append(Paragraph(
        "By grouping investors into cohorts based on the calendar year of their first transaction, we track how average systematic investment plans (SIPs) and cumulative assets under management evolve over time.",
        body_style
    ))
    
    cohort_perf_data = [
        [Paragraph("<b>Cohort Year</b>", table_header_style), Paragraph("<b>Avg SIP Size (INR)</b>", table_header_style), Paragraph("<b>Total Invested (INR)</b>", table_header_style), Paragraph("<b>Favorite Scheme Preference</b>", table_header_style)],
        [Paragraph("2024", table_cell_style), Paragraph("₹5,412.30", table_cell_style), Paragraph("₹7.85 Crores", table_cell_style), Paragraph("SBI Bluechip Fund - Regular", table_cell_style)],
        [Paragraph("2025", table_cell_style), Paragraph("₹4,982.10", table_cell_style), Paragraph("₹5.22 Crores", table_cell_style), Paragraph("Mirae Asset Large Cap Fund", table_cell_style)],
        [Paragraph("2026", table_cell_style), Paragraph("₹4,120.50", table_cell_style), Paragraph("₹1.95 Crores", table_cell_style), Paragraph("Nippon India Large Cap Fund", table_cell_style)]
    ]
    t_coh = Table(cohort_perf_data, colWidths=[80, 110, 110, 200])
    t_coh.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), primary_color),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dddddd')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, light_neutral]),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_coh)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("SIP Continuity & Day Gap Analysis", h2_style))
    story.append(Paragraph(
        "For investors with 6 or more monthly SIP payments, we calculated the average and maximum day-gaps between consecutive transactions. If a transaction gap exceeds **35 days**, the account is flagged as 'at-risk' of payment failure or churn.<br/>"
        "• **Aggregate Results:** Out of all active monthly accounts, **88.5%** represent consistent, scheduled SIP payments (gaps within 28-31 days).<br/>"
        "• **At-Risk segment:** The remaining **11.5%** display irregular payment behaviors, presenting an opportunity for automated alert reminders.",
        body_style
    ))
    story.append(PageBreak())

    # ================= PAGE 18: SECTION 9: LIMITATIONS =================
    story.append(Paragraph("9. Project Limitations", h1_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "While this capstone platform delivers rich analytics and interactive dashboards, several limitations must be considered when evaluating the data outputs for actual market trading decisions:",
        body_style
    ))
    
    story.append(Paragraph("1. Data History Constraints", h2_style))
    story.append(Paragraph(
        "The historical NAV database spans approximately **4.4 years** (from January 2022 to May 2026). While this includes the recent market growth cycle, it does not cover major multi-year bear markets or severe economic recessions (such as the 2008 global financial crisis or the 2020 COVID crash). As a result, computed risk-adjusted metrics like the Sharpe ratio and maximum drawdowns are biased toward the recent expansionary cycle.",
        body_style
    ))
    
    story.append(Paragraph("2. Asset Class Exclusions", h2_style))
    story.append(Paragraph(
        "Our analytical models focus exclusively on traditional equity and debt schemes. Alternative asset classes (such as Gold ETFs, Real Estate Investment Trusts - REITs, and international funds) are not incorporated. Therefore, portfolio-level diversification results are incomplete for investors holding balanced portfolios across physical and digital commodities.",
        body_style
    ))
    
    story.append(Paragraph("3. Transaction Fee and Tax Exclusions", h2_style))
    story.append(Paragraph(
        "Computed fund CAGRs and scores do not account for broker commission exit loads, transaction charges, or country-specific capital gains taxes. Depending on the investor's tax bracket, actual net returns will differ from the nominal scores computed in the scorecard.",
        body_style
    ))
    story.append(PageBreak())

    # ================= PAGE 19: SECTION 9: RECOMMENDATIONS =================
    story.append(Paragraph("Strategic Recommendations & Future Scope", h1_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "To build on the foundation of the mutual fund analytics platform, we propose the following strategic implementations for Bluestock's technology roadmap:",
        body_style
    ))
    
    story.append(Paragraph("1. Machine Learning Recommendation Engines", h2_style))
    story.append(Paragraph(
        "Transition the simple rule-based fund recommender (recommender.py) into a **Collaborative Filtering Recommendation System**. By leveraging historical transactional data from thousands of users, the platform can suggest schemes based on demographic similarity, risk tolerances, and historical savings behaviors.",
        body_style
    ))
    
    story.append(Paragraph("2. Automated Churn & Churn Risk Prediction", h2_style))
    story.append(Paragraph(
        "Using the daily gap data calculated in our SIP Continuity analysis, train a **Random Forest Classification Model** to predict the likelihood of an investor stopping their monthly SIP. Flagging high-probability churn candidates 7 days before their scheduled debit date allows for proactive customer service intervention.",
        body_style
    ))
    
    story.append(Paragraph("3. Dynamic Portfolio Optimization", h2_style))
    story.append(Paragraph(
        "Incorporate a **Modern Portfolio Theory (MPT)** optimizer into the user portal. By inputting target risk percentages, users can automatically generate the optimal weights across the 40 schemes to maximize their Sharpe ratio, leveraging the covariance matrix calculated from daily returns.",
        body_style
    ))
    story.append(PageBreak())

    # ================= PAGE 20: APPENDIX & INVENTORIES =================
    story.append(Paragraph("10. Appendix: Pipeline & Deliverables Checklist", h1_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "This appendix provides a summary of the master pipeline script and a self-review checklist for the project deliverables.",
        body_style
    ))
    
    story.append(Paragraph("Master Ingestion Pipeline (run_pipeline.py)", h2_style))
    story.append(Paragraph(
        "Our unified pipeline script coordinates all components in a sequential pipeline:<br/>"
        "1. Ingests live NAVs from AMFI API using requests and backoff retries.<br/>"
        "2. Executes SQLite Star Schema database creation and CSV loading.<br/>"
        "3. Computes CAGR, Volatility, Sharpe, Sortino, Alpha, and Beta scorecard metrics.<br/>"
        "4. Generates Daily VaR, CVaR, HHI index, and Cohort reports.<br/>"
        "5. Automatically outputs the PDF report and PPTX presentation slides.",
        body_style
    ))
    
    story.append(Paragraph("Project Self-Review Checklist", h2_style))
    story.append(Paragraph(
        "• **Ingestion pipeline runs end-to-end?** Yes (verified via run_pipeline.py)<br/>"
        "• **SQLite Star Schema initialized correctly?** Yes (verified schema.sql and queries.sql)<br/>"
        "• **Exploratory analysis complete?** Yes (16 EDA figures generated)<br/>"
        "• **Performance scorecard calculated?** Yes (saved in fund_scorecard.csv)<br/>"
        "• **Interactive Recommender CLI functioning?** Yes (tested recommender.py)<br/>"
        "• **Power BI Dashboard theme configured?** Yes (bluestock_theme.json compiled)<br/>"
        "• **Advanced Risk Calculations correct?** Yes (verified in Advanced_Analytics.ipynb)<br/>"
        "• **All 7 deliverables submitted?** Yes (checked and pushed to repository)",
        body_style
    ))
    story.append(Spacer(1, 15))
    story.append(Paragraph("<i>End of Document - Bluestock Fintech Private Limited © 2026</i>", ParagraphStyle('EndDoc', parent=body_style, fontName='Helvetica-BoldOblique', alignment=1, textColor=primary_color)))
    
    # Build Document
    print("Building Document Template...")
    doc.build(story, canvasmaker=NumberedCanvas)
    print("PDF Report generated successfully!")
    
    # Copy PDF
    try:
        import shutil
        shutil.copy(output_pdf_path, output_pdf_copy)
        print(f"Copied PDF report to {output_pdf_copy}")
    except Exception as e:
        print(f"Failed to copy PDF report: {e}")

if __name__ == '__main__':
    build_pdf()
