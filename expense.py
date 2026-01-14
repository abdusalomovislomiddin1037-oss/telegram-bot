"""
SmartWallet AI Bot - Expense Handler
====================================
Xarajat qo'shish handler'i

Flow:
    1. Summa kiritish (AI parser)
    2. Kategoriya tanlash
    3. Tavsif (ixtiyoriy)
    4. Tasdiqlash va saqlash

Author: SmartWallet AI Team
Version: 1.0.0
"""

import logging
from decimal import Decimal
from datetime import datetime

from telegram import Update
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from config import Categories
from database.db_manager import DatabaseManager
from keyboards.inline import get_category_keyboard, get_yes_no_keyboard, get_back_button, get_edit_cancel_keyboard
from states.user_states import EXPENSE_AMOUNT, EXPENSE_CATEGORY, EXPENSE_DESCRIPTION, EXPENSE_CONFIRM, MAIN_MENU
from utils.ai_parser import parse_expense_text
from utils.translations import get_text, get_category_name, format_currency, format_date
from utils.validators import validate_amount

# Logger
logger = logging.getLogger(__name__)

# Database manager
db_manager = DatabaseManager()


# =====================================================
# ADD EXPENSE COMMAND
# =====================================================
async def add_expense_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Xarajat qo'shishni boshlash
    
    Args:
        update: Telegram update
        context: Callback context
        
    Returns:
        int: EXPENSE_AMOUNT state
    """
    user_language = context.user_data.get('language', 'uz')
    
    # Prompt matni
    prompt = get_text('expense_amount_prompt', user_language)
    
    # Xabar yuborish
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(
            text=prompt,
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            text=prompt,
            parse_mode='HTML'
        )
    
    logger.info(f"User {context.user_data.get('telegram_id')} xarajat qo'shishni boshladi")
    
    return EXPENSE_AMOUNT


# =====================================================
# EXPENSE AMOUNT HANDLER
# =====================================================
async def expense_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Summa kiritish va AI bilan tahlil qilish
    
    Args:
        update: Telegram update
        context: Callback context
        
    Returns:
        int: EXPENSE_CATEGORY state
    """
    user_language = context.user_data.get('language', 'uz')
    text = update.message.text
    
    # AI parser bilan tahlil qilish
    parsed = parse_expense_text(text)
    
    # Summa tekshirish
    if not parsed['amount']:
        error_msg = get_text('invalid_amount', user_language)
        await update.message.reply_text(error_msg)
        return EXPENSE_AMOUNT
    
    # Validatsiya
    is_valid, amount, error = validate_amount(parsed['amount'])
    if not is_valid:
        await update.message.reply_text(f"❌ {error}")
        return EXPENSE_AMOUNT
    
    # Context'ga saqlash
    context.user_data['expense_amount'] = amount
    context.user_data['expense_ai_category'] = parsed['category_key']
    context.user_data['expense_ai_description'] = parsed['description']
    context.user_data['expense_ai_confidence'] = parsed['confidence']
    
    logger.info(f"Expense amount: {amount}, AI category: {parsed['category_key']}, confidence: {parsed['confidence']}")
    
    # Agar AI kategoriya aniqlagan bo'lsa va confidence yuqori bo'lsa
    if parsed['category_key'] and parsed['confidence'] > 0.7:
        category_name = get_category_name(parsed['category_key'], user_language)
        
        # Kategoriya topildi - foydalanuvchiga tasdiqlash uchun so'rash
        category_obj = db_manager.get_category_by_key(parsed['category_key'])
        if category_obj:
            confirm_texts = {
                'uz': f"✅ AI kategoriya aniqladi:\n\n"
                      f"💰 Summa: {format_currency(amount, user_language)}\n"
                      f"📂 Kategoriya: {category_obj.icon} {category_name}\n\n"
                      f"To'g'rimi?",
                'ru': f"✅ AI определил категорию:\n\n"
                      f"💰 Сумма: {format_currency(amount, user_language)}\n"
                      f"📂 Категория: {category_obj.icon} {category_name}\n\n"
                      f"Правильно?",
                'en': f"✅ AI detected category:\n\n"
                      f"💰 Amount: {format_currency(amount, user_language)}\n"
                      f"📂 Category: {category_obj.icon} {category_name}\n\n"
                      f"Correct?",
                'tr': f"✅ AI kategori belirledi:\n\n"
                      f"💰 Tutar: {format_currency(amount, user_language)}\n"
                      f"📂 Kategori: {category_obj.icon} {category_name}\n\n"
                      f"Doğru mu?",
                'ar': f"✅ حدد الذكاء الاصطناعي الفئة:\n\n"
                      f"💰 المبلغ: {format_currency(amount, user_language)}\n"
                      f"📂 الفئة: {category_obj.icon} {category_name}\n\n"
                      f"صحيح؟"
            }
            
            keyboard = get_yes_no_keyboard(
                language=user_language,
                yes_callback='expense_confirm_category',
                no_callback='expense_choose_category'
            )
            
            await update.message.reply_text(
                text=confirm_texts.get(user_language, confirm_texts['uz']),
                reply_markup=keyboard
            )
            
            return EXPENSE_CATEGORY
    
    # Kategoriya topilmadi yoki confidence past - foydalanuvchi tanlaydi
    prompt = get_text('expense_category_prompt', user_language)
    keyboard = get_category_keyboard(language=user_language)
    
    await update.message.reply_text(
        text=prompt,
        reply_markup=keyboard
    )
    
    return EXPENSE_CATEGORY


