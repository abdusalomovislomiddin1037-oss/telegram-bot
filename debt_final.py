"""
SmartWallet AI Bot - Debt Handler (Final Working Version)
==========================================================
INLINE KEYBOARD ONLY - NO WEB APP - NO MESSAGE HANDLER CONFLICTS
"""

import logging
from decimal import Decimal
from datetime import datetime, date, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database.db_manager import DatabaseManager
from utils.translations import get_text, format_currency

logger = logging.getLogger(__name__)
db_manager = DatabaseManager()


# =====================================================
# DEBT MENU
# =====================================================
async def debt_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Qarzlar menyusi"""
    query = update.callback_query if update.callback_query else None
    if query:
        await query.answer()
    
    language = context.user_data.get('language', 'uz')
    
    menu_text = "💼 <b>Qarzlar Menyusi</b>\n\nKerakli bo'limni tanlang:"
    
    keyboard = [
        [InlineKeyboardButton("📤 Qarz berdim", callback_data='debt_add_given')],
        [InlineKeyboardButton("📥 Qarz oldim", callback_data='debt_add_taken')],
        [InlineKeyboardButton("📊 Bergan qarzlarim", callback_data='debt_list_given')],
        [InlineKeyboardButton("📊 Olgan qarzlarim", callback_data='debt_list_taken')],
        [InlineKeyboardButton("📈 Statistika", callback_data='debt_statistics')],
        [InlineKeyboardButton("🔙 Orqaga", callback_data='back_main')],
    ]
    
    if query:
        try:
            await query.edit_message_text(text=menu_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        except:
            await query.message.reply_text(text=menu_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
    else:
        await update.message.reply_text(text=menu_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')


# =====================================================
# ADD DEBT - STEP BY STEP WITH INLINE KEYBOARDS
# =====================================================
async def add_debt_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Qarz qo'shish - 1-qadam: Shaxs ismini so'rash"""
    query = update.callback_query
    await query.answer()
    
    language = context.user_data.get('language', 'uz')
    
    # Qarz turini saqlash
    if 'debt_add_given' in query.data:
        context.user_data['temp_debt_type'] = 'given'
        title = '📤 <b>Qarz berdim</b>'
    else:
        context.user_data['temp_debt_type'] = 'taken'
        title = '📥 <b>Qarz oldim</b>'
    
    # Shaxs ismini inline keyboard orqali kiritish uchun text so'raymiz
    text = (
        f"{title}\n\n"
        f"👤 <b>Shaxs ismini kiriting:</b>\n\n"
        f"💡 Misol: Ali Valiyev\n\n"
        f"<i>Quyidagi xabarda yozing va yuboringandan keyin avtomatik davom etadi</i>"
    )
    
    # Temp flag o'rnatamiz
    context.user_data['awaiting_debt_person'] = True
    
    keyboard = [[InlineKeyboardButton("❌ Bekor qilish", callback_data='debt_cancel')]]
    
    await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')


