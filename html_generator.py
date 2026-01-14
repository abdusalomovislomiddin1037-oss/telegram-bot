"""
SmartWallet AI Bot - HTML Generator (Fixed)
============================================
HTML hisobotlar yaratish - demo dizayniga to'liq o'xshash

Author: SmartWallet AI Team
Version: 3.0.0 - FIXED
"""

import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any

from config import Paths
from utils.translations import format_currency, format_date, get_category_name

logger = logging.getLogger(__name__)


def generate_html_report(
    user_language: str,
    device_type: str,
    report_type: str,
    total_expense: Decimal,
    total_income: Decimal,
    balance: Decimal,
    expenses_by_category: List[Dict[str, Any]],
    expenses: List,
    start_date: datetime,
    end_date: datetime
) -> Path:
    """
    HTML hisobot yaratish (demo dizayniga to'liq o'xshash)
    
    Returns:
        Path: HTML fayl yo'li
    """
    try:
        # Papka yaratish
        Paths.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Fayl nomi
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"report_{report_type}_{timestamp}.html"
        file_path = Paths.REPORTS_DIR / filename
        
        # Kategoriya ma'lumotlari uchun
        pie_values = []
        pie_labels = []
        pie_colors = []
        
        # Kategoriyalar bo'yicha ma'lumotlar
        if expenses_by_category:
            for item in expenses_by_category:
                try:
                    category = item.get('category')
                    if category:
                        category_name = get_category_name(category.key, user_language)
                        pie_labels.append(f"{category.icon} {category_name}")
                        pie_values.append(float(item.get('total', 0)))
                        pie_colors.append(category.color)
                except Exception as e:
                    logger.error(f"Kategoriya qayta ishlashda xato: {e}")
                    continue
        
        # Agar kategoriyalar bo'sh bo'lsa, standart qiymatlar
        if not pie_values:
            pie_values = [1]
            pie_labels = ["Ma'lumot yo'q"]
            pie_colors = ["#6b7280"]
        
        # Xarajatlar jadvali
        table_rows = ""
        if expenses:
            for exp in expenses[:100]:  # Birinchi 100 ta
                try:
                    date_str = exp.expense_date.strftime('%d.%m.%Y')
                    
                    # Kategoriya ma'lumotlarini olish
                    if hasattr(exp, 'category') and exp.category:
                        category_key = exp.category.key
                        category_name = get_category_name(category_key, user_language)
                        category_icon = exp.category.icon
                        badge_class = f"badge-{category_key}"
                    else:
                        category_key = 'other'
                        category_name = 'Boshqa'
                        category_icon = '📝'
                        badge_class = 'badge-other'
                    
                    desc = exp.description if exp.description else '-'
                    amount = float(exp.amount)
                    
                    table_rows += f"""
                    <tr>
                        <td>{date_str}</td>
                        <td><span class="category-badge {badge_class}">{category_icon} {category_name}</span></td>
                        <td>{desc}</td>
                        <td style="font-weight: bold; color: #ef4444;">-{amount:,.0f} so'm</td>
                    </tr>
                    """
                except Exception as e:
                    logger.error(f"Xarajat jadvalga qo'shishda xato: {e}")
                    continue
        
        if not table_rows:
            table_rows = '<tr><td colspan="4" style="text-align: center; padding: 20px;">Ma\'lumot topilmadi</td></tr>'
        
        # Kunlik xarajatlar trendi (oxirgi 7 kun)
        line_dates = []
        line_values = []
        
        for i in range(6, -1, -1):
            day = end_date - timedelta(days=i)
            day_start = datetime.combine(day.date(), datetime.min.time())
            day_end = datetime.combine(day.date(), datetime.max.time())
            
            # O'sha kundagi xarajatlar
            day_total = 0
            if expenses:
                for e in expenses:
                    try:
                        if day_start <= e.expense_date <= day_end:
                            day_total += float(e.amount)
                    except:
                        continue
            
            line_dates.append(day.strftime('%d.%m'))
            line_values.append(day_total)
        
        # JSON encode
        pie_values_json = json.dumps(pie_values)
        pie_labels_json = json.dumps(pie_labels)
        pie_colors_json = json.dumps(pie_colors)
        line_dates_json = json.dumps(line_dates)
        line_values_json = json.dumps(line_values)
        
        # HTML yaratish
        html_content = f"""<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartWallet AI - Moliyaviy Hisobot</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        :root {{
            --primary: #6366f1;
            --success: #10b981;
            --danger: #ef4444;
            --warning: #f59e0b;
            --info: #3b82f6;
            --dark: #1f2937;
            --light: #f3f4f6;
        }}

        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}

        .logo {{
            font-size: 48px;
            margin-bottom: 10px;
        }}

        .header h1 {{
            font-size: 32px;
            margin-bottom: 5px;
        }}

        .header p {{
            font-size: 16px;
            opacity: 0.9;
        }}

        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            padding: 30px;
        }}

        .stat-card {{
            background: var(--light);
            padding: 25px;
            border-radius: 15px;
            border-left: 5px solid var(--primary);
            transition: transform 0.3s;
        }}

        .stat-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}

        .stat-card.income {{
            border-left-color: var(--success);
        }}

        .stat-card.expense {{
            border-left-color: var(--danger);
        }}

        .stat-card.balance {{
            border-left-color: var(--info);
        }}

        .stat-icon {{
            font-size: 40px;
            margin-bottom: 10px;
        }}

        .stat-label {{
            color: #6b7280;
            font-size: 14px;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 5px;
        }}

        .stat-value {{
            font-size: 32px;
            font-weight: bold;
            color: var(--dark);
        }}

        .charts-section {{
            padding: 30px;
            background: #fafafa;
        }}

        .section-title {{
            font-size: 24px;
            color: var(--dark);
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .chart-container {{
            background: white;
            padding: 20px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }}

        .table-section {{
            padding: 30px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        }}

        thead {{
            background: var(--primary);
            color: white;
        }}

        th, td {{
            padding: 15px;
            text-align: left;
        }}

        tbody tr:hover {{
            background: var(--light);
        }}

        tbody tr:nth-child(even) {{
            background: #f9fafb;
        }}

        .category-badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 12px;
            font-weight: 600;
            color: white;
        }}

        .badge-food {{ background: #f59e0b; }}
        .badge-home {{ background: #3b82f6; }}
        .badge-transport {{ background: #8b5cf6; }}
        .badge-health {{ background: #ec4899; }}
        .badge-education {{ background: #14b8a6; }}
        .badge-entertainment {{ background: #f43f5e; }}
        .badge-shopping {{ background: #06b6d4; }}
        .badge-bills {{ background: #f97316; }}
        .badge-other {{ background: #6b7280; }}

        .footer {{
            background: var(--dark);
            color: white;
            text-align: center;
            padding: 20px;
            font-size: 14px;
        }}

        @media (max-width: 768px) {{
            body {{
                padding: 10px;
            }}

            .header h1 {{
                font-size: 24px;
            }}

            .logo {{
                font-size: 36px;
            }}

            .stats-grid {{
                grid-template-columns: 1fr;
                padding: 20px;
            }}

            .stat-value {{
                font-size: 24px;
            }}

            .charts-section, .table-section {{
                padding: 20px;
            }}

            th, td {{
                padding: 10px;
                font-size: 14px;
            }}

            table {{
                font-size: 12px;
            }}
        }}

        @media (max-width: 480px) {{
            .header h1 {{
                font-size: 20px;
            }}

            .stat-value {{
                font-size: 20px;
            }}

            .section-title {{
                font-size: 18px;
            }}
        }}

        @media print {{
            body {{
                background: white;
                padding: 0;
            }}

            .container {{
                box-shadow: none;
            }}

            .stat-card:hover {{
                transform: none;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div class="logo">💼</div>
            <h1>SmartWallet AI</h1>
            <p>Moliyaviy Hisobot | {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}</p>
        </div>

        <div class="stats-grid">
            <div class="stat-card income">
                <div class="stat-icon">💰</div>
                <div class="stat-label">Umumiy Daromad</div>
                <div class="stat-value">{float(total_income):,.0f} so'm</div>
            </div>

            <div class="stat-card expense">
                <div class="stat-icon">💸</div>
                <div class="stat-label">Umumiy Xarajat</div>
                <div class="stat-value">{float(total_expense):,.0f} so'm</div>
            </div>

            <div class="stat-card balance">
                <div class="stat-icon">🏦</div>
                <div class="stat-label">Qolgan Pul</div>
                <div class="stat-value">{float(balance):,.0f} so'm</div>
            </div>
        </div>

        <div class="charts-section">
            <h2 class="section-title">📊 Xarajatlar Diagrammasi</h2>
            
            <div class="chart-container">
                <div id="pieChart"></div>
            </div>

            <div class="chart-container">
                <div id="lineChart"></div>
            </div>
        </div>

        <div class="table-section">
            <h2 class="section-title">📋 Batafsil Xarajatlar</h2>
            <table>
                <thead>
                    <tr>
                        <th>Sana</th>
                        <th>Kategoriya</th>
                        <th>Izoh</th>
                        <th>Summa</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>

        <div class="footer">
            <p>© 2025 SmartWallet AI | Telegram Bot</p>
            <p style="margin-top: 5px; opacity: 0.8;">Kunlik xarajatlaringizni AI yordamida oson boshqaring</p>
        </div>
    </div>

    <script>
        var pieData = [{{
            values: {pie_values_json},
            labels: {pie_labels_json},
            type: 'pie',
            hole: 0.4,
            marker: {{
                colors: {pie_colors_json}
            }},
            textinfo: 'label+percent',
            textposition: 'outside',
            automargin: true
        }}];

        var pieLayout = {{
            title: {{
                text: 'Xarajatlar taqsimoti',
                font: {{ size: 20, color: '#1f2937' }}
            }},
            showlegend: false,
            height: 400,
            margin: {{ t: 60, b: 20, l: 20, r: 20 }}
        }};

        var config = {{responsive: true, displayModeBar: false}};
        Plotly.newPlot('pieChart', pieData, pieLayout, config);

        var lineData = [{{
            x: {line_dates_json},
            y: {line_values_json},
            type: 'scatter',
            mode: 'lines+markers',
            name: 'Xarajatlar',
            line: {{
                color: '#ef4444',
                width: 3
            }},
            marker: {{
                size: 10,
                color: '#ef4444'
            }}
        }}];

        var lineLayout = {{
            title: {{
                text: 'Kunlik xarajatlar trendi',
                font: {{ size: 20, color: '#1f2937' }}
            }},
            xaxis: {{
                title: 'Sana',
                gridcolor: '#e5e7eb'
            }},
            yaxis: {{
                title: 'Summa (so\\'m)',
                gridcolor: '#e5e7eb'
            }},
            height: 400,
            margin: {{ t: 60, b: 60, l: 80, r: 40 }},
            plot_bgcolor: '#fafafa',
            paper_bgcolor: 'white'
        }};

        Plotly.newPlot('lineChart', lineData, lineLayout, config);
    </script>
</body>
</html>
"""
        
        # Faylga yozish
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"✅ HTML hisobot yaratildi: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"❌ HTML yaratishda xato: {e}", exc_info=True)
        raise
