"""
SmartWallet AI Bot - Debt Handler (Inline Only)
================================================
Qarz boshqarish - FAQAT inline button'lar orqali

Flow: HAMMA NARSA inline keyboard'lar orqali

Author: SmartWallet AI Team  
Version: 2.0.0 - Inline Only
"""

import logging
from decimal import Decimal
from datetime import datetime, date, timedelta
import re

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ForceReply
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from database.db_manager import DatabaseManager
from keyboards.inline import (
    get_debt_menu_keyboard,
    get_debt_reminder_keyboard,
    get_debt_action_keyboard,
    get_yes_no_keyboard
)
from states.user_states import MAIN_MENU
from utils.translations import get_text, format_currency, format_date
from utils.validators import validate_amount

# Logger
logger = logging.getLogger(__name__)

# Database manager
db_manager = DatabaseManager()


# State for inline data entry
WAITING_DEBT_DATA = 999  # Special state


# =====================================================
# DEBT MENU
# =====================================================
async def debt_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Qarzlar menyusi"""
    query = update.callback_query if update.callback_query else None
    if query:
        await query.answer()
    
    language = context.user_data.get('language', 'uz')
    
    menu_text = get_text('debt_menu', language)
    keyboard = get_debt_menu_keyboard(language)
    
    if query:
        try:
            await query.edit_message_text(
                text=menu_text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
        except:
            await query.message.reply_text(
                text=menu_text,
                reply_markup=keyboard,
                parse_mode='HTML'
            )
    else:
        await update.message.reply_text(
            text=menu_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    
    return MAIN_MENU


# =====================================================
# ADD DEBT - START
# =====================================================
async def add_debt_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Qarz qo'shishni boshlash"""
    query = update.callback_query
    await query.answer()
    
    language = context.user_data.get('language', 'uz')
    
    # Qarz turini saqlash
    if 'debt_add_given' in query.data:
        context.user_data['debt_type'] = 'given'
        debt_type_text = {'uz': '📤 Qarz berdim', 'ru': '📤 Я дал долг', 'en': '📤 I gave debt', 'tr': '📤 Borç verdim', 'ar': '📤 أقرضت'}
    else:
        context.user_data['debt_type'] = 'taken'
        debt_type_text = {'uz': '📥 Qarz oldim', 'ru': '📥 Я взял долг', 'en': '📥 I took debt', 'tr': '📥 Borç aldım', 'ar': '📥 استلفت'}
    
    # Reset context
    context.user_data['debt_step'] = 'person'
    
    # Shaxs ismini so'rash - inline input
    texts = {
        'uz': f"{debt_type_text['uz']}\n\n👤 <b>Shaxs ismini kiriting:</b>\n\n💡 Misol: Ali Valiyev\n\n<i>Quyidagi xabarda yozing</i>",
        'ru': f"{debt_type_text['ru']}\n\n👤 <b>Введите имя человека:</b>\n\n💡 Например: Али Валиев\n\n<i>Напишите в следующем сообщении</i>",
        'en': f"{debt_type_text['en']}\n\n👤 <b>Enter person name:</b>\n\n💡 Example: Ali Valiev\n\n<i>Write in next message</i>",
        'tr': f"{debt_type_text['tr']}\n\n👤 <b>Kişi adını girin:</b>\n\n💡 Örnek: Ali Valiyev\n\n<i>Sonraki mesajda yazın</i>",
        'ar': f"{debt_type_text['ar']}\n\n👤 <b>أدخل اسم الشخص:</b>\n\n💡 مثال: علي فاليف\n\n<i>اكتب في الرسالة التالية</i>"
    }
    
    cancel_btn = {'uz': '❌ Bekor qilish', 'ru': '❌ Отмена', 'en': '❌ Cancel', 'tr': '❌ İptal', 'ar': '❌ إلغاء'}
    
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(cancel_btn.get(language, cancel_btn['uz']), callback_data='debt_cancel')
    ]])
    
    await query.edit_message_text(
        text=texts.get(language, texts['uz']),
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    return WAITING_DEBT_DATA


# =====================================================
# DEBT DATA INPUT HANDLER
# =====================================================
async def debt_data_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Qarz ma'lumotlarini kiritish (text message)"""
    
    # Agar context'da debt_step yo'q bo'lsa, ignore qilish
    if 'debt_step' not in context.user_data:
        return MAIN_MENU
    
    language = context.user_data.get('language', 'uz')
    step = context.user_data.get('debt_step')
    text = update.message.text.strip()
    
    # STEP 1: Person name
    if step == 'person':
        if len(text) < 2 or len(text) > 255:
            await update.message.reply_text("❌ Iltimos, to'g'ri ism kiriting (2-255 belgi)!")
            return WAITING_DEBT_DATA
        
        context.user_data['debt_person'] = text
        context.user_data['debt_step'] = 'amount'
        
        # Summa so'rash
        texts = {
            'uz': '💰 <b>Qarz summasini kiriting:</b>\n\n💡 Misol: 500000',
            'ru': '💰 <b>Введите сумму долга:</b>\n\n💡 Например: 500000',
            'en': '💰 <b>Enter debt amount:</b>\n\n💡 Example: 500000',
            'tr': '💰 <b>Borç tutarını girin:</b>\n\n💡 Örnek: 500000',
            'ar': '💰 <b>أدخل مبلغ الدين:</b>\n\n💡 مثال: 500000'
        }
        
        cancel_btn = {'uz': '❌ Bekor qilish', 'ru': '❌ Отмена', 'en': '❌ Cancel', 'tr': '❌ İptal', 'ar': '❌ إلغاء'}
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(cancel_btn.get(language, cancel_btn['uz']), callback_data='debt_cancel')
        ]])
        
        await update.message.reply_text(
            text=texts.get(language, texts['uz']),
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        return WAITING_DEBT_DATA
    
    # STEP 2: Amount
    elif step == 'amount':
        is_valid, amount, error = validate_amount(text)
        if not is_valid:
            await update.message.reply_text(f"❌ {error}")
            return WAITING_DEBT_DATA
        
        context.user_data['debt_amount'] = amount
        context.user_data['debt_step'] = 'due_date'
        
        # Sana so'rash - inline buttons
        texts = {
            'uz': '📅 <b>Qaytarish sanasini tanlang:</b>',
            'ru': '📅 <b>Выберите дату возврата:</b>',
            'en': '📅 <b>Select due date:</b>',
            'tr': '📅 <b>İade tarihini seçin:</b>',
            'ar': '📅 <b>اختر تاريخ الاستحقاق:</b>'
        }
        
        # Tezkor sanalar
        today = date.today()
        dates = [
            (today + timedelta(days=7), '7 kun'),
            (today + timedelta(days=14), '14 kun'),
            (today + timedelta(days=30), '1 oy'),
            (today + timedelta(days=90), '3 oy'),
        ]
        
        keyboard_buttons = []
        for dt, label in dates:
            btn_labels = {
                '7 kun': {'uz': '7 kun', 'ru': '7 дн.', 'en': '7 days', 'tr': '7 gün', 'ar': '7 أيام'},
                '14 kun': {'uz': '14 kun', 'ru': '14 дн.', 'en': '14 days', 'tr': '14 gün', 'ar': '14 يوم'},
                '1 oy': {'uz': '1 oy', 'ru': '1 мес.', 'en': '1 month', 'tr': '1 ay', 'ar': 'شهر'},
                '3 oy': {'uz': '3 oy', 'ru': '3 мес.', 'en': '3 months', 'tr': '3 ay', 'ar': '3 أشهر'},
            }
            btn_text = f"{btn_labels[label].get(language, label)} ({dt.strftime('%d.%m')})"
            keyboard_buttons.append([
                InlineKeyboardButton(btn_text, callback_data=f'debt_date_{dt.isoformat()}')
            ])
        
        skip_btn = {'uz': '⏭️ Sana kerak emas', 'ru': '⏭️ Дата не нужна', 'en': '⏭️ No date', 'tr': '⏭️ Tarih gerek yok', 'ar': '⏭️ لا تاريخ'}
        cancel_btn = {'uz': '❌ Bekor qilish', 'ru': '❌ Отмена', 'en': '❌ Cancel', 'tr': '❌ İptal', 'ar': '❌ إلغاء'}
        
        keyboard_buttons.append([InlineKeyboardButton(skip_btn.get(language, skip_btn['uz']), callback_data='debt_date_skip')])
        keyboard_buttons.append([InlineKeyboardButton(cancel_btn.get(language, cancel_btn['uz']), callback_data='debt_cancel')])
        
        await update.message.reply_text(
            text=texts.get(language, texts['uz']),
            reply_markup=InlineKeyboardMarkup(keyboard_buttons),
            parse_mode='HTML'
        )
        return WAITING_DEBT_DATA
    
    # STEP 3: Description (optional)
    elif step == 'description':
        if text != '/skip' and len(text) > 500:
            await update.message.reply_text("❌ Tavsif juda uzun! (max 500 belgi)")
            return WAITING_DEBT_DATA
        
        context.user_data['debt_description'] = None if text == '/skip' else text
        
        # Tasdiqlash
        return await show_debt_confirmation(update, context)
    
    return WAITING_DEBT_DATA


# =====================================================
# DEBT DATE HANDLER
# =====================================================
async def debt_date_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Sana tanlash"""
    query = update.callback_query
    await query.answer()
    
    language = context.user_data.get('language', 'uz')
    
    if 'debt_date_skip' in query.data:
        context.user_data['debt_due_date'] = None
        context.user_data['debt_reminder_days'] = None
    else:
        date_str = query.data.replace('debt_date_', '')
        context.user_data['debt_due_date'] = date.fromisoformat(date_str)
    
    # Eslatma so'rash (agar sana tanlangan bo'lsa)
    if context.user_data.get('debt_due_date'):
        context.user_data['debt_step'] = 'reminder'
        
        texts = {
            'uz': '⏰ <b>Eslatma kunlarini tanlang:</b>\n\nNecha kun oldin eslatish kerak?',
            'ru': '⏰ <b>Выберите дни напоминания:</b>\n\nЗа сколько дней напомнить?',
            'en': '⏰ <b>Select reminder days:</b>\n\nHow many days before?',
            'tr': '⏰ <b>Hatırlatma günlerini seçin:</b>\n\nKaç gün önce?',
            'ar': '⏰ <b>اختر أيام التذكير:</b>\n\nكم يوم قبل؟'
        }
        
        keyboard = get_debt_reminder_keyboard(language)
        
        await query.edit_message_text(
            text=texts.get(language, texts['uz']),
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        return WAITING_DEBT_DATA
    else:
        # Sana yo'q, eslatma ham yo'q
        context.user_data['debt_reminder_days'] = None
        context.user_data['debt_step'] = 'description'
        
        # Tavsif so'rash
        texts = {
            'uz': '📝 <b>Izoh qo\'shing</b> (ixtiyoriy)\n\n💡 Misol: Biznes uchun qarz\n\n⏭️ /skip bosing o\'tkazish uchun',
            'ru': '📝 <b>Добавьте описание</b> (необязательно)\n\n💡 Например: Долг для бизнеса\n\n⏭️ /skip чтобы пропустить',
            'en': '📝 <b>Add description</b> (optional)\n\n💡 Example: Loan for business\n\n⏭️ /skip to skip',
            'tr': '📝 <b>Açıklama ekleyin</b> (isteğe bağlı)\n\n💡 Örnek: İş için borç\n\n⏭️ /skip atlamak için',
            'ar': '📝 <b>أضف وصفاً</b> (اختياري)\n\n💡 مثال: قرض للعمل\n\n⏭️ /skip للتخطي'
        }
        
        cancel_btn = {'uz': '❌ Bekor qilish', 'ru': '❌ Отмена', 'en': '❌ Cancel', 'tr': '❌ İptal', 'ar': '❌ إلغاء'}
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(cancel_btn.get(language, cancel_btn['uz']), callback_data='debt_cancel')
        ]])
        
        await query.edit_message_text(
            text=texts.get(language, texts['uz']),
            reply_markup=keyboard,
            parse_mode='HTML'
        )
        return WAITING_DEBT_DATA


# =====================================================
# DEBT REMINDER HANDLER
# =====================================================
async def debt_reminder_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Eslatma tanlash"""
    query = update.callback_query
    await query.answer()
    
    language = context.user_data.get('language', 'uz')
    
    if 'debt_reminder_1' in query.data:
        context.user_data['debt_reminder_days'] = 1
    elif 'debt_reminder_3' in query.data:
        context.user_data['debt_reminder_days'] = 3
    elif 'debt_reminder_7' in query.data:
        context.user_data['debt_reminder_days'] = 7
    else:
        context.user_data['debt_reminder_days'] = None
    
    context.user_data['debt_step'] = 'description'
    
    # Tavsif so'rash
    texts = {
        'uz': '📝 <b>Izoh qo\'shing</b> (ixtiyoriy)\n\n💡 Misol: Biznes uchun qarz\n\n⏭️ /skip bosing o\'tkazish uchun',
        'ru': '📝 <b>Добавьте описание</b> (необязательно)\n\n💡 Например: Долг для бизнеса\n\n⏭️ /skip чтобы пропустить',
        'en': '📝 <b>Add description</b> (optional)\n\n💡 Example: Loan for business\n\n⏭️ /skip to skip',
        'tr': '📝 <b>Açıklama ekleyin</b> (isteğe bağlı)\n\n💡 Örnek: İş için borç\n\n⏭️ /skip atlamak için',
        'ar': '📝 <b>أضف وصفاً</b> (اختياري)\n\n💡 مثال: قرض للعمل\n\n⏭️ /skip للتخطي'
    }
    
    cancel_btn = {'uz': '❌ Bekor qilish', 'ru': '❌ Отмена', 'en': '❌ Cancel', 'tr': '❌ İptal', 'ar': '❌ إلغاء'}
    keyboard = InlineKeyboardMarkup([[
        InlineKeyboardButton(cancel_btn.get(language, cancel_btn['uz']), callback_data='debt_cancel')
    ]])
    
    await query.edit_message_text(
        text=texts.get(language, texts['uz']),
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    return WAITING_DEBT_DATA


# =====================================================
# SHOW CONFIRMATION
# =====================================================
async def show_debt_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Tasdiqlash oynasi"""
    language = context.user_data.get('language', 'uz')
    
    debt_type = context.user_data.get('debt_type')
    person = context.user_data.get('debt_person')
    amount = context.user_data.get('debt_amount')
    due_date = context.user_data.get('debt_due_date')
    reminder = context.user_data.get('debt_reminder_days')
    description = context.user_data.get('debt_description')
    
    # Type text
    type_labels = {
        'given': {'uz': '📤 Siz berdingiz', 'ru': '📤 Вы дали', 'en': '📤 You gave', 'tr': '📤 Verdiniz', 'ar': '📤 أقرضت'},
        'taken': {'uz': '📥 Siz oldingiz', 'ru': '📥 Вы взяли', 'en': '📥 You took', 'tr': '📥 Aldınız', 'ar': '📥 استلفت'}
    }
    
    type_text = type_labels[debt_type].get(language, type_labels[debt_type]['uz'])
    due_date_text = due_date.strftime('%d.%m.%Y') if due_date else '-'
    reminder_text = f"{reminder} kun oldin" if reminder else '-'
    
    confirm_text = (
        f"📝 <b>Qarzni tasdiqlang:</b>\n\n"
        f"{type_text}\n"
        f"👤 <b>Shaxs:</b> {person}\n"
        f"💰 <b>Summa:</b> {format_currency(amount, language)}\n"
        f"📅 <b>Muddat:</b> {due_date_text}\n"
        f"⏰ <b>Eslatma:</b> {reminder_text}\n"
        f"📝 <b>Izoh:</b> {description or '-'}\n\n"
        f"✅ Saqlashni xohlaysizmi?"
    )
    
    save_btn = {'uz': '✅ Saqlash', 'ru': '✅ Сохранить', 'en': '✅ Save', 'tr': '✅ Kaydet', 'ar': '✅ حفظ'}
    cancel_btn = {'uz': '❌ Bekor qilish', 'ru': '❌ Отмена', 'en': '❌ Cancel', 'tr': '❌ İptal', 'ar': '❌ إلغاء'}
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(save_btn.get(language, save_btn['uz']), callback_data='debt_save')],
        [InlineKeyboardButton(cancel_btn.get(language, cancel_btn['uz']), callback_data='debt_cancel')]
    ])
    
    await update.message.reply_text(
        text=confirm_text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )
    
    return WAITING_DEBT_DATA


# =====================================================
# SAVE DEBT
# =====================================================
async def debt_save_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Qarzni saqlash"""
    query = update.callback_query
    await query.answer()
    
    language = context.user_data.get('language', 'uz')
    telegram_id = context.user_data.get('telegram_id')
    
    debt = db_manager.add_debt(
        telegram_id=telegram_id,
        person_name=context.user_data.get('debt_person'),
        amount=context.user_data.get('debt_amount'),
        debt_type=context.user_data.get('debt_type'),
        due_date=context.user_data.get('debt_due_date'),
        description=context.user_data.get('debt_description'),
        reminder_days=context.user_data.get('debt_reminder_days')
    )
    
    if debt:
        debt_type = context.user_data.get('debt_type')
        success_key = 'debt_given_added' if debt_type == 'given' else 'debt_taken_added'
        
        due_date_text = debt.due_date.strftime('%d.%m.%Y') if debt.due_date else '-'
        
        success_msg = get_text(
            success_key,
            language,
            person=debt.person_name,
            amount=format_currency(debt.amount, language),
            due_date=due_date_text
        )
        
        await query.edit_message_text(success_msg, parse_mode='HTML')
    else:
        await query.edit_message_text("❌ Xatolik yuz berdi")
    
    _clear_debt_context(context)
    return ConversationHandler.END


# =====================================================
# LIST, VIEW, STATS, PAY, DELETE - SAME AS BEFORE
# =====================================================
async def list_debts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Qarzlar ro'yxati"""
    query = update.callback_query
    await query.answer()
    
    language = context.user_data.get('language', 'uz')
    telegram_id = context.user_data.get('telegram_id')
    
    debt_type = 'given' if 'debt_list_given' in query.data else 'taken'
    
    debts = db_manager.get_user_debts(telegram_id=telegram_id, debt_type=debt_type, status='active')
    
    if not debts:
        no_data = get_text('no_debts_found', language)
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('« Orqaga', callback_data='debt_menu')]])
        await query.edit_message_text(text=no_data, reply_markup=keyboard)
        return MAIN_MENU
    
    header_texts = {
        'uz': '📤 <b>Bergan qarzlarim</b>\n\nTanlang:' if debt_type == 'given' else '📥 <b>Olgan qarzlarim</b>\n\nTanlang:',
        'ru': '📤 <b>Выданные долги</b>\n\nВыберите:' if debt_type == 'given' else '📥 <b>Взятые долги</b>\n\nВыберите:',
        'en': '📤 <b>Given debts</b>\n\nSelect:' if debt_type == 'given' else '📥 <b>Taken debts</b>\n\nSelect:',
        'tr': '📤 <b>Verilen borçlar</b>\n\nSeçin:' if debt_type == 'given' else '📥 <b>Alınan borçlar</b>\n\nSeçin:',
        'ar': '📤 <b>الديون المقدمة</b>\n\nاختر:' if debt_type == 'given' else '📥 <b>الديون المستلمة</b>\n\nاختر:'
    }
    
    keyboard_buttons = []
    for debt in debts[:10]:
        amount_formatted = f"{debt.amount:,.0f}".replace(',', ' ')
        due_date_text = debt.due_date.strftime('%d.%m.%Y') if debt.due_date else '-'
        
        days_left = ''
        if debt.due_date:
            days = (debt.due_date - date.today()).days
            if days >= 0:
                days_left = f" ({days} kun)"
        
        btn_text = f"👤 {debt.person_name}\n💰 {amount_formatted} so'm\n📅 {due_date_text}{days_left}"
        keyboard_buttons.append([InlineKeyboardButton(btn_text, callback_data=f'debt_view_{debt.id}')])
    
    keyboard_buttons.append([InlineKeyboardButton('« Orqaga', callback_data='debt_menu')])
    
    await query.edit_message_text(
        text=header_texts.get(language, header_texts['uz']),
        reply_markup=InlineKeyboardMarkup(keyboard_buttons),
        parse_mode='HTML'
    )
    
    return MAIN_MENU


