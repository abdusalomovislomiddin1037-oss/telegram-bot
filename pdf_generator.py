"""
SmartWallet AI Bot - PDF Generator
==================================
PDF hisobotlar yaratish

Author: SmartWallet AI Team
Version: 1.0.0
"""

import logging
from pathlib import Path
from datetime import datetime
from decimal import Decimal
from typing import List, Dict, Any

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from config import Paths, ReportConfig
from utils.translations import format_currency, format_date, get_category_name, get_month_name
from utils.charts import create_pie_chart, create_bar_chart

logger = logging.getLogger(__name__)


def generate_pdf_report(
    user_language: str,
    report_type: str,
    total_expense: Decimal,
    total_income: Decimal,
    balance: Decimal,
    expenses_by_category: List[Dict[str, Any]],
    start_date: datetime,
    end_date: datetime
) -> Path:
    """
    PDF hisobot yaratish
    
    Returns:
        Path: PDF fayl yo'li
    """
    try:
        # Papka yaratish
        Paths.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Fayl nomi
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"report_{report_type}_{timestamp}.pdf"
        file_path = Paths.REPORTS_DIR / filename
        
        # PDF yaratish
        doc = SimpleDocTemplate(str(file_path), pagesize=A4)
        story = []
        
        styles = getSampleStyleSheet()
        
        # Sarlavha
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=30,
            alignment=TA_CENTER
        )
        
        report_titles = {
            'uz': 'SmartWallet AI - Hisobot',
            'ru': 'SmartWallet AI - Отчёт',
            'en': 'SmartWallet AI - Report',
            'tr': 'SmartWallet AI - Rapor',
            'ar': 'SmartWallet AI - تقرير'
        }
        
        title = Paragraph(report_titles.get(user_language, report_titles['uz']), title_style)
        story.append(title)
        story.append(Spacer(1, 1*cm))
        
        # Davr
        period_text = f"{format_date(start_date, user_language)} - {format_date(end_date, user_language)}"
        period = Paragraph(f"<para align=center>{period_text}</para>", styles['Normal'])
        story.append(period)
        story.append(Spacer(1, 1*cm))
        
        # Umumiy ma'lumotlar jadvali
        summary_data = [
            ['Daromad:', format_currency(total_income, user_language)],
            ['Xarajat:', format_currency(total_expense, user_language)],
            ['Balans:', format_currency(balance, user_language)]
        ]
        
        summary_table = Table(summary_data, colWidths=[8*cm, 8*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f3f4f6')),
            ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#1f2937')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 14),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.white)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 2*cm))
        
        # Kategoriyalar jadvali
        if expenses_by_category:
            category_title = Paragraph("<para align=left><b>Kategoriyalar bo'yicha:</b></para>", styles['Heading2'])
            story.append(category_title)
            story.append(Spacer(1, 0.5*cm))
            
            category_data = [['Kategoriya', 'Summa', '%']]
            
            for item in expenses_by_category:
                category_name = get_category_name(item['category'].key, user_language)
                amount = format_currency(item['total'], user_language)
                percentage = f"{(item['total'] / total_expense * 100):.1f}%" if total_expense > 0 else "0%"
                
                category_data.append([
                    f"{item['category'].icon} {category_name}",
                    amount,
                    percentage
                ])
            
            category_table = Table(category_data, colWidths=[8*cm, 6*cm, 2*cm])
            category_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3b82f6')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(category_table)
        
        # PDF yaratish
        doc.build(story)
        
        logger.info(f"PDF generated: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"PDF generation error: {e}")
        raise
