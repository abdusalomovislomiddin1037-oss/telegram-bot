"""
SmartWallet AI Bot - Translations
=================================
5 tilda tarjimalar (O'zbek, Rus, Ingliz, Turk, Arab)

Functions:
    - get_text: Matnni tarjima qilish
    - get_category_name: Kategoriya nomini olish
    - format_date: Sanani formatlash
    - format_currency: Valyutani formatlash

Author: SmartWallet AI Team
Version: 1.0.0
"""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, Dict, Any

from config import Categories, Currency


# =====================================================
# TRANSLATIONS DICTIONARY
# =====================================================
TRANSLATIONS = {
    # Umumiy matnlar
    'back': {
        'uz': '🔙 Orqaga qaytish',
        'ru': '🔙 Вернуться назад',
        'en': '🔙 Go Back',
        'tr': '🔙 Geri Dön',
        'ar': '🔙 العودة'
    },
    'cancel': {
        'uz': '🚫 Bekor qilish',
        'ru': '🚫 Отменить',
        'en': '🚫 Cancel',
        'tr': '🚫 İptal Et',
        'ar': '🚫 إلغاء'
    },
    'confirm': {
        'uz': '✅ Tasdiqlash',
        'ru': '✅ Подтвердить',
        'en': '✅ Confirm',
        'tr': '✅ Onayla',
        'ar': '✅ تأكيد'
    },
    'yes': {
        'uz': '👍 Ha',
        'ru': '👍 Да',
        'en': '👍 Yes',
        'tr': '👍 Evet',
        'ar': '👍 نعم'
    },
    'no': {
        'uz': '👎 Yo\'q',
        'ru': '👎 Нет',
        'en': '👎 No',
        'tr': '👎 Hayır',
        'ar': '👎 لا'
    },
    
    # Xarajat matnlari
    'expense_amount_prompt': {
        'uz': '💳 <b>Xarajat summasini kiriting:</b>\n\n'
              '💡 <i>Misol uchun:</i>\n'
              '• <code>50000 oziq-ovqat</code>\n'
              '• <code>taxi 25000</code>\n'
              '• <code>100000 restoran</code>',
        'ru': '💳 <b>Введите сумму расхода:</b>\n\n'
              '💡 <i>Например:</i>\n'
              '• <code>50000 продукты</code>\n'
              '• <code>такси 25000</code>\n'
              '• <code>100000 ресторан</code>',
        'en': '💳 <b>Enter expense amount:</b>\n\n'
              '💡 <i>Examples:</i>\n'
              '• <code>50000 groceries</code>\n'
              '• <code>taxi 25000</code>\n'
              '• <code>100000 restaurant</code>',
        'tr': '💳 <b>Gider tutarını girin:</b>\n\n'
              '💡 <i>Örnekler:</i>\n'
              '• <code>50000 yiyecek</code>\n'
              '• <code>taksi 25000</code>\n'
              '• <code>100000 restoran</code>',
        'ar': '💳 <b>أدخل مبلغ المصروف:</b>\n\n'
              '💡 <i>أمثلة:</i>\n'
              '• <code>50000 بقالة</code>\n'
              '• <code>تاكسي 25000</code>\n'
              '• <code>100000 مطعم</code>'
    },
    'expense_category_prompt': {
        'uz': '🏷️ <b>Kategoriyani tanlang</b>\n\n'
              'Xarajat qaysi turga tegishli?',
        'ru': '🏷️ <b>Выберите категорию</b>\n\n'
              'К какому типу относится расход?',
        'en': '🏷️ <b>Select Category</b>\n\n'
              'What type of expense is this?',
        'tr': '🏷️ <b>Kategori Seçin</b>\n\n'
              'Bu gider hangi türe ait?',
        'ar': '🏷️ <b>اختر الفئة</b>\n\n'
              'ما نوع هذا المصروف؟'
    },
    'expense_description_prompt': {
        'uz': '📝 <b>Izoh qo\'shing</b> (ixtiyoriy)\n\n'
              '💡 <i>Masalan:</i>\n'
              '• "Korzinka supermarket"\n'
              '• "Taxi - uyga"\n\n'
              '⏭️ O\'tkazib yuborish uchun /skip bosing',
        'ru': '📝 <b>Добавьте описание</b> (необязательно)\n\n'
              '💡 <i>Например:</i>\n'
              '• "Супермаркет Корзинка"\n'
              '• "Такси - домой"\n\n'
              '⏭️ Нажмите /skip чтобы пропустить',
        'en': '📝 <b>Add Description</b> (optional)\n\n'
              '💡 <i>Examples:</i>\n'
              '• "Korzinka supermarket"\n'
              '• "Taxi - home"\n\n'
              '⏭️ Press /skip to skip',
        'tr': '📝 <b>Açıklama Ekleyin</b> (isteğe bağlı)\n\n'
              '💡 <i>Örnekler:</i>\n'
              '• "Korzinka süpermarket"\n'
              '• "Taksi - eve"\n\n'
              '⏭️ Atlamak için /skip basın',
        'ar': '📝 <b>أضف وصفاً</b> (اختياري)\n\n'
              '💡 <i>أمثلة:</i>\n'
              '• "سوبرماركت كورزينكا"\n'
              '• "تاكسي - المنزل"\n\n'
              '⏭️ اضغط /skip للتخطي'
    },
    'expense_added': {
        'uz': '✅ <b>Xarajat muvaffaqiyatli saqlandi!</b>\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n'
              '💵 <b>Summa:</b> {amount}\n'
              '🏷️ <b>Kategoriya:</b> {category}\n'
              '📅 <b>Sana:</b> {date}\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '💡 Yana xarajat qo\'shish uchun summa yozing',
        'ru': '✅ <b>Расход успешно сохранён!</b>\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n'
              '💵 <b>Сумма:</b> {amount}\n'
              '🏷️ <b>Категория:</b> {category}\n'
              '📅 <b>Дата:</b> {date}\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '💡 Для нового расхода введите сумму',
        'en': '✅ <b>Expense saved successfully!</b>\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n'
              '💵 <b>Amount:</b> {amount}\n'
              '🏷️ <b>Category:</b> {category}\n'
              '📅 <b>Date:</b> {date}\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '💡 Enter amount to add another expense',
        'tr': '✅ <b>Gider başarıyla kaydedildi!</b>\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n'
              '💵 <b>Tutar:</b> {amount}\n'
              '🏷️ <b>Kategori:</b> {category}\n'
              '📅 <b>Tarih:</b> {date}\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '💡 Başka gider için tutar girin',
        'ar': '✅ <b>تم حفظ المصروف بنجاح!</b>\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n'
              '💵 <b>المبلغ:</b> {amount}\n'
              '🏷️ <b>الفئة:</b> {category}\n'
              '📅 <b>التاريخ:</b> {date}\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '💡 أدخل مبلغ لإضافة مصروف آخر'
    },
    'invalid_amount': {
        'uz': '⚠️ <b>Noto\'g\'ri format!</b>\n\n'
              'Iltimos, faqat raqam kiriting.\n\n'
              '💡 <i>To\'g\'ri format:</i>\n'
              '• <code>50000</code>\n'
              '• <code>1500000</code>',
        'ru': '⚠️ <b>Неверный формат!</b>\n\n'
              'Пожалуйста, введите только число.\n\n'
              '💡 <i>Правильный формат:</i>\n'
              '• <code>50000</code>\n'
              '• <code>1500000</code>',
        'en': '⚠️ <b>Invalid format!</b>\n\n'
              'Please enter numbers only.\n\n'
              '💡 <i>Correct format:</i>\n'
              '• <code>50000</code>\n'
              '• <code>1500000</code>',
        'tr': '⚠️ <b>Geçersiz format!</b>\n\n'
              'Lütfen sadece sayı girin.\n\n'
              '💡 <i>Doğru format:</i>\n'
              '• <code>50000</code>\n'
              '• <code>1500000</code>',
        'ar': '⚠️ <b>تنسيق غير صالح!</b>\n\n'
              'الرجاء إدخال أرقام فقط.\n\n'
              '💡 <i>التنسيق الصحيح:</i>\n'
              '• <code>50000</code>\n'
              '• <code>1500000</code>'
    },
    
    # Daromad matnlari
    'income_amount_prompt': {
        'uz': '💰 <b>Daromad summasini kiriting:</b>\n\n'
              '💡 Misol: <code>5000000 Oylik</code>',
        'ru': '💰 <b>Введите сумму дохода:</b>\n\n'
              '💡 Пример: <code>5000000 Зарплата</code>',
        'en': '💰 <b>Enter income amount:</b>\n\n'
              '💡 Example: <code>5000000 Salary</code>',
        'tr': '💰 <b>Gelir tutarını girin:</b>\n\n'
              '💡 Örnek: <code>5000000 Maaş</code>',
        'ar': '💰 <b>أدخل مبلغ الدخل:</b>\n\n'
              '💡 مثال: <code>5000000 راتب</code>'
    },
    'income_source_prompt': {
        'uz': '🏢 <b>Daromad manbasi</b>\n\n'
              'Daromad qayerdan keldi?\n\n'
              '💡 <i>Masalan:</i>\n'
              '• "IT Park" — ish joyi\n'
              '• "Frilanser loyiha" — qo\'shimcha\n'
              '• "Oylik maosh"',
        'ru': '🏢 <b>Источник дохода</b>\n\n'
              'Откуда поступил доход?\n\n'
              '💡 <i>Например:</i>\n'
              '• "IT Park" — место работы\n'
              '• "Фриланс проект" — дополнительно\n'
              '• "Зарплата"',
        'en': '🏢 <b>Income Source</b>\n\n'
              'Where did the income come from?\n\n'
              '💡 <i>Examples:</i>\n'
              '• "IT Park" — workplace\n'
              '• "Freelance project" — additional\n'
              '• "Monthly salary"',
        'tr': '🏢 <b>Gelir Kaynağı</b>\n\n'
              'Gelir nereden geldi?\n\n'
              '💡 <i>Örnekler:</i>\n'
              '• "IT Park" — iş yeri\n'
              '• "Serbest proje" — ek\n'
              '• "Aylık maaş"',
        'ar': '🏢 <b>مصدر الدخل</b>\n\n'
              'من أين جاء الدخل؟\n\n'
              '💡 <i>أمثلة:</i>\n'
              '• "IT Park" — مكان العمل\n'
              '• "مشروع حر" — إضافي\n'
              '• "راتب شهري"'
    },
    'income_type_prompt': {
        'uz': '📋 <b>Daromad turini tanlang</b>\n\n'
              'Qaysi turdagi daromad?',
        'ru': '📋 <b>Выберите тип дохода</b>\n\n'
              'Какой тип дохода?',
        'en': '📋 <b>Select Income Type</b>\n\n'
              'What type of income is this?',
        'tr': '📋 <b>Gelir Türünü Seçin</b>\n\n'
              'Bu ne tür bir gelir?',
        'ar': '📋 <b>اختر نوع الدخل</b>\n\n'
              'ما نوع هذا الدخل؟'
    },
    'income_added': {
        'uz': '✅ <b>Daromad muvaffaqiyatli saqlandi!</b>\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n'
              '💵 <b>Summa:</b> {amount}\n'
              '🏢 <b>Manba:</b> {source}\n'
              '📅 <b>Sana:</b> {date}\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '📊 Statistikani ko\'rish uchun "Hisobotlar" ni bosing',
        'ru': '✅ <b>Доход успешно сохранён!</b>\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n'
              '💵 <b>Сумма:</b> {amount}\n'
              '🏢 <b>Источник:</b> {source}\n'
              '📅 <b>Дата:</b> {date}\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '📊 Нажмите "Отчёты" для просмотра статистики',
        'en': '✅ <b>Income saved successfully!</b>\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n'
              '💵 <b>Amount:</b> {amount}\n'
              '🏢 <b>Source:</b> {source}\n'
              '📅 <b>Date:</b> {date}\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '📊 Press "Reports" to view statistics',
        'tr': '✅ <b>Gelir başarıyla kaydedildi!</b>\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n'
              '💵 <b>Tutar:</b> {amount}\n'
              '🏢 <b>Kaynak:</b> {source}\n'
              '📅 <b>Tarih:</b> {date}\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '📊 İstatistikleri görüntülemek için "Raporlar"a basın',
        'ar': '✅ <b>تم حفظ الدخل بنجاح!</b>\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n'
              '💵 <b>المبلغ:</b> {amount}\n'
              '🏢 <b>المصدر:</b> {source}\n'
              '📅 <b>التاريخ:</b> {date}\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '📊 اضغط "التقارير" لعرض الإحصائيات'
    },
    
    # Qarz matnlari
    'debt_menu': {
        'uz': '💼 <b>Qarzlar</b>\n\nKerakli bo\'limni tanlang:',
        'ru': '💼 <b>Долги</b>\n\nВыберите раздел:',
        'en': '💼 <b>Debts</b>\n\nSelect section:',
        'tr': '💼 <b>Borçlar</b>\n\nBir bölüm seçin:',
        'ar': '💼 <b>الديون</b>\n\nاختر القسم:'
    },
    'debt_type_prompt': {
        'uz': '💼 Qarz turini tanlang:',
        'ru': '💼 Выберите тип долга:',
        'en': '💼 Select debt type:',
        'tr': '💼 Borç türünü seçin:',
        'ar': '💼 اختر نوع الدين:'
    },
    'debt_person_prompt': {
        'uz': '👤 <b>Shaxs ismini kiriting:</b>\n\n'
              '💡 <i>Misol:</i> Ali Valiyev',
        'ru': '👤 <b>Введите имя человека:</b>\n\n'
              '💡 <i>Например:</i> Али Валиев',
        'en': '👤 <b>Enter person name:</b>\n\n'
              '💡 <i>Example:</i> Ali Valiev',
        'tr': '👤 <b>Kişi adını girin:</b>\n\n'
              '💡 <i>Örnek:</i> Ali Valiyev',
        'ar': '👤 <b>أدخل اسم الشخص:</b>\n\n'
              '💡 <i>مثال:</i> علي فاليف'
    },
    'debt_amount_prompt': {
        'uz': '💰 <b>Qarz summasini kiriting:</b>\n\n'
              '💡 <i>Misol:</i> 500000',
        'ru': '💰 <b>Введите сумму долга:</b>\n\n'
              '💡 <i>Например:</i> 500000',
        'en': '💰 <b>Enter debt amount:</b>\n\n'
              '💡 <i>Example:</i> 500000',
        'tr': '💰 <b>Borç tutarını girin:</b>\n\n'
              '💡 <i>Örnek:</i> 500000',
        'ar': '💰 <b>أدخل مبلغ الدين:</b>\n\n'
              '💡 <i>مثال:</i> 500000'
    },
    'debt_due_date_prompt': {
        'uz': '📅 <b>Qaytarish sanasini kiriting:</b>\n\n'
              '💡 <i>Format:</i> kun.oy.yil\n'
              '📝 <i>Misol:</i> 25.01.2026\n\n'
              'Yoki /skip bosing (sana kerak emas)',
        'ru': '📅 <b>Введите дату возврата:</b>\n\n'
              '💡 <i>Формат:</i> день.месяц.год\n'
              '📝 <i>Например:</i> 25.01.2026\n\n'
              'Или нажмите /skip (дата не обязательна)',
        'en': '📅 <b>Enter due date:</b>\n\n'
              '💡 <i>Format:</i> day.month.year\n'
              '📝 <i>Example:</i> 25.01.2026\n\n'
              'Or press /skip (date optional)',
        'tr': '📅 <b>İade tarihini girin:</b>\n\n'
              '💡 <i>Format:</i> gün.ay.yıl\n'
              '📝 <i>Örnek:</i> 25.01.2026\n\n'
              'Veya /skip basın (tarih isteğe bağlı)',
        'ar': '📅 <b>أدخل تاريخ الاستحقاق:</b>\n\n'
              '💡 <i>التنسيق:</i> يوم.شهر.سنة\n'
              '📝 <i>مثال:</i> 25.01.2026\n\n'
              'أو اضغط /skip (التاريخ اختياري)'
    },
    'debt_reminder_prompt': {
        'uz': '⏰ <b>Eslatma kunlarini tanlang:</b>\n\n'
              'Necha kun oldin eslatish kerak?',
        'ru': '⏰ <b>Выберите дни напоминания:</b>\n\n'
              'За сколько дней напомнить?',
        'en': '⏰ <b>Select reminder days:</b>\n\n'
              'How many days before to remind?',
        'tr': '⏰ <b>Hatırlatma günlerini seçin:</b>\n\n'
              'Kaç gün önce hatırlatılsın?',
        'ar': '⏰ <b>اختر أيام التذكير:</b>\n\n'
              'كم يوم قبل التذكير؟'
    },
    'debt_description_prompt': {
        'uz': '📝 <b>Izoh qo\'shing</b> (ixtiyoriy)\n\n'
              '💡 <i>Masalan:</i>\n'
              '• "Biznes uchun qarz"\n'
              '• "Do\'kon ochish uchun"\n\n'
              '⏭️ /skip bosing o\'tkazib yuborish uchun',
        'ru': '📝 <b>Добавьте описание</b> (необязательно)\n\n'
              '💡 <i>Например:</i>\n'
              '• "Долг для бизнеса"\n'
              '• "Для открытия магазина"\n\n'
              '⏭️ Нажмите /skip чтобы пропустить',
        'en': '📝 <b>Add description</b> (optional)\n\n'
              '💡 <i>Examples:</i>\n'
              '• "Loan for business"\n'
              '• "For opening shop"\n\n'
              '⏭️ Press /skip to skip',
        'tr': '📝 <b>Açıklama ekleyin</b> (isteğe bağlı)\n\n'
              '💡 <i>Örnekler:</i>\n'
              '• "İş için borç"\n'
              '• "Dükkan açmak için"\n\n'
              '⏭️ Atlamak için /skip basın',
        'ar': '📝 <b>أضف وصفاً</b> (اختياري)\n\n'
              '💡 <i>أمثلة:</i>\n'
              '• "قرض للعمل"\n'
              '• "لفتح متجر"\n\n'
              '⏭️ اضغط /skip للتخطي'
    },
    'debt_given_added': {
        'uz': '✅ <b>Qarz muvaffaqiyatli saqlandi!</b>\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n'
              '📤 <b>Siz berdingiz</b>\n'
              '👤 <b>Kimga:</b> {person}\n'
              '💵 <b>Summa:</b> {amount}\n'
              '📅 <b>Muddat:</b> {due_date}\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '💡 "Bergan qarzlarim"da ko\'rishingiz mumkin',
        'ru': '✅ <b>Долг успешно сохранён!</b>\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n'
              '📤 <b>Вы дали</b>\n'
              '👤 <b>Кому:</b> {person}\n'
              '💵 <b>Сумма:</b> {amount}\n'
              '📅 <b>Срок:</b> {due_date}\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '💡 Можете посмотреть в "Выданные долги"',
        'en': '✅ <b>Debt saved successfully!</b>\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n'
              '📤 <b>You gave</b>\n'
              '👤 <b>To:</b> {person}\n'
              '💵 <b>Amount:</b> {amount}\n'
              '📅 <b>Due:</b> {due_date}\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '💡 Check "Given debts" section',
        'tr': '✅ <b>Borç başarıyla kaydedildi!</b>\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n'
              '📤 <b>Verdiniz</b>\n'
              '👤 <b>Kime:</b> {person}\n'
              '💵 <b>Tutar:</b> {amount}\n'
              '📅 <b>Vade:</b> {due_date}\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '💡 "Verilen borçlar" bölümünde görebilirsiniz',
        'ar': '✅ <b>تم حفظ الدين بنجاح!</b>\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n'
              '📤 <b>أقرضت</b>\n'
              '👤 <b>إلى:</b> {person}\n'
              '💵 <b>المبلغ:</b> {amount}\n'
              '📅 <b>الموعد:</b> {due_date}\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '💡 يمكنك العرض في "الديون المقدمة"'
    },
    'debt_taken_added': {
        'uz': '✅ <b>Qarz muvaffaqiyatli saqlandi!</b>\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n'
              '📥 <b>Siz oldingiz</b>\n'
              '👤 <b>Kimdan:</b> {person}\n'
              '💵 <b>Summa:</b> {amount}\n'
              '📅 <b>Muddat:</b> {due_date}\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '💡 "Olgan qarzlarim"da ko\'rishingiz mumkin',
        'ru': '✅ <b>Долг успешно сохранён!</b>\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n'
              '📥 <b>Вы взяли</b>\n'
              '👤 <b>У кого:</b> {person}\n'
              '💵 <b>Сумма:</b> {amount}\n'
              '📅 <b>Срок:</b> {due_date}\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '💡 Можете посмотреть в "Взятые долги"',
        'en': '✅ <b>Debt saved successfully!</b>\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n'
              '📥 <b>You took</b>\n'
              '👤 <b>From:</b> {person}\n'
              '💵 <b>Amount:</b> {amount}\n'
              '📅 <b>Due:</b> {due_date}\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '💡 Check "Taken debts" section',
        'tr': '✅ <b>Borç başarıyla kaydedildi!</b>\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n'
              '📥 <b>Aldınız</b>\n'
              '👤 <b>Kimden:</b> {person}\n'
              '💵 <b>Tutar:</b> {amount}\n'
              '📅 <b>Vade:</b> {due_date}\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '💡 "Alınan borçlar" bölümünde görebilirsiniz',
        'ar': '✅ <b>تم حفظ الدين بنجاح!</b>\n\n'
              '━━━━━━━━━━━━━━━━━━━━\n'
              '📥 <b>استلفت</b>\n'
              '👤 <b>من:</b> {person}\n'
              '💵 <b>المبلغ:</b> {amount}\n'
              '📅 <b>الموعد:</b> {due_date}\n'
              '━━━━━━━━━━━━━━━━━━━━\n\n'
              '💡 يمكنك العرض في "الديون المستلمة"'
    },
    'debt_payment_confirm': {
        'uz': '💰 <b>Qarzni qaytardimi?</b>\n\n'
              '👤 {person}\n'
              '💵 {amount}\n'
              '📅 Muddat: {due_date}',
        'ru': '💰 <b>Долг возвращён?</b>\n\n'
              '👤 {person}\n'
              '💵 {amount}\n'
              '📅 Срок: {due_date}',
        'en': '💰 <b>Debt returned?</b>\n\n'
              '👤 {person}\n'
              '💵 {amount}\n'
              '📅 Due: {due_date}',
        'tr': '💰 <b>Borç iade edildi mi?</b>\n\n'
              '👤 {person}\n'
              '💵 {amount}\n'
              '📅 Vade: {due_date}',
        'ar': '💰 <b>تم إرجاع الدين؟</b>\n\n'
              '👤 {person}\n'
              '💵 {amount}\n'
              '📅 الموعد: {due_date}'
    },
    'debt_marked_paid': {
        'uz': '✅ Qarz to\'langan deb belgilandi!',
        'ru': '✅ Долг отмечен как оплаченный!',
        'en': '✅ Debt marked as paid!',
        'tr': '✅ Borç ödenmiş olarak işaretlendi!',
        'ar': '✅ تم وضع علامة على الدين كمدفوع!'
    },
    'debt_reminder': {
        'uz': '⚠️ <b>ESLATMA: Qarz muddati yaqinlashmoqda!</b>\n\n'
              '👤 <b>Shaxs:</b> {person}\n'
              '💰 <b>Summa:</b> {amount}\n'
              '📅 <b>Muddat:</b> {due_date}\n'
              '⏰ <b>Qoldi:</b> {days_left} kun\n\n'
              '{debt_type}',
        'ru': '⚠️ <b>НАПОМИНАНИЕ: Срок долга приближается!</b>\n\n'
              '👤 <b>Человек:</b> {person}\n'
              '💰 <b>Сумма:</b> {amount}\n'
              '📅 <b>Срок:</b> {due_date}\n'
              '⏰ <b>Осталось:</b> {days_left} дн.\n\n'
              '{debt_type}',
        'en': '⚠️ <b>REMINDER: Debt due date approaching!</b>\n\n'
              '👤 <b>Person:</b> {person}\n'
              '💰 <b>Amount:</b> {amount}\n'
              '📅 <b>Due:</b> {due_date}\n'
              '⏰ <b>Left:</b> {days_left} days\n\n'
              '{debt_type}',
        'tr': '⚠️ <b>HATIRLATMA: Borç vade tarihi yaklaşıyor!</b>\n\n'
              '👤 <b>Kişi:</b> {person}\n'
              '💰 <b>Tutar:</b> {amount}\n'
              '📅 <b>Vade:</b> {due_date}\n'
              '⏰ <b>Kaldı:</b> {days_left} gün\n\n'
              '{debt_type}',
        'ar': '⚠️ <b>تذكير: اقتراب موعد استحقاق الدين!</b>\n\n'
              '👤 <b>الشخص:</b> {person}\n'
              '💰 <b>المبلغ:</b> {amount}\n'
              '📅 <b>الموعد:</b> {due_date}\n'
              '⏰ <b>المتبقي:</b> {days_left} يوم\n\n'
              '{debt_type}'
    },
    'no_debts_found': {
        'uz': '📭 Qarzlar topilmadi',
        'ru': '📭 Долги не найдены',
        'en': '📭 No debts found',
        'tr': '📭 Borç bulunamadı',
        'ar': '📭 لم يتم العثور على ديون'
    },
    
    # Hisobot matnlari
    'report_generating': {
        'uz': '⏳ <b>Hisobot tayyorlanmoqda...</b>\n\n'
              '🔄 Iltimos, biroz kuting.\n'
              '📊 Ma\'lumotlar tahlil qilinmoqda...',
        'ru': '⏳ <b>Подготовка отчёта...</b>\n\n'
              '🔄 Пожалуйста, подождите.\n'
              '📊 Анализируем данные...',
        'en': '⏳ <b>Generating report...</b>\n\n'
              '🔄 Please wait.\n'
              '📊 Analyzing data...',
        'tr': '⏳ <b>Rapor hazırlanıyor...</b>\n\n'
              '🔄 Lütfen bekleyin.\n'
              '📊 Veriler analiz ediliyor...',
        'ar': '⏳ <b>جاري إنشاء التقرير...</b>\n\n'
              '🔄 الرجاء الانتظار.\n'
              '📊 جاري تحليل البيانات...'
    },
    'report_ready': {
        'uz': '✅ <b>Hisobot tayyor!</b>\n\n'
              '📥 Quyida hisobotingiz:',
        'ru': '✅ <b>Отчёт готов!</b>\n\n'
              '📥 Ваш отчёт ниже:',
        'en': '✅ <b>Report ready!</b>\n\n'
              '📥 Your report is below:',
        'tr': '✅ <b>Rapor hazır!</b>\n\n'
              '📥 Raporunuz aşağıda:',
        'ar': '✅ <b>التقرير جاهز!</b>\n\n'
              '📥 تقريرك أدناه:'
    },
    'no_data_for_report': {
        'uz': '📭 <b>Ma\'lumot topilmadi</b>\n\n'
              'Bu davr uchun xarajat yoki daromad yo\'q.\n\n'
              '💡 <i>Birinchi xarajat/daromad qo\'shing:</i>\n'
              '• 💸 "Xarajat qo\'shish" tugmasini bosing\n'
              '• 💰 Yoki "Daromad qo\'shish" ni tanlang',
        'ru': '📭 <b>Данные не найдены</b>\n\n'
              'За этот период нет расходов или доходов.\n\n'
              '💡 <i>Добавьте первую запись:</i>\n'
              '• 💸 Нажмите "Добавить расход"\n'
              '• 💰 Или выберите "Добавить доход"',
        'en': '📭 <b>No Data Found</b>\n\n'
              'No expenses or income for this period.\n\n'
              '💡 <i>Add your first entry:</i>\n'
              '• 💸 Press "Add Expense"\n'
              '• 💰 Or select "Add Income"',
        'tr': '📭 <b>Veri Bulunamadı</b>\n\n'
              'Bu dönem için gider veya gelir yok.\n\n'
              '💡 <i>İlk kaydınızı ekleyin:</i>\n'
              '• 💸 "Gider Ekle"ye basın\n'
              '• 💰 Veya "Gelir Ekle"yi seçin',
        'ar': '📭 <b>لم يتم العثور على بيانات</b>\n\n'
              'لا توجد مصروفات أو دخل لهذه الفترة.\n\n'
              '💡 <i>أضف أول إدخال:</i>\n'
              '• 💸 اضغط "إضافة مصروف"\n'
              '• 💰 أو اختر "إضافة دخل"'
    },
    
    # Xatolar
    'error_occurred': {
        'uz': '❌ <b>Xatolik yuz berdi</b>\n\n'
              'Nimadir noto\'g\'ri ketdi.\n\n'
              '🔄 Qaytadan urinib ko\'ring yoki\n'
              '🏠 /start buyrug\'ini yuboring',
        'ru': '❌ <b>Произошла ошибка</b>\n\n'
              'Что-то пошло не так.\n\n'
              '🔄 Попробуйте снова или\n'
              '🏠 Отправьте команду /start',
        'en': '❌ <b>An Error Occurred</b>\n\n'
              'Something went wrong.\n\n'
              '🔄 Please try again or\n'
              '🏠 Send /start command',
        'tr': '❌ <b>Bir Hata Oluştu</b>\n\n'
              'Bir şeyler yanlış gitti.\n\n'
              '🔄 Tekrar deneyin veya\n'
              '🏠 /start komutunu gönderin',
        'ar': '❌ <b>حدث خطأ</b>\n\n'
              'حدث خطأ ما.\n\n'
              '🔄 حاول مرة أخرى أو\n'
              '🏠 أرسل أمر /start'
    },
    'process_cancelled': {
        'uz': '🚫 <b>Jarayon bekor qilindi</b>\n\n'
              '🏠 Asosiy menyuga qaytish uchun /start bosing',
        'ru': '🚫 <b>Процесс отменён</b>\n\n'
              '🏠 Нажмите /start для возврата в меню',
        'en': '🚫 <b>Process cancelled</b>\n\n'
              '🏠 Press /start to return to menu',
        'tr': '🚫 <b>İşlem iptal edildi</b>\n\n'
              '🏠 Menüye dönmek için /start basın',
        'ar': '🚫 <b>تم إلغاء العملية</b>\n\n'
              '🏠 اضغط /start للعودة إلى القائمة'
    },
}


