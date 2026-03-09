"""Profile & Favorites handlers"""
import httpx
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()
API = __import__('os').getenv('DJANGO_API_URL', 'http://backend:8000/api/v1')


async def get_lang(tid):
    try:
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{API}/patients/global/{tid}/", timeout=4)
            if r.status_code == 200: return r.json().get('telegram_language', 'uz')
    except: pass
    return 'uz'


@router.callback_query(F.data == 'my_profile')
async def my_profile(callback: CallbackQuery):
    lang = await get_lang(callback.from_user.id)
    user = callback.from_user

    try:
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{API}/patients/global/{user.id}/", timeout=4)
            p = r.json() if r.status_code == 200 else {}
    except:
        p = {}

    texts = {
        'uz': (
            f"👤 <b>Mening profilim</b>\n\n"
            f"📛 Ism: <b>{p.get('display_name', user.first_name)}</b>\n"
            f"📞 Telefon: <b>{p.get('phone', 'Kiritilmagan')}</b>\n"
            f"🏙 Shahar: <b>{p.get('city', 'Kiritilmagan')}</b>\n"
            f"📅 Jami navbatlar: <b>{p.get('total_appointments', 0)}</b>\n"
            f"🏥 Tashrif etgan klinikalar: <b>{p.get('total_clinics_visited', 0)}</b>"
        ),
        'ru': (
            f"👤 <b>Мой профиль</b>\n\n"
            f"📛 Имя: <b>{p.get('display_name', user.first_name)}</b>\n"
            f"📞 Телефон: <b>{p.get('phone', 'Не указан')}</b>\n"
            f"🏙 Город: <b>{p.get('city', 'Не указан')}</b>\n"
            f"📅 Всего записей: <b>{p.get('total_appointments', 0)}</b>\n"
            f"🏥 Клиник посещено: <b>{p.get('total_clinics_visited', 0)}</b>"
        ),
        'en': (
            f"👤 <b>My Profile</b>\n\n"
            f"📛 Name: <b>{p.get('display_name', user.first_name)}</b>\n"
            f"📞 Phone: <b>{p.get('phone', 'Not set')}</b>\n"
            f"🏙 City: <b>{p.get('city', 'Not set')}</b>\n"
            f"📅 Total appointments: <b>{p.get('total_appointments', 0)}</b>\n"
            f"🏥 Clinics visited: <b>{p.get('total_clinics_visited', 0)}</b>"
        ),
    }

    btn = {'uz': '🏠 Asosiy menyu', 'ru': '🏠 Главное меню', 'en': '🏠 Main Menu'}
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=btn.get(lang, btn['uz']), callback_data='main_menu')]
    ])
    await callback.message.edit_text(texts.get(lang, texts['uz']), reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data == 'favorites')
async def favorites(callback: CallbackQuery):
    lang = await get_lang(callback.from_user.id)
    msgs = {
        'uz': "⭐ <b>Sevimli klinikalar</b>\n\nBu funksiya tez kunda. Hozircha klinikalarni qidiring!",
        'ru': "⭐ <b>Избранные клиники</b>\n\nЭта функция скоро появится!",
        'en': "⭐ <b>Favorite Clinics</b>\n\nThis feature is coming soon!",
    }
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='🔍 Klinika topish', callback_data='search_clinic'),
         InlineKeyboardButton(text='🏠', callback_data='main_menu')]
    ])
    await callback.message.edit_text(msgs.get(lang, msgs['uz']), reply_markup=kb)
    await callback.answer()
