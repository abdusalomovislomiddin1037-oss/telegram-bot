"""
SmartWallet AI Bot - Quick Expense/Income Handler (Smart)
=========================================================
Tezkor xarajat/daromad qo'shish - AQLLI TIZIM!

AQLLI FUNKSIYALAR:
- "50000 ovqat" → Xarajatga qo'shiladi
- "5000000 oylik" → DAROMADGA qo'shiladi (avtomatik!)
- "3000000 maosh" → DAROMADGA qo'shiladi (avtomatik!)

Author: SmartWallet AI Team
Version: 3.0.0 - SMART AUTO-DETECTION
"""

import logging
import re
from datetime import datetime
from decimal import Decimal

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database.db_manager import DatabaseManager
from keyboards.inline import get_edit_cancel_keyboard
from utils.ai_parser import parse_expense_text
from utils.translations import get_text, get_category_name, format_currency, format_date
from utils.validators import validate_amount

# Logger
logger = logging.getLogger(__name__)

# Database manager
db_manager = DatabaseManager()

# State import
from states.user_states import MAIN_MENU


# =====================================================
# DAROMAD KALIT SO'ZLARI (INCOME KEYWORDS)
# =====================================================
INCOME_KEYWORDS = {
    'uz': ['oylik', 'maosh', 'ish haqi', 'daromad', 'kirim', 'oldi', 'bonus', 
           'freelance', 'freelans', 'mukofot', 'stipendiya', 'pension',
           'ustama', 'grant', 'investitsiya', 'foyda', 'daromat'],
    'ru': ['зарплата', 'оклад', 'доход', 'получил', 'бонус', 'фриланс',
           'премия', 'стипендия', 'пенсия', 'надбавка', 'грант',
           'инвестиция', 'прибыль'],
    'en': ['salary', 'wage', 'income', 'received', 'bonus', 'freelance',
           'reward', 'scholarship', 'pension', 'allowance', 'grant',
           'investment', 'profit']
}


def detect_income_keyword(text: str) -> tuple[bool, str]:
    """
    Matnda daromad kalit so'zini topish
    
    Args:
        text: Tekshiriladigan matn
        
    Returns:
        tuple: (topildi_mi, topilgan_so'z)
    """
    text_lower = text.lower()
    
    # Barcha tillardagi kalit so'zlarni tekshirish
    for lang_keywords in INCOME_KEYWORDS.values():
        for keyword in lang_keywords:
            if keyword in text_lower:
                logger.info(f"💰 DAROMAD SO'ZI TOPILDI: '{keyword}'")
                return True, keyword
    
    return False, ""


