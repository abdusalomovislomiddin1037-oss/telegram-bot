"""
Debt Handler with Telegram Web App
"""
import logging
import json
from datetime import date

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ContextTypes

from database.db_manager import DatabaseManager
from keyboards.inline import get_debt_menu_keyboard
from utils.translations import get_text, format_currency

logger = logging.getLogger(__name__)
db_manager = DatabaseManager()

# Web App URL - O'zingizning server IP manzilingizni yozing!
WEB_APP_URL = "http://YOUR_SERVER_IP:8000/debt_form.html"


# =====================================================
# DEBT MENU
# =====================================================
async def debt_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Qarzlar menyusi"""
    query = update.callback_query if update.callback_query else None
    if query:
        await query.answer()
    
    language = context.user_data.get('language', 'uz')
    
    # Custom menu with Web App button
    menu_text = "💼 <b>Qarzlar</b>\n\nKerakli bo'limni tanlang:"
    
    keyboard = [
        [InlineKeyboardButton("📤 Qarz berdim", web_app=WebAppInfo(url=WEB_APP_URL + "?type=given"))],
        [InlineKeyboardButton("📥 Qarz oldim", web_app=WebAppInfo(url=WEB_APP_URL + "?type=taken"))],
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
# WEB APP DATA HANDLER
# =====================================================
async def handle_web_app_data(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Web App'dan kelgan ma'lumotni qabul qilish"""
    try:
        data = json.loads(update.effective_message.web_app_data.data)
        
        telegram_id = update.effective_user.id
        language = context.user_data.get('language', 'uz')
        
        # Ma'lumotlarni olish
        debt_type = data.get('type')
        person_name = data.get('person')
        amount = data.get('amount')
        due_date = data.get('due_date')
        reminder_days = data.get('reminder_days')
        description = data.get('description')
        
        # Due date parse
        due_date_obj = None
        if due_date:
            try:
                due_date_obj = date.fromisoformat(due_date)
            except:
                pass
        
        # Database'ga saqlash
        debt = db_manager.add_debt(
            telegram_id=telegram_id,
            person_name=person_name,
            amount=amount,
            debt_type=debt_type,
            due_date=due_date_obj,
            description=description,
            reminder_days=reminder_days
        )
        
        if debt:
            success_key = 'debt_given_added' if debt_type == 'given' else 'debt_taken_added'
            due_date_text = due_date_obj.strftime('%d.%m.%Y') if due_date_obj else '-'
            
            success_msg = get_text(
                success_key,
                language,
                person=person_name,
                amount=format_currency(amount, language),
                due_date=due_date_text
            )
            
            await update.message.reply_text(success_msg, parse_mode='HTML')
            logger.info(f"✅ Qarz saqlandi: {person_name}, {amount}, {debt_type}")
        else:
            await update.message.reply_text("❌ Xatolik yuz berdi")
            
    except Exception as e:
        logger.error(f"Web App data error: {e}")
        await update.message.reply_text("❌ Ma'lumotlarni qayta ishlashda xatolik")


# =====================================================
# LIST DEBTS
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
        due_text = debt.due_date.strftime('%d.%m.%Y') if debt.due_date else '-'
        
        days_left = ''
        if debt.due_date:
            days = (debt.due_date - date.today()).days
            if days >= 0:
                days_left = f" ({days} kun)"
        
        btn_text = f"👤 {debt.person_name}\n💰 {amount_fmt} so'm\n📅 {due_text}{days_left}"
        keyboard_buttons.append([InlineKeyboardButton(btn_text, callback_data=f'debt_view_{debt.id}')])
    
    keyboard_buttons.append([InlineKeyboardButton('« Orqaga', callback_data='debt_menu')])
    
    await query.edit_message_text(text=header + "Tanlang:", reply_markup=InlineKeyboardMarkup(keyboard_buttons), parse_mode='HTML')


# =====================================================
# VIEW, STATISTICS, DELETE - SAME AS BEFORE
# =====================================================
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
            days_text = f" (❗ {abs(days)} kun kechikdi!)"
    
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
        [
            InlineKeyboardButton("✅ To'liq to'landi", callback_data=f'debt_paid_full_{debt.id}'),
            InlineKeyboardButton("💵 Qisman", callback_data=f'debt_paid_partial_{debt.id}')
        ],
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
    given_paid = f"{given.get('paid', 0):,.0f}".replace(',', ' ')
    
    taken_total = f"{taken.get('total', 0):,.0f}".replace(',', ' ')
    taken_active = f"{taken.get('active', 0):,.0f}".replace(',', ' ')
    taken_paid = f"{taken.get('paid', 0):,.0f}".replace(',', ' ')
    
    text = (
        f"📈 <b>Qarzlar Statistikasi</b>\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📤 <b>BERGAN QARZLARIM</b>\n"
        f"💰 Jami: {given_total} so'm\n"
        f"🟢 Aktiv: {given_active} so'm ({given.get('count', 0)} ta)\n"
        f"✅ To'langan: {given_paid} so'm\n\n"
        f"━━━━━━━━━━━━━━━━━━━━\n"
        f"📥 <b>OLGAN QARZLARIM</b>\n"
        f"💰 Jami: {taken_total} so'm\n"
        f"🟢 Aktiv: {taken_active} so'm ({taken.get('count', 0)} ta)\n"
        f"✅ To'langan: {taken_paid} so'm\n"
        f"━━━━━━━━━━━━━━━━━━━━"
    )
    
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton('« Orqaga', callback_data='debt_menu')]])
    await query.edit_message_text(text=text, reply_markup=keyboard, parse_mode='HTML')


async def mark_debt_paid(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """To'langan"""
    query = update.callback_query
    await query.answer()
    
    telegram_id = context.user_data.get('telegram_id')
    
    if 'debt_paid_full_' in query.data:
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
