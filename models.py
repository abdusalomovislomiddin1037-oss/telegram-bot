"""
SmartWallet AI Bot - Database Models
====================================
SQLAlchemy model'lari - barcha database jadvallar

Tables:
    - users: Foydalanuvchi ma'lumotlari
    - categories: Xarajat kategoriyalari
    - expenses: Xarajatlar
    - incomes: Daromadlar
    - reminders: Eslatmalar

Author: SmartWallet AI Team
Version: 1.0.0
"""

from datetime import datetime, date
from typing import Optional, List
from decimal import Decimal

from sqlalchemy import (
    Column, Integer, BigInteger, String, Numeric, 
    Boolean, DateTime, Date, Text, ForeignKey,
    Index, CheckConstraint, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func

# Base class
Base = declarative_base()


# =====================================================
# USER MODEL
# =====================================================
class User(Base):
    """
    Foydalanuvchi modeli
    
    Attributes:
        id: Primary key
        telegram_id: Telegram user ID (unique)
        username: Telegram username
        first_name: Ism
        last_name: Familiya
        language: Tanlangan til (uz, ru, en, tr, ar)
        is_active: Faol holat
        created_at: Yaratilgan vaqt
        updated_at: Yangilangan vaqt
    """
    __tablename__ = 'users'
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Telegram ma'lumotlari
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    username: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Sozlamalar
    language: Mapped[str] = mapped_column(String(5), default='uz', nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )
    
    # Relationships
    expenses: Mapped[List["Expense"]] = relationship(
        "Expense", 
        back_populates="user",
        cascade="all, delete-orphan"
    )
    incomes: Mapped[List["Income"]] = relationship(
        "Income",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    debts: Mapped[List["Debt"]] = relationship(
        "Debt",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    reminders: Mapped[List["Reminder"]] = relationship(
        "Reminder",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
    # Indexes
    __table_args__ = (
        Index('idx_user_telegram_id', 'telegram_id'),
        Index('idx_user_created_at', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, telegram_id={self.telegram_id}, username={self.username})>"


# =====================================================
# CATEGORY MODEL
# =====================================================
class Category(Base):
    """
    Kategoriya modeli
    
    Attributes:
        id: Primary key
        key: Kategoriya kaliti (food, home, transport, ...)
        name_uz: O'zbek nomi
        name_ru: Rus nomi
        name_en: Ingliz nomi
        name_tr: Turk nomi
        name_ar: Arab nomi
        icon: Emoji icon
        color: Hex rang kodi
        is_active: Faol holat
    """
    __tablename__ = 'categories'
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Kategoriya ma'lumotlari
    key: Mapped[str] = mapped_column(String(50), unique=True, nullable=False, index=True)
    
    # Tarjimalar
    name_uz: Mapped[str] = mapped_column(String(100), nullable=False)
    name_ru: Mapped[str] = mapped_column(String(100), nullable=False)
    name_en: Mapped[str] = mapped_column(String(100), nullable=False)
    name_tr: Mapped[str] = mapped_column(String(100), nullable=False)
    name_ar: Mapped[str] = mapped_column(String(100), nullable=False)
    
    # Vizual ma'lumotlar
    icon: Mapped[str] = mapped_column(String(10), nullable=False)
    color: Mapped[str] = mapped_column(String(7), nullable=False)  # HEX color
    
    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    
    # Relationships
    expenses: Mapped[List["Expense"]] = relationship(
        "Expense",
        back_populates="category"
    )
    
    def __repr__(self) -> str:
        return f"<Category(id={self.id}, key={self.key}, icon={self.icon})>"
    
    def get_name(self, language: str = 'uz') -> str:
        """Tilga qarab nom qaytarish"""
        return getattr(self, f'name_{language}', self.name_uz)


# =====================================================
# EXPENSE MODEL
# =====================================================
class Expense(Base):
    """
    Xarajat modeli
    
    Attributes:
        id: Primary key
        user_id: Foydalanuvchi ID (FK)
        category_id: Kategoriya ID (FK)
        amount: Summa
        description: Tavsif
        expense_date: Xarajat sanasi
        created_at: Yaratilgan vaqt
        updated_at: Yangilangan vaqt
    """
    __tablename__ = 'expenses'
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    user_id: Mapped[int] = mapped_column(
        BigInteger, 
        ForeignKey('users.telegram_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    category_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey('categories.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    
    # Xarajat ma'lumotlari
    amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        index=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Sanalar
    expense_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="expenses")
    category: Mapped[Optional["Category"]] = relationship("Category", back_populates="expenses")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('amount > 0', name='check_expense_amount_positive'),
        Index('idx_expense_user_date', 'user_id', 'expense_date'),
        Index('idx_expense_category', 'category_id'),
        Index('idx_expense_created_at', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<Expense(id={self.id}, user_id={self.user_id}, amount={self.amount}, category_id={self.category_id})>"


# =====================================================
# INCOME MODEL
# =====================================================
class Income(Base):
    """
    Daromad modeli
    
    Attributes:
        id: Primary key
        user_id: Foydalanuvchi ID (FK)
        amount: Summa
        source: Manba (oylik, bonus, ...)
        income_type: Turi (salary, bonus, other)
        is_recurring: Takrorlanadigan (oylik)
        income_date: Daromad sanasi
        created_at: Yaratilgan vaqt
        updated_at: Yangilangan vaqt
    """
    __tablename__ = 'incomes'
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('users.telegram_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Daromad ma'lumotlari
    amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        index=True
    )
    source: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    income_type: Mapped[str] = mapped_column(
        String(50),
        default='other',
        nullable=False
    )  # salary, bonus, freelance, investment, other
    
    # Takrorlanish
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Sanalar
    income_date: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        nullable=False,
        index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="incomes")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('amount > 0', name='check_income_amount_positive'),
        Index('idx_income_user_date', 'user_id', 'income_date'),
        Index('idx_income_created_at', 'created_at'),
        Index('idx_income_type', 'income_type'),
    )
    
    def __repr__(self) -> str:
        return f"<Income(id={self.id}, user_id={self.user_id}, amount={self.amount}, source={self.source})>"


# =====================================================
# DEBT MODEL
# =====================================================
class Debt(Base):
    """
    Qarz modeli
    
    Attributes:
        id: Primary key
        user_id: Foydalanuvchi ID (FK)
        person_name: Shaxs ismi
        amount: Summa
        debt_type: Qarz turi (given=berdim, taken=oldim)
        due_date: Qaytarish sanasi
        description: Izoh
        status: Holat (active, partially_paid, paid, overdue)
        paid_amount: To'langan summa
        reminder_days: Eslatma kunlari oldin (1, 3, 7)
        created_at: Yaratilgan vaqt
        updated_at: Yangilangan vaqt
    """
    __tablename__ = 'debts'
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Key
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('users.telegram_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Qarz ma'lumotlari
    person_name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        nullable=False,
        index=True
    )
    debt_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        index=True
    )  # given (berdim), taken (oldim)
    
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status va to'lov
    status: Mapped[str] = mapped_column(
        String(20),
        default='active',
        nullable=False,
        index=True
    )  # active, partially_paid, paid, overdue
    
    paid_amount: Mapped[Decimal] = mapped_column(
        Numeric(15, 2),
        default=0,
        nullable=False
    )
    
    # Eslatma
    reminder_days: Mapped[Optional[int]] = mapped_column(
        Integer,
        nullable=True
    )  # 1, 3, 7 kun oldin eslatish
    
    # Sanalar
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="debts")
    
    # Constraints
    __table_args__ = (
        CheckConstraint('amount > 0', name='check_debt_amount_positive'),
        CheckConstraint('paid_amount >= 0', name='check_debt_paid_amount_positive'),
        CheckConstraint('paid_amount <= amount', name='check_debt_paid_not_exceeding'),
        CheckConstraint("debt_type IN ('given', 'taken')", name='check_debt_type'),
        CheckConstraint("status IN ('active', 'partially_paid', 'paid', 'overdue')", 
                       name='check_debt_status'),
        Index('idx_debt_user_type', 'user_id', 'debt_type'),
        Index('idx_debt_status', 'status'),
        Index('idx_debt_due_date', 'due_date'),
        Index('idx_debt_created_at', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<Debt(id={self.id}, user_id={self.user_id}, person={self.person_name}, amount={self.amount}, type={self.debt_type}, status={self.status})>"


# =====================================================
# REMINDER MODEL
# =====================================================
class Reminder(Base):
    """
    Eslatma modeli
    
    Attributes:
        id: Primary key
        user_id: Foydalanuvchi ID (FK)
        reminder_type: Eslatma turi (income, daily, weekly)
        reminder_date: Eslatma sanasi
        message: Eslatma matni
        is_sent: Yuborilganmi
        sent_at: Yuborilgan vaqt
        created_at: Yaratilgan vaqt
    """
    __tablename__ = 'reminders'
    
    # Primary Key
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Foreign Keys
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey('users.telegram_id', ondelete='CASCADE'),
        nullable=False,
        index=True
    )
    
    # Eslatma ma'lumotlari
    reminder_type: Mapped[str] = mapped_column(
        String(50),
        default='income',
        nullable=False,
        index=True
    )  # income, daily_summary, weekly_summary
    reminder_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        index=True
    )
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    # Status
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False, index=True)
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Timestamp
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="reminders")
    
    # Constraints
    __table_args__ = (
        CheckConstraint("reminder_type IN ('income', 'daily_summary', 'weekly_summary')", 
                       name='check_reminder_type'),
        Index('idx_reminder_user_date', 'user_id', 'reminder_date'),
        Index('idx_reminder_sent', 'is_sent', 'reminder_date'),
        Index('idx_reminder_type', 'reminder_type'),
    )
    
    def __repr__(self) -> str:
        return f"<Reminder(id={self.id}, user_id={self.user_id}, type={self.reminder_type}, is_sent={self.is_sent})>"


# =====================================================
# HELPER FUNCTIONS
# =====================================================
def init_categories(session) -> None:
    """
    Database'ga standart kategoriyalarni qo'shish
    Faqat birinchi marta ishga tushganda chaqiriladi
    
    Args:
        session: SQLAlchemy session
    """
    from config import Categories as CategoriesConfig
    
    # Kategoriyalar mavjudligini tekshirish
    existing = session.query(Category).count()
    if existing > 0:
        return  # Kategoriyalar allaqachon mavjud
    
    # Kategoriyalarni qo'shish
    for cat_data in CategoriesConfig.LIST:
        key = cat_data['key']
        names = CategoriesConfig.NAMES.get(key, {})
        
        category = Category(
            key=key,
            name_uz=names.get('uz', key),
            name_ru=names.get('ru', key),
            name_en=names.get('en', key),
            name_tr=names.get('tr', key),
            name_ar=names.get('ar', key),
            icon=cat_data['icon'],
            color=cat_data['color'],
            is_active=True
        )
        session.add(category)
    
    session.commit()
