"""
SmartWallet AI Bot - Global Configuration
=========================================
Bu fayl loyihaning barcha konfiguratsiyalarini boshqaradi.
Environment variablelarni o'qiydi va global sozlamalarni belgilaydi.
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import time
import pytz
from dotenv import load_dotenv

# =====================================================
# ENVIRONMENT VARIABLES YUKLASH
# =====================================================
# .env faylini yuklash
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)


# =====================================================
# BASE PATHS
# =====================================================
class Paths:
    """Loyiha yo'llari"""
    BASE_DIR = Path(__file__).parent.resolve()
    STATIC_DIR = BASE_DIR / os.getenv('STATIC_DIR', 'static')
    TEMPLATES_DIR = BASE_DIR / os.getenv('TEMPLATES_DIR', 'templates')
    REPORTS_DIR = BASE_DIR / os.getenv('REPORTS_DIR', 'reports_output')
    LOGS_DIR = BASE_DIR / os.getenv('LOGS_DIR', 'logs')
    BACKUP_DIR = Path(os.getenv('BACKUP_DIR', '/tmp/smartwallet_backups'))
    
    @classmethod
    def create_directories(cls):
        """Kerakli papkalarni yaratish"""
        for directory in [cls.STATIC_DIR, cls.TEMPLATES_DIR, 
                         cls.REPORTS_DIR, cls.LOGS_DIR, cls.BACKUP_DIR]:
            directory.mkdir(parents=True, exist_ok=True)


# =====================================================
# TELEGRAM BOT CONFIGURATION
# =====================================================
class BotConfig:
    """Telegram bot sozlamalari"""
    TOKEN: str = os.getenv('BOT_TOKEN', '')
    
    if not TOKEN:
        raise ValueError("BOT_TOKEN topilmadi! .env faylni tekshiring.")
    
    # Admin Telegram ID
    ADMIN_ID: Optional[int] = None
    if os.getenv('ADMIN_TELEGRAM_ID'):
        try:
            ADMIN_ID = int(os.getenv('ADMIN_TELEGRAM_ID'))
        except ValueError:
            pass
    
    # Webhook settings (production uchun)
    WEBHOOK_URL: Optional[str] = os.getenv('WEBHOOK_URL')
    WEBHOOK_PORT: int = int(os.getenv('WEBHOOK_PORT', '8443'))
    
    # Rate limiting
    RATE_LIMIT_PER_SECOND: int = int(os.getenv('RATE_LIMIT_PER_SECOND', '3'))
    SESSION_TIMEOUT_HOURS: int = int(os.getenv('SESSION_TIMEOUT_HOURS', '24'))


# =====================================================
# DATABASE CONFIGURATION
# =====================================================
class DatabaseConfig:
    """Database sozlamalari"""
    # DATABASE_URL .env dan o'qiladi
    # Default: SQLite (PostgreSQL o'rniga)
    DATABASE_URL: str = os.getenv('DATABASE_URL', 'sqlite:///./smartwallet.db')
    
    # Legacy PostgreSQL settings (agar kerak bo'lsa)
    HOST: str = os.getenv('DB_HOST', 'localhost')
    PORT: int = int(os.getenv('DB_PORT', '5432'))
    NAME: str = os.getenv('DB_NAME', 'smartwallet_db')
    USER: str = os.getenv('DB_USER', 'postgres')
    PASSWORD: str = os.getenv('DB_PASSWORD', '')
    
    # Connection pool settings
    POOL_SIZE: int = int(os.getenv('DB_POOL_SIZE', '10'))
    MAX_OVERFLOW: int = int(os.getenv('DB_MAX_OVERFLOW', '20'))
    
    @classmethod
    def get_url(cls, async_mode: bool = False) -> str:
        """
        Database URL qaytarish
        
        Agar DATABASE_URL environment variable bo'lsa, uni ishlatadi.
        Aks holda PostgreSQL URL yaratadi (legacy support).
        """
        # Agar DATABASE_URL .env da berilgan bo'lsa
        if os.getenv('DATABASE_URL'):
            return os.getenv('DATABASE_URL')
        
        # Aks holda PostgreSQL URL yaratish (legacy)
        driver = 'postgresql+asyncpg' if async_mode else 'postgresql+psycopg2'
        return f"{driver}://{cls.USER}:{cls.PASSWORD}@{cls.HOST}:{cls.PORT}/{cls.NAME}"
    
    # Async URL (agar kerak bo'lsa)
    @classmethod
    def get_async_url(cls) -> str:
        """Async database URL"""
        url = cls.get_url()
        # SQLite uchun aiosqlite
        if url.startswith('sqlite:'):
            return url.replace('sqlite:', 'sqlite+aiosqlite:')
        # PostgreSQL uchun asyncpg
        elif url.startswith('postgresql:'):
            return url.replace('postgresql:', 'postgresql+asyncpg:')
        return url


