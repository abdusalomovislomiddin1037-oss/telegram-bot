"""
SmartWallet AI Bot - Main Entry Point
=====================================
Bot'ni ishga tushirish va boshqarish uchun asosiy fayl.

Author: SmartWallet AI Team
Version: 1.0.0
"""

import asyncio
import logging
import sys
from datetime import datetime
from typing import Optional

from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
)

# Local imports
from config import BotConfig, AppConfig, SchedulerConfig, initialize as config_init
from database.db_manager import DatabaseManager
from utils.reminders import ReminderScheduler

# Handlers
from handlers.start import (
    start_command,
    language_selection,
    setup_conversation_handler as setup_start_handler
)
from handlers.expense import (
    add_expense_command,
    expense_amount_handler,
    expense_category_handler,
    setup_conversation_handler as setup_expense_handler
)
from handlers.income import (
    add_income_command,
    income_amount_handler,
    income_source_handler,
    setup_conversation_handler as setup_income_handler
)
from handlers.debt import (
    debt_menu,
    list_debts,
    view_debt_details,
    debt_statistics,
    mark_debt_paid,
    delete_debt,
    add_debt_start,
    handle_debt_date_selection,
    handle_debt_reminder_selection,
    handle_debt_description_skip,
    handle_debt_save,
    handle_debt_cancel
)
from handlers.reports import (
    reports_menu_command,
    report_type_handler,
    report_bot_handler,
    report_html_handler,
    daily_report_handler,
    weekly_report_handler,
    monthly_report_handler,
    yearly_report_handler,
    custom_report_handler,
    export_handler
)

# Logging setup
logger = logging.getLogger(__name__)


