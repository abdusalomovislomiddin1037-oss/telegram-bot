"""
SmartWallet AI Bot - User States
================================
Conversation handler uchun barcha state'lar (FSM)

FSM - Finite State Machine
Har bir conversation jarayoni uchun state'lar

Author: SmartWallet AI Team
Version: 1.0.0
"""

# =====================================================
# START & MAIN MENU STATES
# =====================================================
SELECTING_LANGUAGE = 0
"""Til tanlash state'i"""

MAIN_MENU = 1
"""Asosiy menyu state'i"""


# =====================================================
# EXPENSE STATES
# =====================================================
EXPENSE_AMOUNT = 10
"""Xarajat summasini kiritish"""

EXPENSE_CATEGORY = 11
"""Xarajat kategoriyasini tanlash"""

EXPENSE_DESCRIPTION = 12
"""Xarajat tavsifini kiritish (ixtiyoriy)"""

EXPENSE_CONFIRM = 13
"""Xarajatni tasdiqlash"""


# =====================================================
# INCOME STATES
# =====================================================
INCOME_AMOUNT = 20
"""Daromad summasini kiritish"""

INCOME_SOURCE = 21
"""Daromad manbasini kiritish"""

INCOME_TYPE = 22
"""Daromad turini tanlash (oylik, bonus, va h.k.)"""

INCOME_RECURRING = 23
"""Daromad takrorlanuvchimi (oylik)"""

INCOME_CONFIRM = 24
"""Daromadni tasdiqlash"""


# =====================================================
# DEBT STATES
# =====================================================
DEBT_TYPE = 30
"""Qarz turi (bergan/olgan)"""

DEBT_PERSON = 31
"""Odam ismini kiritish"""

DEBT_AMOUNT = 32
"""Qarz summasini kiritish"""

DEBT_DUE_DATE = 33
"""Qaytarish sanasini kiritish"""

DEBT_REMINDER = 34
"""Eslatma kunlarini kiritish"""

DEBT_DESCRIPTION = 35
"""Qarz tavsifini kiritish (ixtiyoriy)"""

DEBT_CONFIRM = 36
"""Qarzni tasdiqlash"""

DEBT_PAYMENT = 37
"""Qarz to'lovini kiritish"""

DEBT_PAY_AMOUNT = 38
"""Qarz to'lov summasini kiritish"""


# =====================================================
# REPORT STATES
# =====================================================
REPORT_TYPE = 40
"""Hisobot turini tanlash"""

REPORT_CUSTOM_DATE = 41
"""Maxsus sana oralig'ini kiritish"""

REPORT_CATEGORY_FILTER = 42
"""Kategoriya filtri"""

EXPORT_FORMAT = 43
"""Eksport formatini tanlash (PDF/HTML/Excel)"""

DEVICE_TYPE = 44
"""Gadjet turini tanlash (telefon/planshet/PC)"""

REPORT_GENERATING = 45
"""Hisobot yaratilmoqda..."""


# =====================================================
# SETTINGS STATES
# =====================================================
SETTINGS_MENU = 50
"""Sozlamalar menyusi"""

NOTIFICATION_SETTINGS = 51
"""Eslatma sozlamalari"""

EXPORT_DATA = 52
"""Ma'lumotlarni eksport qilish"""

DELETE_DATA_CONFIRM = 53
"""Ma'lumotlarni o'chirishni tasdiqlash"""


# =====================================================
# SPECIAL STATES
# =====================================================
WAITING_INPUT = 60
"""Foydalanuvchi kiritishini kutish (umumiy)"""

PROCESSING = 61
"""Ma'lumot qayta ishlanmoqda"""

ERROR_STATE = 62
"""Xatolik yuz berdi"""


