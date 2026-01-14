"""
SmartWallet AI Bot - Start Handler
==================================
/start buyrug'i va til tanlash handler'lari

Functions:
    - start_command: Bot ishga tushirish
    - language_selection: Til tanlash
    - main_menu: Asosiy menyu
    - settings_menu: Sozlamalar menyusi

Author: SmartWallet AI Team
Version: 1.0.0
"""

import logging
from typing import Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ContextTypes,
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from config import Messages, AppConfig
from database.db_manager import DatabaseManager
from keyboards.inline import (
    get_language_keyboard,
    get_main_menu_keyboard,
    get_settings_keyboard
)
from utils.translations import get_text
from handlers.quick_expense import quick_expense_handler

# Logger
logger = logging.getLogger(__name__)

# Conversation states
SELECTING_LANGUAGE = 0
MAIN_MENU = 1

# Database manager
db_manager = DatabaseManager()


# =====================================================
# START COMMAND
# =====================================================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    /start buyrug'ini qayta ishlash
    
    Args:
        update: Telegram update
        context: Callback context
        
    Returns:
        int: Conversation state
    """
    user = update.effective_user
    
    # Foydalanuvchini database'ga qo'shish yoki olish
    db_user = db_manager.get_or_create_user(
        telegram_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )
    
    # Context'ga til saqlash
    context.user_data['language'] = db_user.language
    context.user_data['telegram_id'] = user.id
    
    logger.info(f"User {user.id} botni boshladi")
    
    # Agar til allaqachon tanlangan bo'lsa, asosiy menyuga o'tish
    if db_user.language and db_user.language != 'uz':
        # Til tanlangan, asosiy menyuni ko'rsatish
        return await show_main_menu(update, context)
    
    # Til tanlash
    welcome_text = Messages.WELCOME.get(db_user.language, Messages.WELCOME['uz'])
    
    keyboard = get_language_keyboard()
    
    # Agar callback query bo'lsa
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text=welcome_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    else:
        # Oddiy xabar
        await update.message.reply_text(
            text=welcome_text,
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    
    return SELECTING_LANGUAGE


# =====================================================
# LANGUAGE SELECTION
# =====================================================
async def language_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Til tanlash handler'i
    
    Args:
        update: Telegram update
        context: Callback context
        
    Returns:
        int: Conversation state
    """
    query = update.callback_query
    await query.answer()
    
    # Tanlangan tilni olish
    callback_data = query.data
    if not callback_data.startswith('lang_'):
        return SELECTING_LANGUAGE
    
    selected_language = callback_data.replace('lang_', '')
    
    # Qo'llab-quvvatlanadigan tillarni tekshirish
    if selected_language not in AppConfig.SUPPORTED_LANGUAGES:
        await query.edit_message_text(
            text="❌ Noto'g'ri til tanlandi. Iltimos, qaytadan tanlang.",
            reply_markup=get_language_keyboard()
        )
        return SELECTING_LANGUAGE
    
    # Tilni database'ga saqlash
    telegram_id = context.user_data.get('telegram_id')
    if telegram_id:
        db_manager.update_user_language(telegram_id, selected_language)
        context.user_data['language'] = selected_language
        logger.info(f"User {telegram_id} til tanladi: {selected_language}")
    
    # Muvaffaqiyatli xabar
    success_messages = {
        'uz': "✅ Til muvaffaqiyatli tanlandi!",
        'ru': "✅ Язык успешно выбран!",
        'en': "✅ Language selected successfully!",
        'tr': "✅ Dil başarıyla seçildi!",
        'ar': "✅ تم اختيار اللغة بنجاح!"
    }
    
    await query.edit_message_text(
        text=success_messages.get(selected_language, success_messages['uz'])
    )
    
    # Asosiy menyuga o'tish
    return await show_main_menu(update, context)


# =====================================================
# MAIN MENU
# =====================================================
async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Asosiy menyuni ko'rsatish (Reply Keyboard)
    
    Args:
        update: Telegram update
        context: Callback context
        
    Returns:
        int: Conversation state
    """
    language = context.user_data.get('language', 'uz')
    
    # Menyu matni
    menu_texts = {
        'uz': """🏠 <b>SmartWallet AI — Asosiy Menyu</b>

━━━━━━━━━━━━━━━━━━━━

📌 <b>Tezkor xarajat kiritish:</b>
Summa va izoh yozing: <code>50000 non</code>

