"""
SmartWallet AI Bot - Validators
===============================
Validatsiya funksiyalari

Functions:
    - validate_amount: Summa validatsiyasi
    - validate_date: Sana validatsiyasi
    - validate_telegram_id: Telegram ID validatsiyasi
    - sanitize_text: Matnni tozalash

Author: SmartWallet AI Team
Version: 1.0.0
"""

import re
import logging
from datetime import datetime, date
from decimal import Decimal, InvalidOperation
from typing import Optional, Tuple

from config import Validation

# Logger
logger = logging.getLogger(__name__)


# =====================================================
# VALIDATE AMOUNT
# =====================================================
def validate_amount(
    amount: Decimal | float | int | str,
    min_amount: Optional[Decimal] = None,
    max_amount: Optional[Decimal] = None
) -> Tuple[bool, Optional[Decimal], Optional[str]]:
    """
    Summa validatsiyasi
    
    Args:
        amount: Summa
        min_amount: Minimal summa
        max_amount: Maksimal summa
        
    Returns:
        Tuple[bool, Optional[Decimal], Optional[str]]: (valid, amount, error_message)
    """
    # Default qiymatlar
    if min_amount is None:
        min_amount = Decimal(str(Validation.MIN_AMOUNT))
    if max_amount is None:
        max_amount = Decimal(str(Validation.MAX_AMOUNT))
    
    try:
        # Decimal ga o'girish
        if isinstance(amount, str):
            # Bo'sh joylarni olib tashlash
            amount = amount.strip().replace(' ', '').replace(',', '')
        
        amount_decimal = Decimal(str(amount))
        
        # Musbat ekanligini tekshirish
        if amount_decimal <= 0:
            return False, None, "Summa musbat bo'lishi kerak"
        
        # Minimal va maksimal tekshirish
        if amount_decimal < min_amount:
            return False, None, f"Summa {min_amount} dan kichik bo'lishi mumkin emas"
        
        if amount_decimal > max_amount:
            return False, None, f"Summa {max_amount} dan katta bo'lishi mumkin emas"
        
        return True, amount_decimal, None
        
    except (ValueError, InvalidOperation) as e:
        logger.error(f"Amount validation error: {e}")
        return False, None, "Noto'g'ri summa formati"


# =====================================================
# VALIDATE DATE
# =====================================================
def validate_date(
    date_value: date | datetime | str,
    allow_future: bool = True,
    allow_past: bool = True,
    max_future_days: Optional[int] = None
) -> Tuple[bool, Optional[date], Optional[str]]:
    """
    Sana validatsiyasi
    
    Args:
        date_value: Sana
        allow_future: Kelajak sanaga ruxsat
        allow_past: O'tmish sanaga ruxsat
        max_future_days: Maksimal kelajak kunlar
        
    Returns:
        Tuple[bool, Optional[date], Optional[str]]: (valid, date, error_message)
    """
    try:
        # Date ga o'girish
        if isinstance(date_value, str):
            # DD.MM.YYYY formatni parse qilish
            match = re.match(r'(\d{1,2})[./](\d{1,2})[./](\d{2,4})', date_value.strip())
            if match:
                day = int(match.group(1))
                month = int(match.group(2))
                year = int(match.group(3))
                
                # Yilni to'liq formatga keltirish
                if year < 100:
                    year += 2000
                
                date_obj = date(year, month, day)
            else:
                return False, None, "Noto'g'ri sana formati. DD.MM.YYYY formatida kiriting"
        
        elif isinstance(date_value, datetime):
            date_obj = date_value.date()
        
        elif isinstance(date_value, date):
            date_obj = date_value
        
        else:
            return False, None, "Noto'g'ri sana turi"
        
        # Bugungi sana
        today = date.today()
        
        # Kelajak sanani tekshirish
        if not allow_future and date_obj > today:
            return False, None, "Kelajak sanasini kiritish mumkin emas"
        
        # O'tmish sanani tekshirish
        if not allow_past and date_obj < today:
            return False, None, "O'tmish sanasini kiritish mumkin emas"
        
        # Maksimal kelajak kunlar
        if max_future_days and date_obj > today:
            max_date = today + timedelta(days=max_future_days)
            if date_obj > max_date:
                return False, None, f"Sana {max_future_days} kundan ortiq kelajakda bo'lishi mumkin emas"
        
        return True, date_obj, None
        
    except (ValueError, OverflowError) as e:
        logger.error(f"Date validation error: {e}")
        return False, None, "Noto'g'ri sana"