def extract_amount_from_text(text: str) -> Decimal:
    """
    Matndan summa ajratib olish
    
    Args:
        text: Matn
        
    Returns:
        Decimal: Summa yoki None
    """
    # Raqamlarni qidirish
    patterns = [
        r'(\d+[\s,]?\d*)\s*so[\'m]?',  # 50000 so'm
        r'(\d+[\s,]?\d*)\s*UZS',        # 50000 UZS
        r'(\d{1,3}(?:[\s,]\d{3})+)',    # 50 000 yoki 50,000
        r'(\d+)',                        # Oddiy raqam
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            amount_str = match.group(1).replace(' ', '').replace(',', '')
            try:
                return Decimal(amount_str)
            except:
                continue
    
    return None


def extract_source_from_text(text: str, found_keyword: str) -> str:
    """
    Matndan daromad manbasini aniqlash
    
    Args:
        text: Matn
        found_keyword: Topilgan kalit so'z
        
    Returns:
        str: Manba
    """
    # Agar kalit so'z bor bo'lsa, uni manba sifatida ishlatish
    if found_keyword:
        return found_keyword.capitalize()
    
    # Aks holda, umumiy
    return "Daromad"


# =====================================================
# QUICK EXPENSE/INCOME HANDLER
# =====================================================
async def quick_expense_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    AQLLI TEZKOR QO'SHISH:
    - Agar "oylik", "maosh" kabi so'zlar bo'lsa → DAROMADGA qo'shadi
    - Aks holda → XARAJATGA qo'shadi
    
    Args:
        update: Telegram update
        context: Callback context
        
    Returns:
        int: MAIN_MENU state
    """
    user_language = context.user_data.get('language', 'uz')
    text = update.message.text
    
    # Faqat foydalanuvchi ro'yxatdan o'tgan bo'lsa ishlaydi
    if 'telegram_id' not in context.user_data:
        return MAIN_MENU
    
    telegram_id = context.user_data.get('telegram_id')
    
    # =====================================================
    # 1. DAROMAD TEKSHIRUVI
    # =====================================================
    is_income, found_keyword = detect_income_keyword(text)
    
    if is_income:
        logger.info(f"💰 DAROMAD ANIQLANDI: '{found_keyword}' - avtomatik daromadga qo'shiladi!")
        
        # Summa ajratib olish
        amount = extract_amount_from_text(text)
        
        if not amount or amount <= 0:
            hint_texts = {
                'uz': """ℹ️ Daromad summasi topilmadi!

Iltimos, to'g'ri formatda yozing:
📝 Masalan: "5000000 oylik" yoki "3000000 maosh"

Yoki "💰 Daromad qo'shish" tugmasini bosing.""",
                'ru': """ℹ️ Сумма дохода не найдена!

Пожалуйста, напишите в правильном формате:
📝 Например: "5000000 зарплата" или "3000000 оклад"

Или нажмите "💰 Добавить доход".""",
            }
            await update.message.reply_text(hint_texts.get(user_language, hint_texts['uz']))
            return MAIN_MENU
        
        # Manba aniqlash
        source = extract_source_from_text(text, found_keyword)
        
        # DAROMAD QO'SHISH
        logger.info(f"💰 AVTOMATIK DAROMAD: user={telegram_id}, amount={amount}, source={source}")
        
        try:
            income = db_manager.add_income(
                telegram_id=telegram_id,
                amount=amount,
                source=source,
                income_type='salary' if found_keyword in ['oylik', 'maosh', 'зарплата', 'salary'] else 'other',
                income_date=datetime.now()
            )
            
            if income:
                logger.info(f"✅ DAROMAD SAQLANDI: id={income.id}, amount={income.amount}")
                
                success_texts = {
                    'uz': f"""✅ <b>DAROMAD QO'SHILDI!</b>

💰 Summa: {amount:,.0f} so'm
📝 Manba: {source}
📅 Sana: {income.income_date.strftime('%d.%m.%Y %H:%M')}

✅ Bu summa umumiy DAROMADINGIZGA qo'shildi!

💡 <i>Keyingi safar ham shunday yozing va avtomatik qo'shiladi!</i>""",
                    'ru': f"""✅ <b>ДОХОД ДОБАВЛЕН!</b>

💰 Сумма: {amount:,.0f} сум
📝 Источник: {source}
📅 Дата: {income.income_date.strftime('%d.%m.%Y %H:%M')}

✅ Эта сумма добавлена к вашему общему ДОХОДУ!

💡 <i>В следующий раз пишите также и будет добавлено автоматически!</i>""",
                }
                
                success_msg = success_texts.get(user_language, success_texts['uz'])
                
                # BEKOR QILISH VA TAHRIRLASH TUGMALARI
                keyboard = get_edit_cancel_keyboard(user_language, 'income', income.id)
                
                await update.message.reply_text(
                    success_msg,
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            else:
                logger.error(f"❌ DAROMAD SAQLANMADI: user={telegram_id}")
                await update.message.reply_text("❌ Xatolik yuz berdi")
                
        except Exception as e:
            logger.error(f"Daromad qo'shishda xato: {e}", exc_info=True)
            await update.message.reply_text("❌ Xatolik yuz berdi")
        
        return MAIN_MENU
    
    # =====================================================
    # 2. XARAJAT QISMI (agar daromad emas bo'lsa)
    # =====================================================
    
    # AI parser bilan tahlil qilish
    parsed = parse_expense_text(text)
    
    # Agar summa va kategoriya topilmasa, oddiy xabar deb qaytarish
    if not parsed['amount'] or not parsed['category_key']:
        return MAIN_MENU
    
    # Summa validatsiyasi
    is_valid, amount, error = validate_amount(parsed['amount'])
    if not is_valid:
        return MAIN_MENU
    
    # Agar confidence juda past bo'lsa, xarajat emas deb qaytarish
    if parsed['confidence'] < 0.5:
        return MAIN_MENU
    
    category_key = parsed['category_key']
    description = parsed['description']
    
    # XARAJAT QO'SHISH
    logger.info(f"💸 AVTOMATIK XARAJAT: user={telegram_id}, amount={amount}, category={category_key}")
    
    try:
        expense = db_manager.add_expense(
            telegram_id=telegram_id,
            amount=amount,
            category_key=category_key,
            description=description,
            expense_date=datetime.now()
        )
        
        if expense:
            logger.info(f"✅ XARAJAT SAQLANDI: id={expense.id}, amount={expense.amount}")
            
            # Kategoriya ma'lumotlari
            category_name = get_category_name(category_key, user_language)
            category_obj = db_manager.get_category_by_key(category_key)
            category_icon = category_obj.icon if category_obj else '📂'
            
            # Muvaffaqiyat xabari
            success_messages = {
                'uz': f"""✅ <b>XARAJAT QO'SHILDI!</b>

{category_icon} Kategoriya: {category_name}
💸 Summa: {format_currency(amount, user_language)}
📝 Tavsif: {description if description else '-'}
📅 Sana: {expense.expense_date.strftime('%d.%m.%Y %H:%M')}

✅ Bu summa umumiy XARAJATLARINGIZGA qo'shildi.""",
                'ru': f"""✅ <b>РАСХОД ДОБАВЛЕН!</b>

{category_icon} Категория: {category_name}
💸 Сумма: {format_currency(amount, user_language)}
📝 Описание: {description if description else '-'}
📅 Дата: {expense.expense_date.strftime('%d.%m.%Y %H:%M')}

✅ Эта сумма добавлена к вашим общим РАСХОДАМ.""",
            }
            
            success_msg = success_messages.get(user_language, success_messages['uz'])
            
            # BEKOR QILISH VA TAHRIRLASH TUGMALARI
            keyboard = get_edit_cancel_keyboard(user_language, 'expense', expense.id)
            
            await update.message.reply_text(
                success_msg,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        else:
            logger.error(f"❌ XARAJAT SAQLANMADI: user={telegram_id}")
            
    except Exception as e:
        logger.error(f"Xarajat qo'shishda xato: {e}", exc_info=True)
    
    return MAIN_MENU


# =====================================================
# DELETE EXPENSE HANDLER
# =====================================================
async def delete_quick_expense_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Tezkor qo'shilgan xarajatni o'chirish
    """
    query = update.callback_query
    await query.answer()
    
    user_language = context.user_data.get('language', 'uz')
    telegram_id = context.user_data.get('telegram_id')
    
    # Expense ID ni olish
    expense_id = int(query.data.replace('delete_expense_', ''))
    
    # O'chirish
    success = db_manager.delete_expense(expense_id, telegram_id)
    
    if success:
        delete_messages = {
            'uz': '✅ Xarajat o\'chirildi',
            'ru': '✅ Расход удалён',
            'en': '✅ Expense deleted'
        }
        await query.edit_message_text(delete_messages.get(user_language, delete_messages['uz']))
    else:
        error_messages = {
            'uz': '❌ Xatolik yuz berdi',
            'ru': '❌ Произошла ошибка',
            'en': '❌ An error occurred'
        }
        await query.edit_message_text(error_messages.get(user_language, error_messages['uz']))
