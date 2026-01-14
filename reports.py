"""
SmartWallet AI Bot - Reports Handler (HTML Format with Charts)
==============================================================
Hisobotlar handler'i - HTML format, diagrammalar bilan

Author: SmartWallet AI Team
Version: 7.0.0 - HTML Edition with Demo Design
"""

import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database.db_manager import DatabaseManager
from keyboards.inline import get_report_type_keyboard, get_report_format_choice_keyboard
from utils.translations import get_text
from utils.filters import (
    get_today_range, 
    get_this_week_range, 
    get_this_month_range, 
    get_this_year_range, 
    get_last_n_days_range
)
from reports.html_generator import generate_html_report
from config import Categories

logger = logging.getLogger(__name__)
db_manager = DatabaseManager()


async def reports_menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hisobotlar menyusini ko'rsatish"""
    user_language = context.user_data.get('language', 'uz')
    
    menu_text = {
        'uz': '📊 <b>Hisobotlar</b>\n\nKerakli hisobot turini tanlang:',
        'ru': '📊 <b>Отчёты</b>\n\nВыберите тип отчёта:',
        'en': '📊 <b>Reports</b>\n\nSelect report type:',
        'tr': '📊 <b>Raporlar</b>\n\nRapor türünü seçin:',
        'ar': '📊 <b>التقارير</b>\n\nاختر نوع التقرير:'
    }
    
    keyboard = get_report_type_keyboard(user_language)
    
    if update.callback_query:
        await update.callback_query.edit_message_text(
            menu_text.get(user_language, menu_text['uz']),
            reply_markup=keyboard,
            parse_mode='HTML'
        )
    else:
        await update.message.reply_text(
            menu_text.get(user_language, menu_text['uz']),
            reply_markup=keyboard,
            parse_mode='HTML'
        )


async def report_type_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hisobot turini tanlash - format so'rash"""
    query = update.callback_query
    await query.answer()
    
    user_language = context.user_data.get('language', 'uz')
    report_type = query.data.replace('report_', '')
    
    # Format tanlash so'rovi
    format_texts = {
        'uz': '📊 <b>Hisobot formatini tanlang:</b>\n\nQayerda ko\'rishni xohlaysiz?',
        'ru': '📊 <b>Выберите формат отчёта:</b>\n\nГде хотите посмотреть?',
        'en': '📊 <b>Select report format:</b>\n\nWhere do you want to view?',
        'tr': '📊 <b>Rapor formatını seçin:</b>\n\nNerede görmek istiyorsunuz?',
        'ar': '📊 <b>اختر صيغة التقرير:</b>\n\nأين تريد المشاهدة؟'
    }
    
    keyboard = get_report_format_choice_keyboard(user_language, report_type)
    
    await query.edit_message_text(
        format_texts.get(user_language, format_texts['uz']),
        reply_markup=keyboard,
        parse_mode='HTML'
    )