# =====================================================
# VALIDATE TELEGRAM ID
# =====================================================
def validate_telegram_id(telegram_id: int | str) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Telegram ID validatsiyasi
    
    Args:
        telegram_id: Telegram user ID
        
    Returns:
        Tuple[bool, Optional[int], Optional[str]]: (valid, telegram_id, error_message)
    """
    try:
        # Int ga o'girish
        if isinstance(telegram_id, str):
            telegram_id = int(telegram_id.strip())
        
        # Musbat ekanligini tekshirish
        if telegram_id <= 0:
            return False, None, "Telegram ID musbat bo'lishi kerak"
        
        # Maksimal qiymat (Telegram limit ~10 billion)
        if telegram_id > 10_000_000_000:
            return False, None, "Telegram ID juda katta"
        
        return True, telegram_id, None
        
    except (ValueError, TypeError) as e:
        logger.error(f"Telegram ID validation error: {e}")
        return False, None, "Noto'g'ri Telegram ID"


# =====================================================
# SANITIZE TEXT
# =====================================================
def sanitize_text(
    text: str,
    max_length: Optional[int] = None,
    remove_html: bool = True,
    remove_urls: bool = False
) -> str:
    """
    Matnni tozalash va xavfsiz qilish
    
    Args:
        text: Asl matn
        max_length: Maksimal uzunlik
        remove_html: HTML teglarini olib tashlash
        remove_urls: URL'larni olib tashlash
        
    Returns:
        str: Tozalangan matn
    """
    if not text:
        return ""
    
    # Strip
    text = text.strip()
    
    # HTML teglarini olib tashlash
    if remove_html:
        text = re.sub(r'<[^>]+>', '', text)
    
    # URL'larni olib tashlash
    if remove_urls:
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    # Ortiqcha bo'sh joylarni olib tashlash
    text = re.sub(r'\s+', ' ', text)
    
    # Maksimal uzunlik
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


# =====================================================
# VALIDATE PERSON NAME
# =====================================================
def validate_person_name(name: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Odam ismi validatsiyasi
    
    Args:
        name: Ism
        
    Returns:
        Tuple[bool, Optional[str], Optional[str]]: (valid, name, error_message)
    """
    if not name:
        return False, None, "Ism bo'sh bo'lishi mumkin emas"
    
    # Tozalash
    name = sanitize_text(name, max_length=Validation.MAX_PERSON_NAME_LENGTH)
    
    # Uzunlik tekshirish
    if len(name) < 2:
        return False, None, "Ism juda qisqa (kamida 2 harf)"
    
    # Raqamlar yo'qligini tekshirish (ixtiyoriy)
    # if re.search(r'\d', name):
    #     return False, None, "Ismda raqam bo'lishi mumkin emas"
    
    return True, name.title(), None


# =====================================================
# VALIDATE DESCRIPTION
# =====================================================
def validate_description(description: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Tavsif validatsiyasi
    
    Args:
        description: Tavsif
        
    Returns:
        Tuple[bool, Optional[str], Optional[str]]: (valid, description, error_message)
    """
    if not description:
        return True, None, None  # Tavsif ixtiyoriy
    
    # Tozalash
    description = sanitize_text(description, max_length=Validation.MAX_DESCRIPTION_LENGTH)
    
    # Maksimal uzunlik
    if len(description) > Validation.MAX_DESCRIPTION_LENGTH:
        return False, None, f"Tavsif juda uzun (maksimal {Validation.MAX_DESCRIPTION_LENGTH} belgi)"
    
    return True, description, None


# =====================================================
# VALIDATE REMINDER DAYS
# =====================================================
def validate_reminder_days(days: int | str) -> Tuple[bool, Optional[int], Optional[str]]:
    """
    Eslatma kunlari validatsiyasi
    
    Args:
        days: Kunlar soni
        
    Returns:
        Tuple[bool, Optional[int], Optional[str]]: (valid, days, error_message)
    """
    try:
        # Int ga o'girish
        if isinstance(days, str):
            days = int(days.strip())
        
        # Musbat ekanligini tekshirish
        if days < 0:
            return False, None, "Kunlar soni manfiy bo'lishi mumkin emas"
        
        # Maksimal qiymat (30 kun)
        if days > 30:
            return False, None, "Kunlar soni 30 dan oshmasligi kerak"
        
        return True, days, None
        
    except (ValueError, TypeError) as e:
        logger.error(f"Reminder days validation error: {e}")
        return False, None, "Noto'g'ri kunlar soni"


# =====================================================
# VALIDATE PHONE NUMBER (optional)
# =====================================================
def validate_phone_number(phone: str) -> Tuple[bool, Optional[str], Optional[str]]:
    """
    Telefon raqami validatsiyasi (O'zbekiston)
    
    Args:
        phone: Telefon raqami
        
    Returns:
        Tuple[bool, Optional[str], Optional[str]]: (valid, phone, error_message)
    """
    if not phone:
        return False, None, "Telefon raqami bo'sh"
    
    # Tozalash (faqat raqamlar)
    phone = re.sub(r'[^\d+]', '', phone)
    
    # O'zbekiston formati: +998XXXXXXXXX
    if phone.startswith('+998'):
        if len(phone) == 13:
            return True, phone, None
        else:
            return False, None, "Noto'g'ri telefon raqami formati (+998XXXXXXXXX)"
    
    # 998XXXXXXXXX formatini +998XXXXXXXXX ga o'girish
    elif phone.startswith('998'):
        if len(phone) == 12:
            return True, f"+{phone}", None
        else:
            return False, None, "Noto'g'ri telefon raqami formati (998XXXXXXXXX)"
    
    # Local format: 9XXXXXXXX
    elif len(phone) == 9 and phone.startswith('9'):
        return True, f"+998{phone}", None
    
    else:
        return False, None, "Noto'g'ri telefon raqami formati"


# =====================================================
# IS VALID EMAIL (optional)
# =====================================================
def is_valid_email(email: str) -> bool:
    """
    Email validatsiyasi
    
    Args:
        email: Email manzil
        
    Returns:
        bool: To'g'ri email
    """
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))