━━━━━━━━━━━━━━━━━━━━

⬇️ <i>Quyidagi tugmalardan birini tanlang:</i>""",
        'ru': """🏠 <b>SmartWallet AI — Главное Меню</b>

━━━━━━━━━━━━━━━━━━━━

📌 <b>Быстрый ввод расхода:</b>
Введите сумму и описание: <code>50000 хлеб</code>

━━━━━━━━━━━━━━━━━━━━

⬇️ <i>Выберите одну из кнопок ниже:</i>""",
        'en': """🏠 <b>SmartWallet AI — Main Menu</b>

━━━━━━━━━━━━━━━━━━━━

📌 <b>Quick expense entry:</b>
Type amount and note: <code>50000 bread</code>

━━━━━━━━━━━━━━━━━━━━

⬇️ <i>Select one of the buttons below:</i>""",
        'tr': """🏠 <b>SmartWallet AI — Ana Menü</b>

━━━━━━━━━━━━━━━━━━━━

📌 <b>Hızlı gider girişi:</b>
Tutar ve not yazın: <code>50000 ekmek</code>

━━━━━━━━━━━━━━━━━━━━

⬇️ <i>Aşağıdaki butonlardan birini seçin:</i>""",
        'ar': """🏠 <b>SmartWallet AI — القائمة الرئيسية</b>

━━━━━━━━━━━━━━━━━━━━

📌 <b>إدخال سريع للمصروف:</b>
اكتب المبلغ والملاحظة: <code>50000 خبز</code>

━━━━━━━━━━━━━━━━━━━━

