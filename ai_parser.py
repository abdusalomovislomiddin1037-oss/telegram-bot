"""
SmartWallet AI Bot - AI Parser
==============================
Bepul AI matn tahlili (regex + pattern matching)

Matndan summa va kategoriya aniqlash:
- "50000 oziq-ovqat" → 50000, food
- "taxi 25000" → 25000, transport
- "non oldim 5000" → 5000, food

Functions:
    - parse_expense_text: Asosiy parser
    - extract_amount: Summa ajratish
    - detect_category: Kategoriya aniqlash
    - parse_date_text: Sana aniqlash

Author: SmartWallet AI Team
Version: 1.0.0
"""

import re
import logging
from typing import Optional, Tuple, Dict, Any
from decimal import Decimal
from datetime import datetime, timedelta, date

from config import Categories

# Logger
logger = logging.getLogger(__name__)


# =====================================================
# REGEX PATTERNS
# =====================================================
# Summa pattern'lari
AMOUNT_PATTERNS = [
    r'(\d+[\s,]?\d*)\s*so[\'m]?',  # 50000 so'm, 50000som
    r'(\d+[\s,]?\d*)\s*UZS',        # 50000 UZS
    r'(\d+[\s,]?\d*)\s*сум',        # 50000 сум (rus)
    r'(\d{1,3}(?:[\s,]\d{3})+)',    # 50 000 yoki 50,000
    r'(\d+)',                        # Oddiy raqam
]

# Sana pattern'lari
DATE_PATTERNS = [
    r'(\d{1,2})[./](\d{1,2})[./](\d{2,4})',  # DD.MM.YYYY
    r'(\d{1,2})\s+(yanvar|fevral|mart|aprel|may|iyun|iyul|avgust|sentabr|oktabr|noyabr|dekabr)',  # DD Month
]


# =====================================================
# PARSE EXPENSE TEXT
# =====================================================
def parse_expense_text(text: str) -> Dict[str, Any]:
    """
    Matnni tahlil qilish va summa + kategoriya aniqlash
    
    Args:
        text: Foydalanuvchi matni
        
    Returns:
        Dict: {
            'amount': Decimal | None,
            'category_key': str | None,
            'description': str | None,
            'confidence': float  # 0-1 oralig'ida
        }
    """
    result = {
        'amount': None,
        'category_key': None,
        'description': None,
        'confidence': 0.0
    }
    
    if not text:
        return result
    
    text = text.strip().lower()
    
    # Summa aniqlash
    amount = extract_amount(text)
    if amount:
        result['amount'] = amount
        result['confidence'] += 0.5
    
    # Kategoriya aniqlash
    category_key, category_confidence = detect_category(text)
    if category_key:
        result['category_key'] = category_key
        result['confidence'] += category_confidence * 0.5
    
    # Tavsif ajratish (summa va kategoriyadan tashqari qism)
    description = extract_description(text, amount, category_key)
    if description:
        result['description'] = description
    
    logger.info(f"Parsed text: '{text}' → Amount: {amount}, Category: {category_key}, Confidence: {result['confidence']:.2f}")
    
    return result


# =====================================================
# EXTRACT AMOUNT
# =====================================================
def extract_amount(text: str) -> Optional[Decimal]:
    """
    Matndan summa ajratish
    
    Args:
        text: Matn
        
    Returns:
        Optional[Decimal]: Summa yoki None
    """
    if not text:
        return None
    
    # Har bir pattern'ni sinab ko'rish
    for pattern in AMOUNT_PATTERNS:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            # Topilgan raqamni olish
            amount_str = match.group(1)
            
            # Bo'sh joy va vergullarni olib tashlash
            amount_str = amount_str.replace(' ', '').replace(',', '')
            
            try:
                amount = Decimal(amount_str)
                
                # Mantiqiy tekshirish (1 dan katta, 1 milliarddan kichik)
                if 1 <= amount <= 1_000_000_000:
                    return amount
            except (ValueError, ArithmeticError):
                continue
    
    return None


# =====================================================
# DETECT CATEGORY
# =====================================================
def detect_category(text: str) -> Tuple[Optional[str], float]:
    """
    Matndan kategoriya aniqlash
    
    Args:
        text: Matn
        
    Returns:
        Tuple[Optional[str], float]: (category_key, confidence)
    """
    if not text:
        return None, 0.0
    
    text = text.lower()
    
    # Har bir kategoriya uchun keyword matching
    category_scores = {}
    
    for category_key, keywords in Categories.KEYWORDS.items():
        score = 0
        matched_keywords = []
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            # To'liq so'z match (yuqori ball)
            if re.search(rf'\b{re.escape(keyword_lower)}\b', text):
                score += 10
                matched_keywords.append(keyword)
            
            # Qisman match (past ball)
            elif keyword_lower in text:
                score += 5
                matched_keywords.append(keyword)
        
        if score > 0:
            category_scores[category_key] = {
                'score': score,
                'keywords': matched_keywords
            }
    
    # Eng yuqori ball olgan kategoriyani tanlash
    if category_scores:
        best_category = max(category_scores.items(), key=lambda x: x[1]['score'])
        category_key = best_category[0]
        max_score = best_category[1]['score']
        
        # Confidence hisoblash (0-1 oralig'ida)
        # 10+ ball → 1.0 confidence
        confidence = min(max_score / 10.0, 1.0)
        
        logger.info(f"Category detected: {category_key} (confidence: {confidence:.2f}, keywords: {best_category[1]['keywords']})")
        return category_key, confidence
    
    # Agar kategoriya topilmasa, 'other'
    return 'other', 0.3