# =====================================================
# DAROMAD TURLARI
# =====================================================
INCOME_TYPES = {
    'salary': {
        'uz': '💼 Oylik maosh',
        'ru': '💼 Зарплата',
        'en': '💼 Salary',
        'tr': '💼 Maaş',
        'ar': '💼 راتب'
    },
    'bonus': {
        'uz': '🎁 Bonus/Mukofot',
        'ru': '🎁 Бонус/Премия',
        'en': '🎁 Bonus/Reward',
        'tr': '🎁 Bonus/Prim',
        'ar': '🎁 مكافأة'
    },
    'freelance': {
        'uz': '💻 Frilanser daromadi',
        'ru': '💻 Фриланс доход',
        'en': '💻 Freelance income',
        'tr': '💻 Serbest meslek geliri',
        'ar': '💻 دخل العمل الحر'
    },
    'investment': {
        'uz': '📈 Investitsiya foydasi',
        'ru': '📈 Инвестиционный доход',
        'en': '📈 Investment returns',
        'tr': '📈 Yatırım geliri',
        'ar': '📈 عوائد الاستثمار'
    },
    'other': {
        'uz': '📦 Boshqa daromad',
        'ru': '📦 Прочий доход',
        'en': '📦 Other income',
        'tr': '📦 Diğer gelir',
        'ar': '📦 دخل آخر'
    }
}


