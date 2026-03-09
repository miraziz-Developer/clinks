"""
Start Handler — /start va deep link (clinic_TOKEN)
"""
import httpx
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import CommandStart, CommandObject

router = Router()
API = __import__('os').getenv('DJANGO_API_URL', 'http://backend:8000/api/v1')


def main_menu_kb(lang='uz') -> InlineKeyboardMarkup:
    texts = {
        'uz': ['🔍 Klinika topish', '📅 Mening navbatlarim', '⭐ Sevimlilar', '👤 Profilim', '🌐 Til'],
        'ru': ['🔍 Найти клинику', '📅 Мои записи', '⭐ Избранные', '👤 Мой профиль', '🌐 Язык'],
        'en': ['🔍 Find Clinic', '📅 My Appointments', '⭐ Favorites', '👤 My Profile', '🌐 Language'],
    }
    t = texts.get(lang, texts['uz'])
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t[0], callback_data='search_clinic')],
        [
            InlineKeyboardButton(text=t[1], callback_data='my_appointments'),
            InlineKeyboardButton(text=t[2], callback_data='favorites'),
        ],
        [
            InlineKeyboardButton(text=t[3], callback_data='my_profile'),
            InlineKeyboardButton(text=t[4], callback_data='change_lang'),
        ],
    ])


async def register_user(tg_user, lang='uz'):
    """Foydalanuvchini platformaga ro'yxatdan o'tkazish vs yangilash"""
    try:
        async with httpx.AsyncClient() as client:
            await client.post(f"{API}/patients/global/register/", json={
                'telegram_id': tg_user.id,
                'telegram_username': tg_user.username or '',
                'telegram_first_name': tg_user.first_name or '',
                'telegram_last_name': tg_user.last_name or '',
                'telegram_language': tg_user.language_code or lang,
            }, timeout=5)
    except Exception:
        pass


async def get_user_lang(telegram_id: int) -> str:
    """Foydalanuvchi tilini olish"""
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{API}/patients/global/{telegram_id}/", timeout=5)
            if r.status_code == 200:
                return r.json().get('telegram_language', 'uz')
    except Exception:
        pass
    return 'uz'


@router.message(CommandStart())
async def cmd_start(message: Message, command: CommandObject):
    """
    /start — asosiy menyu
    /start clinic_TOKEN — bevosita klinikaga
    """
    user = message.from_user
    lang = user.language_code[:2] if user.language_code else 'uz'
    if lang not in ('uz', 'ru', 'en'):
        lang = 'uz'

    # Foydalanuvchini ro'yxatdan o'tkazish
    await register_user(user, lang)

    args = command.args  # clinic_TOKEN yoki bo'sh

    if args and args.startswith('clinic_'):
        # Deep link — bevosita klinikaga yo'naltirish
        token = args.replace('clinic_', '')
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{API}/clinics/by_token/{token}/", timeout=5)
                if r.status_code == 200:
                    clinic = r.json()
                    await show_clinic_detail(message, clinic, lang)
                    return
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Deep link parsing error: {e}", exc_info=True)
            pass
        # Token topilmadi
        err = {
            'uz': '❌ Klinika topilmadi. Havola eskirgan bo\'lishi mumkin.',
            'ru': '❌ Клиника не найдена. Ссылка могла устареть.',
            'en': '❌ Clinic not found. The link may have expired.',
        }
        await message.answer(err.get(lang, err['uz']))

    # Asosiy menyu
    greet = {
        'uz': (
            f"👋 Assalomu alaykum, <b>{user.first_name}</b>!\n\n"
            "🏥 <b>CLinks.uz</b> ga xush kelibsiz!\n"
            "Sizga yaqin klinikalarda navbat oling.\n\n"
            "Quyidagilardan birini tanlang:"
        ),
        'ru': (
            f"👋 Здравствуйте, <b>{user.first_name}</b>!\n\n"
            "🏥 Добро пожаловать в <b>CLinks.uz</b>!\n"
            "Записывайтесь к врачам в ближайших клиниках.\n\n"
            "Выберите одно из следующих:"
        ),
        'en': (
            f"👋 Hello, <b>{user.first_name}</b>!\n\n"
            "🏥 Welcome to <b>CLinks.uz</b>!\n"
            "Book appointments at clinics near you.\n\n"
            "Choose one of the following:"
        ),
    }
    await message.answer(
        greet.get(lang, greet['uz']),
        reply_markup=main_menu_kb(lang)
    )