# =====================================================
# EXTRACT DESCRIPTION
# =====================================================
def extract_description(
    text: str,
    amount: Optional[Decimal],
    category_key: Optional[str]
) -> Optional[str]:
    """
    Matndan tavsif ajratish (summa va kategoriya so'zlarini olib tashlash)
    
    Args:
        text: Asl matn
        amount: Topilgan summa
        category_key: Topilgan kategoriya
        
    Returns:
        Optional[str]: Tavsif
    """
    if not text:
        return None
    
    description = text.lower()
    
    # Summa so'zlarini olib tashlash
    if amount:
        amount_str = str(amount).replace('.', '')
        description = re.sub(rf'\b{amount_str}\b', '', description, flags=re.IGNORECASE)
        description = re.sub(r'\bso[\'m]?\b', '', description, flags=re.IGNORECASE)
        description = re.sub(r'\bUZS\b', '', description, flags=re.IGNORECASE)
        description = re.sub(r'\bсум\b', '', description, flags=re.IGNORECASE)
    
    # Kategoriya keyword'larini olib tashlash
    if category_key and category_key in Categories.KEYWORDS:
        for keyword in Categories.KEYWORDS[category_key]:
            description = re.sub(rf'\b{re.escape(keyword.lower())}\b', '', description, flags=re.IGNORECASE)
    
    # Ortiqcha bo'sh joylarni tozalash
    description = re.sub(r'\s+', ' ', description).strip()
    
    # Agar tavsif juda qisqa yoki bo'sh bo'lsa, None qaytarish
    if len(description) < 3:
        return None
    
    return description.capitalize()


# =====================================================
# PARSE DATE TEXT
# =====================================================
def parse_date_text(text: str) -> Optional[date]:
    """
    Matndan sana aniqlash
    
    Args:
        text: Matn
        
    Returns:
        Optional[date]: Sana yoki None
    """
    if not text:
        return None
    
    text = text.strip().lower()
    
    # Maxsus so'zlar
    today = date.today()
    
    # "bugun", "today"
    if text in ['bugun', 'today', 'сегодня', 'bugün']:
        return today
    
    # "kecha", "yesterday"
    if text in ['kecha', 'yesterday', 'вчера', 'dün']:
        return today - timedelta(days=1)
    
    # "ertaga", "tomorrow"
    if text in ['ertaga', 'tomorrow', 'завтра', 'yarın']:
        return today + timedelta(days=1)
    
    # DD.MM.YYYY format
    match = re.search(r'(\d{1,2})[./](\d{1,2})[./](\d{2,4})', text)
    if match:
        try:
            day = int(match.group(1))
            month = int(match.group(2))
            year = int(match.group(3))
            
            # Yilni to'liq formatga keltirish
            if year < 100:
                year += 2000
            
            return date(year, month, day)
        except (ValueError, OverflowError):
            pass
    
    # "3 kun", "3 days"
    match = re.search(r'(\d+)\s*(kun|day|дня|дней|gün)', text)
    if match:
        days = int(match.group(1))
        return today + timedelta(days=days)
    
    # "2 hafta", "2 weeks"
    match = re.search(r'(\d+)\s*(hafta|week|недел|hafta)', text)
    if match:
        weeks = int(match.group(1))
        return today + timedelta(weeks=weeks)
    
    # "1 oy", "1 month"
    match = re.search(r'(\d+)\s*(oy|month|месяц|ay)', text)
    if match:
        months = int(match.group(1))
        # Soddalashtirilgan: 1 oy ≈ 30 kun
        return today + timedelta(days=months * 30)
    
    return None


# =====================================================
# VALIDATE AMOUNT
# =====================================================
def is_valid_amount(amount: Decimal) -> bool:
    """
    Summa to'g'riligini tekshirish
    
    Args:
        amount: Summa
        
    Returns:
        bool: To'g'ri summa
    """
    return 1 <= amount <= 1_000_000_000


# =====================================================
# NORMALIZE TEXT
# =====================================================
def normalize_text(text: str) -> str:
    """
    Matnni normallash (tozalash va standartlashtirish)
    
    Args:
        text: Asl matn
        
    Returns:
        str: Normallashgan matn
    """
    if not text:
        return ""
    
    # Ortiqcha bo'sh joylarni olib tashlash
    text = re.sub(r'\s+', ' ', text)
    
    # Bosh va oxiridagi bo'sh joylarni olib tashlash
    text = text.strip()
    
    return text