async def view_debt_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Qarz tafsilotlari"""
    query = update.callback_query
    await query.answer()
    
    language = context.user_data.get('language', 'uz')
    telegram_id = context.user_data.get('telegram_id')
    
    debt_id = int(query.data.replace('debt_view_', ''))
    debt = db_manager.get_debt_by_id(debt_id, telegram_id)
    
    if not debt:
        await query.edit_message_text("❌ Qarz topilmadi")
        return MAIN_MENU
    
    amount_formatted = f"{debt.amount:,.0f}".replace(',', ' ')
    paid_formatted = f"{debt.paid_amount:,.0f}".replace(',', ' ')
    remaining = debt.amount - debt.paid_amount
    remaining_formatted = f"{remaining:,.0f}".replace(',', ' ')
    
    due_date_text = debt.due_date.strftime('%d.%m.%Y') if debt.due_date else '-'
    
    days_left_text = ''
    if debt.due_date:
        days = (debt.due_date - date.today()).days
        if days >= 0:
            days_left_text = f" ({days} kun qoldi)"
        else:
            days_left_text = f" (❗ {abs(days)} kun kechikdi!)"
    
    status_icons = {'active': '🟢', 'partially_paid': '🟡', 'paid': '✅', 'overdue': '🔴'}
    status_icon = status_icons.get(debt.status, '⚪')
    
    debt_type_text = '📤 Siz berdingiz' if debt.debt_type == 'given' else '📥 Siz oldingiz'
    
    detail_text = (
        f"💼 <b>Qarz ma'lumotlari</b>\n\n"
        f"{debt_type_text}\n"
        f"👤 <b>Shaxs:</b> {debt.person_name}\n"
        f"💰 <b>Summa:</b> {amount_formatted} so'm\n"
        f"✅ <b>To'landi:</b> {paid_formatted} so'm\n"
        f"⏳ <b>Qoldi:</b> {remaining_formatted} so'm\n"
        f"📅 <b>Muddat:</b> {due_date_text}{days_left_text}\n"
        f"{status_icon} <b>Status:</b> {debt.status}\n"
        f"📝 <b>Izoh:</b> {debt.description or '-'}\n"
    )
    
    keyboard = get_debt_action_keyboard(language, debt.id)
    
    await query.edit_message_text(text=detail_text, reply_markup=keyboard, parse_mode='HTML')
    
    return MAIN_MENU


async def debt_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Statistika"""
    query = update.callback_query
    await query.answer()
    
    language = context.user_data.get('language', 'uz')
    telegram_id = context.user_data.get('telegram_id')
    
    stats = db_manager.get_debt_statistics(telegram_id)
    
    given = stats.get('given', {})
    taken = stats.get('taken', {})
    
    given_total = f"{given.get('total', 0):,.0f}".replace(',', ' ')
    given_active = f"{given.get('active', 0):,.0f}".replace(',', ' ')
    given_paid = f"{given.get('paid', 0):,.0f}".replace(',', ' ')
    
    taken_total = f"{taken.get('total', 0):,.0f}".replace(',', ' ')
    taken_active = f"{taken.get('active', 0):,.0f}".replace(',', ' ')
    taken_paid = f"{taken.get('paid', 0):,.0f}".replace(',', ' ')
    
    stats_text = (
        f"📈 <b>Qarzlar Statistikasi</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📤 <b>BERGAN QARZLARIM</b>\n"
        f"💰 Jami: {given_total} so'm\n"
        f"🟢 Aktiv: {given_active} so'm ({given.get('count', 0)} ta)\n"
        f"✅ To'langan: {given_paid} so'm\n"
        f"🔴 Kechikkan: {given.get('overdue', 0)} ta\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📥 <b>OLGAN QARZLARIM</b>\n"
        f"💰 Jami: {taken_total} so'm\n"
        f"🟢 Aktiv: {taken_active} so'm ({taken.get('count', 0)} ta)\n"
        f"✅ To'langan: {taken_paid} so'm\n"
        f"🔴 Kechikkan: {taken.get('overdue', 0)} ta\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('« Orqaga', callback_data='debt_menu')]])
    
    await query.edit_message_text(text=stats_text, reply_markup=keyboard, parse_mode='HTML')
    
    return MAIN_MENU


async def mark_debt_paid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """To'langan deb belgilash"""
    query = update.callback_query
    await query.answer()
    
    language = context.user_data.get('language', 'uz')
    telegram_id = context.user_data.get('telegram_id')
    
    if 'debt_paid_full_' in query.data:
        debt_id = int(query.data.replace('debt_paid_full_', ''))
        success = db_manager.mark_debt_paid(debt_id, telegram_id, None)
    elif 'debt_paid_partial_' in query.data:
        debt_id = int(query.data.replace('debt_paid_partial_', ''))
        context.user_data['debt_payment_id'] = debt_id
        await query.edit_message_text("💵 To'langan summani kiriting:", parse_mode='HTML')
        return WAITING_DEBT_DATA
    
    if success:
        success_msg = get_text('debt_marked_paid', language)
        await query.edit_message_text(success_msg)
    else:
        await query.edit_message_text("❌ Xatolik")
    
    return ConversationHandler.END


async def delete_debt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """O'chirish"""
    query = update.callback_query
    await query.answer()
    
    telegram_id = context.user_data.get('telegram_id')
    debt_id = int(query.data.replace('debt_delete_', ''))
    
    success = db_manager.delete_debt(debt_id, telegram_id)
    
    if success:
        await query.edit_message_text("✅ Qarz o'chirildi!")
    else:
        await query.edit_message_text("❌ Xatolik")
    
    return ConversationHandler.END


async def cancel_debt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Bekor qilish"""
    language = context.user_data.get('language', 'uz')
    cancel_msg = get_text('process_cancelled', language)
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(cancel_msg)
    else:
        await update.message.reply_text(cancel_msg)
    
    _clear_debt_context(context)
    
    return ConversationHandler.END


def _clear_debt_context(context: ContextTypes.DEFAULT_TYPE):
    """Context tozalash"""
    keys = ['debt_type', 'debt_person', 'debt_amount', 'debt_due_date', 'debt_reminder_days', 'debt_description', 'debt_step', 'debt_payment_id']
    for key in keys:
        context.user_data.pop(key, None)


def setup_conversation_handler() -> ConversationHandler:
    """Conversation handler"""
    return ConversationHandler(
        entry_points=[
            CallbackQueryHandler(add_debt_start, pattern='^debt_add_(given|taken)$'),
        ],
        states={
            WAITING_DEBT_DATA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, debt_data_input),
                CallbackQueryHandler(debt_date_handler, pattern='^debt_date_'),
                CallbackQueryHandler(debt_reminder_handler, pattern='^debt_reminder_'),
                CallbackQueryHandler(debt_save_handler, pattern='^debt_save$'),
                CallbackQueryHandler(cancel_debt, pattern='^debt_cancel$'),
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel_debt),
            CallbackQueryHandler(cancel_debt, pattern='^debt_cancel$'),
        ],
        name="debt_conversation",
        persistent=False,
    )
