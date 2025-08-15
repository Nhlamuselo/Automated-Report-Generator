#!/usr/bin/env python3
"""
PDF Report Generator Module
Creates professional, branded PDF reports with charts, tables, and insights.
"""

import pandas as pd
from pathlib import Path
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing
from reportlab.graphics import renderPDF


class PDFReportGenerator:
    """Creates professional PDF business reports with comprehensive formatting."""

    def __init__(self, csv_path: str, output_path: str, logo_path: str = None):
        self.csv_path = csv_path
        self.output_path = output_path
        self.logo_path = logo_path
        self.data = pd.read_csv(csv_path)
        self.styles = getSampleStyleSheet()

    def generate(self):
        doc = SimpleDocTemplate(
            self.output_path, pagesize=A4,
            rightMargin=30, leftMargin=30,
            topMargin=30, bottomMargin=18
        )

        elements = []

        # Optional Logo
        if self.logo_path and Path(self.logo_path).exists():
            elements.append(Image(self.logo_path, width=100, height=50))
            elements.append(Spacer(1, 12))

        # Title
        title_style = ParagraphStyle(
            name="TitleStyle", fontSize=20,
            alignment=1, spaceAfter=20
        )
        elements.append(Paragraph("Weekly Business Report", title_style))

        # Date
        date_style = ParagraphStyle(name="DateStyle", fontSize=12, alignment=1)
        elements.append(Paragraph(f"Generated on {datetime.now().strftime('%Y-%m-%d')}", date_style))
        elements.append(Spacer(1, 12))

        # Table
        table_data = [list(self.data.columns)] + self.data.values.tolist()
        table = Table(table_data, repeatRows=1)
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#003366")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
            ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ]))
        elements.append(table)
        elements.append(Spacer(1, 20))

        # Chart
        drawing = Drawing(400, 200)
        chart = VerticalBarChart()
        chart.x = 50
        chart.y = 50
        chart.height = 125
        chart.width = 300
        chart.data = [list(self.data["Total_Sales"])]
        chart.categoryAxis.categoryNames = [
            f"W{i+1}" for i in range(len(self.data))
        ]
        chart.bars[0].fillColor = colors.HexColor("#336699")
        drawing.add(chart)
        elements.append(drawing)
        elements.append(Spacer(1, 20))

        # Summary
        total_sales = self.data["Total_Sales"].sum()
        avg_sales = self.data["Total_Sales"].mean()
        summary_text = f"""
        <b>Summary:</b><br/>
        Total Sales: ${total_sales:,.2f}<br/>
        Average Weekly Sales: ${avg_sales:,.2f}
        """
        elements.append(Paragraph(summary_text, self.styles["Normal"]))

        # Build PDF
        doc.build(elements)
        print(f"✅ PDF report generated: {self.output_path}")


if __name__ == "__main__":
    csv_path = "weekly_business_report.csv"
    output_path = "weekly_report.pdf"
    logo_path = "logo.png"  # Optional, replace with your file

    generator = PDFReportGenerator(csv_path, output_path, logo_path)
    generator.generate()
