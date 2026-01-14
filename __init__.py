"""
SmartWallet AI Bot - Utils Package
==================================
Yordamchi funksiyalar va utilitylar

Modules:
    - ai_parser: AI matn tahlili (summa va kategoriya aniqlash)
    - reminders: Eslatmalar scheduler
    - translations: Ko'p tilli tarjimalar
    - charts: Grafik va diagrammalar
    - filters: Ma'lumotlarni filtrlash
    - colors: Rang palitrasi
    - validators: Validatsiya funksiyalari

Author: SmartWallet AI Team
Version: 1.0.0
"""

from .ai_parser import (
    parse_expense_text,
    extract_amount,
    detect_category,
    parse_date_text
)

from .reminders import (
    ReminderScheduler
)

from .translations import (
    get_text,
    get_category_name,
    format_date,
    format_currency
)

# Charts - ixtiyoriy (matplotlib kerak)
try:
    from .charts import (
        create_pie_chart,
        create_line_chart,
        create_bar_chart,
        save_chart_to_file
    )
    CHARTS_AVAILABLE = True
except ImportError:
    # matplotlib o'rnatilmagan
    CHARTS_AVAILABLE = False
    create_pie_chart = None
    create_line_chart = None
    create_bar_chart = None
    save_chart_to_file = None

from .filters import (
    filter_by_date_range,
    filter_by_category,
    filter_by_amount_range
)

from .colors import (
    get_category_color,
    get_color_palette,
    hex_to_rgb
)

from .validators import (
    validate_amount,
    validate_date,
    validate_telegram_id,
    sanitize_text
)

__all__ = [
    # AI Parser
    'parse_expense_text',
    'extract_amount',
    'detect_category',
    'parse_date_text',
    
    # Reminders
    'ReminderScheduler',
    
    # Translations
    'get_text',
    'get_category_name',
    'format_date',
    'format_currency',
    
    # Charts
    'create_pie_chart',
    'create_line_chart',
    'create_bar_chart',
    'save_chart_to_file',
    
    # Filters
    'filter_by_date_range',
    'filter_by_category',
    'filter_by_amount_range',
    
    # Colors
    'get_category_color',
    'get_color_palette',
    'hex_to_rgb',
    
    # Validators
    'validate_amount',
    'validate_date',
    'validate_telegram_id',
    'sanitize_text',
]