# =====================================================
# EXTRACT PERSON NAME (for debts)
# =====================================================
def extract_person_name(text: str) -> Optional[str]:
    """
    Matndan odam ismini ajratish (qarzlar uchun)
    
    Args:
        text: Matn
        
    Returns:
        Optional[str]: Ism
    """
    if not text:
        return None
    
    text = normalize_text(text)
    
    # Oddiy holat: matnning o'zi ism
    if len(text) > 2 and len(text) < 100:
        # Raqamlar yo'qligini tekshirish
        if not re.search(r'\d', text):
            return text.title()
    
    return None


# =====================================================
# SMART SUGGESTIONS
# =====================================================
def get_category_suggestions(text: str, top_n: int = 3) -> list:
    """
    Eng mos kategoriyalarni tavsiya qilish
    
    Args:
        text: Matn
        top_n: Nechta tavsiya
        
    Returns:
        list: [(category_key, confidence), ...]
    """
    text = text.lower()
    
    category_scores = {}
    
    for category_key, keywords in Categories.KEYWORDS.items():
        score = 0
        
        for keyword in keywords:
            keyword_lower = keyword.lower()
            
            if re.search(rf'\b{re.escape(keyword_lower)}\b', text):
                score += 10
            elif keyword_lower in text:
                score += 5
        
        if score > 0:
            confidence = min(score / 10.0, 1.0)
            category_scores[category_key] = confidence
    
    # Eng yuqori skorli kategoriyalarni tanlash
    sorted_categories = sorted(
        category_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )
    
    return sorted_categories[:top_n]


# =====================================================
# DETECT LANGUAGE
# =====================================================
def detect_language(text: str) -> str:
    """
    Matn tilini aniqlash (oddiy variant)
    
    Args:
        text: Matn
        
    Returns:
        str: Til kodi (uz, ru, en, tr, ar)
    """
    if not text:
        return 'uz'
    
    text = text.lower()
    
    # Kirill harflari → rus
    if re.search(r'[а-яё]', text):
        return 'ru'
    
    # Arab harflari
    if re.search(r'[\u0600-\u06FF]', text):
        return 'ar'
    
    # Ingliz/Turk/O'zbek - keyword bo'yicha
    uz_keywords = ['som', 'oziq', 'ovqat', 'kun', 'oy', 'yil']
    ru_keywords = ['сум', 'рубль', 'день', 'месяц']
    en_keywords = ['dollar', 'pound', 'day', 'month', 'year']
    tr_keywords = ['lira', 'gün', 'ay', 'yıl']
    
    for keyword in uz_keywords:
        if keyword in text:
            return 'uz'
    
    for keyword in ru_keywords:
        if keyword in text:
            return 'ru'
    
    for keyword in en_keywords:
        if keyword in text:
            return 'en'
    
    for keyword in tr_keywords:
        if keyword in text:
            return 'tr'
    
    # Default
    return 'uz'


# =====================================================
# FUZZY MATCH (for category keywords)
# =====================================================
def fuzzy_match(text: str, keyword: str, threshold: float = 0.8) -> bool:
    """
    Taxminiy match (typo'larga chidamli)
    
    Args:
        text: Matn
        keyword: Keyword
        threshold: Minimal o'xshashlik (0-1)
        
    Returns:
        bool: Match topildi
    """
    # Oddiy Levenshtein distance alternative
    # Agar uzunlik farqi katta bo'lsa, False
    len_diff = abs(len(text) - len(keyword))
    if len_diff > 3:
        return False
    
    # Oddiy substring match
    if keyword.lower() in text.lower():
        return True
    
    # Boshlanish match
    if text.lower().startswith(keyword[:3].lower()):
        return True
    
    return False


# =====================================================
# EXAMPLES
# =====================================================
def get_parser_examples(language: str = 'uz') -> list:
    """
    Parser misollari
    
    Args:
        language: Til kodi
        
    Returns:
        list: Misollar ro'yxati
    """
    examples = {
        'uz': [
            "50000 oziq-ovqat",
            "taxi 25000",
            "non oldim 5000",
            "15000SOM transport",
            "100000 kommunal to'lov",
        ],
        'ru': [
            "50000 продукты",
            "такси 25000",
            "купил хлеб 5000",
            "15000 транспорт",
            "100000 коммунальные",
        ],
        'en': [
            "50000 groceries",
            "taxi 25000",
            "bought bread 5000",
            "15000 transport",
            "100000 utilities",
        ],
        'tr': [
            "50000 gıda",
            "taksi 25000",
            "ekmek aldım 5000",
            "15000 ulaşım",
            "100000 faturalar",
        ],
        'ar': [
            "50000 بقالة",
            "تاكسي 25000",
            "اشتريت خبز 5000",
            "15000 نقل",
            "100000 فواتير",
        ]
    }
    
    return examples.get(language, examples['uz'])