⬇️ <i>اختر أحد الأزرار أدناه:</i>"""
    }
    
    menu_text = menu_texts.get(language, menu_texts['uz'])
    
    # Reply Keyboard yaratish
    button_texts = {
        'uz': {
            'add_expense': '💳 Xarajat qo\'shish',
            'add_income': '💰 Daromad qo\'shish',
            'debts': '💼 Qarzlar',
            'reports': '📊 Hisobotlar',
            'settings': '⚙️ Sozlamalar',
        },
        'ru': {
            'add_expense': '💳 Добавить расход',
            'add_income': '💰 Добавить доход',
            'debts': '💼 Долги',
            'reports': '📊 Отчёты',
            'settings': '⚙️ Настройки',
        },
        'en': {
            'add_expense': '💳 Add Expense',
            'add_income': '💰 Add Income',
            'debts': '💼 Debts',
            'reports': '📊 Reports',
            'settings': '⚙️ Settings',
        },
        'tr': {
            'add_expense': '💳 Gider Ekle',
            'add_income': '💰 Gelir Ekle',
            'debts': '💼 Borçlar',
            'reports': '📊 Raporlar',
            'settings': '⚙️ Ayarlar',
        },
        'ar': {
            'add_expense': '💳 إضافة مصروف',
            'add_income': '💰 إضافة دخل',
            'debts': '💼 الديون',
            'reports': '📊 التقارير',
            'settings': '⚙️ الإعدادات',
        }
    }
    
    t = button_texts.get(language, button_texts['uz'])
    
    # Reply keyboard - 2x2 grid + 1 bottom button
    keyboard = [
        [KeyboardButton(t['add_expense']), KeyboardButton(t['add_income'])],
        [KeyboardButton(t['debts']), KeyboardButton(t['reports'])],
        [KeyboardButton(t['settings'])],
    ]
    
    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    # Xabar yuborish
    if update.callback_query:
        try:
            await update.callback_query.answer()
            await update.callback_query.message.reply_text(
                text=menu_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"show_main_menu callback error: {e}")
            # Yangi xabar yuborish
            await update.effective_chat.send_message(
                text=menu_text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
    else:
        await update.effective_chat.send_message(
            text=menu_text,
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    return MAIN_MENU


# =====================================================
# SETTINGS MENU
# =====================================================
async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Sozlamalar menyusini ko'rsatish
    
    Args:
        update: Telegram update
        context: Callback context
        
    Returns:
        int: Conversation state
    """
    query = update.callback_query
    
    # Callback query yoki message
    if query:
        await query.answer()
    
    language = context.user_data.get('language', 'uz')
    
    settings_texts = {
        'uz': """⚙️ <b>Sozlamalar</b>

Kerakli sozlamani tanlang:""",
        'ru': """⚙️ <b>Настройки</b>

Выберите настройку:""",
        'en': """⚙️ <b>Settings</b>

Choose a setting:""",
        'tr': """⚙️ <b>Ayarlar</b>

Bir ayar seçin:""",
        'ar': """⚙️ <b>الإعدادات</b>

اختر إعداداً:"""
    }
    
    keyboard = get_settings_keyboard(language)
    
    if query:
        await query.edit_message_text(
            text=settings_texts.get(language, settings_texts['uz']),
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            text=settings_texts.get(language, settings_texts['uz']),
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    
    return MAIN_MENU


# =====================================================
# CHANGE LANGUAGE
# =====================================================
async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Tilni o'zgartirish
    
    Args:
        update: Telegram update
        context: Callback context
        
    Returns:
        int: Conversation state
    """
    query = update.callback_query
    await query.answer()
    
    language = context.user_data.get('language', 'uz')
    
    change_lang_texts = {
        'uz': "🌍 Tilni tanlang:",
        'ru': "🌍 Выберите язык:",
        'en': "🌍 Choose language:",
        'tr': "🌍 Dil seçin:",
        'ar': "🌍 اختر اللغة:"
    }
    
    keyboard = get_language_keyboard()
    
    await query.edit_message_text(
        text=change_lang_texts.get(language, change_lang_texts['uz']),
        reply_markup=keyboard
    )
    
    return SELECTING_LANGUAGE


# =====================================================
# HELP COMMAND
# =====================================================
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    /help buyrug'i - yordam ma'lumoti
    
    Args:
        update: Telegram update
        context: Callback context
    """
    language = context.user_data.get('language', 'uz')
    
    help_texts = {
        'uz': """📖 <b>SmartWallet AI - Yordam</b>

<b>Asosiy buyruqlar:</b>
/start - Botni ishga tushirish
/help - Yordam ma'lumoti

<b>Qanday ishlatish:</b>

1️⃣ <b>Xarajat qo'shish:</b>
   • "Xarajat qo'shish" tugmasini bosing
   • Summani kiriting (masalan: 50000)
   • Kategoriyani tanlang
   • AI avtomatik aniqlaydi!

2️⃣ <b>Daromad qo'shish:</b>
   • "Daromad qo'shish" tugmasini bosing
   • Summani kiriting
   • Manba va turini belgilang

3️⃣ <b>Hisobotlar:</b>
   • Kunlik/Haftalik/Oylik hisobotlar
   • PDF va HTML formatda
   • Grafiklar va tahlil

<b>AI xususiyatlari:</b>
• Matndan summa aniqlash
• Kategoriya tavsiya qilish
• Smart eslatmalar

Savollar bo'lsa, /start ni bosing!""",
        
        'ru': """📖 <b>SmartWallet AI - Справка</b>

<b>Основные команды:</b>
/start - Запустить бота
/help - Справочная информация

<b>Как использовать:</b>

1️⃣ <b>Добавить расход:</b>
   • Нажмите "Добавить расход"
   • Введите сумму (например: 50000)
   • Выберите категорию
   • AI автоматически определит!

2️⃣ <b>Добавить доход:</b>
   • Нажмите "Добавить доход"
   • Введите сумму
   • Укажите источник и тип

3️⃣ <b>Отчёты:</b>
   • Ежедневные/Недельные/Месячные отчёты
   • Форматы PDF и HTML
   • Графики и анализ

<b>Возможности AI:</b>
• Определение суммы из текста
• Рекомендация категории
• Умные напоминания

При вопросах нажмите /start!""",
        
        'en': """📖 <b>SmartWallet AI - Help</b>

<b>Main commands:</b>
/start - Start bot
/help - Help information

<b>How to use:</b>

1️⃣ <b>Add expense:</b>
   • Click "Add expense"
   • Enter amount (e.g.: 50000)
   • Select category
   • AI detects automatically!

2️⃣ <b>Add income:</b>
   • Click "Add income"
   • Enter amount
   • Specify source and type

3️⃣ <b>Reports:</b>
   • Daily/Weekly/Monthly reports
   • PDF and HTML formats
   • Charts and analysis

<b>AI features:</b>
• Detect amount from text
• Recommend category
• Smart reminders

Questions? Press /start!""",
        
        'tr': """📖 <b>SmartWallet AI - Yardım</b>

<b>Ana komutlar:</b>
/start - Botu başlat
/help - Yardım bilgisi

<b>Nasıl kullanılır:</b>

1️⃣ <b>Gider ekle:</b>
   • "Gider ekle" düğmesine basın
   • Tutarı girin (örn: 50000)
   • Kategori seçin
   • AI otomatik algılar!

2️⃣ <b>Gelir ekle:</b>
   • "Gelir ekle" düğmesine basın
   • Tutarı girin
   • Kaynak ve türü belirtin

3️⃣ <b>Raporlar:</b>
   • Günlük/Haftalık/Aylık raporlar
   • PDF ve HTML formatları
   • Grafikler ve analiz

<b>AI özellikleri:</b>
• Metinden tutar algılama
• Kategori önerisi
• Akıllı hatırlatmalar

Sorularınız mı var? /start'a basın!""",
        
        'ar': """📖 <b>SmartWallet AI - مساعدة</b>

<b>الأوامر الرئيسية:</b>
/start - تشغيل البوت
/help - معلومات المساعدة

<b>كيفية الاستخدام:</b>

1️⃣ <b>إضافة مصروف:</b>
   • انقر على "إضافة مصروف"
   • أدخل المبلغ (مثال: 50000)
   • اختر الفئة
   • الذكاء الاصطناعي يكتشف تلقائياً!

2️⃣ <b>إضافة دخل:</b>
   • انقر على "إضافة دخل"
   • أدخل المبلغ
   • حدد المصدر والنوع

3️⃣ <b>التقارير:</b>
   • تقارير يومية/أسبوعية/شهرية
   • صيغ PDF و HTML
   • رسوم بيانية وتحليل

<b>ميزات الذكاء الاصطناعي:</b>
• اكتشاف المبلغ من النص
• اقتراح الفئة
• تذكيرات ذكية

أسئلة؟ اضغط /start!"""
    }
    
    help_text = help_texts.get(language, help_texts['uz'])
    
    await update.message.reply_text(
        text=help_text,
        parse_mode='HTML'
    )


# =====================================================
# MENU BUTTON HANDLER
# =====================================================
async def menu_button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Reply keyboard tugmalarini qayta ishlash
    
    Args:
        update: Telegram update
        context: Callback context
        
    Returns:
        int: Conversation state
    """
    text = update.message.text
    language = context.user_data.get('language', 'uz')
    
    logger.info(f"🔍 MENU_BUTTON_HANDLER: text='{text}', language='{language}'")
    
    # Tugma matnlarini tekshirish
    button_mapping = {
        'uz': {
            '💳 Xarajat qo\'shish': 'add_expense',
            '💰 Daromad qo\'shish': 'add_income',
            '💼 Qarzlar': 'debts',
            '📊 Hisobotlar': 'reports',
            '⚙️ Sozlamalar': 'settings',
        },
        'ru': {
            '💳 Добавить расход': 'add_expense',
            '💰 Добавить доход': 'add_income',
            '💼 Долги': 'debts',
            '📊 Отчёты': 'reports',
            '⚙️ Настройки': 'settings',
        },
        'en': {
            '💳 Add Expense': 'add_expense',
            '💰 Add Income': 'add_income',
            '💼 Debts': 'debts',
            '📊 Reports': 'reports',
            '⚙️ Settings': 'settings',
        },
        'tr': {
            '💳 Gider Ekle': 'add_expense',
            '💰 Gelir Ekle': 'add_income',
            '💼 Borçlar': 'debts',
            '📊 Raporlar': 'reports',
            '⚙️ Ayarlar': 'settings',
        },
        'ar': {
            '💳 إضافة مصروف': 'add_expense',
            '💰 إضافة دخل': 'add_income',
            '💼 الديون': 'debts',
            '📊 التقارير': 'reports',
            '⚙️ الإعدادات': 'settings',
        }
    }
    
    mapping = button_mapping.get(language, button_mapping['uz'])
    action = mapping.get(text)
    
    logger.info(f"🎯 Aniqlangan action: '{action}'")
    
    if action == 'add_expense':
        logger.info("💸 Xarajat qo'shish handler'iga yo'naltirish...")
        from handlers.expense import add_expense_command
        await add_expense_command(update, context)
        return MAIN_MENU
    
    elif action == 'add_income':
        logger.info("💰 Daromad qo'shish handler'iga yo'naltirish...")
        from handlers.income import add_income_command
        await add_income_command(update, context)
        return MAIN_MENU
    
    elif action == 'debts':
        logger.info("💼 Qarzlar handler'iga yo'naltirish...")
        from handlers.debt import debt_menu
        await debt_menu(update, context)
        return MAIN_MENU
    
    elif action == 'reports':
        logger.info("📊 Hisobotlar handler'iga yo'naltirish...")
        from handlers.reports import reports_menu_command
        await reports_menu_command(update, context)
        return MAIN_MENU
    
    elif action == 'settings':
        logger.info("⚙️ Sozlamalar handler'iga yo'naltirish...")
        await settings_menu(update, context)
        return MAIN_MENU
    
    else:
        # BIRINCHI: Qarz flag'larini tekshirish
        if (context.user_data.get('awaiting_debt_person') or 
            context.user_data.get('awaiting_debt_amount') or 
            context.user_data.get('awaiting_debt_description')):
            logger.info("💼 Qarz ma'lumot kiritish...")
            from handlers.debt import handle_debt_text_input
            await handle_debt_text_input(update, context)
            return MAIN_MENU
        
        # Agar tugma emas va qarz flag'i yo'q - quick expense handler
        logger.info("📝 Quick expense handler'iga yo'naltirish...")
        from handlers.quick_expense import quick_expense_handler
        await quick_expense_handler(update, context)
        return MAIN_MENU


# =====================================================
# CANCEL HANDLER
# =====================================================
async def cancel_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Jarayonni bekor qilish
    
    Args:
        update: Telegram update
        context: Callback context
        
    Returns:
        int: ConversationHandler.END
    """
    language = context.user_data.get('language', 'uz')
    
    cancel_texts = {
        'uz': "❌ Jarayon bekor qilindi. /start ni bosing.",
        'ru': "❌ Процесс отменён. Нажмите /start.",
        'en': "❌ Process cancelled. Press /start.",
        'tr': "❌ İşlem iptal edildi. /start'a basın.",
        'ar': "❌ تم إلغاء العملية. اضغط /start."
    }
    
    if update.callback_query:
        await update.callback_query.answer()
        await update.callback_query.edit_message_text(
            text=cancel_texts.get(language, cancel_texts['uz'])
        )
    else:
        await update.message.reply_text(
            text=cancel_texts.get(language, cancel_texts['uz'])
        )
    
    return ConversationHandler.END


# =====================================================
# DELETE DATA HANDLER
# =====================================================
async def delete_data_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Ma'lumot o'chirish menyusi - Daromad va Xarajatlar
    """
    query = update.callback_query
    await query.answer()
    
    language = context.user_data.get('language', 'uz')
    
    delete_texts = {
        'uz': '🗑️ <b>Ma\'lumot o\'chirish</b>\n\nNimani tahrirlash/o\'chirmoqchisiz?',
        'ru': '🗑️ <b>Удаление данных</b>\n\nЧто хотите редактировать/удалить?',
        'en': '🗑️ <b>Delete Data</b>\n\nWhat do you want to edit/delete?',
        'tr': '🗑️ <b>Veri Silme</b>\n\nNeyi düzenlemek/silmek istiyorsunuz?',
        'ar': '🗑️ <b>حذف البيانات</b>\n\nماذا تريد تعديل/حذف؟'
    }
    
    from keyboards.inline import get_delete_data_keyboard
    keyboard = get_delete_data_keyboard(language)
    
    try:
        await query.edit_message_text(
            delete_texts.get(language, delete_texts['uz']),
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    except Exception:
        await query.message.reply_text(
            delete_texts.get(language, delete_texts['uz']),
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    
    return MAIN_MENU


async def delete_expenses_list_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Xarajatlar ro'yxatini ko'rsatish"""
    query = update.callback_query
    await query.answer()
    
    language = context.user_data.get('language', 'uz')
    telegram_id = context.user_data.get('telegram_id')
    
    from utils.filters import get_last_n_days_range
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    from config import Categories
    
    start_date, end_date = get_last_n_days_range(30)
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
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(back_text.get(language, back_text['uz']), callback_data='delete_data')]])
        try:
            await query.edit_message_text(no_data.get(language, no_data['uz']), reply_markup=keyboard)
        except Exception:
            pass
        return MAIN_MENU
    
    header = {
        'uz': '💸 <b>Xarajatlar</b>\n\nTahrirlash uchun tanlang:',
        'ru': '💸 <b>Расходы</b>\n\nВыберите для редактирования:',
        'en': '💸 <b>Expenses</b>\n\nSelect to edit:',
        'tr': '💸 <b>Giderler</b>\n\nDüzenlemek için seçin:',
        'ar': '💸 <b>المصروفات</b>\n\nاختر للتعديل:'
    }
    
    keyboard_buttons = []
    for exp in expenses[:10]:
        # Get category info
        cat_icon = '📌'
        cat_name_short = 'other'  # default category key
        
        # Get category from relationship
        if hasattr(exp, 'category') and exp.category:
            cat_icon = exp.category.icon if hasattr(exp.category, 'icon') else '📌'
            # Get localized category name
            if hasattr(exp.category, 'key'):
                cat_name_short = Categories.NAMES.get(exp.category.key, {}).get(language, exp.category.key)
        
        # Format display
        amount_formatted = f"{exp.amount:,.0f}".replace(',', ' ')
        date_formatted = exp.created_at.strftime('%d.%m.%Y')
        
        # Add description if exists (max 25 chars)
        description_text = ""
        if exp.description:
            desc_short = exp.description[:25] + "..." if len(exp.description) > 25 else exp.description
            description_text = f"\n📝 {desc_short}"
        
        btn_text = f"{cat_icon} {cat_name_short}\n💰 {amount_formatted} so'm\n📅 {date_formatted}{description_text}"
        keyboard_buttons.append([InlineKeyboardButton(btn_text, callback_data=f'edit_expense_{exp.id}')])
    
    back_text = {'uz': '« Orqaga', 'ru': '« Назад', 'en': '« Back', 'tr': '« Geri', 'ar': '« رجوع'}
    keyboard_buttons.append([InlineKeyboardButton(back_text.get(language, back_text['uz']), callback_data='delete_data')])
    
    try:
        await query.edit_message_text(
            header.get(language, header['uz']),
            reply_markup=InlineKeyboardMarkup(keyboard_buttons),
            parse_mode='HTML'
        )
    except Exception:
        pass
    
    return MAIN_MENU


