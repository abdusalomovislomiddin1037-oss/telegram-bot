"""
SmartWallet AI Bot - Inline Keyboards
=====================================
Barcha inline keyboard'lar (tugmalar)

Functions:
    - get_language_keyboard: Til tanlash
    - get_main_menu_keyboard: Asosiy menyu
    - get_settings_keyboard: Sozlamalar
    - get_category_keyboard: Kategoriyalar
    - get_report_type_keyboard: Hisobot turlari
    - get_export_format_keyboard: Eksport formatlari
    - get_device_type_keyboard: Gadjet turlari
    - get_yes_no_keyboard: Ha/Yo'q
    - get_back_button: Orqaga

Author: SmartWallet AI Team
Version: 1.0.0
"""

from typing import Optional, List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from config import Categories


# =====================================================
# LANGUAGE KEYBOARD
# =====================================================
def get_language_keyboard() -> InlineKeyboardMarkup:
    """
    Til tanlash keyboard'i
    
    Returns:
        InlineKeyboardMarkup: 5 tilli keyboard
    """
    keyboard = [
        [
            InlineKeyboardButton("🇺🇿 O'zbek", callback_data='lang_uz'),
            InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru'),
        ],
        [
            InlineKeyboardButton("🇬🇧 English", callback_data='lang_en'),
            InlineKeyboardButton("🇹🇷 Türkçe", callback_data='lang_tr'),
        ],
        [
            InlineKeyboardButton("🇸🇦 العربية", callback_data='lang_ar'),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# =====================================================
# MAIN MENU KEYBOARD
# =====================================================
def get_main_menu_keyboard(language: str = 'uz') -> InlineKeyboardMarkup:
    """
    Asosiy menyu keyboard'i
    
    Args:
        language: Til kodi
        
    Returns:
        InlineKeyboardMarkup: Asosiy menyu
    """
    # Tarjimalar
    texts = {
        'uz': {
            'add_expense': '💳 Xarajat qo\'shish',
            'add_income': '💰 Daromad qo\'shish',
            'debts': '💼 Qarzlar',
            'reports': '📊 Hisobotlar',
            'settings': '⚙️ Sozlamalar',
        },
        'ru': {
            'add_expense': '💳 Добавить расход',
            'add_income': '💰 Добавить доход',
            'debts': '💼 Долги',
            'reports': '📊 Отчёты',
            'settings': '⚙️ Настройки',
        },
        'en': {
            'add_expense': '💳 Add Expense',
            'add_income': '💰 Add Income',
            'debts': '💼 Debts',
            'reports': '📊 Reports',
            'settings': '⚙️ Settings',
        },
        'tr': {
            'add_expense': '💳 Gider Ekle',
            'add_income': '💰 Gelir Ekle',
            'debts': '💼 Borçlar',
            'reports': '📊 Raporlar',
            'settings': '⚙️ Ayarlar',
        },
        'ar': {
            'add_expense': '💳 إضافة مصروف',
            'add_income': '💰 إضافة دخل',
            'debts': '💼 الديون',
            'reports': '📊 التقارير',
            'settings': '⚙️ الإعدادات',
        }
    }
    
    t = texts.get(language, texts['uz'])
    
    keyboard = [
        [
            InlineKeyboardButton(t['add_expense'], callback_data='add_expense'),
        ],
        [
            InlineKeyboardButton(t['add_income'], callback_data='add_income'),
        ],
        [
            InlineKeyboardButton(t['debts'], callback_data='debt_menu'),
        ],
        [
            InlineKeyboardButton(t['reports'], callback_data='reports'),
        ],
        [
            InlineKeyboardButton(t['settings'], callback_data='settings'),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# =====================================================
# SETTINGS KEYBOARD
# =====================================================
def get_settings_keyboard(language: str = 'uz') -> InlineKeyboardMarkup:
    """
    Sozlamalar keyboard'i
    
    Args:
        language: Til kodi
        
    Returns:
        InlineKeyboardMarkup: Sozlamalar menyusi
    """
    texts = {
        'uz': {
            'change_language': '🌐 Tilni o\'zgartirish',
            'export_data': '📤 Ma\'lumotlarni yuklab olish',
            'delete_data': '🗑️ Ma\'lumotlarni boshqarish',
            'back': '🔙 Orqaga qaytish',
        },
        'ru': {
            'change_language': '🌐 Сменить язык',
            'export_data': '📤 Скачать данные',
            'delete_data': '🗑️ Управление данными',
            'back': '🔙 Вернуться назад',
        },
        'en': {
            'change_language': '🌐 Change Language',
            'export_data': '📤 Download Data',
            'delete_data': '🗑️ Manage Data',
            'back': '🔙 Go Back',
        },
        'tr': {
            'change_language': '🌐 Dili Değiştir',
            'export_data': '📤 Verileri İndir',
            'delete_data': '🗑️ Veri Yönetimi',
            'back': '🔙 Geri Dön',
        },
        'ar': {
            'change_language': '🌐 تغيير اللغة',
            'export_data': '📤 تحميل البيانات',
            'delete_data': '🗑️ إدارة البيانات',
            'back': '🔙 العودة',
        }
    }
    
    t = texts.get(language, texts['uz'])
    
    keyboard = [
        [InlineKeyboardButton(t['change_language'], callback_data='change_language')],
        [InlineKeyboardButton(t['export_data'], callback_data='export_data')],
        [InlineKeyboardButton(t['delete_data'], callback_data='delete_data')],
        [InlineKeyboardButton(t['back'], callback_data='back_main')],
    ]
    return InlineKeyboardMarkup(keyboard)


# =====================================================
# CATEGORY KEYBOARD
# =====================================================
def get_category_keyboard(language: str = 'uz', columns: int = 2) -> InlineKeyboardMarkup:
    """
    Kategoriyalar keyboard'i
    
    Args:
        language: Til kodi
        columns: Ustun soni (default: 2)
        
    Returns:
        InlineKeyboardMarkup: Kategoriyalar
    """
    keyboard = []
    row = []
    
    for category in Categories.LIST:
        # Kategoriya nomini olish
        name = Categories.NAMES[category['key']].get(language, category['key'])
        button_text = f"{category['icon']} {name}"
        
        button = InlineKeyboardButton(
            button_text,
            callback_data=f"category_{category['key']}"
        )
        row.append(button)
        
        # Agar qator to'lsa, yangi qator boshlash
        if len(row) == columns:
            keyboard.append(row)
            row = []
    
    # Oxirgi qatorni qo'shish (agar tugallanmagan bo'lsa)
    if row:
        keyboard.append(row)
    
    # Orqaga tugmasi
    back_texts = {
        'uz': '🔙 Orqaga qaytish',
        'ru': '🔙 Вернуться назад',
        'en': '🔙 Go Back',
        'tr': '🔙 Geri Dön',
        'ar': '🔙 العودة'
    }
    keyboard.append([
        InlineKeyboardButton(
            back_texts.get(language, back_texts['uz']),
            callback_data='back_main'
        )
    ])
    
    return InlineKeyboardMarkup(keyboard)


# =====================================================
# REPORT TYPE KEYBOARD
# =====================================================
def get_report_type_keyboard(language: str = 'uz') -> InlineKeyboardMarkup:
    """
    Hisobot turlari keyboard'i
    
    Args:
        language: Til kodi
        
    Returns:
        InlineKeyboardMarkup: Hisobot turlari
    """
    texts = {
        'uz': {
            'daily': '📆 Bugungi hisobot',
            'three_days': '🗓️ Oxirgi 3 kun',
            'weekly': '📅 Haftalik hisobot',
            'monthly': '🗓️ Oylik hisobot',
            'yearly': '📊 Yillik hisobot',
            'custom': '🔍 Maxsus davr (filtr)',
            'back': '🔙 Orqaga qaytish',
        },
        'ru': {
            'daily': '📆 Сегодняшний отчёт',
            'three_days': '🗓️ Последние 3 дня',
            'weekly': '📅 Недельный отчёт',
            'monthly': '🗓️ Месячный отчёт',
            'yearly': '📊 Годовой отчёт',
            'custom': '🔍 Свой период (фильтр)',
            'back': '🔙 Вернуться назад',
        },
        'en': {
            'daily': '📆 Today\'s Report',
            'three_days': '🗓️ Last 3 Days',
            'weekly': '📅 Weekly Report',
            'monthly': '🗓️ Monthly Report',
            'yearly': '📊 Yearly Report',
            'custom': '🔍 Custom Period (filter)',
            'back': '🔙 Go Back',
        },
        'tr': {
            'daily': '📆 Bugünkü Rapor',
            'three_days': '🗓️ Son 3 Gün',
            'weekly': '📅 Haftalık Rapor',
            'monthly': '🗓️ Aylık Rapor',
            'yearly': '📊 Yıllık Rapor',
            'custom': '🔍 Özel Dönem (filtre)',
            'back': '🔙 Geri Dön',
        },
        'ar': {
            'daily': '📆 تقرير اليوم',
            'three_days': '🗓️ آخر 3 أيام',
            'weekly': '📅 تقرير أسبوعي',
            'monthly': '🗓️ تقرير شهري',
            'yearly': '📊 تقرير سنوي',
            'custom': '🔍 فترة مخصصة (فلتر)',
            'back': '🔙 العودة',
        }
    }
    
    t = texts.get(language, texts['uz'])
    
    keyboard = [
        [InlineKeyboardButton(t['daily'], callback_data='report_daily')],
        [InlineKeyboardButton(t['three_days'], callback_data='report_three_days')],
        [InlineKeyboardButton(t['weekly'], callback_data='report_weekly')],
        [InlineKeyboardButton(t['monthly'], callback_data='report_monthly')],
        [InlineKeyboardButton(t['yearly'], callback_data='report_yearly')],
        [InlineKeyboardButton(t['custom'], callback_data='report_custom')],
        [InlineKeyboardButton(t['back'], callback_data='back_main')],
    ]
    return InlineKeyboardMarkup(keyboard)


# =====================================================
# EXPORT FORMAT KEYBOARD
# =====================================================
def get_export_format_keyboard(language: str = 'uz') -> InlineKeyboardMarkup:
    """
    Eksport format keyboard'i
    
    Args:
        language: Til kodi
        
    Returns:
        InlineKeyboardMarkup: Format tanlash
    """
    texts = {
        'uz': {
            'html': '🌐 HTML — Brauzerda ko\'rish',
            'pdf': '📑 PDF — Chop etish uchun',
            'excel': '📊 Excel — Tahlil qilish',
            'back': '🔙 Orqaga qaytish',
        },
        'ru': {
            'html': '🌐 HTML — Просмотр в браузере',
            'pdf': '📑 PDF — Для печати',
            'excel': '📊 Excel — Для анализа',
            'back': '🔙 Вернуться назад',
        },
        'en': {
            'html': '🌐 HTML — View in browser',
            'pdf': '📑 PDF — For printing',
            'excel': '📊 Excel — For analysis',
            'back': '🔙 Go Back',
        },
        'tr': {
            'html': '🌐 HTML — Tarayıcıda görüntüle',
            'pdf': '📑 PDF — Yazdırmak için',
            'excel': '📊 Excel — Analiz için',
            'back': '🔙 Geri Dön',
        },
        'ar': {
            'html': '🌐 HTML — عرض في المتصفح',
            'pdf': '📑 PDF — للطباعة',
            'excel': '📊 Excel — للتحليل',
            'back': '🔙 العودة',
        }
    }
    
    t = texts.get(language, texts['uz'])
    
    keyboard = [
        [InlineKeyboardButton(t['html'], callback_data='export_html')],
        [InlineKeyboardButton(t['pdf'], callback_data='export_pdf')],
        [InlineKeyboardButton(t['excel'], callback_data='export_excel')],
        [InlineKeyboardButton(t['back'], callback_data='back_reports')],
    ]
    return InlineKeyboardMarkup(keyboard)


# =====================================================
# DEVICE TYPE KEYBOARD
# =====================================================
def get_device_type_keyboard(language: str = 'uz') -> InlineKeyboardMarkup:
    """
    Gadjet turi keyboard'i
    
    Args:
        language: Til kodi
        
    Returns:
        InlineKeyboardMarkup: Gadjet tanlash
    """
    texts = {
        'uz': {
            'phone': '📱 Telefon',
            'tablet': '📲 Planshet',
            'computer': '💻 Kompyuter',
            'back': '« Orqaga',
        },
        'ru': {
            'phone': '📱 Телефон',
            'tablet': '📲 Планшет',
            'computer': '💻 Компьютер',
            'back': '« Назад',
        },
        'en': {
            'phone': '📱 Phone',
            'tablet': '📲 Tablet',
            'computer': '💻 Computer',
            'back': '« Back',
        },
        'tr': {
            'phone': '📱 Telefon',
            'tablet': '📲 Tablet',
            'computer': '💻 Bilgisayar',
            'back': '« Geri',
        },
        'ar': {
            'phone': '📱 هاتف',
            'tablet': '📲 جهاز لوحي',
            'computer': '💻 كمبيوتر',
            'back': '« رجوع',
        }
    }
    
    t = texts.get(language, texts['uz'])
    
    keyboard = [
        [InlineKeyboardButton(t['phone'], callback_data='device_phone')],
        [InlineKeyboardButton(t['tablet'], callback_data='device_tablet')],
        [InlineKeyboardButton(t['computer'], callback_data='device_computer')],
        [InlineKeyboardButton(t['back'], callback_data='back_export')],
    ]
    return InlineKeyboardMarkup(keyboard)


# =====================================================
# DEBT TYPE KEYBOARD
# =====================================================


# =====================================================
# YES/NO KEYBOARD
# =====================================================
def get_yes_no_keyboard(
    language: str = 'uz',
    yes_callback: str = 'yes',
    no_callback: str = 'no'
) -> InlineKeyboardMarkup:
    """
    Ha/Yo'q keyboard'i
    
    Args:
        language: Til kodi
        yes_callback: "Ha" tugmasi callback data
        no_callback: "Yo'q" tugmasi callback data
        
    Returns:
        InlineKeyboardMarkup: Ha/Yo'q tugmalar
    """
    texts = {
        'uz': {'yes': '✅ Ha', 'no': '❌ Yo\'q'},
        'ru': {'yes': '✅ Да', 'no': '❌ Нет'},
        'en': {'yes': '✅ Yes', 'no': '❌ No'},
        'tr': {'yes': '✅ Evet', 'no': '❌ Hayır'},
        'ar': {'yes': '✅ نعم', 'no': '❌ لا'},
    }
    
    t = texts.get(language, texts['uz'])
    
    keyboard = [
        [
            InlineKeyboardButton(t['yes'], callback_data=yes_callback),
            InlineKeyboardButton(t['no'], callback_data=no_callback),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# =====================================================
# BACK BUTTON
# =====================================================
def get_back_button(
    language: str = 'uz',
    callback_data: str = 'back_main'
) -> InlineKeyboardMarkup:
    """
    Orqaga tugmasi
    
    Args:
        language: Til kodi
        callback_data: Callback data
        
    Returns:
        InlineKeyboardMarkup: Orqaga tugmasi
    """
    texts = {
        'uz': '« Orqaga',
        'ru': '« Назад',
        'en': '« Back',
        'tr': '« Geri',
        'ar': '« رجوع'
    }
    
    text = texts.get(language, texts['uz'])
    
    keyboard = [[InlineKeyboardButton(text, callback_data=callback_data)]]
    return InlineKeyboardMarkup(keyboard)


# =====================================================
# PAGINATION KEYBOARD
# =====================================================
def get_pagination_keyboard(
    current_page: int,
    total_pages: int,
    callback_prefix: str = 'page',
    language: str = 'uz'
) -> InlineKeyboardMarkup:
    """
    Sahifalash keyboard'i
    
    Args:
        current_page: Joriy sahifa
        total_pages: Jami sahifalar
        callback_prefix: Callback prefix
        language: Til kodi
        
    Returns:
        InlineKeyboardMarkup: Sahifalash tugmalari
    """
    keyboard = []
    row = []
    
    # Previous button
    if current_page > 1:
        row.append(InlineKeyboardButton(
            "⬅️",
            callback_data=f"{callback_prefix}_{current_page - 1}"
        ))
    
    # Page indicator
    row.append(InlineKeyboardButton(
        f"{current_page}/{total_pages}",
        callback_data='current_page'
    ))
    
    # Next button
    if current_page < total_pages:
        row.append(InlineKeyboardButton(
            "➡️",
            callback_data=f"{callback_prefix}_{current_page + 1}"
        ))
    
    keyboard.append(row)
    
    # Back button
    back_texts = {
        'uz': '🔙 Orqaga qaytish',
        'ru': '🔙 Вернуться назад',
        'en': '🔙 Go Back',
        'tr': '🔙 Geri Dön',
        'ar': '🔙 العودة'
    }
    keyboard.append([
        InlineKeyboardButton(
            back_texts.get(language, back_texts['uz']),
            callback_data='back_main'
        )
    ])
    
    return InlineKeyboardMarkup(keyboard)


# =====================================================
# INCOME TYPE KEYBOARD
# =====================================================
def get_income_type_keyboard(language: str = 'uz') -> InlineKeyboardMarkup:
    """
    Daromad turi keyboard'i
    
    Args:
        language: Til kodi
        
    Returns:
        InlineKeyboardMarkup: Daromad turlari
    """
    texts = {
        'uz': {
            'salary': '💼 Oylik maosh',
            'bonus': '🎁 Bonus / Mukofot',
            'freelance': '💻 Frilanser daromadi',
            'investment': '📈 Investitsiya foydasi',
            'other': '📦 Boshqa daromad',
            'back': '🔙 Orqaga qaytish',
        },
        'ru': {
            'salary': '💼 Зарплата',
            'bonus': '🎁 Бонус / Премия',
            'freelance': '💻 Фриланс доход',
            'investment': '📈 Инвестиционный доход',
            'other': '📦 Прочий доход',
            'back': '🔙 Вернуться назад',
        },
        'en': {
            'salary': '💼 Salary',
            'bonus': '🎁 Bonus / Reward',
            'freelance': '💻 Freelance income',
            'investment': '📈 Investment returns',
            'other': '📦 Other income',
            'back': '🔙 Go Back',
        },
        'tr': {
            'salary': '💼 Maaş',
            'bonus': '🎁 Bonus / Prim',
            'freelance': '💻 Serbest meslek geliri',
            'investment': '📈 Yatırım geliri',
            'other': '📦 Diğer gelir',
            'back': '🔙 Geri Dön',
        },
        'ar': {
            'salary': '💼 راتب',
            'bonus': '🎁 مكافأة / علاوة',
            'freelance': '💻 دخل العمل الحر',
            'investment': '📈 عوائد الاستثمار',
            'other': '📦 دخل آخر',
            'back': '🔙 العودة',
        }
    }
    
    t = texts.get(language, texts['uz'])
    
    keyboard = [
        [InlineKeyboardButton(t['salary'], callback_data='income_type_salary')],
        [InlineKeyboardButton(t['bonus'], callback_data='income_type_bonus')],
        [InlineKeyboardButton(t['freelance'], callback_data='income_type_freelance')],
        [InlineKeyboardButton(t['investment'], callback_data='income_type_investment')],
        [InlineKeyboardButton(t['other'], callback_data='income_type_other')],
        [InlineKeyboardButton(t['back'], callback_data='back_main')],
    ]
    return InlineKeyboardMarkup(keyboard)


# =====================================================
# EDIT & CANCEL KEYBOARD FOR INCOME/EXPENSE
# =====================================================
def get_edit_cancel_keyboard(
    language: str = 'uz',
    item_type: str = 'expense',
    item_id: int = None
) -> InlineKeyboardMarkup:
    """
    Tahrirlash va Bekor qilish keyboard'i
    
    Args:
        language: Til kodi
        item_type: 'expense' yoki 'income'
        item_id: Element ID
        
    Returns:
        InlineKeyboardMarkup: Tahrirlash va Bekor qilish tugmalari
    """
    texts = {
        'uz': {
            'cancel': '🗑️ O\'chirish',
            'edit': '✏️ Tahrirlash',
        },
        'ru': {
            'cancel': '🗑️ Удалить',
            'edit': '✏️ Редактировать',
        },
        'en': {
            'cancel': '🗑️ Delete',
            'edit': '✏️ Edit',
        },
        'tr': {
            'cancel': '🗑️ Sil',
            'edit': '✏️ Düzenle',
        },
        'ar': {
            'cancel': '🗑️ حذف',
            'edit': '✏️ تعديل',
        }
    }
    
    t = texts.get(language, texts['uz'])
    
    keyboard = [
        [
            InlineKeyboardButton(
                t['cancel'], 
                callback_data=f'cancel_{item_type}_{item_id}'
            ),
            InlineKeyboardButton(
                t['edit'], 
                callback_data=f'edit_{item_type}_{item_id}'
            ),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)


# =====================================================
# DELETE DATA KEYBOARD
# =====================================================
def get_delete_data_keyboard(language: str = 'uz') -> InlineKeyboardMarkup:
    """
    Ma'lumot o'chirish keyboard'i - Daromad va Xarajatlar
    
    Args:
        language: Til kodi
        
    Returns:
        InlineKeyboardMarkup: Daromad va Xarajat tugmalari
    """
    texts = {
        'uz': {
            'expenses': '💳 Xarajatlar ro\'yxati',
            'incomes': '💰 Daromadlar ro\'yxati',
            'back': '🔙 Orqaga qaytish',
        },
        'ru': {
            'expenses': '💳 Список расходов',
            'incomes': '💰 Список доходов',
            'back': '🔙 Вернуться назад',
        },
        'en': {
            'expenses': '💳 Expenses List',
            'incomes': '💰 Incomes List',
            'back': '🔙 Go Back',
        },
        'tr': {
            'expenses': '💳 Gider Listesi',
            'incomes': '💰 Gelir Listesi',
            'back': '🔙 Geri Dön',
        },
        'ar': {
            'expenses': '💳 قائمة المصروفات',
            'incomes': '💰 قائمة الدخل',
            'back': '🔙 العودة',
        }
    }
    
    t = texts.get(language, texts['uz'])
    
    keyboard = [
        [InlineKeyboardButton(t['expenses'], callback_data='delete_expenses_list')],
        [InlineKeyboardButton(t['incomes'], callback_data='delete_incomes_list')],
        [InlineKeyboardButton(t['back'], callback_data='settings')],
    ]
    return InlineKeyboardMarkup(keyboard)


# =====================================================
# REPORT FORMAT CHOICE KEYBOARD
# =====================================================
def get_report_format_choice_keyboard(language: str = 'uz', report_type: str = 'daily') -> InlineKeyboardMarkup:
    """
    Hisobot formatini tanlash keyboard'i - Botda yoki HTML
    
    Args:
        language: Til kodi
        report_type: Hisobot turi
        
    Returns:
        InlineKeyboardMarkup: Botda va HTML tugmalari
    """
    texts = {
        'uz': {
            'bot': '📱 Shu yerda ko\'rish',
            'html': '🌐 HTML faylda yuklab olish',
            'back': '🔙 Orqaga qaytish',
        },
        'ru': {
            'bot': '📱 Показать здесь',
            'html': '🌐 Скачать HTML файл',
            'back': '🔙 Вернуться назад',
        },
        'en': {
            'bot': '📱 View here',
            'html': '🌐 Download HTML file',
            'back': '🔙 Go Back',
        },
        'tr': {
            'bot': '📱 Burada göster',
            'html': '🌐 HTML dosyası indir',
            'back': '🔙 Geri Dön',
        },
        'ar': {
            'bot': '📱 عرض هنا',
            'html': '🌐 تحميل ملف HTML',
            'back': '🔙 العودة',
        }
    }
    
    t = texts.get(language, texts['uz'])
    
    keyboard = [
        [InlineKeyboardButton(t['bot'], callback_data=f'report_bot_{report_type}')],
        [InlineKeyboardButton(t['html'], callback_data=f'report_html_{report_type}')],
        [InlineKeyboardButton(t['back'], callback_data='reports')],
    ]
    return InlineKeyboardMarkup(keyboard)


# =====================================================
# DEBT KEYBOARDS
# =====================================================
def get_debt_menu_keyboard(language: str = 'uz') -> InlineKeyboardMarkup:
    """Qarzlar menyu keyboard'i"""
    texts = {
        'uz': {
            'given': '📤 Qarz berdim',
            'taken': '📥 Qarz oldim',
            'my_given': '📊 Bergan qarzlarim',
            'my_taken': '📊 Olgan qarzlarim',
            'statistics': '📈 Statistika',
            'back': '🔙 Bosh menyuga qaytish',
        },
        'ru': {
            'given': '📤 Я дал долг',
            'taken': '📥 Я взял долг',
            'my_given': '📊 Выданные долги',
            'my_taken': '📊 Взятые долги',
            'statistics': '📈 Статистика',
            'back': '🔙 Вернуться в меню',
        },
        'en': {
            'given': '📤 I gave debt',
            'taken': '📥 I took debt',
            'my_given': '📊 Given debts',
            'my_taken': '📊 Taken debts',
            'statistics': '📈 Statistics',
            'back': '🔙 Back to menu',
        },
        'tr': {
            'given': '📤 Borç verdim',
            'taken': '📥 Borç aldım',
            'my_given': '📊 Verilen borçlar',
            'my_taken': '📊 Alınan borçlar',
            'statistics': '📈 İstatistikler',
            'back': '🔙 Menüye dön',
        },
        'ar': {
            'given': '📤 أقرضت',
            'taken': '📥 استلفت',
            'my_given': '📊 الديون المقدمة',
            'my_taken': '📊 الديون المستلمة',
            'statistics': '📈 الإحصائيات',
            'back': '🔙 العودة للقائمة',
        }
    }
    
    t = texts.get(language, texts['uz'])
    
    keyboard = [
        [InlineKeyboardButton(t['given'], callback_data='debt_add_given')],
        [InlineKeyboardButton(t['taken'], callback_data='debt_add_taken')],
        [InlineKeyboardButton(t['my_given'], callback_data='debt_list_given')],
        [InlineKeyboardButton(t['my_taken'], callback_data='debt_list_taken')],
        [InlineKeyboardButton(t['statistics'], callback_data='debt_statistics')],
        [InlineKeyboardButton(t['back'], callback_data='back_main')],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_debt_reminder_keyboard(language: str = 'uz') -> InlineKeyboardMarkup:
    """Qarz eslatma kunlari keyboard'i"""
    texts = {
        'uz': ['1 kun oldin', '3 kun oldin', '7 kun oldin', 'Eslatma kerak emas', 'Orqaga'],
        'ru': ['За 1 день', 'За 3 дня', 'За 7 дней', 'Не нужно', 'Назад'],
        'en': ['1 day before', '3 days before', '7 days before', 'No reminder', 'Back'],
        'tr': ['1 gün önce', '3 gün önce', '7 gün önce', 'Gerek yok', 'Geri'],
        'ar': ['قبل يوم', 'قبل 3 أيام', 'قبل 7 أيام', 'لا حاجة', 'رجوع']
    }
    
    t = texts.get(language, texts['uz'])
    
    keyboard = [
        [InlineKeyboardButton(t[0], callback_data='debt_reminder_1')],
        [InlineKeyboardButton(t[1], callback_data='debt_reminder_3')],
        [InlineKeyboardButton(t[2], callback_data='debt_reminder_7')],
        [InlineKeyboardButton(t[3], callback_data='debt_reminder_none')],
        [InlineKeyboardButton(t[4], callback_data='debt_cancel')],
    ]
    return InlineKeyboardMarkup(keyboard)


def get_debt_action_keyboard(language: str = 'uz', debt_id: int = None) -> InlineKeyboardMarkup:
    """Qarz tahrirlash/o'chirish keyboard'i"""
    texts = {
        'uz': {
            'paid_full': '✅ To\'liq to\'landi',
            'paid_partial': '💵 Qisman to\'landi',
            'edit': '✏️ Tahrirlash',
            'delete': '🗑️ O\'chirish',
            'back': '« Orqaga'
        },
        'ru': {
            'paid_full': '✅ Полностью оплачено',
            'paid_partial': '💵 Частично оплачено',
            'edit': '✏️ Редактировать',
            'delete': '🗑️ Удалить',
            'back': '« Назад'
        },
        'en': {
            'paid_full': '✅ Fully paid',
            'paid_partial': '💵 Partially paid',
            'edit': '✏️ Edit',
            'delete': '🗑️ Delete',
            'back': '« Back'
        },
        'tr': {
            'paid_full': '✅ Tamamen ödendi',
            'paid_partial': '💵 Kısmen ödendi',
            'edit': '✏️ Düzenle',
            'delete': '🗑️ Sil',
            'back': '« Geri'
        },
        'ar': {
            'paid_full': '✅ مدفوع بالكامل',
            'paid_partial': '💵 مدفوع جزئياً',
            'edit': '✏️ تعديل',
            'delete': '🗑️ حذف',
            'back': '« رجوع'
        }
    }
    
    t = texts.get(language, texts['uz'])
    
    keyboard = [
        [
            InlineKeyboardButton(t['paid_full'], callback_data=f'debt_paid_full_{debt_id}'),
            InlineKeyboardButton(t['paid_partial'], callback_data=f'debt_paid_partial_{debt_id}')
        ],
        [
            InlineKeyboardButton(t['edit'], callback_data=f'debt_edit_{debt_id}'),
            InlineKeyboardButton(t['delete'], callback_data=f'debt_delete_{debt_id}')
        ],
        [InlineKeyboardButton(t['back'], callback_data='debt_menu')]
    ]
    return InlineKeyboardMarkup(keyboard)