# =====================================================
# STATE DESCRIPTIONS (for debugging)
# =====================================================
STATE_DESCRIPTIONS = {
    # Start
    SELECTING_LANGUAGE: "Til tanlash",
    MAIN_MENU: "Asosiy menyu",
    
    # Expense
    EXPENSE_AMOUNT: "Xarajat summasi",
    EXPENSE_CATEGORY: "Xarajat kategoriyasi",
    EXPENSE_DESCRIPTION: "Xarajat tavsifi",
    EXPENSE_CONFIRM: "Xarajat tasdiqlash",
    
    # Income
    INCOME_AMOUNT: "Daromad summasi",
    INCOME_SOURCE: "Daromad manbasi",
    INCOME_TYPE: "Daromad turi",
    INCOME_RECURRING: "Daromad takrorlanishi",
    INCOME_CONFIRM: "Daromad tasdiqlash",
    
    # Debt
    DEBT_TYPE: "Qarz turi",
    DEBT_PERSON: "Odam ismi",
    DEBT_AMOUNT: "Qarz summasi",
    DEBT_DUE_DATE: "Qaytarish sanasi",
    DEBT_REMINDER: "Eslatma kunlari",
    DEBT_DESCRIPTION: "Qarz tavsifi",
    DEBT_CONFIRM: "Qarz tasdiqlash",
    DEBT_PAYMENT: "Qarz to'lovi",
    DEBT_PAY_AMOUNT: "Qarz to'lov summasi",
    
    # Report
    REPORT_TYPE: "Hisobot turi",
    REPORT_CUSTOM_DATE: "Maxsus sana",
    REPORT_CATEGORY_FILTER: "Kategoriya filtri",
    EXPORT_FORMAT: "Eksport format",
    DEVICE_TYPE: "Gadjet turi",
    REPORT_GENERATING: "Hisobot yaratilmoqda",
    
    # Settings
    SETTINGS_MENU: "Sozlamalar",
    NOTIFICATION_SETTINGS: "Eslatma sozlamalari",
    EXPORT_DATA: "Ma'lumotlarni eksport",
    DELETE_DATA_CONFIRM: "O'chirishni tasdiqlash",
    
    # Special
    WAITING_INPUT: "Kiritish kutilmoqda",
    PROCESSING: "Qayta ishlanmoqda",
    ERROR_STATE: "Xatolik holati",
}


def get_state_description(state: int) -> str:
    """
    State tavsifini olish (debugging uchun)
    
    Args:
        state: State raqami
        
    Returns:
        str: State tavsifi
    """
    return STATE_DESCRIPTIONS.get(state, f"Noma'lum state: {state}")


# =====================================================
# STATE GROUPS (for validation)
# =====================================================
START_STATES = {SELECTING_LANGUAGE, MAIN_MENU}
"""Boshlang'ich state'lar"""

EXPENSE_STATES = {
    EXPENSE_AMOUNT,
    EXPENSE_CATEGORY,
    EXPENSE_DESCRIPTION,
    EXPENSE_CONFIRM
}
"""Xarajat state'lari"""

INCOME_STATES = {
    INCOME_AMOUNT,
    INCOME_SOURCE,
    INCOME_TYPE,
    INCOME_RECURRING,
    INCOME_CONFIRM
}
"""Daromad state'lari"""

DEBT_STATES = {
    DEBT_TYPE,
    DEBT_PERSON,
    DEBT_AMOUNT,
    DEBT_DUE_DATE,
    DEBT_REMINDER,
    DEBT_DESCRIPTION,
    DEBT_CONFIRM,
    DEBT_PAYMENT,
    DEBT_PAY_AMOUNT
}
"""Qarz state'lari"""

REPORT_STATES = {
    REPORT_TYPE,
    REPORT_CUSTOM_DATE,
    REPORT_CATEGORY_FILTER,
    EXPORT_FORMAT,
    DEVICE_TYPE,
    REPORT_GENERATING
}
"""Hisobot state'lari"""

SETTINGS_STATES = {
    SETTINGS_MENU,
    NOTIFICATION_SETTINGS,
    EXPORT_DATA,
    DELETE_DATA_CONFIRM
}
"""Sozlamalar state'lari"""

ALL_STATES = (
    START_STATES |
    EXPENSE_STATES |
    INCOME_STATES |
    DEBT_STATES |
    REPORT_STATES |
    SETTINGS_STATES |
    {WAITING_INPUT, PROCESSING, ERROR_STATE}
)
"""Barcha state'lar"""