# =====================================================
# STEP 2: PERSON NAME INPUT
# =====================================================
async def handle_debt_person_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Shaxs ismi kiritilganda"""
    # Agar flag bo'lmasa, ignore
    if not context.user_data.get('awaiting_debt_person'):
        return
    
    person_name = update.message.text.strip()
    
    if len(person_name) < 2:
        await update.message.reply_text("❌ Iltimos, to'g'ri ism kiriting (kamida 2 ta belgi)")
        return
    
    context.user_data['temp_debt_person'] = person_name
    context.user_data.pop('awaiting_debt_person', None)
    context.user_data['awaiting_debt_amount'] = True
    
    language = context.user_data.get('language', 'uz')
    
    text = (
        f"✅ Shaxs: <b>{person_name}</b>\n\n"
        f"💰 <b>Summa kiriting (so'mda):</b>\n\n"
        f"💡 Misol: 500000"
    )
    
    keyboard = [[InlineKeyboardButton("❌ Bekor qilish", callback_data='debt_cancel')]]
    
    await update.message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')


# =====================================================
# STEP 3: AMOUNT INPUT
# =====================================================
async def handle_debt_amount_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Summa kiritilganda"""
    if not context.user_data.get('awaiting_debt_amount'):
        return
    
    try:
        amount = float(update.message.text.strip().replace(' ', '').replace(',', ''))
        if amount <= 0:
            raise ValueError
    except:
        await update.message.reply_text("❌ Iltimos, to'g'ri summa kiriting!")
        return
    
    context.user_data['temp_debt_amount'] = amount
    context.user_data.pop('awaiting_debt_amount', None)
    
    language = context.user_data.get('language', 'uz')
    
    # Sana tanlash
    text = (
        f"✅ Summa: <b>{amount:,.0f}</b> so'm\n\n"
        f"📅 <b>Qaytarish sanasini tanlang:</b>"
    )
    
    today = date.today()
    keyboard = [
        [InlineKeyboardButton(f"7 kun ({(today + timedelta(days=7)).strftime('%d.%m')})", 
                              callback_data=f'debt_date_{(today + timedelta(days=7)).isoformat()}')],
        [InlineKeyboardButton(f"14 kun ({(today + timedelta(days=14)).strftime('%d.%m')})", 
                              callback_data=f'debt_date_{(today + timedelta(days=14)).isoformat()}')],
        [InlineKeyboardButton(f"1 oy ({(today + timedelta(days=30)).strftime('%d.%m')})", 
                              callback_data=f'debt_date_{(today + timedelta(days=30)).isoformat()}')],
        [InlineKeyboardButton(f"3 oy ({(today + timedelta(days=90)).strftime('%d.%m')})", 
                              callback_data=f'debt_date_{(today + timedelta(days=90)).isoformat()}')],
        [InlineKeyboardButton("⏭️ Sana kerak emas", callback_data='debt_date_skip')],
        [InlineKeyboardButton("❌ Bekor qilish", callback_data='debt_cancel')]
    ]
    
    await update.message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')


# =====================================================
# STEP 4: DATE SELECTION
# =====================================================
async def handle_debt_date_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sana tanlaganda"""
    query = update.callback_query
    await query.answer()
    
    language = context.user_data.get('language', 'uz')
    
    if 'debt_date_skip' in query.data:
        context.user_data['temp_debt_due_date'] = None
        context.user_data['temp_debt_reminder'] = None
        # To'g'ridan-to'g'ri description'ga o'tish
        await ask_debt_description(query, context)
    else:
        date_str = query.data.replace('debt_date_', '')
        due_date = date.fromisoformat(date_str)
        context.user_data['temp_debt_due_date'] = due_date
        
        # Eslatma so'rash
        text = (
            f"✅ Sana: <b>{due_date.strftime('%d.%m.%Y')}</b>\n\n"
            f"⏰ <b>Eslatma kunlarini tanlang:</b>\n\n"
            f"Muddatdan necha kun oldin eslatsin?"
        )
        
        keyboard = [
            [InlineKeyboardButton("1 kun oldin", callback_data='debt_reminder_1')],
            [InlineKeyboardButton("3 kun oldin", callback_data='debt_reminder_3')],
            [InlineKeyboardButton("7 kun oldin", callback_data='debt_reminder_7')],
            [InlineKeyboardButton("⏭️ Eslatma kerak emas", callback_data='debt_reminder_skip')],
            [InlineKeyboardButton("❌ Bekor qilish", callback_data='debt_cancel')]
        ]
        
        await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')


# =====================================================
# STEP 5: REMINDER SELECTION
# =====================================================
async def handle_debt_reminder_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Eslatma tanlaganda"""
    query = update.callback_query
    await query.answer()
    
    if 'debt_reminder_1' in query.data:
        context.user_data['temp_debt_reminder'] = 1
    elif 'debt_reminder_3' in query.data:
        context.user_data['temp_debt_reminder'] = 3
    elif 'debt_reminder_7' in query.data:
        context.user_data['temp_debt_reminder'] = 7
    else:
        context.user_data['temp_debt_reminder'] = None
    
    # Description so'rash
    await ask_debt_description(query, context)


