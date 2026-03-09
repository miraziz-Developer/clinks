"""Admin notification handler — klinikaga navbat haqida xabar"""
import httpx
from aiogram import Router, Bot
from aiogram.types import Message
from aiogram.filters import Command

router = Router()
API = __import__('os').getenv('DJANGO_API_URL', 'http://backend:8000/api/v1')


async def notify_clinic_admin(bot: Bot, clinic_id: str, message: str):
    """Klinika adminlariga xabar yuborish"""
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{API}/clinics/{clinic_id}/admin_telegram_ids/", timeout=5)
            if r.status_code == 200:
                tg_ids = r.json().get('telegram_ids', [])
                for tg_id in tg_ids:
                    try:
                        await bot.send_message(tg_id, message, parse_mode='HTML')
                    except Exception:
                        pass
    except Exception:
        pass


async def notify_patient_reminder(bot: Bot, telegram_id: int, message: str):
    """Bemorga eslatma yuborish"""
    try:
        await bot.send_message(telegram_id, message, parse_mode='HTML')
    except Exception:
        pass