async def delete_incomes_list_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Daromadlar ro'yxatini ko'rsatish"""
    query = update.callback_query
    await query.answer()
    
    language = context.user_data.get('language', 'uz')
    telegram_id = context.user_data.get('telegram_id')
    
    from utils.filters import get_last_n_days_range
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    start_date, end_date = get_last_n_days_range(30)
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
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton(back_text.get(language, back_text['uz']), callback_data='delete_data')]])
        try:
            await query.edit_message_text(no_data.get(language, no_data['uz']), reply_markup=keyboard)
        except Exception:
            pass
        return MAIN_MENU
    
    header = {
        'uz': '💰 <b>Daromadlar</b>\n\nTahrirlash uchun tanlang:',
        'ru': '💰 <b>Доходы</b>\n\nВыберите для редактирования:',
        'en': '💰 <b>Incomes</b>\n\nSelect to edit:',
        'tr': '💰 <b>Gelirler</b>\n\nDüzenlemek için seçin:',
        'ar': '💰 <b>الدخل</b>\n\nاختر للتعديل:'
    }
    
    keyboard_buttons = []
    for inc in incomes[:10]:
        # Format display
        amount_formatted = f"{inc.amount:,.0f}".replace(',', ' ')
        date_formatted = inc.created_at.strftime('%d.%m.%Y')
        
        # Add source if exists (max 25 chars)
        source_text = ""
        if inc.source:
            source_short = inc.source[:25] + "..." if len(inc.source) > 25 else inc.source
            source_text = f"\n📝 {source_short}"
        
        # Localized "Income" label
        income_labels = {
            'uz': '💰 Daromad',
            'ru': '💰 Доход', 
            'en': '💰 Income',
            'tr': '💰 Gelir',
            'ar': '💰 دخل'
        }
        
        btn_text = f"{income_labels.get(language, income_labels['uz'])}\n💵 {amount_formatted} so'm\n📅 {date_formatted}{source_text}"
        keyboard_buttons.append([InlineKeyboardButton(btn_text, callback_data=f'edit_income_{inc.id}')])
    
    back_text = {'uz': '« Orqaga', 'ru': '« Назад', 'en': '« Back', 'tr': '« Geri', 'ar': '« رجوع'}
    keyboard_buttons.append([InlineKeyboardButton(back_text.get(language, back_text['uz']), callback_data='delete_data')])
    
    try:
        await query.edit_message_text(
            header.get(language, header['uz']),
            reply_markup=InlineKeyboardMarkup(keyboard_buttons),
            parse_mode='HTML'
        )
    except Exception:
        pass
    
    return MAIN_MENU


async def edit_expense_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Xarajat ma'lumotlarini ko'rsatish"""
    query = update.callback_query
    await query.answer()
    
    language = context.user_data.get('language', 'uz')
    telegram_id = context.user_data.get('telegram_id')
    expense_id = int(query.data.replace('edit_expense_', ''))
    
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    from config import Categories
    
    expense = db_manager.get_expense_by_id(expense_id, telegram_id)
    
    if not expense:
        try:
            await query.edit_message_text("❌ Xarajat topilmadi")
        except Exception:
            pass
        return MAIN_MENU
    
    # Get category key properly from relationship
    category_key = expense.category.key if hasattr(expense, 'category') and expense.category and hasattr(expense.category, 'key') else 'other'
    
    cat_name = Categories.NAMES.get(category_key, {}).get(language, category_key)
    cat_icon = '📌'
    for cat in Categories.LIST:
        if cat['key'] == category_key:
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
    btn = btn_texts.get(language, btn_texts['uz'])
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(btn['delete'], callback_data=f'confirm_del_expense_{expense_id}'),
            InlineKeyboardButton(btn['edit'], callback_data=f'do_edit_expense_{expense_id}')
        ],
        [InlineKeyboardButton(btn['back'], callback_data='delete_expenses_list')]
    ])
    
    try:
        await query.edit_message_text(
            detail_texts.get(language, detail_texts['uz']),
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    except Exception:
        pass
    
    return MAIN_MENU


async def edit_income_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Daromad ma'lumotlarini ko'rsatish"""
    query = update.callback_query
    await query.answer()
    
    language = context.user_data.get('language', 'uz')
    telegram_id = context.user_data.get('telegram_id')
    income_id = int(query.data.replace('edit_income_', ''))
    
    from telegram import InlineKeyboardButton, InlineKeyboardMarkup
    
    income = db_manager.get_income_by_id(income_id, telegram_id)
    
    if not income:
        try:
            await query.edit_message_text("❌ Daromad topilmadi")
        except Exception:
            pass
        return MAIN_MENU
    
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
    btn = btn_texts.get(language, btn_texts['uz'])
    
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(btn['delete'], callback_data=f'confirm_del_income_{income_id}'),
            InlineKeyboardButton(btn['edit'], callback_data=f'do_edit_income_{income_id}')
        ],
        [InlineKeyboardButton(btn['back'], callback_data='delete_incomes_list')]
    ])
    
    try:
        await query.edit_message_text(
            detail_texts.get(language, detail_texts['uz']),
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    except Exception:
        pass
    
    return MAIN_MENU


async def confirm_delete_expense_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Xarajatni o'chirish"""
    query = update.callback_query
    await query.answer()
    
    language = context.user_data.get('language', 'uz')
    telegram_id = context.user_data.get('telegram_id')
    expense_id = int(query.data.replace('confirm_del_expense_', ''))
    
    if db_manager.delete_expense(expense_id, telegram_id):
        msg = {
            'uz': '✅ Xarajat o\'chirildi!',
            'ru': '✅ Расход удалён!',
            'en': '✅ Expense deleted!',
            'tr': '✅ Gider silindi!',
            'ar': '✅ تم حذف المصروف!'
        }
        try:
            await query.edit_message_text(msg.get(language, msg['uz']))
        except Exception:
            pass
    else:
        try:
            await query.edit_message_text("❌ Xato yuz berdi")
        except Exception:
            pass
    
    return MAIN_MENU


async def confirm_delete_income_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Daromadni o'chirish"""
    query = update.callback_query
    await query.answer()
    
    language = context.user_data.get('language', 'uz')
    telegram_id = context.user_data.get('telegram_id')
    income_id = int(query.data.replace('confirm_del_income_', ''))
    
    if db_manager.delete_income(income_id, telegram_id):
        msg = {
            'uz': '✅ Daromad o\'chirildi!',
            'ru': '✅ Доход удалён!',
            'en': '✅ Income deleted!',
            'tr': '✅ Gelir silindi!',
            'ar': '✅ تم حذف الدخل!'
        }
        try:
            await query.edit_message_text(msg.get(language, msg['uz']))
        except Exception:
            pass
    else:
        try:
            await query.edit_message_text("❌ Xato yuz berdi")
        except Exception:
            pass
    
    return MAIN_MENU


async def do_edit_expense_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Xarajatni tahrirlash - o'chirib qayta qo'shish"""
    query = update.callback_query
    await query.answer()
    
    language = context.user_data.get('language', 'uz')
    telegram_id = context.user_data.get('telegram_id')
    expense_id = int(query.data.replace('do_edit_expense_', ''))
    
    if db_manager.delete_expense(expense_id, telegram_id):
        msg = {
            'uz': '✏️ Xarajat o\'chirildi.\n\n💸 Endi yangi xarajat qo\'shing:',
            'ru': '✏️ Расход удалён.\n\n💸 Теперь добавьте новый расход:',
            'en': '✏️ Expense deleted.\n\n💸 Now add new expense:',
            'tr': '✏️ Gider silindi.\n\n💸 Şimdi yeni gider ekleyin:',
            'ar': '✏️ تم حذف المصروف.\n\n💸 الآن أضف مصروف جديد:'
        }
        try:
            await query.edit_message_text(msg.get(language, msg['uz']))
        except Exception:
            pass
        
        from handlers.expense import add_expense_command
        await add_expense_command(update, context)
    else:
        try:
            await query.edit_message_text("❌ Xato yuz berdi")
        except Exception:
            pass
    
    return MAIN_MENU


async def do_edit_income_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Daromadni tahrirlash - o'chirib qayta qo'shish"""
    query = update.callback_query
    await query.answer()
    
    language = context.user_data.get('language', 'uz')
    telegram_id = context.user_data.get('telegram_id')
    income_id = int(query.data.replace('do_edit_income_', ''))
    
    if db_manager.delete_income(income_id, telegram_id):
        msg = {
            'uz': '✏️ Daromad o\'chirildi.\n\n💰 Endi yangi daromad qo\'shing:',
            'ru': '✏️ Доход удалён.\n\n💰 Теперь добавьте новый доход:',
            'en': '✏️ Income deleted.\n\n💰 Now add new income:',
            'tr': '✏️ Gelir silindi.\n\n💰 Şimdi yeni gelir ekleyin:',
            'ar': '✏️ تم حذف الدخل.\n\n💰 الآن أضف دخل جديد:'
        }
        try:
            await query.edit_message_text(msg.get(language, msg['uz']))
        except Exception:
            pass
        
        from handlers.income import add_income_command
        await add_income_command(update, context)
    else:
        try:
            await query.edit_message_text("❌ Xato yuz berdi")
        except Exception:
            pass
    
    return MAIN_MENU


# =====================================================
# DEBT HANDLERS (wrappers)
# =====================================================
# =====================================================
# CONVERSATION HANDLER SETUP
# =====================================================
def setup_conversation_handler() -> ConversationHandler:
    """
    Start conversation handler'ni yaratish
    
    Returns:
        ConversationHandler: Configured handler
    """
    return ConversationHandler(
        entry_points=[
            CommandHandler('start', start_command),
        ],
        states={
            SELECTING_LANGUAGE: [
                CallbackQueryHandler(language_selection, pattern='^lang_'),
            ],
            MAIN_MENU: [
                CallbackQueryHandler(settings_menu, pattern='^settings$'),
                CallbackQueryHandler(change_language, pattern='^change_language$'),
                CallbackQueryHandler(delete_data_menu, pattern='^delete_data$'),
                CallbackQueryHandler(delete_expenses_list_handler, pattern='^delete_expenses_list$'),
                CallbackQueryHandler(delete_incomes_list_handler, pattern='^delete_incomes_list$'),
                CallbackQueryHandler(edit_expense_handler, pattern='^edit_expense_'),
                CallbackQueryHandler(edit_income_handler, pattern='^edit_income_'),
                CallbackQueryHandler(confirm_delete_expense_handler, pattern='^confirm_del_expense_'),
                CallbackQueryHandler(confirm_delete_income_handler, pattern='^confirm_del_income_'),
                CallbackQueryHandler(do_edit_expense_handler, pattern='^do_edit_expense_'),
                CallbackQueryHandler(do_edit_income_handler, pattern='^do_edit_income_'),
                CallbackQueryHandler(show_main_menu, pattern='^back_main$'),
                # Reply keyboard tugmalari va tezkor xarajat
                MessageHandler(filters.TEXT & ~filters.COMMAND, menu_button_handler),
            ],
        },
        fallbacks=[
            CommandHandler('cancel', cancel_handler),
            CommandHandler('start', start_command),
        ],
        name="start_conversation",
        persistent=False,
        allow_reentry=True
    )
