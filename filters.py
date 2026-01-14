"""
SmartWallet AI Bot - Data Filters
=================================
Ma'lumotlarni filtrlash funksiyalari

Functions:
    - filter_by_date_range: Sana oralig'i bo'yicha
    - filter_by_category: Kategoriya bo'yicha
    - filter_by_amount_range: Summa oralig'i bo'yicha

Author: SmartWallet AI Team
Version: 1.0.0
"""

import logging
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
from decimal import Decimal

from database.models import Expense, Income

# Logger
logger = logging.getLogger(__name__)


# =====================================================
# DATE RANGE FILTER
# =====================================================
def filter_by_date_range(
    items: List[Any],
    start_date: Optional[datetime | date] = None,
    end_date: Optional[datetime | date] = None,
    date_field: str = 'expense_date'
) -> List[Any]:
    """
    Sana oralig'i bo'yicha filtrlash
    
    Args:
        items: Ob'ektlar ro'yxati (Expense, Income)
        start_date: Boshlanish sanasi
        end_date: Tugash sanasi
        date_field: Sana maydoni nomi
        
    Returns:
        List[Any]: Filtrlangan ro'yxat
    """
    if not items:
        return []
    
    filtered = items
    
    # Start date filtri
    if start_date:
        if isinstance(start_date, date) and not isinstance(start_date, datetime):
            start_date = datetime.combine(start_date, datetime.min.time())
        
        filtered = [
            item for item in filtered
            if hasattr(item, date_field) and getattr(item, date_field) >= start_date
        ]
    
    # End date filtri
    if end_date:
        if isinstance(end_date, date) and not isinstance(end_date, datetime):
            end_date = datetime.combine(end_date, datetime.max.time())
        
        filtered = [
            item for item in filtered
            if hasattr(item, date_field) and getattr(item, date_field) <= end_date
        ]
    
    logger.info(f"Date filter: {len(items)} → {len(filtered)} items")
    return filtered


# =====================================================
# CATEGORY FILTER
# =====================================================
def filter_by_category(
    expenses: List[Expense],
    category_keys: Optional[List[str]] = None
) -> List[Expense]:
    """
    Kategoriya bo'yicha filtrlash
    
    Args:
        expenses: Xarajatlar ro'yxati
        category_keys: Kategoriya key'lari (None = barchasi)
        
    Returns:
        List[Expense]: Filtrlangan xarajatlar
    """
    if not expenses:
        return []
    
    if not category_keys:
        return expenses
    
    filtered = [
        expense for expense in expenses
        if expense.category and expense.category.key in category_keys
    ]
    
    logger.info(f"Category filter: {len(expenses)} → {len(filtered)} items")
    return filtered


# =====================================================
# AMOUNT RANGE FILTER
# =====================================================
def filter_by_amount_range(
    items: List[Any],
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None,
    amount_field: str = 'amount'
) -> List[Any]:
    """
    Summa oralig'i bo'yicha filtrlash
    
    Args:
        items: Ob'ektlar ro'yxati
        min_amount: Minimal summa
        max_amount: Maksimal summa
        amount_field: Summa maydoni nomi
        
    Returns:
        List[Any]: Filtrlangan ro'yxat
    """
    if not items:
        return []
    
    filtered = items
    
    # Min amount filtri
    if min_amount is not None:
        filtered = [
            item for item in filtered
            if hasattr(item, amount_field) and getattr(item, amount_field) >= min_amount
        ]
    
    # Max amount filtri
    if max_amount is not None:
        filtered = [
            item for item in filtered
            if hasattr(item, amount_field) and getattr(item, amount_field) <= max_amount
        ]
    
    logger.info(f"Amount filter: {len(items)} → {len(filtered)} items")
    return filtered


# =====================================================
# DESCRIPTION SEARCH
# =====================================================
def filter_by_description(
    items: List[Any],
    search_text: str,
    description_field: str = 'description'
) -> List[Any]:
    """
    Tavsif bo'yicha qidirish
    
    Args:
        items: Ob'ektlar ro'yxati
        search_text: Qidiruv matni
        description_field: Tavsif maydoni nomi
        
    Returns:
        List[Any]: Topilgan ob'ektlar
    """
    if not items or not search_text:
        return items
    
    search_text = search_text.lower()
    
    filtered = [
        item for item in items
        if hasattr(item, description_field)
        and getattr(item, description_field)
        and search_text in getattr(item, description_field).lower()
    ]
    
    logger.info(f"Description search '{search_text}': {len(items)} → {len(filtered)} items")
    return filtered



# =====================================================
# DATE RANGE HELPERS
# =====================================================
def get_today_range() -> tuple:
    """Bugun (00:00 - 23:59)"""
    today = datetime.now().date()
    start = datetime.combine(today, datetime.min.time())
    end = datetime.combine(today, datetime.max.time())
    return start, end


def get_yesterday_range() -> tuple:
    """Kecha (00:00 - 23:59)"""
    yesterday = datetime.now().date() - timedelta(days=1)
    start = datetime.combine(yesterday, datetime.min.time())
    end = datetime.combine(yesterday, datetime.max.time())
    return start, end


def get_this_week_range() -> tuple:
    """Joriy hafta (dushanba - bugun)"""
    today = datetime.now().date()
    start = today - timedelta(days=today.weekday())  # Dushanba
    start_dt = datetime.combine(start, datetime.min.time())
    end_dt = datetime.combine(today, datetime.max.time())
    return start_dt, end_dt