# =====================================================
# APPLICATION SETTINGS
# =====================================================
class AppConfig:
    """Asosiy dastur sozlamalari"""
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    TIMEZONE: pytz.timezone = pytz.timezone(os.getenv('TIMEZONE', 'Asia/Tashkent'))
    DEFAULT_LANGUAGE: str = os.getenv('DEFAULT_LANGUAGE', 'uz')
    
    # Supported languages
    SUPPORTED_LANGUAGES: List[str] = os.getenv(
        'SUPPORTED_LANGUAGES', 
        'uz,ru,en,tr,ar'
    ).split(',')
    
    # Cache settings
    CACHE_TTL: int = int(os.getenv('CACHE_TTL', '300'))


# =====================================================
# CATEGORIYALAR VA RANGLAR
# =====================================================
class Categories:
    """Xarajat kategoriyalari va ularning ranglari"""
    
    # Kategoriya ro'yxati (emoji bilan)
    LIST = [
        {'key': 'food', 'icon': '🍕', 'color': '#f59e0b'},
        {'key': 'home', 'icon': '🏠', 'color': '#3b82f6'},
        {'key': 'transport', 'icon': '🚕', 'color': '#8b5cf6'},
        {'key': 'restaurant', 'icon': '🍽️', 'color': '#f59e0b'},
        {'key': 'health', 'icon': '💊', 'color': '#ec4899'},
        {'key': 'education', 'icon': '🎓', 'color': '#14b8a6'},
        {'key': 'entertainment', 'icon': '🎮', 'color': '#f43f5e'},
        {'key': 'clothing', 'icon': '👕', 'color': '#a855f7'},
        {'key': 'communication', 'icon': '📱', 'color': '#06b6d4'},
        {'key': 'utilities', 'icon': '⚡', 'color': '#eab308'},
        {'key': 'other', 'icon': '➕', 'color': '#6b7280'},
    ]
    
    # Kategoriya nomlari (tarjima uchun key'lar)
    NAMES = {
        'food': {
            'uz': "Oziq-ovqat",
            'ru': "Продукты",
            'en': "Groceries",
            'tr': "Gıda",
            'ar': "البقالة"
        },
        'home': {
            'uz': "Uy-ro'zg'or",
            'ru': "Домашние товары",
            'en': "Household",
            'tr': "Ev eşyaları",
            'ar': "المنزلية"
        },
        'transport': {
            'uz': "Transport",
            'ru': "Транспорт",
            'en': "Transport",
            'tr': "Ulaşım",
            'ar': "النقل"
        },
        'restaurant': {
            'uz': "Ovqatlanish",
            'ru': "Общепит",
            'en': "Dining",
            'tr': "Yemek",
            'ar': "المطاعم"
        },
        'health': {
            'uz': "Sog'liqni saqlash",
            'ru': "Здоровье",
            'en': "Healthcare",
            'tr': "Sağlık",
            'ar': "الصحة"
        },
        'education': {
            'uz': "Ta'lim",
            'ru': "Образование",
            'en': "Education",
            'tr': "Eğitim",
            'ar': "التعليم"
        },
        'entertainment': {
            'uz': "Ko'ngilochar",
            'ru': "Развлечения",
            'en': "Entertainment",
            'tr': "Eğlence",
            'ar': "الترفيه"
        },
        'clothing': {
            'uz': "Kiyim-kechak",
            'ru': "Одежда",
            'en': "Clothing",
            'tr': "Giyim",
            'ar': "الملابس"
        },
        'communication': {
            'uz': "Aloqa",
            'ru': "Связь",
            'en': "Communication",
            'tr': "İletişim",
            'ar': "الاتصالات"
        },
        'utilities': {
            'uz': "Kommunal to'lovlar",
            'ru': "Коммунальные",
            'en': "Utilities",
            'tr': "Faturalar",
            'ar': "الفواتير"
        },
        'other': {
            'uz': "Boshqa",
            'ru': "Другое",
            'en': "Other",
            'tr': "Diğer",
            'ar': "أخرى"
        }
    }
    
    # Kalit so'zlar (AI parser uchun)
    KEYWORDS = {
        'food': ['oziq', 'ovqat', 'non', 'go\'sht', 'sabzavot', 'meva', 
                 'supermarket', 'korzinka', 'makro', 'havas', 'продукты', 
                 'еда', 'food', 'grocery', 'gıda'],
        'home': ['uy', 'ro\'zg\'or', 'mebel', 'jihozlar', 'дом', 'home', 
                 'furniture', 'ev'],
        'transport': ['taxi', 'taksi', 'yandex', 'uber', 'transport', 
                      'avtomobil', 'benzin', 'транспорт', 'ulaşım'],
        'restaurant': ['restoran', 'kafe', 'evos', 'makdonalds', 'ресторан', 
                       'restaurant', 'cafe', 'restoran'],
        'health': ['dorixona', 'shifoxona', 'apteka', 'dori', 'health', 
                   'hospital', 'sağlık', 'здоровье'],
        'education': ['ta\'lim', 'maktab', 'universitet', 'kurs', 'образование', 
                      'education', 'eğitim'],
        'entertainment': ['kino', 'o\'yin', 'razvlecheniya', 'entertainment', 
                          'eğlence'],
        'clothing': ['kiyim', 'oyoq-kiyim', 'одежда', 'clothing', 'giyim'],
        'communication': ['internet', 'telefon', 'aloqa', 'связь', 'communication'],
        'utilities': ['kommunal', 'elektr', 'gaz', 'suv', 'коммунальные', 'utilities']
    }
    
    @classmethod
    def get_color(cls, category_key: str) -> str:
        """Kategoriya rangini olish"""
        for cat in cls.LIST:
            if cat['key'] == category_key:
                return cat['color']
        return '#6b7280'  # Default: kulrang
    
    @classmethod
    def get_icon(cls, category_key: str) -> str:
        """Kategoriya emoji'sini olish"""
        for cat in cls.LIST:
            if cat['key'] == category_key:
                return cat['icon']
        return '➕'  # Default: plus