# =====================================================
# EXPENSE CATEGORY HANDLER
# =====================================================
async def expense_category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Kategoriya tanlash
    
    Args:
        update: Telegram update
        context: Callback context
        
    Returns:
        int: EXPENSE_CONFIRM state
    """
    query = update.callback_query
    await query.answer()
    
    user_language = context.user_data.get('language', 'uz')
    callback_data = query.data
    
    # AI kategoriyani tasdiqlash
    if callback_data == 'expense_confirm_category':
        category_key = context.user_data.get('expense_ai_category')
    
    # Boshqa kategoriya tanlash
    elif callback_data == 'expense_choose_category':
        keyboard = get_category_keyboard(language=user_language)
        prompt = get_text('expense_category_prompt', user_language)
        
        await query.edit_message_text(
            text=prompt,
            reply_markup=keyboard
        )
        return EXPENSE_CATEGORY
    
    # Kategoriya tanlandi
    elif callback_data.startswith('category_'):
        category_key = callback_data.replace('category_', '')
    
    else:
        return EXPENSE_CATEGORY
    
    # Kategoriyani saqlash
    context.user_data['expense_category'] = category_key
    
    logger.info(f"Selected category: {category_key}")
    
    # Tavsif so'rash yoki to'g'ridan-to'g'ri tasdiqlashga o'tish
    # Agar AI tavsif aniqlagan bo'lsa, to'g'ridan-to'g'ri tasdiqlashga
    if context.user_data.get('expense_ai_description'):
        return await show_expense_confirmation(update, context)
    
    # Tavsif so'rash
    description_prompt = get_text('expense_description_prompt', user_language)
    
    skip_texts = {
        'uz': '⏭️ O\'tkazib yuborish',
        'ru': '⏭️ Пропустить',
        'en': '⏭️ Skip',
        'tr': '⏭️ Atla',
        'ar': '⏭️ تخطي'
    }
    
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(
            skip_texts.get(user_language, skip_texts['uz']),
            callback_data='expense_skip_description'
        )
    ]])
    
    await query.edit_message_text(
        text=description_prompt,
        reply_markup=keyboard
    )
    
    return EXPENSE_DESCRIPTION


# =====================================================
# EXPENSE DESCRIPTION HANDLER
# =====================================================
async def expense_description_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Tavsif kiritish (ixtiyoriy)
    
    Args:
        update: Telegram update
        context: Callback context
        
    Returns:
        int: EXPENSE_CONFIRM state
    """
    # Callback query (skip)
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        
        if query.data == 'expense_skip_description':
            context.user_data['expense_description'] = None
            return await show_expense_confirmation(update, context)
    
    # Text message (description)
    else:
        description = update.message.text.strip()
        context.user_data['expense_description'] = description
        
        return await show_expense_confirmation(update, context)
    
    return EXPENSE_CONFIRM