# =====================================================
# ERROR HANDLER
# =====================================================
async def error_handler(update: object, context: Exception) -> None:
    """
    Global error handler - barcha xatolarni ushlaydi
    
    Args:
        update: Telegram update object
        context: Error context
    """
    logger.error(f"Exception while handling an update: {context.error}", exc_info=context.error)
    
    # Foydalanuvchiga xabar yuborish
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ Xatolik yuz berdi. Iltimos, qaytadan urinib ko'ring.\n"
                "Muammo davom etsa, /start buyrug'ini yuboring."
            )
        except Exception as e:
            logger.error(f"Xato xabarini yuborishda muammo: {e}")
    
    # Admin'ga xabar yuborish (agar mavjud bo'lsa)
    if BotConfig.ADMIN_ID and context.application:
        try:
            error_text = (
                f"⚠️ <b>Bot Xatosi</b>\n\n"
                f"<b>Vaqt:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"<b>Xato:</b> {str(context.error)[:500]}\n"
            )
            if isinstance(update, Update) and update.effective_user:
                error_text += f"<b>Foydalanuvchi:</b> {update.effective_user.id}\n"
            
            await context.application.bot.send_message(
                chat_id=BotConfig.ADMIN_ID,
                text=error_text,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Admin'ga xabar yuborishda xato: {e}")


# =====================================================
# SHUTDOWN HANDLER
# =====================================================
async def shutdown_handler(application: Application) -> None:
    """
    Bot to'xtatilganda chaqiriladi - resurslarni tozalash
    
    Args:
        application: Bot application
    """
    logger.info("Bot to'xtatilmoqda...")
    
    # Database connection'ni yopish
    try:
        db_manager = DatabaseManager()
        await db_manager.close()
        logger.info("Database ulanishi yopildi")
    except Exception as e:
        logger.error(f"Database yopishda xato: {e}")
    
    logger.info("Bot to'xtatildi")


# =====================================================
# POST INITIALIZATION
# =====================================================
async def post_init(application: Application) -> None:
    """
    Bot ishga tushgandan keyin chaqiriladi
    
    Args:
        application: Bot application
    """
    logger.info("Bot ishga tushirilmoqda...")
    
    # Database'ni tekshirish va yaratish
    try:
        db_manager = DatabaseManager()
        await db_manager.create_tables()
        logger.info("Database jadvallar tekshirildi/yaratildi")
    except Exception as e:
        logger.error(f"Database yaratishda xato: {e}")
        raise
    
    # Scheduler'ni ishga tushirish
    if SchedulerConfig.REMINDER_CHECK_INTERVAL > 0:
        try:
            scheduler = ReminderScheduler(application.bot)
            scheduler.start()
            logger.info("Reminder scheduler ishga tushdi")
        except Exception as e:
            logger.error(f"Scheduler ishga tushirishda xato: {e}")
    
    # Admin'ga xabar yuborish
# Line 168-180 fix
    if BotConfig.ADMIN_ID:
        try:
            debug_status = 'Yoqilgan' if AppConfig.DEBUG else "O'chirilgan"
            bot_me = await application.bot.get_me()
            await application.bot.send_message(
                chat_id=BotConfig.ADMIN_ID,
                text=(
                    f"✅ Bot muvaffaqiyatli ishga tushdi!\n\n"
                    f"🕐 Vaqt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    f"🤖 Bot username: @{bot_me.username}\n"
                    f"🔧 Debug rejimi: {debug_status}"
                )
            )
        except Exception as e:
            logger.error(f"Admin'ga start xabari yuborishda xato: {e}")
    
    logger.info("Bot muvaffaqiyatli ishga tushdi!")


# =====================================================
# SETUP HANDLERS
# =====================================================
def setup_handlers(application: Application) -> None:
    """
    Barcha handler'larni ro'yxatdan o'tkazish
    
    Args:
        application: Bot application
    """
    logger.info("Handler'lar ro'yxatdan o'tkazilmoqda...")
    
    # 1. Start conversation handler (GROUP -1 = YUQORI PRIORITET)
    start_conv_handler = setup_start_handler()
    application.add_handler(start_conv_handler, group=-1)
    
    # 2. Expense conversation handler
    expense_conv_handler = setup_expense_handler()
    application.add_handler(expense_conv_handler, group=-1)
    
    # 3. Income conversation handler
    income_conv_handler = setup_income_handler()
    application.add_handler(income_conv_handler, group=-1)
    
    # 4. Debt callback handlers (text input handled inside start conversation handler)
    application.add_handler(CallbackQueryHandler(debt_menu, pattern='^debt_menu$'), group=-1)
    application.add_handler(CallbackQueryHandler(add_debt_start, pattern='^debt_add_(given|taken)$'), group=-1)
    application.add_handler(CallbackQueryHandler(list_debts, pattern='^debt_list_(given|taken)$'), group=-1)
    application.add_handler(CallbackQueryHandler(view_debt_details, pattern='^debt_view_'), group=-1)
    application.add_handler(CallbackQueryHandler(debt_statistics, pattern='^debt_statistics$'), group=-1)
    application.add_handler(CallbackQueryHandler(handle_debt_date_selection, pattern='^debt_date_'), group=-1)
    application.add_handler(CallbackQueryHandler(handle_debt_reminder_selection, pattern='^debt_reminder_'), group=-1)
    application.add_handler(CallbackQueryHandler(handle_debt_description_skip, pattern='^debt_desc_skip$'), group=-1)
    application.add_handler(CallbackQueryHandler(handle_debt_save, pattern='^debt_save$'), group=-1)
    application.add_handler(CallbackQueryHandler(handle_debt_cancel, pattern='^debt_cancel$'), group=-1)
    application.add_handler(CallbackQueryHandler(mark_debt_paid, pattern='^debt_paid_(full|partial)_'), group=-1)
    application.add_handler(CallbackQueryHandler(delete_debt, pattern='^debt_delete_'), group=-1)
    
    # 5. Callback query handler (global - barcha inline button'lar uchun)
    # GROUP 0 = Default, conversation handler'lardan KEYIN ishlaydi
    application.add_handler(CallbackQueryHandler(handle_callback), group=0)
    
    # 6. Unknown command handler - /start va /help ni chiqarib tashlash
    application.add_handler(MessageHandler(
        filters.COMMAND & ~filters.Regex(r'^/(start|help|cancel)'),
        unknown_command_handler
    ))
    
    # 7. Error handler
    application.add_error_handler(error_handler)
    
    logger.info("Barcha handler'lar ro'yxatdan o'tkazildi")


# =====================================================
# CALLBACK QUERY HANDLER
# =====================================================
async def handle_callback(update: Update, context) -> None:
    """
    Global callback query handler - barcha inline button'larni qayta ishlaydi
    
    Args:
        update: Telegram update
        context: Callback context
    """
    query = update.callback_query
    await query.answer()
    
    callback_data = query.data
    
    # Database manager
    db_manager = DatabaseManager()
    user_language = context.user_data.get('language', 'uz')
    telegram_id = context.user_data.get('telegram_id')
    
    # Helper function for safe message editing
    async def safe_edit_message(text, reply_markup=None, parse_mode=None):
        """Xabarni xavfsiz tahrirlash - xato bo'lsa yangi xabar yuborish"""
        try:
            await safe_edit_message(text, reply_markup=reply_markup, parse_mode=parse_mode)
        except Exception:
            try:
                await query.message.reply_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
            except Exception:
                pass
    
    # Callback data'ga qarab yo'naltirish
    # NOTE: lang_ callbacks are handled by start conversation handler
    
    if callback_data == 'add_expense':
        # Xarajat qo'shish
        await add_expense_command(update, context)
    
    elif callback_data == 'add_income':
        # Daromad qo'shish
        await add_income_command(update, context)
    
    elif callback_data == 'reports':
        # Hisobotlar menyusi
        await reports_menu_command(update, context)
    
    elif callback_data == 'settings':
        # Sozlamalar menyusiga qaytish
        from handlers.start import settings_menu
        await settings_menu(update, context)
    
    elif callback_data == 'delete_data':
        # Ma'lumot o'chirish menyusi - Daromad va Xarajatlar
        from keyboards.inline import get_delete_data_keyboard
        
        delete_texts = {
            'uz': '🗑️ <b>Ma\'lumot o\'chirish</b>\n\nNimani tahrirlash/o\'chirmoqchisiz?',
            'ru': '🗑️ <b>Удаление данных</b>\n\nЧто хотите редактировать/удалить?',
            'en': '🗑️ <b>Delete Data</b>\n\nWhat do you want to edit/delete?',
            'tr': '🗑️ <b>Veri Silme</b>\n\nNeyi düzenlemek/silmek istiyorsunuz?',
            'ar': '🗑️ <b>حذف البيانات</b>\n\nماذا تريد تعديل/حذف؟'
        }
        
        keyboard = get_delete_data_keyboard(user_language)
        await safe_edit_message(
            delete_texts.get(user_language, delete_texts['uz']),
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    
    elif callback_data == 'delete_expenses_list':
        # Xarajatlar ro'yxatini ko'rsatish
        from utils.filters import get_last_n_days_range
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        start_date, end_date = get_last_n_days_range(30)  # Oxirgi 30 kun
        expenses = db_manager.get_user_expenses(telegram_id, start_date, end_date)
        
        if not expenses:
            no_data = {
                'uz': '📭 Xarajatlar topilmadi.',
                'ru': '📭 Расходы не найдены.',
                'en': '📭 No expenses found.',
                'tr': '📭 Gider bulunamadı.',
                'ar': '📭 لم يتم العثور على مصروفات.'
            }
            back_text = {'uz': '« Orqaga', 'ru': '« Назад', 'en': '« Back', 'tr': '« Geri', 'ar': '« رجوع'}
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(back_text.get(user_language, back_text['uz']), callback_data='delete_data')]])
            await safe_edit_message(no_data.get(user_language, no_data['uz']), reply_markup=keyboard)
            return
        
        # Xarajatlar ro'yxati
        from config import Categories
        
        header = {
            'uz': '💸 <b>Xarajatlar</b>\n\nTahrirlash uchun tanlang:',
            'ru': '💸 <b>Расходы</b>\n\nВыберите для редактирования:',
            'en': '💸 <b>Expenses</b>\n\nSelect to edit:',
            'tr': '💸 <b>Giderler</b>\n\nDüzenlemek için seçin:',
            'ar': '💸 <b>المصروفات</b>\n\nاختر للتعديل:'
        }
        
        keyboard_buttons = []
        for exp in expenses[:10]:  # Oxirgi 10 ta
            cat_icon = '📌'
            for cat in Categories.LIST:
                if cat['key'] == exp.category:
                    cat_icon = cat['icon']
                    break
            
            btn_text = f"{cat_icon} {exp.amount:,.0f} - {exp.created_at.strftime('%d.%m')}"
            keyboard_buttons.append([InlineKeyboardButton(btn_text, callback_data=f'edit_expense_{exp.id}')])
        
        back_text = {'uz': '« Orqaga', 'ru': '« Назад', 'en': '« Back', 'tr': '« Geri', 'ar': '« رجوع'}
        keyboard_buttons.append([InlineKeyboardButton(back_text.get(user_language, back_text['uz']), callback_data='delete_data')])
        
        await safe_edit_message(
            header.get(user_language, header['uz']),
            reply_markup=InlineKeyboardMarkup(keyboard_buttons),
            parse_mode='HTML'
        )
    
    elif callback_data == 'delete_incomes_list':
        # Daromadlar ro'yxatini ko'rsatish
        from utils.filters import get_last_n_days_range
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        start_date, end_date = get_last_n_days_range(30)  # Oxirgi 30 kun
        incomes = db_manager.get_user_incomes(telegram_id, start_date, end_date)
        
        if not incomes:
            no_data = {
                'uz': '📭 Daromadlar topilmadi.',
                'ru': '📭 Доходы не найдены.',
                'en': '📭 No incomes found.',
                'tr': '📭 Gelir bulunamadı.',
                'ar': '📭 لم يتم العثور على دخل.'
            }
            back_text = {'uz': '« Orqaga', 'ru': '« Назад', 'en': '« Back', 'tr': '« Geri', 'ar': '« رجوع'}
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(back_text.get(user_language, back_text['uz']), callback_data='delete_data')]])
            await safe_edit_message(no_data.get(user_language, no_data['uz']), reply_markup=keyboard)
            return
        
        # Daromadlar ro'yxati
        header = {
            'uz': '💰 <b>Daromadlar</b>\n\nTahrirlash uchun tanlang:',
            'ru': '💰 <b>Доходы</b>\n\nВыберите для редактирования:',
            'en': '💰 <b>Incomes</b>\n\nSelect to edit:',
            'tr': '💰 <b>Gelirler</b>\n\nDüzenlemek için seçin:',
            'ar': '💰 <b>الدخل</b>\n\nاختر للتعديل:'
        }
        
        keyboard_buttons = []
        for inc in incomes[:10]:  # Oxirgi 10 ta
            btn_text = f"💰 {inc.amount:,.0f} - {inc.created_at.strftime('%d.%m')}"
            keyboard_buttons.append([InlineKeyboardButton(btn_text, callback_data=f'edit_income_{inc.id}')])
        
        back_text = {'uz': '« Orqaga', 'ru': '« Назад', 'en': '« Back', 'tr': '« Geri', 'ar': '« رجوع'}
        keyboard_buttons.append([InlineKeyboardButton(back_text.get(user_language, back_text['uz']), callback_data='delete_data')])
        
        await safe_edit_message(
            header.get(user_language, header['uz']),
            reply_markup=InlineKeyboardMarkup(keyboard_buttons),
            parse_mode='HTML'
        )
    
    elif callback_data.startswith('report_bot_'):
        # Hisobotni botda ko'rsatish
        await report_bot_handler(update, context)
    
    elif callback_data.startswith('report_html_'):
        # Hisobotni HTML formatida yuborish
        await report_html_handler(update, context)
    
    elif callback_data.startswith('category_'):
        # Kategoriya tanlash
        await expense_category_handler(update, context)
    
    elif callback_data.startswith('report_'):
        # Hisobot turi tanlash - format so'rash
        await report_type_handler(update, context)
    
    elif callback_data.startswith('export_'):
        # Export handler
        await export_handler(update, context)
    
    elif callback_data.startswith('delete_expense_'):
        # Xarajatni o'chirish
        user_language = context.user_data.get('language', 'uz')
        telegram_id = context.user_data.get('telegram_id')
        expense_id = callback_data.replace('delete_expense_', '')
        
        try:
            # Xarajatni o'chirish
            if db_manager.delete_expense(int(expense_id), telegram_id):
                delete_messages = {
                    'uz': '✅ Xarajat o\'chirildi!',
                    'ru': '✅ Расход удалён!',
                    'en': '✅ Expense deleted!',
                    'tr': '✅ Gider silindi!',
                    'ar': '✅ تم حذف المصروف!'
                }
                await safe_edit_message(delete_messages.get(user_language, delete_messages['uz']))
            else:
                await safe_edit_message("❌ Xato yuz berdi")
        except Exception as e:
            logger.error(f"Delete expense error: {e}")
            await safe_edit_message("❌ Xato yuz berdi")
    
    elif callback_data.startswith('cancel_expense_'):
        # Xarajatni bekor qilish
        user_language = context.user_data.get('language', 'uz')
        telegram_id = context.user_data.get('telegram_id')
        expense_id = int(callback_data.replace('cancel_expense_', ''))
        
        try:
            # Xarajatni o'chirish
            if db_manager.delete_expense(expense_id, telegram_id):
                cancel_messages = {
                    'uz': '✅ Xarajat bekor qilindi va o\'chirildi!',
                    'ru': '✅ Расход отменён и удалён!',
                    'en': '✅ Expense cancelled and deleted!',
                    'tr': '✅ Gider iptal edildi ve silindi!',
                    'ar': '✅ تم إلغاء وحذف المصروف!'
                }
                await safe_edit_message(cancel_messages.get(user_language, cancel_messages['uz']))
            else:
                await safe_edit_message("❌ Xato yuz berdi")
        except Exception as e:
            logger.error(f"Cancel expense error: {e}")
            await safe_edit_message("❌ Xato yuz berdi")
    
    elif callback_data.startswith('cancel_income_'):
        # Daromadni bekor qilish
        user_language = context.user_data.get('language', 'uz')
        telegram_id = context.user_data.get('telegram_id')
        income_id = int(callback_data.replace('cancel_income_', ''))
        
        try:
            # Daromadni o'chirish
            if db_manager.delete_income(income_id, telegram_id):
                cancel_messages = {
                    'uz': '✅ Daromad bekor qilindi va o\'chirildi!',
                    'ru': '✅ Доход отменён и удалён!',
                    'en': '✅ Income cancelled and deleted!',
                    'tr': '✅ Gelir iptal edildi ve silindi!',
                    'ar': '✅ تم إلغاء وحذف الدخل!'
                }
                await safe_edit_message(cancel_messages.get(user_language, cancel_messages['uz']))
            else:
                await safe_edit_message("❌ Xato yuz berdi")
        except Exception as e:
            logger.error(f"Cancel income error: {e}")
            await safe_edit_message("❌ Xato yuz berdi")
    
    elif callback_data.startswith('edit_expense_'):
        # Xarajat ma'lumotlarini ko'rsatish va tahrirlash/o'chirish opsiyalari
        expense_id = int(callback_data.replace('edit_expense_', ''))
        
        try:
            # Xarajat ma'lumotlarini olish
            expense = db_manager.get_expense_by_id(expense_id, telegram_id)
            
            if expense:
                from config import Categories
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                
                # Kategoriya nomini olish
                cat_name = Categories.NAMES.get(expense.category, {}).get(user_language, expense.category)
                cat_icon = '📌'
                for cat in Categories.LIST:
                    if cat['key'] == expense.category:
                        cat_icon = cat['icon']
                        break
                
                detail_texts = {
                    'uz': f"💸 <b>Xarajat ma'lumotlari</b>\n\n{cat_icon} Kategoriya: {cat_name}\n💵 Summa: {expense.amount:,.0f} so'm\n📅 Sana: {expense.created_at.strftime('%d.%m.%Y %H:%M')}\n\nNima qilmoqchisiz?",
                    'ru': f"💸 <b>Информация о расходе</b>\n\n{cat_icon} Категория: {cat_name}\n💵 Сумма: {expense.amount:,.0f} сум\n📅 Дата: {expense.created_at.strftime('%d.%m.%Y %H:%M')}\n\nЧто хотите сделать?",
                    'en': f"💸 <b>Expense details</b>\n\n{cat_icon} Category: {cat_name}\n💵 Amount: {expense.amount:,.0f} sum\n📅 Date: {expense.created_at.strftime('%d.%m.%Y %H:%M')}\n\nWhat do you want to do?",
                    'tr': f"💸 <b>Gider detayları</b>\n\n{cat_icon} Kategori: {cat_name}\n💵 Tutar: {expense.amount:,.0f} sum\n📅 Tarih: {expense.created_at.strftime('%d.%m.%Y %H:%M')}\n\nNe yapmak istiyorsunuz?",
                    'ar': f"💸 <b>تفاصيل المصروف</b>\n\n{cat_icon} الفئة: {cat_name}\n💵 المبلغ: {expense.amount:,.0f} سوم\n📅 التاريخ: {expense.created_at.strftime('%d.%m.%Y %H:%M')}\n\nماذا تريد أن تفعل?"
                }
                
                btn_texts = {
                    'uz': {'delete': '🔴 O\'chirish', 'edit': '✏️ Tahrirlash', 'back': '« Orqaga'},
                    'ru': {'delete': '🔴 Удалить', 'edit': '✏️ Редактировать', 'back': '« Назад'},
                    'en': {'delete': '🔴 Delete', 'edit': '✏️ Edit', 'back': '« Back'},
                    'tr': {'delete': '🔴 Sil', 'edit': '✏️ Düzenle', 'back': '« Geri'},
                    'ar': {'delete': '🔴 حذف', 'edit': '✏️ تعديل', 'back': '« رجوع'}
                }
                btn = btn_texts.get(user_language, btn_texts['uz'])
                
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(btn['delete'], callback_data=f'confirm_del_expense_{expense_id}'),
                        InlineKeyboardButton(btn['edit'], callback_data=f'do_edit_expense_{expense_id}')
                    ],
                    [InlineKeyboardButton(btn['back'], callback_data='delete_expenses_list')]
                ])
                
                await safe_edit_message(
                    detail_texts.get(user_language, detail_texts['uz']),
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            else:
                await safe_edit_message("❌ Xarajat topilmadi")
        except Exception as e:
            logger.error(f"Edit expense error: {e}")
            await safe_edit_message("❌ Xato yuz berdi")
    
    elif callback_data.startswith('confirm_del_expense_'):
        # Xarajatni o'chirish
        expense_id = int(callback_data.replace('confirm_del_expense_', ''))
        
        try:
            if db_manager.delete_expense(expense_id, telegram_id):
                delete_messages = {
                    'uz': '✅ Xarajat o\'chirildi!',
                    'ru': '✅ Расход удалён!',
                    'en': '✅ Expense deleted!',
                    'tr': '✅ Gider silindi!',
                    'ar': '✅ تم حذف المصروف!'
                }
                await safe_edit_message(delete_messages.get(user_language, delete_messages['uz']))
            else:
                await safe_edit_message("❌ Xato yuz berdi")
        except Exception as e:
            logger.error(f"Confirm delete expense error: {e}")
            await safe_edit_message("❌ Xato yuz berdi")
    
    elif callback_data.startswith('do_edit_expense_'):
        # Xarajatni tahrirlash - o'chirib, qayta qo'shish
        expense_id = int(callback_data.replace('do_edit_expense_', ''))
        
        try:
            if db_manager.delete_expense(expense_id, telegram_id):
                edit_messages = {
                    'uz': '✏️ Xarajat o\'chirildi.\n\n💸 Endi yangi xarajat qo\'shing:',
                    'ru': '✏️ Расход удалён.\n\n💸 Теперь добавьте новый расход:',
                    'en': '✏️ Expense deleted.\n\n💸 Now add new expense:',
                    'tr': '✏️ Gider silindi.\n\n💸 Şimdi yeni gider ekleyin:',
                    'ar': '✏️ تم حذف المصروف.\n\n💸 الآن أضف مصروف جديد:'
                }
                
                await safe_edit_message(edit_messages.get(user_language, edit_messages['uz']))
                await add_expense_command(update, context)
            else:
                await safe_edit_message("❌ Xato yuz berdi")
        except Exception as e:
            logger.error(f"Do edit expense error: {e}")
            await safe_edit_message("❌ Xato yuz berdi")
    
    elif callback_data.startswith('edit_income_'):
        # Daromad ma'lumotlarini ko'rsatish va tahrirlash/o'chirish opsiyalari
        income_id = int(callback_data.replace('edit_income_', ''))
        
        try:
            # Daromad ma'lumotlarini olish
            income = db_manager.get_income_by_id(income_id, telegram_id)
            
            if income:
                from telegram import InlineKeyboardButton, InlineKeyboardMarkup
                
                detail_texts = {
                    'uz': f"💰 <b>Daromad ma'lumotlari</b>\n\n💵 Summa: {income.amount:,.0f} so'm\n📝 Manba: {income.source or '-'}\n📅 Sana: {income.created_at.strftime('%d.%m.%Y %H:%M')}\n\nNima qilmoqchisiz?",
                    'ru': f"💰 <b>Информация о доходе</b>\n\n💵 Сумма: {income.amount:,.0f} сум\n📝 Источник: {income.source or '-'}\n📅 Дата: {income.created_at.strftime('%d.%m.%Y %H:%M')}\n\nЧто хотите сделать?",
                    'en': f"💰 <b>Income details</b>\n\n💵 Amount: {income.amount:,.0f} sum\n📝 Source: {income.source or '-'}\n📅 Date: {income.created_at.strftime('%d.%m.%Y %H:%M')}\n\nWhat do you want to do?",
                    'tr': f"💰 <b>Gelir detayları</b>\n\n💵 Tutar: {income.amount:,.0f} sum\n📝 Kaynak: {income.source or '-'}\n📅 Tarih: {income.created_at.strftime('%d.%m.%Y %H:%M')}\n\nNe yapmak istiyorsunuz?",
                    'ar': f"💰 <b>تفاصيل الدخل</b>\n\n💵 المبلغ: {income.amount:,.0f} سوم\n📝 المصدر: {income.source or '-'}\n📅 التاريخ: {income.created_at.strftime('%d.%m.%Y %H:%M')}\n\nماذا تريد أن تفعل?"
                }
                
                btn_texts = {
                    'uz': {'delete': '🔴 O\'chirish', 'edit': '✏️ Tahrirlash', 'back': '« Orqaga'},
                    'ru': {'delete': '🔴 Удалить', 'edit': '✏️ Редактировать', 'back': '« Назад'},
                    'en': {'delete': '🔴 Delete', 'edit': '✏️ Edit', 'back': '« Back'},
                    'tr': {'delete': '🔴 Sil', 'edit': '✏️ Düzenle', 'back': '« Geri'},
                    'ar': {'delete': '🔴 حذف', 'edit': '✏️ تعديل', 'back': '« رجوع'}
                }
                btn = btn_texts.get(user_language, btn_texts['uz'])
                
                keyboard = InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(btn['delete'], callback_data=f'confirm_del_income_{income_id}'),
                        InlineKeyboardButton(btn['edit'], callback_data=f'do_edit_income_{income_id}')
                    ],
                    [InlineKeyboardButton(btn['back'], callback_data='delete_incomes_list')]
                ])
                
                await safe_edit_message(
                    detail_texts.get(user_language, detail_texts['uz']),
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
            else:
                await safe_edit_message("❌ Daromad topilmadi")
        except Exception as e:
            logger.error(f"Edit income error: {e}")
            await safe_edit_message("❌ Xato yuz berdi")
    
    elif callback_data.startswith('confirm_del_income_'):
        # Daromadni o'chirish
        income_id = int(callback_data.replace('confirm_del_income_', ''))
        
        try:
            if db_manager.delete_income(income_id, telegram_id):
                delete_messages = {
                    'uz': '✅ Daromad o\'chirildi!',
                    'ru': '✅ Доход удалён!',
                    'en': '✅ Income deleted!',
                    'tr': '✅ Gelir silindi!',
                    'ar': '✅ تم حذف الدخل!'
                }
                await safe_edit_message(delete_messages.get(user_language, delete_messages['uz']))
            else:
                await safe_edit_message("❌ Xato yuz berdi")
        except Exception as e:
            logger.error(f"Confirm delete income error: {e}")
            await safe_edit_message("❌ Xato yuz berdi")
    
    elif callback_data.startswith('do_edit_income_'):
        # Daromadni tahrirlash - o'chirib, qayta qo'shish
        income_id = int(callback_data.replace('do_edit_income_', ''))
        
        try:
            if db_manager.delete_income(income_id, telegram_id):
                edit_messages = {
                    'uz': '✏️ Daromad o\'chirildi.\n\n💰 Endi yangi daromad qo\'shing:',
                    'ru': '✏️ Доход удалён.\n\n💰 Теперь добавьте новый доход:',
                    'en': '✏️ Income deleted.\n\n💰 Now add new income:',
                    'tr': '✏️ Gelir silindi.\n\n💰 Şimdi yeni gelir ekleyin:',
                    'ar': '✏️ تم حذف الدخل.\n\n💰 الآن أضف دخل جديد:'
                }
                
                await safe_edit_message(edit_messages.get(user_language, edit_messages['uz']))
                await add_income_command(update, context)
            else:
                await safe_edit_message("❌ Xato yuz berdi")
        except Exception as e:
            logger.error(f"Do edit income error: {e}")
            await safe_edit_message("❌ Xato yuz berdi")
    
    elif callback_data == 'back_main' or callback_data == 'main_menu':
        # Asosiy menyuga qaytish
        await start_command(update, context)
    
    else:
        # Noma'lum callback - conversation handler ichida qayta ishlangan bo'lishi mumkin
        # Faqat log qilamiz, xabar yubormimiz
        logger.info(f"Callback '{callback_data}' handled by conversation handler or ignored")
        # Query.answer() allaqachon yuqorida chaqirilgan, shuning uchun hech narsa qilmasimiz


# =====================================================
# UNKNOWN COMMAND HANDLER
# =====================================================
async def unknown_command_handler(update: Update, context) -> None:
    """
    Noma'lum buyruqlarni qayta ishlash
    
    Args:
        update: Telegram update
        context: Message context
    """
    user_lang = context.user_data.get('language', 'uz')
    
    messages = {
        'uz': "❌ Noma'lum buyruq. /start ni bosing.",
        'ru': "❌ Неизвестная команда. Нажмите /start.",
        'en': "❌ Unknown command. Press /start.",
        'tr': "❌ Bilinmeyen komut. /start'a basın.",
        'ar': "❌ أمر غير معروف. اضغط /start."
    }
    
    await update.message.reply_text(
        messages.get(user_lang, messages['uz'])
    )


# =====================================================
# MAIN FUNCTION
# =====================================================
def main() -> None:
    """
    Bot'ni ishga tushirish - asosiy funksiya
    """
    # Konfiguratsiyani yuklash
    try:
        config_init()
        logger.info("Konfiguratsiya yuklandi")
    except Exception as e:
        logger.critical(f"Konfiguratsiya yuklashda xato: {e}")
        sys.exit(1)
    
    # Bot tokenini tekshirish
    if not BotConfig.TOKEN:
        logger.critical("BOT_TOKEN topilmadi! .env faylni tekshiring.")
        sys.exit(1)
    
    # Application yaratish
    try:
        application = (
            Application.builder()
            .token(BotConfig.TOKEN)
            .post_init(post_init)
            .post_shutdown(shutdown_handler)
            .build()
        )
        logger.info("Application yaratildi")
    except Exception as e:
        logger.critical(f"Application yaratishda xato: {e}")
        sys.exit(1)
    
    # Handler'larni setup qilish
    try:
        setup_handlers(application)
    except Exception as e:
        logger.critical(f"Handler'larni setup qilishda xato: {e}")
        sys.exit(1)
    
    # Bot'ni ishga tushirish
    logger.info("="*50)
    logger.info("SmartWallet AI Bot ishga tushmoqda...")
    logger.info(f"Debug rejimi: {AppConfig.DEBUG}")
    logger.info(f"Timezone: {AppConfig.TIMEZONE}")
    logger.info("="*50)
    
    try:
        # Polling rejimida ishga tushirish
        application.run_polling(
            allowed_updates=Update.ALL_TYPES,
            drop_pending_updates=True
        )
    except KeyboardInterrupt:
        logger.info("Bot foydalanuvchi tomonidan to'xtatildi")
    except Exception as e:
        logger.critical(f"Bot ishga tushirishda xato: {e}")
        sys.exit(1)


# =====================================================
# ENTRY POINT
# =====================================================
if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        logger.critical(f"Fatal error: {e}")
        sys.exit(1)