# =====================================================
# SCHEDULER CONFIGURATION
# =====================================================
class SchedulerConfig:
    """Scheduler sozlamalari"""
    # Eslatmalarni tekshirish intervali (soniyalarda)
    REMINDER_CHECK_INTERVAL: int = int(os.getenv('REMINDER_CHECK_INTERVAL', '3600'))
    
    # Default eslatma kunlari
    DEFAULT_REMINDER_DAYS: int = int(os.getenv('DEFAULT_REMINDER_DAYS', '3'))
    
    # Kunlik xulosani yuborish vaqti
    DAILY_SUMMARY_TIME_STR: str = os.getenv('DAILY_SUMMARY_TIME', '20:00')
    DAILY_SUMMARY_TIME: time = time(
        hour=int(DAILY_SUMMARY_TIME_STR.split(':')[0]),
        minute=int(DAILY_SUMMARY_TIME_STR.split(':')[1])
    )
    
    # Haftalik xulosani yuborish kuni (0=Dushanba, 6=Yakshanba)
    WEEKLY_SUMMARY_DAY: int = int(os.getenv('WEEKLY_SUMMARY_DAY', '6'))


# =====================================================
# AI CONFIGURATION
# =====================================================
class AIConfig:
    """AI va NLP sozlamalari"""
    # AI parser turi
    PARSER_TYPE: str = os.getenv('AI_PARSER_TYPE', 'simple')
    
    # OpenAI API (kelajak uchun)
    OPENAI_API_KEY: Optional[str] = os.getenv('OPENAI_API_KEY')
    
    # spaCy models
    SPACY_MODELS = {
        'uz': None,  # O'zbek tili uchun model yo'q
        'ru': 'ru_core_news_sm',
        'en': 'en_core_web_sm',
    }


