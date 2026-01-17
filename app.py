from flask import Flask, render_template, request, send_file
from reportlab.platypus import SimpleDocTemplate, Table, Paragraph, TableStyle, Spacer
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import io
import json

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    try:
        data = request.json
        year = data.get('year')
        month = data.get('month')
        expenses = data.get('expenses', [])

        if not expenses:
            return {"error": "No expenses provided"}, 400

        # PDF Setup
        buffer = io.BytesIO()
        file_name = f"{month}_{year}_Expenses_Report.pdf"
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=30)
        styles = getSampleStyleSheet()
        elements = []

        # Styles
        title_style = ParagraphStyle(
            'ReportTitle',
            parent=styles['Heading1'],
            fontSize=26,
            fontName='Helvetica-Bold',
            spaceAfter=15,
            alignment=1, # Center
            textColor=colors.HexColor("#2c3e50")
        )
        
        subtitle_style = ParagraphStyle(
            'ReportSubtitle',
            parent=styles['Normal'],
            fontSize=14,
            fontName='Helvetica',
            spaceAfter=40,
            alignment=1,
            textColor=colors.HexColor("#7f8c8d")
        )

        elements.append(Paragraph(f"{month} Expenses Report", title_style))
        elements.append(Paragraph(f"Year: {year} | Generated On: {datetime.now().strftime('%d-%m-%Y')}", subtitle_style))

        # Table Data
        table_data = [["Date", "Description", "Category", "Amount"]]
        total_amount = 0

        for item in expenses:
            # item dict should have date, name, category, price
            try:
                price_val = float(str(item['price']).replace(",", ""))
                formatted_price = f"{price_val:,.2f}"
                total_amount += price_val
                
                table_data.append([
                    item['date'],
                    item['name'],
                    item['category'],
                    formatted_price
                ])
            except (ValueError, KeyError):
                continue
        
        # Total Row
        table_data.append(["", "", "Total Expenses:", f"{total_amount:,.2f}"])

        # Table Styling
        table = Table(table_data, colWidths=[1.1*inch, 2.6*inch, 1.3*inch, 1.2*inch])
        ts = TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#2980b9")),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -2), colors.HexColor("#ecf0f1")),
            ('ALIGN', (1, 1), (1, -2), 'LEFT'),
            ('ALIGN', (3, 1), (3, -1), 'RIGHT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -2), 1, colors.white),
            ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor("#bdc3c7")),
            ('TEXTCOLOR', (2, -1), (-1, -1), colors.HexColor("#2c3e50")),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (2, -1), (-1, -1), 12),
            ('LINEABOVE', (0, -1), (-1, -1), 2, colors.HexColor("#2c3e50")),
        ])
        table.setStyle(ts)
        elements.append(table)
        
        elements.append(Spacer(1, 40))
        elements.append(Paragraph("Authorized Signature _______________________", styles['Normal']))

        doc.build(elements)
        buffer.seek(0)
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=file_name,
            mimetype='application/pdf'
        )

    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