async def ask_debt_description(query, context):
    """Izoh so'rash"""
    context.user_data['awaiting_debt_description'] = True
    
    text = (
        f"📝 <b>Izoh qo'shing</b> (ixtiyoriy)\n\n"
        f"💡 Misol: Biznes uchun qarz\n\n"
        f"<i>Izoh yozmasangiz, /skip yuboring</i>"
    )
    
    keyboard = [
        [InlineKeyboardButton("⏭️ Izohsiz davom etish", callback_data='debt_desc_skip')],
        [InlineKeyboardButton("❌ Bekor qilish", callback_data='debt_cancel')]
    ]
    
    await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')


# =====================================================
# STEP 6: DESCRIPTION INPUT
# =====================================================
async def handle_debt_description_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Izoh kiritilganda"""
    if not context.user_data.get('awaiting_debt_description'):
        return
    
    description = update.message.text.strip()
    
    if description == '/skip':
        context.user_data['temp_debt_description'] = None
    elif len(description) > 500:
        await update.message.reply_text("❌ Izoh juda uzun (max 500 belgi)")
        return
    else:
        context.user_data['temp_debt_description'] = description
    
    context.user_data.pop('awaiting_debt_description', None)
    
    # Tasdiqlash
    await show_debt_confirmation(update, context)


async def handle_debt_description_skip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Izohni o'tkazib yuborish"""
    query = update.callback_query
    await query.answer()
    
    context.user_data['temp_debt_description'] = None
    context.user_data.pop('awaiting_debt_description', None)
    
    # Tasdiqlash - query orqali
    await show_debt_confirmation_from_query(query, context)


# =====================================================
# STEP 7: CONFIRMATION
# =====================================================
async def show_debt_confirmation(update, context):
    """Tasdiqlash (message'dan)"""
    language = context.user_data.get('language', 'uz')
    
    debt_type = context.user_data.get('temp_debt_type')
    person = context.user_data.get('temp_debt_person')
    amount = context.user_data.get('temp_debt_amount')
    due_date = context.user_data.get('temp_debt_due_date')
    reminder = context.user_data.get('temp_debt_reminder')
    description = context.user_data.get('temp_debt_description')
    
    type_text = '📤 Siz berdingiz' if debt_type == 'given' else '📥 Siz oldingiz'
    due_text = due_date.strftime('%d.%m.%Y') if due_date else '-'
    reminder_text = f"{reminder} kun oldin" if reminder else '-'
    
    text = (
        f"📝 <b>Qarzni tasdiqlang:</b>\n\n"
        f"{type_text}\n"
        f"👤 <b>Shaxs:</b> {person}\n"
        f"💰 <b>Summa:</b> {amount:,.0f} so'm\n"
        f"📅 <b>Muddat:</b> {due_text}\n"
        f"⏰ <b>Eslatma:</b> {reminder_text}\n"
        f"📝 <b>Izoh:</b> {description or '-'}\n\n"
        f"✅ Saqlashni xohlaysizmi?"
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ Saqlash", callback_data='debt_save')],
        [InlineKeyboardButton("❌ Bekor qilish", callback_data='debt_cancel')]
    ]
    
    await update.message.reply_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')