# =====================================================
# REPORT CONFIGURATION
# =====================================================
class ReportConfig:
    """Hisobot sozlamalari"""
    # Maksimal tranzaksiyalar soni
    MAX_TRANSACTIONS: int = int(os.getenv('MAX_TRANSACTIONS_IN_REPORT', '100'))
    
    # PDF sozlamalari
    PDF_PAGE_SIZE: str = os.getenv('PDF_PAGE_SIZE', 'A4')
    
    # Chart o'lchamlari
    CHART_WIDTH: int = int(os.getenv('CHART_WIDTH', '800'))
    CHART_HEIGHT: int = int(os.getenv('CHART_HEIGHT', '400'))
    
    # DPI for charts
    CHART_DPI: int = 100
    
    # Export formatlar
    ENABLE_PDF: bool = os.getenv('ENABLE_EXPORT_PDF', 'True').lower() == 'true'
    ENABLE_HTML: bool = os.getenv('ENABLE_EXPORT_HTML', 'True').lower() == 'true'
    ENABLE_EXCEL: bool = os.getenv('ENABLE_EXPORT_EXCEL', 'True').lower() == 'true'


# =====================================================
# FEATURE FLAGS
# =====================================================
class Features:
    """Funksiyalarni yoqish/o'chirish"""
    CHARTS: bool = os.getenv('ENABLE_CHARTS', 'True').lower() == 'true'
    AI_PARSER: bool = os.getenv('ENABLE_AI_PARSER', 'True').lower() == 'true'
    REMINDERS: bool = os.getenv('ENABLE_REMINDERS', 'True').lower() == 'true'
    BACKUP: bool = os.getenv('ENABLE_BACKUP', 'True').lower() == 'true'


# =====================================================
# CURRENCY SETTINGS
# =====================================================
class Currency:
    """Valyuta sozlamalari"""
    DEFAULT: str = "so'm"
    SYMBOL: str = "so'm"
    CODE: str = "UZS"
    
    @staticmethod
    def format_amount(amount: float, with_symbol: bool = True) -> str:
        """Summani formatlash"""
        formatted = f"{amount:,.0f}".replace(',', ' ')
        if with_symbol:
            return f"{formatted} {Currency.SYMBOL}"
        return formatted


# =====================================================
# LOGGING CONFIGURATION
# =====================================================
class LogConfig:
    """Logging sozlamalari"""
    
    @staticmethod
    def setup_logging():
        """Logging'ni sozlash"""
        # Log papkasini yaratish
        Paths.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        
        # Log fayli
        log_file = Paths.LOGS_DIR / 'bot.log'
        
        # Log level
        level = getattr(logging, AppConfig.LOG_LEVEL.upper(), logging.INFO)
        
        # Format
        log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        
        # Handlers
        handlers = [
            logging.StreamHandler(),  # Console
            logging.FileHandler(log_file, encoding='utf-8')  # File
        ]
        
        # Basic config
        logging.basicConfig(
            level=level,
            format=log_format,
            datefmt=date_format,
            handlers=handlers
        )
        
        # Disable some verbose loggers
        logging.getLogger('telegram').setLevel(logging.WARNING)
        logging.getLogger('httpx').setLevel(logging.WARNING)
        logging.getLogger('apscheduler').setLevel(logging.WARNING)