# =====================================================
# SHOW EXPENSE CONFIRMATION
# =====================================================
async def show_expense_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Xarajatni tasdiqlash ekranini ko'rsatish
    
    Args:
        update: Telegram update
        context: Callback context
        
    Returns:
        int: EXPENSE_CONFIRM state
    """
    user_language = context.user_data.get('language', 'uz')
    
    # Ma'lumotlarni olish
    amount = context.user_data.get('expense_amount')
    category_key = context.user_data.get('expense_category')
    description = context.user_data.get('expense_description') or context.user_data.get('expense_ai_description')
    
    # Kategoriya ma'lumotlari
    category_name = get_category_name(category_key, user_language)
    category_obj = db_manager.get_category_by_key(category_key)
    category_icon = category_obj.icon if category_obj else '📂'
    
    # Tasdiqlash matni
    confirm_texts = {
        'uz': f"📝 <b>Xarajatni tasdiqlang:</b>\n\n"
              f"💰 Summa: {format_currency(amount, user_language)}\n"
              f"📂 Kategoriya: {category_icon} {category_name}\n"
              f"📝 Tavsif: {description or '-'}\n\n"
              f"Saqlashni xohlaysizmi?",
        'ru': f"📝 <b>Подтвердите расход:</b>\n\n"
              f"💰 Сумма: {format_currency(amount, user_language)}\n"
              f"📂 Категория: {category_icon} {category_name}\n"
              f"📝 Описание: {description or '-'}\n\n"
              f"Сохранить?",
        'en': f"📝 <b>Confirm expense:</b>\n\n"
              f"💰 Amount: {format_currency(amount, user_language)}\n"
              f"📂 Category: {category_icon} {category_name}\n"
              f"📝 Description: {description or '-'}\n\n"
              f"Save?",
        'tr': f"📝 <b>Gideri onaylayın:</b>\n\n"
              f"💰 Tutar: {format_currency(amount, user_language)}\n"
              f"📂 Kategori: {category_icon} {category_name}\n"
              f"📝 Açıklama: {description or '-'}\n\n"
              f"Kaydet?",
        'ar': f"📝 <b>تأكيد المصروف:</b>\n\n"
              f"💰 المبلغ: {format_currency(amount, user_language)}\n"
              f"📂 الفئة: {category_icon} {category_name}\n"
              f"📝 الوصف: {description or '-'}\n\n"
              f"حفظ؟"
    }
    
    keyboard = get_yes_no_keyboard(
        language=user_language,
        yes_callback='expense_save',
        no_callback='expense_cancel'
    )
    
    # Xabar yuborish
    if update.callback_query:
        await update.callback_query.edit_message_text(
            text=confirm_texts.get(user_language, confirm_texts['uz']),
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            text=confirm_texts.get(user_language, confirm_texts['uz']),
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    
    return EXPENSE_CONFIRM


# =====================================================
# EXPENSE CONFIRM HANDLER
# =====================================================
async def expense_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Xarajatni saqlash yoki bekor qilish
    
    Args:
        update: Telegram update
        context: Callback context
        
    Returns:
        int: ConversationHandler.END
    """
    query = update.callback_query
    await query.answer()
    
    user_language = context.user_data.get('language', 'uz')
    callback_data = query.data
    
    # Bekor qilish
    if callback_data == 'expense_cancel':
        cancel_msg = get_text('process_cancelled', user_language)
        await query.edit_message_text(cancel_msg)
        
        # Context'ni tozalash
        _clear_expense_context(context)
        
        return ConversationHandler.END
    
    # Saqlash
    elif callback_data == 'expense_save':
        telegram_id = context.user_data.get('telegram_id')
        amount = context.user_data.get('expense_amount')
        category_key = context.user_data.get('expense_category')
        description = context.user_data.get('expense_description') or context.user_data.get('expense_ai_description')
        
        # Database'ga saqlash
        expense = db_manager.add_expense(
            telegram_id=telegram_id,
            amount=amount,
            category_key=category_key,
            description=description,
            expense_date=datetime.now()
        )
        
        if expense:
            # Muvaffaqiyatli xabar
            category_name = get_category_name(category_key, user_language)
            
            success_msg = get_text(
                'expense_added',
                user_language,
                amount=format_currency(amount, user_language),
                category=category_name,
                date=format_date(expense.expense_date, user_language, 'long')
            )
            
            keyboard = get_edit_cancel_keyboard(user_language, 'expense', expense.id)
            
            await query.edit_message_text(
                text=success_msg,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
            logger.info(f"Expense saved: user={telegram_id}, amount={amount}, category={category_key}")
        else:
            # Xato
            error_msg = get_text('error_occurred', user_language)
            await query.edit_message_text(error_msg)
        
        # Context'ni tozalash
        _clear_expense_context(context)
        
        return ConversationHandler.END
    
    return EXPENSE_CONFIRM


# =====================================================
# CANCEL HANDLER
# =====================================================
async def cancel_expense(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Xarajat qo'shishni bekor qilish
    
    Args:
        update: Telegram update
        context: Callback context
        
    Returns:
        int: ConversationHandler.END
    """
    user_language = context.user_data.get('language', 'uz')
    cancel_msg = get_text('process_cancelled', user_language)
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(cancel_msg)
    else:
        await update.message.reply_text(cancel_msg)
    
    _clear_expense_context(context)
    
    return ConversationHandler.END


# =====================================================
# HELPER FUNCTIONS
# =====================================================
def _clear_expense_context(context: ContextTypes.DEFAULT_TYPE):
    """Context'dan xarajat ma'lumotlarini tozalash"""
    keys_to_remove = [
        'expense_amount',
        'expense_category',
        'expense_description',
        'expense_ai_category',
        'expense_ai_description',
        'expense_ai_confidence'
    ]
    
    for key in keys_to_remove:
        context.user_data.pop(key, None)


# =====================================================
# CONVERSATION HANDLER SETUP
# =====================================================
def setup_conversation_handler() -> ConversationHandler:
    """
    Expense conversation handler'ni yaratish
    
    Returns:
        ConversationHandler: Configured handler
    """
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(add_expense_command, pattern='^add_expense$'),
            CommandHandler('expense', add_expense_command),
        ],
        states={
            EXPENSE_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, expense_amount_handler),
            ],
            EXPENSE_CATEGORY: [
                CallbackQueryHandler(expense_category_handler, pattern='^(category_|expense_confirm_category|expense_choose_category)'),
            ],
            EXPENSE_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, expense_description_handler),
                CallbackQueryHandler(expense_description_handler, pattern='^expense_skip_description$'),
            ],
            EXPENSE_CONFIRM: [
                CallbackQueryHandler(expense_confirm_handler, pattern='^(expense_save|expense_cancel)$'),
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel_expense),
            CallbackQueryHandler(cancel_expense, pattern='^cancel$'),
        ],
        name="expense_conversation",
        persistent=False,
    )