async def report_bot_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hisobotni bot ichida text ko'rinishida ko'rsatish"""
    query = update.callback_query
    await query.answer()
    
    user_language = context.user_data.get('language', 'uz')
    # report_bot_daily -> daily
    report_type = query.data.replace('report_bot_', '')
    telegram_id = context.user_data.get('telegram_id')
    
    # Sana oralig'ini aniqlash
    if report_type == 'daily':
        start_date, end_date = get_today_range()
        period_name = {'uz': 'Kunlik', 'ru': 'Ежедневный', 'en': 'Daily', 'tr': 'Günlük', 'ar': 'يومي'}
    elif report_type == 'three_days':
        start_date, end_date = get_last_n_days_range(3)
        period_name = {'uz': '3 kunlik', 'ru': '3-дневный', 'en': '3-Day', 'tr': '3 Günlük', 'ar': '3 أيام'}
    elif report_type == 'weekly':
        start_date, end_date = get_this_week_range()
        period_name = {'uz': 'Haftalik', 'ru': 'Недельный', 'en': 'Weekly', 'tr': 'Haftalık', 'ar': 'أسبوعي'}
    elif report_type == 'monthly':
        start_date, end_date = get_this_month_range()
        period_name = {'uz': 'Oylik', 'ru': 'Месячный', 'en': 'Monthly', 'tr': 'Aylık', 'ar': 'شهري'}
    elif report_type == 'yearly':
        start_date, end_date = get_this_year_range()
        period_name = {'uz': 'Yillik', 'ru': 'Годовой', 'en': 'Yearly', 'tr': 'Yıllık', 'ar': 'سنوي'}
    else:
        start_date, end_date = get_this_week_range()
        period_name = {'uz': 'Haftalik', 'ru': 'Недельный', 'en': 'Weekly', 'tr': 'Haftalık', 'ar': 'أسبوعي'}
    
    # Ma'lumotlarni olish
    expenses = db_manager.get_user_expenses(telegram_id, start_date, end_date)
    incomes = db_manager.get_user_incomes(telegram_id, start_date, end_date)
    
    if not expenses and not incomes:
        no_data_msg = get_text('no_data_for_report', user_language)
        await query.edit_message_text(no_data_msg)
        return
    
    # Ma'lumotlarni hisoblash
    total_expense = db_manager.get_total_expenses(telegram_id, start_date, end_date)
    total_income = db_manager.get_total_income(telegram_id, start_date, end_date)
    balance = total_income - total_expense
    expenses_by_category = db_manager.get_expenses_by_category(telegram_id, start_date, end_date)
    
    # Text hisobot yaratish
    period = period_name.get(user_language, period_name['uz'])
    
    # Header
    report_text = f"📊 <b>{period} hisobot</b>\n"
    report_text += f"📅 {start_date.strftime('%d.%m.%Y')} - {end_date.strftime('%d.%m.%Y')}\n"
    report_text += "━" * 25 + "\n\n"
    
    # Summary
    summary_labels = {
        'uz': {'income': '💰 Jami daromad', 'expense': '💸 Jami xarajat', 'balance': '💵 Balans'},
        'ru': {'income': '💰 Всего доход', 'expense': '💸 Всего расход', 'balance': '💵 Баланс'},
        'en': {'income': '💰 Total Income', 'expense': '💸 Total Expense', 'balance': '💵 Balance'},
        'tr': {'income': '💰 Toplam Gelir', 'expense': '💸 Toplam Gider', 'balance': '💵 Bakiye'},
        'ar': {'income': '💰 إجمالي الدخل', 'expense': '💸 إجمالي المصروف', 'balance': '💵 الرصيد'}
    }
    labels = summary_labels.get(user_language, summary_labels['uz'])
    
    report_text += f"{labels['income']}: <b>{total_income:,.0f}</b> so'm\n"
    report_text += f"{labels['expense']}: <b>{total_expense:,.0f}</b> so'm\n"
    
    balance_emoji = "📈" if balance >= 0 else "📉"
    report_text += f"{balance_emoji} {labels['balance']}: <b>{balance:,.0f}</b> so'm\n\n"
    
    # Kategoriyalar bo'yicha xarajatlar
    if expenses_by_category:
        category_header = {
            'uz': '📂 Kategoriyalar bo\'yicha:',
            'ru': '📂 По категориям:',
            'en': '📂 By categories:',
            'tr': '📂 Kategorilere göre:',
            'ar': '📂 حسب الفئات:'
        }
        report_text += f"\n{category_header.get(user_language, category_header['uz'])}\n"
        report_text += "─" * 20 + "\n"
        
        # expenses_by_category is a list of dicts: [{'category': Category, 'total': Decimal, 'count': int}]
        for item in expenses_by_category:
            cat_obj = item.get('category')
            amount = item.get('total', 0)
            
            if cat_obj:
                cat_key = cat_obj.key
                cat_name = Categories.NAMES.get(cat_key, {}).get(user_language, cat_key)
                cat_icon = '📌'
                for cat in Categories.LIST:
                    if cat['key'] == cat_key:
                        cat_icon = cat['icon']
                        break
                
                percent = (float(amount) / float(total_expense) * 100) if total_expense > 0 else 0
                report_text += f"{cat_icon} {cat_name}: {amount:,.0f} ({percent:.1f}%)\n"
    
    # Oxirgi tranzaksiyalar
    if expenses or incomes:
        transactions_header = {
            'uz': '\n📋 Oxirgi tranzaksiyalar:',
            'ru': '\n📋 Последние транзакции:',
            'en': '\n📋 Recent transactions:',
            'tr': '\n📋 Son işlemler:',
            'ar': '\n📋 آخر المعاملات:'
        }
        report_text += f"\n{transactions_header.get(user_language, transactions_header['uz'])}\n"
        report_text += "─" * 20 + "\n"
        
        # Oxirgi 5 ta xarajat
        for exp in expenses[:5]:
            cat_icon = '📌'
            for cat in Categories.LIST:
                if cat['key'] == exp.category:
                    cat_icon = cat['icon']
                    break
            report_text += f"💸 {cat_icon} {exp.amount:,.0f} - {exp.created_at.strftime('%d.%m')}\n"
        
        # Oxirgi 5 ta daromad
        for inc in incomes[:5]:
            report_text += f"💰 +{inc.amount:,.0f} - {inc.created_at.strftime('%d.%m')}\n"
    
    # Orqaga tugmasi
    back_texts = {
        'uz': '« Orqaga',
        'ru': '« Назад',
        'en': '« Back',
        'tr': '« Geri',
        'ar': '« رجوع'
    }
    
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(back_texts.get(user_language, back_texts['uz']), callback_data='reports')]
    ])
    
    await query.edit_message_text(
        report_text,
        reply_markup=keyboard,
        parse_mode='HTML'
    )


async def report_html_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hisobotni HTML formatida yaratish va yuborish"""
    query = update.callback_query
    await query.answer()
    
    user_language = context.user_data.get('language', 'uz')
    # report_html_daily -> daily
    report_type = query.data.replace('report_html_', '')
    telegram_id = context.user_data.get('telegram_id')
    
    # Sana oralig'ini aniqlash
    if report_type == 'daily':
        start_date, end_date = get_today_range()
    elif report_type == 'three_days':
        start_date, end_date = get_last_n_days_range(3)
    elif report_type == 'weekly':
        start_date, end_date = get_this_week_range()
    elif report_type == 'monthly':
        start_date, end_date = get_this_month_range()
    elif report_type == 'yearly':
        start_date, end_date = get_this_year_range()
    else:
        start_date, end_date = get_this_week_range()
    
    # Ma'lumotlarni olish
    expenses = db_manager.get_user_expenses(telegram_id, start_date, end_date)
    incomes = db_manager.get_user_incomes(telegram_id, start_date, end_date)
    
    if not expenses and not incomes:
        no_data_msg = get_text('no_data_for_report', user_language)
        await query.edit_message_text(no_data_msg)
        return
    
    # Hisobot yaratish xabari - har safar boshqacha qilib yuborish
    generating_texts = {
        'uz': '⏳ HTML hisobot tayyorlanmoqda...',
        'ru': '⏳ Подготовка HTML отчёта...',
        'en': '⏳ Generating HTML report...',
        'tr': '⏳ HTML rapor hazırlanıyor...',
        'ar': '⏳ جاري إنشاء تقرير HTML...'
    }
    
    try:
        await query.edit_message_text(generating_texts.get(user_language, generating_texts['uz']))
    except Exception:
        # Xabar bir xil bo'lsa, davom etamiz
        pass
    
    try:
        # Ma'lumotlarni tayyorlash
        total_expense = db_manager.get_total_expenses(telegram_id, start_date, end_date)
        total_income = db_manager.get_total_income(telegram_id, start_date, end_date)
        balance = total_income - total_expense
        
        # Kategoriyalar bo'yicha
        expenses_by_category = db_manager.get_expenses_by_category(telegram_id, start_date, end_date)
        
        # HTML yaratish
        device_type = 'desktop'  # Standart
        file_path = generate_html_report(
            user_language=user_language,
            device_type=device_type,
            report_type=report_type,
            total_expense=total_expense,
            total_income=total_income,
            balance=balance,
            expenses_by_category=expenses_by_category,
            expenses=expenses,
            start_date=start_date,
            end_date=end_date
        )
        
        # HTML faylni yuborish
        # Fayl nomini yaratish
        report_names = {
            'daily': {'uz': 'Kunlik', 'en': 'Daily'},
            'three_days': {'uz': '3kunlik', 'en': '3days'},
            'weekly': {'uz': 'Haftalik', 'en': 'Weekly'},
            'monthly': {'uz': 'Oylik', 'en': 'Monthly'},
            'yearly': {'uz': 'Yillik', 'en': 'Yearly'}
        }
        
        report_name = report_names.get(report_type, report_names['daily']).get(user_language, 'Report')
        filename = f"SmartWallet_{report_name}_{datetime.now().strftime('%d%m%Y_%H%M')}.html"
        
        success_texts = {
            'uz': '✅ HTML hisobot tayyor! Brauzerda oching 🌐',
            'ru': '✅ HTML отчёт готов! Откройте в браузере 🌐',
            'en': '✅ HTML report ready! Open in browser 🌐',
            'tr': '✅ HTML rapor hazır! Tarayıcıda açın 🌐',
            'ar': '✅ تقرير HTML جاهز! افتح في المتصفح 🌐'
        }
        
        # Avval xabarni yangilab, keyin fayl yuboramiz
        try:
            await query.edit_message_text(success_texts.get(user_language, success_texts['uz']))
        except Exception:
            pass
        
        with open(file_path, 'rb') as f:
            await query.message.reply_document(
                document=f,
                filename=filename,
                caption=success_texts.get(user_language, success_texts['uz'])
            )
        
        logger.info(f"HTML hisobot yuborildi: user={telegram_id}, type={report_type}")
        
    except Exception as e:
        logger.error(f"HTML yaratishda xato: {e}", exc_info=True)
        error_texts = {
            'uz': '❌ Xatolik yuz berdi. Qaytadan urinib ko\'ring.',
            'ru': '❌ Произошла ошибка. Попробуйте снова.',
            'en': '❌ An error occurred. Please try again.',
            'tr': '❌ Bir hata oluştu. Lütfen tekrar deneyin.',
            'ar': '❌ حدث خطأ. يرجى المحاولة مرة أخرى.'
        }
        try:
            await query.edit_message_text(error_texts.get(user_language, error_texts['uz']))
        except Exception:
            await query.message.reply_text(error_texts.get(user_language, error_texts['uz']))


# Dummy functions
async def daily_report_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await report_type_handler(update, context)

async def weekly_report_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await report_type_handler(update, context)

async def monthly_report_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await report_type_handler(update, context)

async def yearly_report_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await report_type_handler(update, context)

async def custom_report_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await report_type_handler(update, context)

async def export_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await report_type_handler(update, context)

def setup_conversation_handler():
    return None
