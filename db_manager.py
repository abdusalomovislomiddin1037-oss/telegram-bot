"""
SmartWallet AI Bot - Database Manager
=====================================
Database bilan barcha operatsiyalarni boshqarish

Operations:
    - Connection management
    - CRUD operations (Create, Read, Update, Delete)
    - Statistics va analytics
    - Transaction management

Author: SmartWallet AI Team
Version: 1.0.0
"""

import logging
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, date, timedelta
from decimal import Decimal
from contextlib import asynccontextmanager

from sqlalchemy import create_engine, select, func, and_, or_, desc, asc, extract
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.exc import SQLAlchemyError

from config import DatabaseConfig
from .models import Base, User, Expense, Income, Debt, Reminder, Category, init_categories

# Logger
logger = logging.getLogger(__name__)


# =====================================================
# DATABASE MANAGER CLASS
# =====================================================
class DatabaseManager:
    """
    Database bilan ishlash uchun asosiy class
    Singleton pattern ishlatadi
    """
    
    _instance = None
    _engine = None
    _session_factory = None
    
    def __new__(cls):
        """Singleton pattern - faqat bitta instance"""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Database engine va session factory yaratish"""
        if self._engine is None:
            try:
                # Sync engine
                self._engine = create_engine(
                    DatabaseConfig.DATABASE_URL,
                    pool_size=DatabaseConfig.POOL_SIZE,
                    max_overflow=DatabaseConfig.MAX_OVERFLOW,
                    echo=False,  # SQL log'larni ko'rsatmaslik (production)
                    pool_pre_ping=True  # Connection'ni tekshirish
                )
                
                # Session factory
                self._session_factory = sessionmaker(
                    bind=self._engine,
                    expire_on_commit=False
                )
                
                logger.info("Database engine yaratildi")
            except Exception as e:
                logger.error(f"Database engine yaratishda xato: {e}")
                raise
    
    def get_session(self) -> Session:
        """
        Yangi session yaratish
        
        Returns:
            Session: SQLAlchemy session
        """
        return self._session_factory()
    
    @asynccontextmanager
    async def session_scope(self):
        """
        Context manager - avtomatik commit/rollback
        
        Usage:
            async with db_manager.session_scope() as session:
                session.add(user)
        """
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Session xatosi: {e}")
            raise
        finally:
            session.close()
    
    async def create_tables(self):
        """
        Barcha jadvallarni yaratish
        """
        try:
            Base.metadata.create_all(self._engine)
            logger.info("Database jadvallar yaratildi/tekshirildi")
            
            # Kategoriyalarni qo'shish
            session = self.get_session()
            try:
                init_categories(session)
                logger.info("Kategoriyalar yuklandi")
            except Exception as e:
                logger.error(f"Kategoriyalarni yuklashda xato: {e}")
            finally:
                session.close()
                
        except Exception as e:
            logger.error(f"Jadvallarni yaratishda xato: {e}")
            raise
    
    async def close(self):
        """Database connection'ni yopish"""
        if self._engine:
            self._engine.dispose()
            logger.info("Database connection yopildi")
    
    
    # =====================================================
    # USER OPERATIONS
    # =====================================================
    
    def get_or_create_user(
        self, 
        telegram_id: int, 
        username: Optional[str] = None,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        language: str = 'uz'
    ) -> User:
        """
        Foydalanuvchini olish yoki yangi yaratish
        
        Args:
            telegram_id: Telegram user ID
            username: Username
            first_name: Ism
            last_name: Familiya
            language: Til
            
        Returns:
            User: User object
        """
        session = self.get_session()
        try:
            # Mavjud foydalanuvchini qidirish
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            
            if user:
                # Ma'lumotlarni yangilash
                updated = False
                if username and user.username != username:
                    user.username = username
                    updated = True
                if first_name and user.first_name != first_name:
                    user.first_name = first_name
                    updated = True
                if last_name and user.last_name != last_name:
                    user.last_name = last_name
                    updated = True
                
                if updated:
                    session.commit()
                    logger.info(f"User {telegram_id} ma'lumotlari yangilandi")
            else:
                # Yangi foydalanuvchi yaratish
                user = User(
                    telegram_id=telegram_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    language=language,
                    is_active=True
                )
                session.add(user)
                session.commit()
                logger.info(f"Yangi foydalanuvchi yaratildi: {telegram_id}")
            
            return user
        except Exception as e:
            session.rollback()
            logger.error(f"get_or_create_user xatosi: {e}")
            raise
        finally:
            session.close()
    
    def update_user_language(self, telegram_id: int, language: str) -> bool:
        """
        Foydalanuvchi tilini yangilash
        
        Args:
            telegram_id: Telegram user ID
            language: Yangi til
            
        Returns:
            bool: Muvaffaqiyatli bajarildi
        """
        session = self.get_session()
        try:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            if user:
                user.language = language
                session.commit()
                logger.info(f"User {telegram_id} til yangilandi: {language}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"update_user_language xatosi: {e}")
            return False
        finally:
            session.close()
    
    def get_user_language(self, telegram_id: int) -> str:
        """
        Foydalanuvchi tilini olish
        
        Args:
            telegram_id: Telegram user ID
            
        Returns:
            str: Til kodi (uz, ru, en, tr, ar)
        """
        session = self.get_session()
        try:
            user = session.query(User).filter(User.telegram_id == telegram_id).first()
            return user.language if user else 'uz'
        finally:
            session.close()
    
    
    # =====================================================
    # CATEGORY OPERATIONS
    # =====================================================
    
    def get_all_categories(self, is_active: bool = True) -> List[Category]:
        """
        Barcha kategoriyalarni olish
        
        Args:
            is_active: Faqat faol kategoriyalar
            
        Returns:
            List[Category]: Kategoriyalar ro'yxati
        """
        session = self.get_session()
        try:
            query = session.query(Category)
            if is_active:
                query = query.filter(Category.is_active == True)
            return query.all()
        finally:
            session.close()
    
    def get_category_by_key(self, key: str) -> Optional[Category]:
        """
        Kategoriyani key bo'yicha olish
        
        Args:
            key: Kategoriya key
            
        Returns:
            Optional[Category]: Kategoriya yoki None
        """
        session = self.get_session()
        try:
            return session.query(Category).filter(Category.key == key).first()
        finally:
            session.close()
    
    
    # =====================================================
    # EXPENSE OPERATIONS
    # =====================================================
    
    def add_expense(
        self,
        telegram_id: int,
        amount: Decimal,
        category_key: str,
        description: Optional[str] = None,
        expense_date: Optional[datetime] = None
    ) -> Optional[Expense]:
        """
        Xarajat qo'shish
        
        Args:
            telegram_id: Foydalanuvchi ID
            amount: Summa
            category_key: Kategoriya key
            description: Tavsif
            expense_date: Xarajat sanasi
            
        Returns:
            Optional[Expense]: Yaratilgan xarajat
        """
        session = self.get_session()
        try:
            # Kategoriyani topish
            category = session.query(Category).filter(Category.key == category_key).first()
            if not category:
                logger.error(f"Kategoriya topilmadi: {category_key}")
                return None
            
            # Xarajat yaratish
            expense = Expense(
                user_id=telegram_id,
                category_id=category.id,
                amount=amount,
                description=description,
                expense_date=expense_date or datetime.now()
            )
            
            session.add(expense)
            session.commit()
            logger.info(f"Xarajat qo'shildi: {telegram_id}, {amount}, {category_key}")
            return expense
        except Exception as e:
            session.rollback()
            logger.error(f"add_expense xatosi: {e}")
            return None
        finally:
            session.close()
    
    def get_user_expenses(
        self,
        telegram_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        category_key: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Expense]:
        """
        Foydalanuvchi xarajatlarini olish
        
        Args:
            telegram_id: Foydalanuvchi ID
            start_date: Boshlanish sanasi
            end_date: Tugash sanasi
            category_key: Kategoriya filtri
            limit: Maksimal soni
            
        Returns:
            List[Expense]: Xarajatlar ro'yxati
        """
        from sqlalchemy.orm import joinedload
        
        session = self.get_session()
        try:
            # EAGER LOADING - category ni oldindan yuklash
            query = session.query(Expense).options(
                joinedload(Expense.category)
            ).filter(Expense.user_id == telegram_id)
            
            if start_date:
                query = query.filter(Expense.expense_date >= start_date)
            if end_date:
                query = query.filter(Expense.expense_date <= end_date)
            if category_key:
                category = session.query(Category).filter(Category.key == category_key).first()
                if category:
                    query = query.filter(Expense.category_id == category.id)
            
            query = query.order_by(desc(Expense.expense_date))
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
        finally:
            session.close()
    
    def get_total_expenses(
        self,
        telegram_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Decimal:
        """
        Jami xarajatlar summasini hisoblash
        
        Args:
            telegram_id: Foydalanuvchi ID
            start_date: Boshlanish sanasi
            end_date: Tugash sanasi
            
        Returns:
            Decimal: Jami summa
        """
        session = self.get_session()
        try:
            query = session.query(func.sum(Expense.amount)).filter(
                Expense.user_id == telegram_id
            )
            
            if start_date:
                query = query.filter(Expense.expense_date >= start_date)
            if end_date:
                query = query.filter(Expense.expense_date <= end_date)
            
            result = query.scalar()
            return result or Decimal('0.00')
        finally:
            session.close()
    
    def get_expenses_by_category(
        self,
        telegram_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        """
        Kategoriya bo'yicha xarajatlar statistikasi
        
        Args:
            telegram_id: Foydalanuvchi ID
            start_date: Boshlanish sanasi
            end_date: Tugash sanasi
            
        Returns:
            List[Dict]: [{'category': Category, 'total': Decimal, 'count': int}]
        """
        session = self.get_session()
        try:
            query = session.query(
                Category,
                func.sum(Expense.amount).label('total'),
                func.count(Expense.id).label('count')
            ).join(
                Expense, Expense.category_id == Category.id
            ).filter(
                Expense.user_id == telegram_id
            )
            
            if start_date:
                query = query.filter(Expense.expense_date >= start_date)
            if end_date:
                query = query.filter(Expense.expense_date <= end_date)
            
            query = query.group_by(Category.id).order_by(desc('total'))
            
            results = []
            for category, total, count in query.all():
                results.append({
                    'category': category,
                    'total': total or Decimal('0.00'),
                    'count': count or 0
                })
            
            return results
        finally:
            session.close()
    
    def delete_expense(self, expense_id: int, telegram_id: int) -> bool:
        """
        Xarajatni o'chirish
        
        Args:
            expense_id: Xarajat ID
            telegram_id: Foydalanuvchi ID (xavfsizlik uchun)
            
        Returns:
            bool: Muvaffaqiyatli o'chirildi
        """
        session = self.get_session()
        try:
            expense = session.query(Expense).filter(
                and_(Expense.id == expense_id, Expense.user_id == telegram_id)
            ).first()
            
            if expense:
                session.delete(expense)
                session.commit()
                logger.info(f"Xarajat o'chirildi: {expense_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"delete_expense xatosi: {e}")
            return False
        finally:
            session.close()
    
    def get_expense_by_id(self, expense_id: int, telegram_id: int) -> Optional[Expense]:
        """
        Xarajatni ID bo'yicha olish
        
        Args:
            expense_id: Xarajat ID
            telegram_id: Foydalanuvchi ID (xavfsizlik uchun)
            
        Returns:
            Optional[Expense]: Xarajat yoki None
        """
        from sqlalchemy.orm import joinedload
        
        session = self.get_session()
        try:
            expense = session.query(Expense).options(
                joinedload(Expense.category)
            ).filter(
                and_(Expense.id == expense_id, Expense.user_id == telegram_id)
            ).first()
            return expense
        finally:
            session.close()
    
    
    # =====================================================
    # INCOME OPERATIONS
    # =====================================================
    
    def add_income(
        self,
        telegram_id: int,
        amount: Decimal,
        source: Optional[str] = None,
        income_type: str = 'other',
        is_recurring: bool = False,
        income_date: Optional[datetime] = None
    ) -> Optional[Income]:
        """
        Daromad qo'shish
        
        Args:
            telegram_id: Foydalanuvchi ID
            amount: Summa
            source: Manba
            income_type: Daromad turi
            is_recurring: Takrorlanuvchi
            income_date: Daromad sanasi
            
        Returns:
            Optional[Income]: Yaratilgan daromad
        """
        session = self.get_session()
        try:
            income = Income(
                user_id=telegram_id,
                amount=amount,
                source=source,
                income_type=income_type,
                is_recurring=is_recurring,
                income_date=income_date or datetime.now()
            )
            
            session.add(income)
            session.commit()
            logger.info(f"Daromad qo'shildi: {telegram_id}, {amount}")
            return income
        except Exception as e:
            session.rollback()
            logger.error(f"add_income xatosi: {e}")
            return None
        finally:
            session.close()
    
    def get_user_incomes(
        self,
        telegram_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: Optional[int] = None
    ) -> List[Income]:
        """
        Foydalanuvchi daromadlarini olish
        
        Args:
            telegram_id: Foydalanuvchi ID
            start_date: Boshlanish sanasi
            end_date: Tugash sanasi
            limit: Maksimal soni
            
        Returns:
            List[Income]: Daromadlar ro'yxati
        """
        session = self.get_session()
        try:
            query = session.query(Income).filter(Income.user_id == telegram_id)
            
            if start_date:
                query = query.filter(Income.income_date >= start_date)
            if end_date:
                query = query.filter(Income.income_date <= end_date)
            
            query = query.order_by(desc(Income.income_date))
            
            if limit:
                query = query.limit(limit)
            
            return query.all()
        finally:
            session.close()
    
    def get_total_income(
        self,
        telegram_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Decimal:
        """
        Jami daromad summasini hisoblash
        
        Args:
            telegram_id: Foydalanuvchi ID
            start_date: Boshlanish sanasi
            end_date: Tugash sanasi
            
        Returns:
            Decimal: Jami summa
        """
        session = self.get_session()
        try:
            query = session.query(func.sum(Income.amount)).filter(
                Income.user_id == telegram_id
            )
            
            if start_date:
                query = query.filter(Income.income_date >= start_date)
            if end_date:
                query = query.filter(Income.income_date <= end_date)
            
            result = query.scalar()
            return result or Decimal('0.00')
        finally:
            session.close()
    
    def delete_income(self, income_id: int, telegram_id: int) -> bool:
        """
        Daromadni o'chirish
        
        Args:
            income_id: Daromad ID
            telegram_id: Foydalanuvchi ID (xavfsizlik uchun)
            
        Returns:
            bool: Muvaffaqiyatli o'chirildi
        """
        session = self.get_session()
        try:
            income = session.query(Income).filter(
                and_(Income.id == income_id, Income.user_id == telegram_id)
            ).first()
            
            if income:
                session.delete(income)
                session.commit()
                logger.info(f"Daromad o'chirildi: {income_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"delete_income xatosi: {e}")
            return False
        finally:
            session.close()
    
    def get_income_by_id(self, income_id: int, telegram_id: int) -> Optional[Income]:
        """
        Daromadni ID bo'yicha olish
        
        Args:
            income_id: Daromad ID
            telegram_id: Foydalanuvchi ID (xavfsizlik uchun)
            
        Returns:
            Optional[Income]: Daromad yoki None
        """
        session = self.get_session()
        try:
            income = session.query(Income).filter(
                and_(Income.id == income_id, Income.user_id == telegram_id)
            ).first()
            return income
        finally:
            session.close()
    
    
    # =====================================================
    # DEBT OPERATIONS
    # =====================================================
    
    def add_debt(
        self,
        telegram_id: int,
        person_name: str,
        amount: Decimal,
        debt_type: str,
        due_date: Optional[date] = None,
        description: Optional[str] = None,
        reminder_days: Optional[int] = None
    ) -> Optional['Debt']:
        """
        Qarz qo'shish
        
        Args:
            telegram_id: Foydalanuvchi ID
            person_name: Shaxs ismi
            amount: Summa
            debt_type: Qarz turi ('given' yoki 'taken')
            due_date: Qaytarish sanasi
            description: Izoh
            reminder_days: Eslatma kunlari oldin
            
        Returns:
            Optional[Debt]: Yaratilgan qarz
        """
        session = self.get_session()
        try:
            debt = Debt(
                user_id=telegram_id,
                person_name=person_name,
                amount=amount,
                debt_type=debt_type,
                due_date=due_date,
                description=description,
                status='active',
                paid_amount=Decimal('0'),
                reminder_days=reminder_days
            )
            
            session.add(debt)
            session.commit()
            session.refresh(debt)
            logger.info(f"Qarz qo'shildi: {telegram_id}, {person_name}, {amount}, {debt_type}")
            
            return debt
        except Exception as e:
            session.rollback()
            logger.error(f"add_debt xatosi: {e}")
            return None
        finally:
            session.close()
    
    def get_user_debts(
        self,
        telegram_id: int,
        debt_type: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List['Debt']:
        """
        Foydalanuvchi qarzlarini olish
        
        Args:
            telegram_id: Foydalanuvchi ID
            debt_type: Qarz turi ('given', 'taken', None=hammasi)
            status: Holat ('active', 'paid', 'overdue', None=hammasi)
            start_date: Boshlanish sanasi
            end_date: Tugash sanasi
            
        Returns:
            List[Debt]: Qarzlar ro'yxati
        """
        session = self.get_session()
        try:
            query = session.query(Debt).filter(Debt.user_id == telegram_id)
            
            if debt_type:
                query = query.filter(Debt.debt_type == debt_type)
            
            if status:
                query = query.filter(Debt.status == status)
            
            if start_date:
                query = query.filter(Debt.created_at >= start_date)
            
            if end_date:
                query = query.filter(Debt.created_at <= end_date)
            
            debts = query.order_by(desc(Debt.created_at)).all()
            return debts
        except Exception as e:
            logger.error(f"get_user_debts xatosi: {e}")
            return []
        finally:
            session.close()
    
    def get_debt_by_id(
        self,
        debt_id: int,
        telegram_id: int
    ) -> Optional['Debt']:
        """
        ID bo'yicha qarzni olish
        
        Args:
            debt_id: Qarz ID
            telegram_id: Foydalanuvchi ID
            
        Returns:
            Optional[Debt]: Qarz
        """
        session = self.get_session()
        try:
            debt = session.query(Debt).filter(
                Debt.id == debt_id,
                Debt.user_id == telegram_id
            ).first()
            return debt
        except Exception as e:
            logger.error(f"get_debt_by_id xatosi: {e}")
            return None
        finally:
            session.close()
    
    def update_debt(
        self,
        debt_id: int,
        telegram_id: int,
        **kwargs
    ) -> Optional['Debt']:
        """
        Qarzni yangilash
        
        Args:
            debt_id: Qarz ID
            telegram_id: Foydalanuvchi ID
            **kwargs: Yangilanadigan maydonlar
            
        Returns:
            Optional[Debt]: Yangilangan qarz
        """
        session = self.get_session()
        try:
            debt = session.query(Debt).filter(
                Debt.id == debt_id,
                Debt.user_id == telegram_id
            ).first()
            
            if not debt:
                return None
            
            # Allowed fields
            allowed_fields = ['person_name', 'amount', 'due_date', 'description', 
                            'status', 'paid_amount', 'reminder_days']
            
            for key, value in kwargs.items():
                if key in allowed_fields and hasattr(debt, key):
                    setattr(debt, key, value)
            
            session.commit()
            session.refresh(debt)
            logger.info(f"Qarz yangilandi: {debt_id}")
            return debt
        except Exception as e:
            session.rollback()
            logger.error(f"update_debt xatosi: {e}")
            return None
        finally:
            session.close()
    
    def mark_debt_paid(
        self,
        debt_id: int,
        telegram_id: int,
        paid_amount: Optional[Decimal] = None
    ) -> bool:
        """
        Qarzni to'langan deb belgilash (to'liq yoki qisman)
        
        Args:
            debt_id: Qarz ID
            telegram_id: Foydalanuvchi ID
            paid_amount: To'langan summa (None bo'lsa to'liq to'langan)
            
        Returns:
            bool: Muvaffaqiyatli belgilandi
        """
        session = self.get_session()
        try:
            debt = session.query(Debt).filter(
                Debt.id == debt_id,
                Debt.user_id == telegram_id
            ).first()
            
            if not debt:
                return False
            
            if paid_amount is None:
                # To'liq to'landi
                debt.paid_amount = debt.amount
                debt.status = 'paid'
            else:
                # Qisman to'landi
                debt.paid_amount += paid_amount
                if debt.paid_amount >= debt.amount:
                    debt.status = 'paid'
                else:
                    debt.status = 'partially_paid'
            
            session.commit()
            logger.info(f"Qarz to'langan deb belgilandi: {debt_id}")
            return True
        except Exception as e:
            session.rollback()
            logger.error(f"mark_debt_paid xatosi: {e}")
            return False
        finally:
            session.close()
    
    def delete_debt(
        self,
        debt_id: int,
        telegram_id: int
    ) -> bool:
        """
        Qarzni o'chirish
        
        Args:
            debt_id: Qarz ID
            telegram_id: Foydalanuvchi ID
            
        Returns:
            bool: Muvaffaqiyatli o'chirildi
        """
        session = self.get_session()
        try:
            debt = session.query(Debt).filter(
                Debt.id == debt_id,
                Debt.user_id == telegram_id
            ).first()
            
            if debt:
                session.delete(debt)
                session.commit()
                logger.info(f"Qarz o'chirildi: {debt_id}")
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"delete_debt xatosi: {e}")
            return False
        finally:
            session.close()
    
    def get_overdue_debts(
        self,
        telegram_id: Optional[int] = None
    ) -> List['Debt']:
        """
        Muddati o'tgan qarzlarni olish
        
        Args:
            telegram_id: Foydalanuvchi ID (None bo'lsa barcha foydalanuvchilar)
            
        Returns:
            List[Debt]: Muddati o'tgan qarzlar
        """
        session = self.get_session()
        try:
            query = session.query(Debt).filter(
                Debt.status.in_(['active', 'partially_paid']),
                Debt.due_date < date.today()
            )
            
            if telegram_id:
                query = query.filter(Debt.user_id == telegram_id)
            
            debts = query.all()
            
            # Statusni yangilash
            for debt in debts:
                debt.status = 'overdue'
            session.commit()
            
            return debts
        except Exception as e:
            session.rollback()
            logger.error(f"get_overdue_debts xatosi: {e}")
            return []
        finally:
            session.close()
    
    def get_debts_with_reminders(
        self,
        telegram_id: Optional[int] = None,
        days_before: int = 3
    ) -> List['Debt']:
        """
        Eslatma kerak bo'lgan qarzlarni olish
        
        Args:
            telegram_id: Foydalanuvchi ID
            days_before: Necha kun oldin eslatish
            
        Returns:
            List[Debt]: Qarzlar ro'yxati
        """
        session = self.get_session()
        try:
            reminder_date = date.today() + timedelta(days=days_before)
            
            query = session.query(Debt).filter(
                Debt.status.in_(['active', 'partially_paid']),
                Debt.due_date == reminder_date,
                Debt.reminder_days == days_before
            )
            
            if telegram_id:
                query = query.filter(Debt.user_id == telegram_id)
            
            debts = query.all()
            return debts
        except Exception as e:
            logger.error(f"get_debts_with_reminders xatosi: {e}")
            return []
        finally:
            session.close()
    
    def get_debt_statistics(
        self,
        telegram_id: int
    ) -> Dict[str, Any]:
        """
        Qarzlar statistikasini olish
        
        Args:
            telegram_id: Foydalanuvchi ID
            
        Returns:
            Dict: Statistika ma'lumotlari
        """
        session = self.get_session()
        try:
            # Bergan qarzlar
            given_debts = session.query(Debt).filter(
                Debt.user_id == telegram_id,
                Debt.debt_type == 'given'
            ).all()
            
            given_total = sum(d.amount for d in given_debts)
            given_active = sum(d.amount - d.paid_amount for d in given_debts if d.status in ['active', 'partially_paid'])
            given_paid = sum(d.paid_amount for d in given_debts)
            
            # Olgan qarzlar
            taken_debts = session.query(Debt).filter(
                Debt.user_id == telegram_id,
                Debt.debt_type == 'taken'
            ).all()
            
            taken_total = sum(d.amount for d in taken_debts)
            taken_active = sum(d.amount - d.paid_amount for d in taken_debts if d.status in ['active', 'partially_paid'])
            taken_paid = sum(d.paid_amount for d in taken_debts)
            
            # Muddati o'tganlar
            overdue_given = len([d for d in given_debts if d.status == 'overdue'])
            overdue_taken = len([d for d in taken_debts if d.status == 'overdue'])
            
            return {
                'given': {
                    'total': given_total,
                    'active': given_active,
                    'paid': given_paid,
                    'count': len(given_debts),
                    'overdue': overdue_given
                },
                'taken': {
                    'total': taken_total,
                    'active': taken_active,
                    'paid': taken_paid,
                    'count': len(taken_debts),
                    'overdue': overdue_taken
                }
            }
        except Exception as e:
            logger.error(f"get_debt_statistics xatosi: {e}")
            return {'given': {}, 'taken': {}}
        finally:
            session.close()
    
    
    # =====================================================
    # REMINDER OPERATIONS
    # =====================================================
    
    def add_reminder(
        self,
        telegram_id: int,
        reminder_type: str,
        reminder_date: datetime,
        debt_id: Optional[int] = None,
        message: Optional[str] = None
    ) -> Optional[Reminder]:
        """
        Eslatma qo'shish
        
        Args:
            telegram_id: Foydalanuvchi ID
            reminder_type: Eslatma turi
            reminder_date: Eslatma sanasi
            debt_id: Qarz ID (agar qarz eslatmasi bo'lsa)
            message: Xabar
            
        Returns:
            Optional[Reminder]: Yaratilgan eslatma
        """
        session = self.get_session()
        try:
            reminder = Reminder(
                user_id=telegram_id,
                debt_id=debt_id,
                reminder_type=reminder_type,
                reminder_date=reminder_date,
                message=message,
                is_sent=False
            )
            
            session.add(reminder)
            session.commit()
            logger.info(f"Eslatma qo'shildi: {telegram_id}, {reminder_type}")
            return reminder
        except Exception as e:
            session.rollback()
            logger.error(f"add_reminder xatosi: {e}")
            return None
        finally:
            session.close()
    
    def get_pending_reminders(self) -> List[Reminder]:
        """
        Yuborilmagan eslatmalarni olish
        
        Returns:
            List[Reminder]: Eslatmalar ro'yxati
        """
        session = self.get_session()
        try:
            now = datetime.now()
            
            query = session.query(Reminder).filter(
                and_(
                    Reminder.is_sent == False,
                    Reminder.reminder_date <= now
                )
            ).order_by(asc(Reminder.reminder_date))
            
            return query.all()
        finally:
            session.close()
    
    def mark_reminder_sent(self, reminder_id: int) -> bool:
        """
        Eslatmani yuborilgan deb belgilash
        
        Args:
            reminder_id: Eslatma ID
            
        Returns:
            bool: Muvaffaqiyatli belgilandi
        """
        session = self.get_session()
        try:
            reminder = session.query(Reminder).filter(Reminder.id == reminder_id).first()
            
            if reminder:
                reminder.is_sent = True
                reminder.sent_at = datetime.now()
                session.commit()
                return True
            return False
        except Exception as e:
            session.rollback()
            logger.error(f"mark_reminder_sent xatosi: {e}")
            return False
        finally:
            session.close()
    
    
    # =====================================================
    # STATISTICS & ANALYTICS
    # =====================================================
    
    def get_balance(
        self,
        telegram_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Decimal:
        """
        Balansni hisoblash (daromad - xarajat)
        
        Args:
            telegram_id: Foydalanuvchi ID
            start_date: Boshlanish sanasi
            end_date: Tugash sanasi
            
        Returns:
            Decimal: Balans
        """
        total_income = self.get_total_income(telegram_id, start_date, end_date)
        total_expense = self.get_total_expenses(telegram_id, start_date, end_date)
        return total_income - total_expense
    
    def get_daily_expenses_trend(
        self,
        telegram_id: int,
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        Kunlik xarajatlar trendi
        
        Args:
            telegram_id: Foydalanuvchi ID
            days: Necha kunlik ma'lumot
            
        Returns:
            List[Dict]: [{'date': date, 'total': Decimal}]
        """
        session = self.get_session()
        try:
            start_date = datetime.now() - timedelta(days=days)
            
            query = session.query(
                func.date(Expense.expense_date).label('date'),
                func.sum(Expense.amount).label('total')
            ).filter(
                and_(
                    Expense.user_id == telegram_id,
                    Expense.expense_date >= start_date
                )
            ).group_by(
                func.date(Expense.expense_date)
            ).order_by(asc('date'))
            
            results = []
            for date_obj, total in query.all():
                results.append({
                    'date': date_obj,
                    'total': total or Decimal('0.00')
                })
            
            return results
        finally:
            session.close()

    
    # =====================================================
    # DEBT STATISTICS (YANGI QO'SHILDI)
    # =====================================================
    