def get_last_week_range() -> tuple:
    """O'tgan hafta (dushanba - yakshanba)"""
    today = datetime.now().date()
    last_week_end = today - timedelta(days=today.weekday() + 1)  # O'tgan yakshanba
    last_week_start = last_week_end - timedelta(days=6)  # O'tgan dushanba
    start_dt = datetime.combine(last_week_start, datetime.min.time())
    end_dt = datetime.combine(last_week_end, datetime.max.time())
    return start_dt, end_dt


def get_this_month_range() -> tuple:
    """Joriy oy (1-kun - bugun)"""
    today = datetime.now().date()
    start = today.replace(day=1)
    start_dt = datetime.combine(start, datetime.min.time())
    end_dt = datetime.combine(today, datetime.max.time())
    return start_dt, end_dt


def get_last_month_range() -> tuple:
    """O'tgan oy (1-kun - oxirgi kun)"""
    today = datetime.now().date()
    first_of_this_month = today.replace(day=1)
    last_month_end = first_of_this_month - timedelta(days=1)
    last_month_start = last_month_end.replace(day=1)
    start_dt = datetime.combine(last_month_start, datetime.min.time())
    end_dt = datetime.combine(last_month_end, datetime.max.time())
    return start_dt, end_dt


def get_this_year_range() -> tuple:
    """Joriy yil (1-yanvar - bugun)"""
    today = datetime.now().date()
    start = today.replace(month=1, day=1)
    start_dt = datetime.combine(start, datetime.min.time())
    end_dt = datetime.combine(today, datetime.max.time())
    return start_dt, end_dt


def get_last_n_days_range(days: int = 7) -> tuple:
    """Oxirgi N kun"""
    today = datetime.now().date()
    start = today - timedelta(days=days - 1)
    start_dt = datetime.combine(start, datetime.min.time())
    end_dt = datetime.combine(today, datetime.max.time())
    return start_dt, end_dt


def get_custom_range(start_date: date, end_date: date) -> tuple:
    """Maxsus sana oralig'i"""
    start_dt = datetime.combine(start_date, datetime.min.time())
    end_dt = datetime.combine(end_date, datetime.max.time())
    return start_dt, end_dt


# =====================================================
# SORTING
# =====================================================
def sort_by_date(items: List[Any], field: str = 'created_at', reverse: bool = True) -> List[Any]:
    """
    Sana bo'yicha saralash
    
    Args:
        items: Ob'ektlar
        field: Sana maydoni
        reverse: Teskari tartib (yangi birinchi)
        
    Returns:
        List[Any]: Saralangan ro'yxat
    """
    return sorted(items, key=lambda x: getattr(x, field, datetime.min), reverse=reverse)


def sort_by_amount(items: List[Any], field: str = 'amount', reverse: bool = True) -> List[Any]:
    """
    Summa bo'yicha saralash
    
    Args:
        items: Ob'ektlar
        field: Summa maydoni
        reverse: Teskari tartib (katta birinchi)
        
    Returns:
        List[Any]: Saralangan ro'yxat
    """
    return sorted(items, key=lambda x: getattr(x, field, 0), reverse=reverse)


# =====================================================
# GROUPING
# =====================================================
def group_by_date(items: List[Any], date_field: str = 'expense_date') -> Dict[date, List[Any]]:
    """
    Sana bo'yicha guruhlash
    
    Args:
        items: Ob'ektlar
        date_field: Sana maydoni
        
    Returns:
        Dict[date, List[Any]]: Guruhlar
    """
    groups = {}
    
    for item in items:
        if hasattr(item, date_field):
            item_date = getattr(item, date_field)
            if isinstance(item_date, datetime):
                item_date = item_date.date()
            
            if item_date not in groups:
                groups[item_date] = []
            groups[item_date].append(item)
    
    return groups


def group_by_category(expenses: List[Expense]) -> Dict[str, List[Expense]]:
    """
    Kategoriya bo'yicha guruhlash
    
    Args:
        expenses: Xarajatlar
        
    Returns:
        Dict[str, List[Expense]]: Guruhlar
    """
    groups = {}
    
    for expense in expenses:
        if expense.category:
            key = expense.category.key
            if key not in groups:
                groups[key] = []
            groups[key].append(expense)
    
    return groups


def group_by_month(items: List[Any], date_field: str = 'expense_date') -> Dict[str, List[Any]]:
    """
    Oy bo'yicha guruhlash
    
    Args:
        items: Ob'ektlar
        date_field: Sana maydoni
        
    Returns:
        Dict[str, List[Any]]: Guruhlar (key: 'YYYY-MM')
    """
    groups = {}
    
    for item in items:
        if hasattr(item, date_field):
            item_date = getattr(item, date_field)
            if isinstance(item_date, datetime):
                item_date = item_date.date()
            
            month_key = f"{item_date.year}-{item_date.month:02d}"
            
            if month_key not in groups:
                groups[month_key] = []
            groups[month_key].append(item)
    
    return groups


# =====================================================
# PAGINATION
# =====================================================
def paginate(items: List[Any], page: int = 1, per_page: int = 10) -> tuple:
    """
    Sahifalash
    
    Args:
        items: Ob'ektlar
        page: Sahifa raqami (1 dan boshlanadi)
        per_page: Har sahifada nechta
        
    Returns:
        tuple: (sahifa_items, jami_sahifalar, jami_items)
    """
    total_items = len(items)
    total_pages = (total_items + per_page - 1) // per_page
    
    if page < 1:
        page = 1
    if page > total_pages:
        page = total_pages
    
    start_idx = (page - 1) * per_page
    end_idx = start_idx + per_page
    
    page_items = items[start_idx:end_idx]
    
    return page_items, total_pages, total_items