def is_valid_state(state: int) -> bool:
    """
    State to'g'riligini tekshirish
    
    Args:
        state: State raqami
        
    Returns:
        bool: To'g'ri state
    """
    return state in ALL_STATES


def get_state_group(state: int) -> str:
    """
    State qaysi guruhga tegishli ekanligini aniqlash
    
    Args:
        state: State raqami
        
    Returns:
        str: Guruh nomi
    """
    if state in START_STATES:
        return "START"
    elif state in EXPENSE_STATES:
        return "EXPENSE"
    elif state in INCOME_STATES:
        return "INCOME"
    elif state in DEBT_STATES:
        return "DEBT"
    elif state in REPORT_STATES:
        return "REPORT"
    elif state in SETTINGS_STATES:
        return "SETTINGS"
    elif state in {WAITING_INPUT, PROCESSING, ERROR_STATE}:
        return "SPECIAL"
    else:
        return "UNKNOWN"


# =====================================================
# STATE TRANSITIONS (allowed transitions)
# =====================================================
ALLOWED_TRANSITIONS = {
    # From MAIN_MENU
    MAIN_MENU: [
        EXPENSE_AMOUNT,
        INCOME_AMOUNT,
        DEBT_TYPE,
        REPORT_TYPE,
        SETTINGS_MENU,
        SELECTING_LANGUAGE
    ],
    
    # Expense flow
    EXPENSE_AMOUNT: [EXPENSE_CATEGORY, MAIN_MENU],
    EXPENSE_CATEGORY: [EXPENSE_DESCRIPTION, EXPENSE_CONFIRM, MAIN_MENU],
    EXPENSE_DESCRIPTION: [EXPENSE_CONFIRM, MAIN_MENU],
    EXPENSE_CONFIRM: [MAIN_MENU],
    
    # Income flow
    INCOME_AMOUNT: [INCOME_SOURCE, MAIN_MENU],
    INCOME_SOURCE: [INCOME_TYPE, MAIN_MENU],
    INCOME_TYPE: [INCOME_RECURRING, INCOME_CONFIRM, MAIN_MENU],
    INCOME_RECURRING: [INCOME_CONFIRM, MAIN_MENU],
    INCOME_CONFIRM: [MAIN_MENU],
    
    # Debt flow
    DEBT_TYPE: [DEBT_PERSON, MAIN_MENU],
    DEBT_PERSON: [DEBT_AMOUNT, MAIN_MENU],
    DEBT_AMOUNT: [DEBT_DUE_DATE, MAIN_MENU],
    DEBT_DUE_DATE: [DEBT_REMINDER, DEBT_DESCRIPTION, MAIN_MENU],
    DEBT_REMINDER: [DEBT_DESCRIPTION, DEBT_CONFIRM, MAIN_MENU],
    DEBT_DESCRIPTION: [DEBT_CONFIRM, MAIN_MENU],
    DEBT_CONFIRM: [MAIN_MENU],
    
    # Report flow
    REPORT_TYPE: [EXPORT_FORMAT, REPORT_CUSTOM_DATE, MAIN_MENU],
    REPORT_CUSTOM_DATE: [EXPORT_FORMAT, MAIN_MENU],
    EXPORT_FORMAT: [DEVICE_TYPE, REPORT_GENERATING, MAIN_MENU],
    DEVICE_TYPE: [REPORT_GENERATING, MAIN_MENU],
    REPORT_GENERATING: [MAIN_MENU],
}


def is_valid_transition(from_state: int, to_state: int) -> bool:
    """
    State o'tish to'g'riligini tekshirish
    
    Args:
        from_state: Joriy state
        to_state: Keyingi state
        
    Returns:
        bool: To'g'ri o'tish
    """
    allowed = ALLOWED_TRANSITIONS.get(from_state, [])
    return to_state in allowed or to_state == MAIN_MENU  # MAIN_MENU'ga har doim qaytish mumkin