# =====================================================
# OY NOMLARI
# =====================================================
MONTH_NAMES = {
    'uz': [
        'Yanvar', 'Fevral', 'Mart', 'Aprel', 'May', 'Iyun',
        'Iyul', 'Avgust', 'Sentabr', 'Oktabr', 'Noyabr', 'Dekabr'
    ],
    'ru': [
        'Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
        'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь'
    ],
    'en': [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ],
    'tr': [
        'Ocak', 'Şubat', 'Mart', 'Nisan', 'Mayıs', 'Haziran',
        'Temmuz', 'Ağustos', 'Eylül', 'Ekim', 'Kasım', 'Aralık'
    ],
    'ar': [
        'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
        'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
    ]
}


# =====================================================
# HELPER FUNCTIONS
# =====================================================
def get_text(key: str, language: str = 'uz', **kwargs) -> str:
    """
    Matnni tarjima qilish
    
    Args:
        key: Tarjima kaliti
        language: Til kodi
        **kwargs: Format parametrlari
        
    Returns:
        str: Tarjima qilingan matn
    """
    translations = TRANSLATIONS.get(key, {})
    text = translations.get(language, translations.get('uz', key))
    
    # Format parametrlarini qo'llash
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass  # Agar format parametrlari to'g'ri kelmasa, ignore qilish
    
    return text