async def show_debt_confirmation_from_query(query, context):
    """Tasdiqlash (query'dan)"""
    language = context.user_data.get('language', 'uz')
    
    debt_type = context.user_data.get('temp_debt_type')
    person = context.user_data.get('temp_debt_person')
    amount = context.user_data.get('temp_debt_amount')
    due_date = context.user_data.get('temp_debt_due_date')
    reminder = context.user_data.get('temp_debt_reminder')
    description = context.user_data.get('temp_debt_description')
    
    type_text = '📤 Siz berdingiz' if debt_type == 'given' else '📥 Siz oldingiz'
    due_text = due_date.strftime('%d.%m.%Y') if due_date else '-'
    reminder_text = f"{reminder} kun oldin" if reminder else '-'
    
    text = (
        f"📝 <b>Qarzni tasdiqlang:</b>\n\n"
        f"{type_text}\n"
        f"👤 <b>Shaxs:</b> {person}\n"
        f"💰 <b>Summa:</b> {amount:,.0f} so'm\n"
        f"📅 <b>Muddat:</b> {due_text}\n"
        f"⏰ <b>Eslatma:</b> {reminder_text}\n"
        f"📝 <b>Izoh:</b> {description or '-'}\n\n"
        f"✅ Saqlashni xohlaysizmi?"
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ Saqlash", callback_data='debt_save')],
        [InlineKeyboardButton("❌ Bekor qilish", callback_data='debt_cancel')]
    ]
    
    await query.edit_message_text(text=text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')


# =====================================================
# STEP 8: SAVE
# =====================================================
async def handle_debt_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Qarzni saqlash"""
    query = update.callback_query
    await query.answer()
    
    language = context.user_data.get('language', 'uz')
    telegram_id = context.user_data.get('telegram_id')
    
    debt = db_manager.add_debt(
        telegram_id=telegram_id,
        person_name=context.user_data.get('temp_debt_person'),
        amount=context.user_data.get('temp_debt_amount'),
        debt_type=context.user_data.get('temp_debt_type'),
        due_date=context.user_data.get('temp_debt_due_date'),
        description=context.user_data.get('temp_debt_description'),
        reminder_days=context.user_data.get('temp_debt_reminder')
    )
    
    if debt:
        debt_type = context.user_data.get('temp_debt_type')
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
        logger.info(f"✅ Qarz saqlandi: {debt.person_name}, {debt.amount}, {debt_type}")
    else:
        await query.edit_message_text("❌ Xatolik yuz berdi")
    
    # Clear temp data
    _clear_temp_debt_data(context)


# =====================================================
# CANCEL
# =====================================================
async def handle_debt_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Bekor qilish"""
    query = update.callback_query
    await query.answer()
    
    _clear_temp_debt_data(context)
    
    await query.edit_message_text("❌ Qarz qo'shish bekor qilindi")


def _clear_temp_debt_data(context):
    """Temp ma'lumotlarni tozalash"""
    keys = [
        'temp_debt_type', 'temp_debt_person', 'temp_debt_amount',
        'temp_debt_due_date', 'temp_debt_reminder', 'temp_debt_description',
        'awaiting_debt_person', 'awaiting_debt_amount', 'awaiting_debt_description'
    ]
    for key in keys:
        context.user_data.pop(key, None)


# =====================================================
# LIST, VIEW, STATS (SAME AS BEFORE)
# =====================================================
async def list_debts(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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
        return
    
    header = '📤 <b>Bergan qarzlarim</b>\n\n' if debt_type == 'given' else '📥 <b>Olgan qarzlarim</b>\n\n'
    
    keyboard_buttons = []
    for debt in debts[:10]:
        amount_fmt = f"{debt.amount:,.0f}".replace(',', ' ')
        due_text = debt.due_date.strftime('%d.%m') if debt.due_date else '-'
        
        days_left = ''
        if debt.due_date:
            days = (debt.due_date - date.today()).days
            if days >= 0:
                days_left = f" ({days}d)"
        
        btn_text = f"{debt.person_name} • {amount_fmt} • {due_text}{days_left}"
        keyboard_buttons.append([InlineKeyboardButton(btn_text, callback_data=f'debt_view_{debt.id}')])
    
    keyboard_buttons.append([InlineKeyboardButton('« Orqaga', callback_data='debt_menu')])
    
    await query.edit_message_text(text=header + "Tanlang:", reply_markup=InlineKeyboardMarkup(keyboard_buttons), parse_mode='HTML')


async def view_debt_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Qarz tafsilotlari"""
    query = update.callback_query
    await query.answer()
    
    telegram_id = context.user_data.get('telegram_id')
    debt_id = int(query.data.replace('debt_view_', ''))
    debt = db_manager.get_debt_by_id(debt_id, telegram_id)
    
    if not debt:
        await query.edit_message_text("❌ Qarz topilmadi")
        return
    
    amount_fmt = f"{debt.amount:,.0f}".replace(',', ' ')
    paid_fmt = f"{debt.paid_amount:,.0f}".replace(',', ' ')
    remaining = debt.amount - debt.paid_amount
    remaining_fmt = f"{remaining:,.0f}".replace(',', ' ')
    
    due_text = debt.due_date.strftime('%d.%m.%Y') if debt.due_date else '-'
    
    days_text = ''
    if debt.due_date:
        days = (debt.due_date - date.today()).days
        if days >= 0:
            days_text = f" ({days} kun qoldi)"
        else:
            days_text = f" (❗{abs(days)} kun kechikdi!)"
    
    status_icons = {'active': '🟢', 'partially_paid': '🟡', 'paid': '✅', 'overdue': '🔴'}
    status_icon = status_icons.get(debt.status, '⚪')
    
    type_text = '📤 Siz berdingiz' if debt.debt_type == 'given' else '📥 Siz oldingiz'
    
    detail = (
        f"💼 <b>Qarz ma'lumotlari</b>\n\n"
        f"{type_text}\n"
        f"👤 <b>Shaxs:</b> {debt.person_name}\n"
        f"💰 <b>Summa:</b> {amount_fmt} so'm\n"
        f"✅ <b>To'landi:</b> {paid_fmt} so'm\n"
        f"⏳ <b>Qoldi:</b> {remaining_fmt} so'm\n"
        f"📅 <b>Muddat:</b> {due_text}{days_text}\n"
        f"{status_icon} <b>Status:</b> {debt.status}\n"
        f"📝 <b>Izoh:</b> {debt.description or '-'}\n"
    )
    
    keyboard = [
        [InlineKeyboardButton("✅ To'liq to'landi", callback_data=f'debt_paid_full_{debt.id}')],
        [InlineKeyboardButton("🗑️ O'chirish", callback_data=f'debt_delete_{debt.id}')],
        [InlineKeyboardButton("« Orqaga", callback_data='debt_menu')]
    ]
    
    await query.edit_message_text(text=detail, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')


async def debt_statistics(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Statistika"""
    query = update.callback_query
    await query.answer()
    
    telegram_id = context.user_data.get('telegram_id')
    stats = db_manager.get_debt_statistics(telegram_id)
    
    given = stats.get('given', {})
    taken = stats.get('taken', {})
    
    given_total = f"{given.get('total', 0):,.0f}".replace(',', ' ')
    given_active = f"{given.get('active', 0):,.0f}".replace(',', ' ')
    
    taken_total = f"{taken.get('total', 0):,.0f}".replace(',', ' ')
    taken_active = f"{taken.get('active', 0):,.0f}".replace(',', ' ')
    
    text = (
        f"📈 <b>Qarzlar Statistikasi</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📤 <b>BERGAN</b>\n"
        f"💰 Jami: {given_total} so'm\n"
        f"🟢 Aktiv: {given_active} so'm ({given.get('count', 0)} ta)\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📥 <b>OLGAN</b>\n"
        f"💰 Jami: {taken_total} so'm\n"
        f"🟢 Aktiv: {taken_active} so'm ({taken.get('count', 0)} ta)\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('« Orqaga', callback_data='debt_menu')]])
    await query.edit_message_text(text=text, reply_markup=keyboard, parse_mode='HTML')


async def mark_debt_paid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """To'langan"""
    query = update.callback_query
    await query.answer()
    
    telegram_id = context.user_data.get('telegram_id')
    debt_id = int(query.data.replace('debt_paid_full_', ''))
    
    success = db_manager.mark_debt_paid(debt_id, telegram_id, None)
    
    if success:
        await query.edit_message_text("✅ Qarz to'langan deb belgilandi!")
    else:
        await query.edit_message_text("❌ Xatolik")


async def delete_debt(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
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


# =====================================================
# UNIVERSAL MESSAGE HANDLER
# =====================================================
async def handle_debt_text_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Barcha text input'larni boshqarish"""
    # Faqat qarz uchun flag'lar tekshiriladi
    if context.user_data.get('awaiting_debt_person'):
        await handle_debt_person_input(update, context)
    elif context.user_data.get('awaiting_debt_amount'):
        await handle_debt_amount_input(update, context)
    elif context.user_data.get('awaiting_debt_description'):
        await handle_debt_description_input(update, context)
    # Aks holda ignore (quick expense ishlaydi)
