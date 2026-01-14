"""
SmartWallet AI Bot - Income Handler (Fixed)
===========================================
Daromad qo'shish handler'i - TO'LIQ TUZATILDI!

DAROMAD FAQAT INCOMES JADVALIGA QO'SHILADI!

Author: SmartWallet AI Team
Version: 2.0.0 - FIXED
"""

import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from database.db_manager import DatabaseManager
from keyboards.inline import get_income_type_keyboard, get_yes_no_keyboard, get_edit_cancel_keyboard
from states.user_states import INCOME_AMOUNT, INCOME_SOURCE, INCOME_TYPE, INCOME_CONFIRM
from utils.translations import get_text, format_currency, format_date, get_income_type_name
from utils.validators import validate_amount

logger = logging.getLogger(__name__)
db_manager = DatabaseManager()


async def add_income_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Daromad qo'shishni boshlash"""
    user_language = context.user_data.get('language', 'uz')
    
    prompt_texts = {
        'uz': """💰 <b>Daromad qo'shish</b>

Daromad summasini kiriting (so'm):

<i>Masalan: 5000000 Oylik</i>""",
        'ru': """💰 <b>Добавить доход</b>

Введите сумму дохода (сум):

<i>Например: 5000000</i>""",
        'en': """💰 <b>Add Income</b>

Enter income amount (UZS):

<i>Example: 5000000</i>"""
    }
    
    prompt = prompt_texts.get(user_language, prompt_texts['uz'])
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.message.reply_text(prompt, parse_mode='HTML')
    else:
        await update.message.reply_text(prompt, parse_mode='HTML')
    
    return INCOME_AMOUNT


async def income_amount_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Summa kiritish"""
    user_language = context.user_data.get('language', 'uz')
    text = update.message.text.strip()
    
    is_valid, amount, error = validate_amount(text)
    if not is_valid:
        await update.message.reply_text(f"❌ {error}\n\nQaytadan kiriting:")
        return INCOME_AMOUNT
    
    context.user_data['income_amount'] = amount
    
    prompt_texts = {
        'uz': """📝 <b>Daromad manbasi</b>

Daromad manbasini kiriting:

<i>Masalan: Oylik, Bonus, Freelance, va boshqalar</i>""",
        'ru': """📝 <b>Источник дохода</b>

Введите источник дохода:

<i>Например: Зарплата, Бонус, Фриланс, и т.д.</i>""",
        'en': """📝 <b>Income Source</b>

Enter income source:

<i>Example: Salary, Bonus, Freelance, etc.</i>"""
    }
    
    prompt = prompt_texts.get(user_language, prompt_texts['uz'])
    await update.message.reply_text(prompt, parse_mode='HTML')
    
    return INCOME_SOURCE


async def income_source_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Manba kiritish"""
    user_language = context.user_data.get('language', 'uz')
    source = update.message.text.strip()
    
    if len(source) < 2:
        await update.message.reply_text("❌ Manba kamida 2 ta harf bo'lishi kerak\n\nQaytadan kiriting:")
        return INCOME_SOURCE
    
    context.user_data['income_source'] = source
    
    prompt_texts = {
        'uz': '💼 Daromad turini tanlang:',
        'ru': '💼 Выберите тип дохода:',
        'en': '💼 Select income type:'
    }
    
    prompt = prompt_texts.get(user_language, prompt_texts['uz'])
    keyboard = get_income_type_keyboard(user_language)
    
    await update.message.reply_text(prompt, reply_markup=keyboard)
    
    return INCOME_TYPE


async def income_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Tur tanlash"""
    query = update.callback_query
    await query.answer()
    
    user_language = context.user_data.get('language', 'uz')
    
    if query.data.startswith('income_type_'):
        income_type = query.data.replace('income_type_', '')
        context.user_data['income_type'] = income_type
        
        # Tasdiqlash
        amount = context.user_data.get('income_amount')
        source = context.user_data.get('income_source')
        type_name = get_income_type_name(income_type, user_language)
        
        confirm_texts = {
            'uz': f"""📝 <b>DAROMADNI TASDIQLANG:</b>

💰 Summa: {amount:,.0f} so'm
📝 Manba: {source}
💼 Turi: {type_name}

⚠️ <b>DI QAT!</b> Bu DAROMAD, XARAJAT emas!
Bu summa umumiy DAROMADINGIZGA qo'shiladi.

Saqlashni xohlaysizmi?""",
            'ru': f"""📝 <b>ПОДТВЕРДИТЕ ДОХОД:</b>

💰 Сумма: {amount:,.0f} сум
📝 Источник: {source}
💼 Тип: {type_name}

⚠️ <b>ВНИМАНИЕ!</b> Это ДОХОД, не РАСХОД!
Эта сумма будет добавлена к вашему общему ДОХОДУ.

Хотите сохранить?""",
            'en': f"""📝 <b>CONFIRM INCOME:</b>