async def show_clinic_detail(message: Message, clinic: dict, lang: str = 'uz'):
    """Klinika detail sahifasi — Premium style 🏥"""
    name = clinic.get('name', '—')
    city = clinic.get('city', '')
    address = clinic.get('address', '')
    rating = float(clinic.get('rating') or 0)
    review_count = clinic.get('review_count', 0)
    clinic_type = clinic.get('clinic_type_display', '')
    description = clinic.get('description', '')
    phone = clinic.get('phone', '')
    work_start = clinic.get('work_start', '08:00')[:5]
    work_end = clinic.get('work_end', '18:00')[:5]
    slug = clinic.get('slug', '')
    clinic_id = clinic.get('id', '')
    cover = clinic.get('cover_image') or clinic.get('logo')

    # Reyting yulduzchalari
    full_star = '⭐'
    stars = full_star * int(rating) + '☆' * (5 - int(rating))
    
    titles = {
        'uz': (
            f"🏥 <b>{name}</b>\n"
            f"🩺 <i>Turi: {clinic_type}</i>\n\n"
            f"📍 <b>Manzil:</b> {city}, {address}\n"
            f"⭐️ <b>Reyting:</b> {stars} ({rating}/5.0 · {review_count} sharh)\n"
            f"🕒 <b>Ish vaqti:</b> {work_start} – {work_end}\n"
            f"📞 <b>Telefon:</b> {phone}\n\n"
            f"💬 <b>Klinika haqida:</b>\n"
            f"{description[:200]}{'...' if len(description or '') > 200 else ''}\n\n"
            f"🌐 <b>Veb-sahifa:</b> <u>clinks.uz/clinic/{slug}</u>"
        ),
        'ru': (
            f"🏥 <b>{name}</b>\n"
            f"🩺 <i>Тип: {clinic_type}</i>\n\n"
            f"📍 <b>Адрес:</b> {city}, {address}\n"
            f"⭐️ <b>Рейтинг:</b> {stars} ({rating}/5.0 · {review_count} отзывов)\n"
            f"🕒 <b>Время работы:</b> {work_start} – {work_end}\n"
            f"📞 <b>Телефон:</b> {phone}\n\n"
            f"💬 <b>О клинике:</b>\n"
            f"{description[:200]}{'...' if len(description or '') > 200 else ''}\n\n"
            f"🌐 <b>Веб-страница:</b> <u>clinks.uz/clinic/{slug}</u>"
        ),
        'en': (
            f"🏥 <b>{name}</b>\n"
            f"🩺 <i>Type: {clinic_type}</i>\n\n"
            f"📍 <b>Address:</b> {city}, {address}\n"
            f"⭐️ <b>Rating:</b> {stars} ({rating}/5.0 · {review_count} reviews)\n"
            f"🕒 <b>Working hours:</b> {work_start} – {work_end}\n"
            f"📞 <b>Phone:</b> {phone}\n\n"
            f"💬 <b>About clinic:</b>\n"
            f"{description[:200]}{'...' if len(description or '') > 200 else ''}\n\n"
            f"🌐 <b>Website:</b> <u>clinks.uz/clinic/{slug}</u>"
        ),
    }

    btn_texts = {
        'uz': ['📅 Navbat olish', '📍 Xaritada ko\'rish', '⭐ Baholash', '🔙 Orqaga'],
        'ru': ['📅 Записаться', '📍 На карте', '⭐ Оценить', '🔙 Назад'],
        'en': ['📅 Book Now', '📍 See on Map', '⭐ Rate', '🔙 Back'],
    }
    t = btn_texts.get(lang, btn_texts['uz'])

    lat, lng = clinic.get('latitude'), clinic.get('longitude')
    
    rows = [
        [InlineKeyboardButton(text=t[0], callback_data=f'book_clinic:{clinic_id}')]
    ]
    
    if lat and lng:
        rows.append([InlineKeyboardButton(text=t[1], url=f'https://www.google.com/maps?q={lat},{lng}')])
    
    rows.append([
        InlineKeyboardButton(text=t[2], callback_data=f'rate_clinic:{clinic_id}'),
        InlineKeyboardButton(text=t[3], callback_data='search_clinic')
    ])

    kb = InlineKeyboardMarkup(inline_keyboard=rows)

    text = titles.get(lang, titles['uz'])
    if cover:
        # Cover URL absolute bo'lishi kerak. Agar local bo'lsa backend domain qo'shiladi.
        if cover.startswith('/'):
            domain = API.replace('/api/v1', '')
            cover = domain + cover
        try:
            await message.answer_photo(cover, caption=text, reply_markup=kb)
        except Exception as e:
            import logging
            logging.getLogger(__name__).error(f"Error sending photo: {e}")
            await message.answer(text, reply_markup=kb)
    else:
        await message.answer(text, reply_markup=kb)


@router.callback_query(F.data == 'main_menu')
async def back_to_menu(callback: CallbackQuery):
    lang = await get_user_lang(callback.from_user.id)
    greet = {
        'uz': "🏠 <b>Asosiy menyu</b>",
        'ru': "🏠 <b>Главное меню</b>",
        'en': "🏠 <b>Main Menu</b>",
    }
    await callback.message.edit_text(greet.get(lang, greet['uz']), reply_markup=main_menu_kb(lang))
    await callback.answer()


@router.callback_query(F.data == 'change_lang')
async def change_language(callback: CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🇺🇿 O'zbekcha", callback_data='set_lang:uz'),
            InlineKeyboardButton(text="🇷🇺 Русский", callback_data='set_lang:ru'),
            InlineKeyboardButton(text="🇬🇧 English", callback_data='set_lang:en'),
        ],
        [InlineKeyboardButton(text="🔙", callback_data='main_menu')],
    ])
    await callback.message.edit_text("🌐 <b>Tilni tanlang / Выберите язык / Choose language:</b>", reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data.startswith('set_lang:'))
async def set_language(callback: CallbackQuery):
    lang = callback.data.split(':')[1]
    try:
        async with httpx.AsyncClient() as client:
            await client.patch(f"{API}/patients/global/{callback.from_user.id}/set_language/",
                               json={'language': lang}, timeout=5)
    except Exception:
        pass
    msgs = {
        'uz': "✅ Til o'zgardi: O'zbekcha",
        'ru': "✅ Язык изменён: Русский",
        'en': "✅ Language changed: English",
    }
    await callback.message.edit_text(msgs.get(lang, msgs['uz']), reply_markup=main_menu_kb(lang))
    await callback.answer()
