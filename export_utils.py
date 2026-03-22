import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from db_config import DatabaseConnection
import datetime
from openpyxl.utils import get_column_letter

class ExportUtils:
    def __init__(self):
        self.db = DatabaseConnection()
        self.db.connect()

    def generate_excel_report(self, report_type='daily', start_date=None, end_date=None):
        """Generate Excel report based on report type"""
        if report_type == 'daily':
            query = """
                SELECT 
                    u.first_name, u.last_name, l.name as location, 
                    s.opened_at, s.closed_at, 
                    COALESCE(r.sales_amount,0) as sales_amount,
                    COALESCE(r.debt_received,0) as debt_received,
                    COALESCE(r.expenses,0) as expenses,
                    COALESCE(r.uzcard_amount,0) as uzcard_amount,
                    COALESCE(r.humo_amount,0) as humo_amount,
                    COALESCE(r.uzcard_refund,0) as uzcard_refund,
                    COALESCE(r.humo_refund,0) as humo_refund,
                    COALESCE(r.other_payments,0) as other_payments,
                    COALESCE(r.debt_payments,0) as debt_payments,
                    COALESCE(r.debt_refunds,0) as debt_refunds,
                    (
                        COALESCE(r.sales_amount,0)
                        + COALESCE(r.debt_received,0)
                        + COALESCE(r.uzcard_amount,0)
                        + COALESCE(r.humo_amount,0)
                        + COALESCE(r.other_payments,0)
                        + COALESCE(r.debt_refunds,0)
                        - COALESCE(r.expenses,0)
                        - COALESCE(r.debt_payments,0)
                        - COALESCE(r.uzcard_refund,0)
                        - COALESCE(r.humo_refund,0)
                    ) as total_balance
                FROM reports r
                JOIN shifts s ON r.shift_id = s.id
                JOIN users u ON s.user_id = u.id
                JOIN locations l ON s.location_id = l.id
                WHERE r.report_type = 'daily_report'
            """
            if start_date and end_date:
                query += " AND s.opened_at BETWEEN %s AND %s"
                df = pd.read_sql(query, self.db.connection, params=[start_date, end_date])
            else:
                df = pd.read_sql(query, self.db.connection)

            # Uzbek column names for Excel
            df = df.rename(columns={
                'first_name': 'Ism',
                'last_name': 'Familiya',
                'location': 'Filial',
                'opened_at': 'Smena ochilgan vaqt',
                'closed_at': 'Smena yopilgan vaqt',
                'sales_amount': 'Savdo',
                'debt_received': 'Kelgan qarz',
                'expenses': 'Chiqim',
                'uzcard_amount': 'Uzcard',
                'humo_amount': 'Humo',
                'uzcard_refund': 'Uzcard vozvrat',
                'humo_refund': 'Humo vozvrat',
                'other_payments': "Boshqa to'lovlar",
                'debt_payments': "Qarzga berilgan to'lovlar",
                'debt_refunds': 'Vozvrat qarzlar',
                'total_balance': 'Sof summa',
            })
        
        elif report_type == 'cashier_performance':
            query = """
                SELECT 
                    u.first_name, u.last_name, u.phone_number,
                    COUNT(s.id) as shifts_count,
                    SUM(r.sales_amount) as total_sales,
                    AVG(r.sales_amount) as avg_sales,
                    SUM(r.expenses) as total_expenses
                FROM users u
                LEFT JOIN shifts s ON u.id = s.user_id
                LEFT JOIN reports r ON s.id = r.shift_id AND r.report_type = 'daily_report'
                WHERE u.role = 'cashier'
                GROUP BY u.id
            """
            df = pd.read_sql(query, self.db.connection)

            df = df.rename(columns={
                'first_name': 'Ism',
                'last_name': 'Familiya',
                'phone_number': 'Telefon',
                'shifts_count': 'Smenalar soni',
                'total_sales': 'Jami savdo',
                'avg_sales': "O'rtacha savdo",
                'total_expenses': 'Jami chiqim',
            })
        
        # Create Excel file in memory
        output = BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            sheet_name = 'Hisobotlar'
            df.to_excel(writer, sheet_name=sheet_name, index=False)

            # Set reasonable column widths to avoid ####### in viewers like WPS
            ws = writer.sheets[sheet_name]
            for col_idx, col_name in enumerate(df.columns, start=1):
                # Prefer header width and sample content width
                max_len = len(str(col_name))
                for val in df.iloc[:50, col_idx - 1].astype(str).tolist():
                    if len(val) > max_len:
                        max_len = len(val)
                ws.column_dimensions[get_column_letter(col_idx)].width = min(max(10, max_len + 2), 40)
        
        output.seek(0)
        return output

    def generate_pdf_report(self, report_type='daily', start_date=None, end_date=None):
        """Generate PDF report based on report type"""
        buffer = BytesIO()
        # Landscape helps fit wider tables.
        doc = SimpleDocTemplate(buffer, pagesize=landscape(letter))
        styles = getSampleStyleSheet()
        elements = []

        # Add title (Uzbek)
        report_titles = {
            'daily': "Kunlik hisobot",
            'cashier_performance': "Kassirlar bo'yicha hisobot",
        }
        title_text = report_titles.get(report_type, report_type.replace('_', ' ').title())
        title = Paragraph(f"Sardoba Restoran - {title_text}", styles['Title'])
        elements.append(title)
        
        # Add date range if specified
        if start_date and end_date:
            date_range = Paragraph(f"Date Range: {start_date} to {end_date}", styles['Normal'])
            elements.append(date_range)
        
        elements.append(Paragraph(" ", styles['Normal']))  # Spacer
        
        # Get data based on report type
        if report_type == 'daily':
            query = """
                SELECT 
                    CONCAT(u.first_name, ' ', u.last_name) as cashier_name,
                    l.name as location,
                    DATE(s.opened_at) as date,
                    TIME(s.opened_at) as open_time,
                    COALESCE(r.sales_amount,0) as sales_amount,
                    COALESCE(r.debt_received,0) as debt_received,
                    COALESCE(r.expenses,0) as expenses,
                    COALESCE(r.uzcard_amount,0) as uzcard_amount,
                    COALESCE(r.humo_amount,0) as humo_amount,
                    COALESCE(r.uzcard_refund,0) as uzcard_refund,
                    COALESCE(r.humo_refund,0) as humo_refund,
                    COALESCE(r.other_payments,0) as other_payments,
                    COALESCE(r.debt_payments,0) as debt_payments,
                    COALESCE(r.debt_refunds,0) as debt_refunds,
                    (
                        COALESCE(r.sales_amount,0)
                        + COALESCE(r.debt_received,0)
                        + COALESCE(r.uzcard_amount,0)
                        + COALESCE(r.humo_amount,0)
                        + COALESCE(r.other_payments,0)
                        + COALESCE(r.debt_refunds,0)
                        - COALESCE(r.expenses,0)
                        - COALESCE(r.debt_payments,0)
                        - COALESCE(r.uzcard_refund,0)
                        - COALESCE(r.humo_refund,0)
                    ) as total_balance
                FROM reports r
                JOIN shifts s ON r.shift_id = s.id
                JOIN users u ON s.user_id = u.id
                JOIN locations l ON s.location_id = l.id
                WHERE r.report_type = 'daily_report'
            """
            if start_date and end_date:
                query += " AND s.opened_at BETWEEN %s AND %s"
                data = self.db.fetch_all(query, (start_date, end_date))
            else:
                data = self.db.fetch_all(query)
        
        elif report_type == 'cashier_performance':
            query = """
                SELECT 
                    CONCAT(u.first_name, ' ', u.last_name) as cashier_name,
                    u.phone_number,
                    COUNT(s.id) as shifts_count,
                    COALESCE(SUM(r.sales_amount), 0) as total_sales,
                    COALESCE(AVG(r.sales_amount), 0) as avg_sales,
                    COALESCE(SUM(r.expenses), 0) as total_expenses
                FROM users u
                LEFT JOIN shifts s ON u.id = s.user_id
                LEFT JOIN reports r ON s.id = r.shift_id AND r.report_type = 'daily_report'
                WHERE u.role = 'cashier'
                GROUP BY u.id
            """
            data = self.db.fetch_all(query)
        
        if data:
            # Create table headers
            if report_type == 'daily':
                headers = [
                    'Kassir', 'Filial', 'Sana', 'Ochilish vaqti', 'Savdo', 'Kelgan qarz', 'Chiqim',
                    'Uzcard', 'Humo', 'Uzcard vozvrat', 'Humo vozvrat', "Boshqa to'lov",
                    'Qarzga berilgan', 'Vozvrat qarz', 'Sof summa'
                ]
            else:  # cashier_performance
                headers = ['Kassir', 'Telefon', 'Smenalar', 'Jami savdo', "O'rtacha savdo", 'Jami chiqim']
            
            # Build tables. For daily report the table is very wide, so we split it into 2 parts
            # to ensure all columns are visible and readable.
            def _apply_style(t: Table):
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 8),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 7),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ]))

            if report_type == 'daily':
                # Split columns: first part (0..7) and second part (8..14)
                part1_idx = list(range(0, 8))
                part2_idx = list(range(8, 15))

                table_data_1 = [[headers[i] for i in part1_idx]]
                table_data_2 = [[headers[i] for i in part2_idx]]

                for row in data:
                    full = [
                        row['cashier_name'],
                        row['location'],
                        str(row['date']),
                        str(row['open_time'])[:5],
                        f"{row['sales_amount']:,.0f}",
                        f"{row['debt_received']:,.0f}",
                        f"{row['expenses']:,.0f}",
                        f"{row['uzcard_amount']:,.0f}",
                        f"{row['humo_amount']:,.0f}",
                        f"{row['uzcard_refund']:,.0f}",
                        f"{row['humo_refund']:,.0f}",
                        f"{row['other_payments']:,.0f}",
                        f"{row['debt_payments']:,.0f}",
                        f"{row['debt_refunds']:,.0f}",
                        f"{row['total_balance']:,.0f}",
                    ]
                    table_data_1.append([full[i] for i in part1_idx])
                    table_data_2.append([full[i] for i in part2_idx])

                table1 = Table(table_data_1, repeatRows=1)
                _apply_style(table1)
                elements.append(table1)
                elements.append(Paragraph(" ", styles['Normal']))

                table2 = Table(table_data_2, repeatRows=1)
                _apply_style(table2)
                elements.append(table2)
            else:
                table_data = [headers]
                for row in data:
                    table_data.append([
                        row['cashier_name'],
                        row['phone_number'],
                        row['shifts_count'],
                        f"{row['total_sales']:,.0f}",
                        f"{row['avg_sales']:,.0f}",
                        f"{row['total_expenses']:,.0f}",
                    ])
                table = Table(table_data, repeatRows=1)
                _apply_style(table)
                elements.append(table)
        else:
            elements.append(Paragraph("Tanlangan davr uchun ma'lumot topilmadi.", styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        buffer.seek(0)
        return buffer

    def close_connection(self):
        """Close database connection"""
        self.db.disconnect()
