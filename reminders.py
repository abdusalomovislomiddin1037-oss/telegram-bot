"""
SmartWallet AI Bot - Reminders (DISABLED)
==========================================
Reminders o'chirilgan - qarz tizimi to'siqsiz ishlashi uchun

Author: SmartWallet AI Team
Version: 2.0.0 - REMINDERS DISABLED
"""

import logging
from datetime import datetime, timedelta, date
from typing import Optional

from telegram import Bot
from database.db_manager import DatabaseManager

logger = logging.getLogger(__name__)


# =====================================================
# REMINDER SCHEDULER CLASS (DISABLED)
# =====================================================
class ReminderScheduler:
    """
    Reminders o'chirilgan - qarz tizimi to'siqsiz ishlashi uchun
    """
    
    def __init__(self, bot: Bot):
        self.bot = bot
        logger.info("ReminderScheduler o'chirilgan (disabled)")
    
    def start(self):
        """Scheduler ishga tushmaydi"""
        logger.info("ReminderScheduler start() - o'chirilgan")
        pass
    
    def stop(self):
        """Scheduler to'xtamaydi"""
        logger.info("ReminderScheduler stop() - o'chirilgan")
        pass

# =====================================================
# HELPER FUNCTIONS (DISABLED)
# =====================================================
# Qarzlar tizimi o'chirilgani uchun bu funksiya ishlamaydi


def get_scheduler_instance(bot: Bot) -> ReminderScheduler:
    """
    Scheduler instance'ni olish (o'chirilgan)
    
    Args:
        bot: Telegram bot
        
    Returns:
        ReminderScheduler: Scheduler instance (o'chirilgan)
    """
    return ReminderScheduler(bot)