# =====================================================
# VALYUTA SETTINGS
# =====================================================
class Messages:
    """Umumiy xabarlar (template'lar)"""
    
    # Xush kelibsiz xabari (5 tilda)
    WELCOME = {
        'uz': """🎉 <b>Assalomu alaykum!</b>

💼 <b>SmartWallet AI</b> — shaxsiy moliyaviy yordamchingiz!

━━━━━━━━━━━━━━━━━━━━

🤖 <b>Men nimalar qila olaman:</b>

💳 Xarajatlarni avtomatik kategoriyalash
💰 Daromadlarni kuzatib borish
📊 Batafsil PDF/HTML hisobotlar
🔔 Eslatmalar va bildirishnomalar

━━━━━━━━━━━━━━━━━━━━

🌍 <b>Davom etish uchun tilni tanlang:</b>""",
        
        'ru': """🎉 <b>Здравствуйте!</b>

💼 <b>SmartWallet AI</b> — ваш персональный финансовый помощник!

━━━━━━━━━━━━━━━━━━━━

🤖 <b>Мои возможности:</b>

💳 Автоматическая категоризация расходов
💰 Отслеживание доходов
📊 Подробные отчёты PDF/HTML
🔔 Напоминания и уведомления

━━━━━━━━━━━━━━━━━━━━

🌍 <b>Выберите язык для продолжения:</b>""",
        
        'en': """🎉 <b>Welcome!</b>

💼 <b>SmartWallet AI</b> — your personal finance assistant!

━━━━━━━━━━━━━━━━━━━━

🤖 <b>What I can do:</b>

💳 Automatic expense categorization
💰 Income tracking
📊 Detailed PDF/HTML reports
🔔 Reminders & notifications

━━━━━━━━━━━━━━━━━━━━

🌍 <b>Choose your language to continue:</b>""",
        
        'tr': """🎉 <b>Merhaba!</b>

💼 <b>SmartWallet AI</b> — kişisel finans asistanınız!

━━━━━━━━━━━━━━━━━━━━

🤖 <b>Neler yapabilirim:</b>

💳 Otomatik gider kategorileme
💰 Gelir takibi
📊 Detaylı PDF/HTML raporlar
🔔 Hatırlatıcılar ve bildirimler

━━━━━━━━━━━━━━━━━━━━

🌍 <b>Devam etmek için dil seçin:</b>""",
        
        'ar': """🎉 <b>مرحباً!</b>

💼 <b>SmartWallet AI</b> — مساعدك المالي الشخصي!

━━━━━━━━━━━━━━━━━━━━

🤖 <b>ما يمكنني فعله:</b>

💳 تصنيف النفقات تلقائياً
💰 تتبع الدخل
📊 تقارير PDF/HTML مفصلة
🔔 تذكيرات وإشعارات

━━━━━━━━━━━━━━━━━━━━

🌍 <b>اختر لغتك للمتابعة:</b>"""
    }


# =====================================================
# VALIDATION RULES
# =====================================================
class Validation:
    """Validatsiya qoidalari"""
    # Minimum va maksimum summalar
    MIN_AMOUNT: float = 1.0
    MAX_AMOUNT: float = 1_000_000_000.0  # 1 milliard
    
    # Matn uzunliklari
    MAX_DESCRIPTION_LENGTH: int = 500
    MAX_PERSON_NAME_LENGTH: int = 100
    
    # Sana chegaralari
    MAX_FUTURE_DAYS: int = 365  # 1 yildan ortiq kelajakka sana kiritib bo'lmaydi


# =====================================================
# INITIALIZATION
# =====================================================
def initialize():
    """Konfiguratsiyani boshlang'ich sozlash"""
    # Papkalarni yaratish
    Paths.create_directories()
    
    # Logging'ni sozlash
    LogConfig.setup_logging()
    
    logger = logging.getLogger(__name__)
    logger.info("SmartWallet AI Bot konfiguratsiyasi yuklandi")
    logger.info(f"Debug rejimi: {AppConfig.DEBUG}")
    logger.info(f"Database: {DatabaseConfig.NAME}")
    logger.info(f"Timezone: {AppConfig.TIMEZONE}")


# Dastur ishga tushganda avtomatik ishga tushirish
if __name__ != '__main__':
    initialize()