def get_category_name(category_key: str, language: str = 'uz') -> str:
    """
    Kategoriya nomini olish
    
    Args:
        category_key: Kategoriya kaliti
        language: Til kodi
        
    Returns:
        str: Kategoriya nomi
    """
    category_names = Categories.NAMES.get(category_key, {})
    return category_names.get(language, category_key)


def get_income_type_name(income_type: str, language: str = 'uz') -> str:
    """
    Daromad turi nomini olish
    
    Args:
        income_type: Daromad turi kaliti
        language: Til kodi
        
    Returns:
        str: Daromad turi nomi
    """
    type_names = INCOME_TYPES.get(income_type, {})
    return type_names.get(language, income_type)


def format_date(
    date_obj: Optional[datetime | date],
    language: str = 'uz',
    format_type: str = 'short'
) -> str:
    """
    Sanani formatlash
    
    Args:
        date_obj: Sana obyekti
        language: Til kodi
        format_type: 'short' (DD.MM.YYYY) yoki 'long' (DD Month YYYY)
        
    Returns:
        str: Formatlangan sana
    """
    if not date_obj:
        return '-'
    
    if isinstance(date_obj, datetime):
        date_obj = date_obj.date()
    
    if format_type == 'short':
        return date_obj.strftime('%d.%m.%Y')
    
    elif format_type == 'long':
        day = date_obj.day
        month = MONTH_NAMES[language][date_obj.month - 1]
        year = date_obj.year
        return f"{day} {month} {year}"
    
    else:
        return date_obj.strftime('%d.%m.%Y')