💰 Amount: {amount:,.0f} UZS
📝 Source: {source}
💼 Type: {type_name}

⚠️ <b>NOTE!</b> This is INCOME, not EXPENSE!
This amount will be added to your total INCOME.

Do you want to save?"""
        }
        
        confirm_text = confirm_texts.get(user_language, confirm_texts['uz'])
        keyboard = get_yes_no_keyboard(user_language, 'income_save', 'income_cancel')
        
        await query.edit_message_text(confirm_text, reply_markup=keyboard, parse_mode='HTML')
        
        return INCOME_CONFIRM
    
    return INCOME_TYPE


async def income_confirm_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Saqlash yoki bekor qilish"""
    query = update.callback_query
    await query.answer()
    
    user_language = context.user_data.get('language', 'uz')
    
    if query.data == 'income_cancel':
        cancel_texts = {
            'uz': '❌ Daromad qo\'shish bekor qilindi',
            'ru': '❌ Добавление дохода отменено',
            'en': '❌ Income adding cancelled'
        }
        cancel_msg = cancel_texts.get(user_language, cancel_texts['uz'])
        await query.edit_message_text(cancel_msg)
        return ConversationHandler.END
    
    elif query.data == 'income_save':
        telegram_id = context.user_data.get('telegram_id')
        amount = context.user_data.get('income_amount')
        source = context.user_data.get('income_source')
        income_type = context.user_data.get('income_type')
        
        # DAROMAD QO'SHISH - INCOMES JADVALIGA!
        logger.info(f"💰 DAROMAD QO'SHISH: user={telegram_id}, amount={amount}, source={source}, type={income_type}")
        
        income = db_manager.add_income(
            telegram_id=telegram_id,
            amount=amount,
            source=source,
            income_type=income_type,
            income_date=datetime.now()
        )
        
        if income:
            logger.info(f"✅ DAROMAD SAQLANDI: id={income.id}, amount={income.amount}")
            
            success_texts = {
                'uz': f"""✅ <b>DAROMAD MUVAFFAQIYATLI QO'SHILDI!</b>

💰 Summa: {amount:,.0f} so'm
📝 Manba: {source}
📅 Sana: {income.income_date.strftime('%d.%m.%Y %H:%M')}

✅ Bu summa umumiy DAROMADINGIZGA qo'shildi.
📊 Hisobotda daromad sifatida ko'rinadi.

💡 <i>Eslatma: Daromad va xarajat alohida hisoblanadi!</i>""",
                'ru': f"""✅ <b>ДОХОД УСПЕШНО ДОБАВЛЕН!</b>

💰 Сумма: {amount:,.0f} сум
📝 Источник: {source}
📅 Дата: {income.income_date.strftime('%d.%m.%Y %H:%M')}

✅ Эта сумма добавлена к вашему общему ДОХОДУ.
📊 В отчете будет показана как доход.

💡 <i>Примечание: Доход и расход считаются отдельно!</i>""",
                'en': f"""✅ <b>INCOME SUCCESSFULLY ADDED!</b>

💰 Amount: {amount:,.0f} UZS
📝 Source: {source}
📅 Date: {income.income_date.strftime('%d.%m.%Y %H:%M')}

✅ This amount has been added to your total INCOME.
📊 Will appear as income in reports.

💡 <i>Note: Income and expenses are calculated separately!</i>"""
            }
            
            success_msg = success_texts.get(user_language, success_texts['uz'])
            keyboard = get_edit_cancel_keyboard(user_language, 'income', income.id)
            await query.edit_message_text(success_msg, reply_markup=keyboard, parse_mode='HTML')
        else:
            logger.error(f"❌ DAROMAD SAQLANMADI: user={telegram_id}")
            
            error_texts = {
                'uz': '❌ Xatolik yuz berdi. Qaytadan urinib ko\'ring.',
                'ru': '❌ Произошла ошибка. Попробуйте снова.',
                'en': '❌ An error occurred. Please try again.'
            }
            error_msg = error_texts.get(user_language, error_texts['uz'])
            await query.edit_message_text(error_msg)
        
        return ConversationHandler.END
    
    return INCOME_CONFIRM


def setup_conversation_handler() -> ConversationHandler:
    """Income conversation handler"""
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(add_income_command, pattern='^add_income$'),
            CommandHandler('income', add_income_command),
        ],
        states={
            INCOME_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, income_amount_handler)],
            INCOME_SOURCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, income_source_handler)],
            INCOME_TYPE: [CallbackQueryHandler(income_type_handler, pattern='^income_type_')],
            INCOME_CONFIRM: [CallbackQueryHandler(income_confirm_handler, pattern='^(income_save|income_cancel)$')],
        },
        fallbacks=[CommandHandler('cancel', lambda u, c: ConversationHandler.END)],
        name="income_conversation",
        persistent=False,
    )