def format_currency(
    amount: Decimal | float | int,
    language: str = 'uz',
    with_symbol: bool = True
) -> str:
    """
    Valyutani formatlash
    
    Args:
        amount: Summa
        language: Til kodi
        with_symbol: Valyuta belgisi bilan
        
    Returns:
        str: Formatlangan summa
    """
    if isinstance(amount, (float, int)):
        amount = Decimal(str(amount))
    
    # Raqamlarni formatlash (space bilan ajratish)
    formatted = f"{amount:,.0f}".replace(',', ' ')
    
    # Valyuta belgisi
    if with_symbol:
        currency_symbols = {
            'uz': 'so\'m',
            'ru': 'сум',
            'en': 'UZS',
            'tr': 'som',
            'ar': 'سوم'
        }
        symbol = currency_symbols.get(language, 'so\'m')
        return f"{formatted} {symbol}"
    
    return formatted


def get_month_name(month: int, language: str = 'uz') -> str:
    """
    Oy nomini olish
    
    Args:
        month: Oy raqami (1-12)
        language: Til kodi
        
    Returns:
        str: Oy nomi
    """
    if 1 <= month <= 12:
        return MONTH_NAMES[language][month - 1]
    return str(month)


def pluralize(
    count: int,
    singular: str,
    plural: str,
    language: str = 'uz'
) -> str:
    """
    Ko'plik shaklini qaytarish (til qoidalariga mos)
    
    Args:
        count: Son
        singular: Birlik shakli
        plural: Ko'plik shakli
        language: Til kodi
        
    Returns:
        str: To'g'ri shakl
    """
    # O'zbek, Turk va Arab tillarda ko'plik qoidalari oddiy
    if language in ['uz', 'tr', 'ar']:
        return plural if count != 1 else singular
    
    # Rus tili uchun murakkab qoidalar
    elif language == 'ru':
        if count % 10 == 1 and count % 100 != 11:
            return singular
        elif 2 <= count % 10 <= 4 and (count % 100 < 10 or count % 100 >= 20):
            return plural
        else:
            return plural
    
    # Ingliz tili
    elif language == 'en':
        return plural if count != 1 else singular
    
    return plural
