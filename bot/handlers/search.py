"""
Search Handler — Klinika qidirish
Shahar, ixtisoslik, nom bo'yicha
"""
import httpx
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()
API = __import__('os').getenv('DJANGO_API_URL', 'http://backend:8000/api/v1')

SPECIALTIES = {
    'uz': [
        ('dental', '🦷 Stomatologiya'), ('eye', '👁 Ko\'z klinikasi'),
        ('skin', '🧴 Teri klinikasi'), ('neuro', '🧠 Nevrologiya'),
        ('cardio', '❤️ Kardiologiya'), ('child', '👶 Bolalar'),
        ('general', '🏥 Umumiy'), ('other', '🏨 Boshqa'),
    ],
    'ru': [
        ('dental', '🦷 Стоматология'), ('eye', '👁 Офтальмология'),
        ('skin', '🧴 Дерматология'), ('neuro', '🧠 Неврология'),
        ('cardio', '❤️ Кардиология'), ('child', '👶 Педиатрия'),
        ('general', '🏥 Общая'), ('other', '🏨 Другое'),
    ],
    'en': [
        ('dental', '🦷 Dentistry'), ('eye', '👁 Ophthalmology'),
        ('skin', '🧴 Dermatology'), ('neuro', '🧠 Neurology'),
        ('cardio', '❤️ Cardiology'), ('child', '👶 Pediatrics'),
        ('general', '🏥 General'), ('other', '🏨 Other'),
    ],
}

CITIES = ['Toshkent', 'Samarqand', 'Namangan', 'Buxoro', 'Andijon', 'Farg\'ona', 'Nukus', 'Barchasi']


class SearchState(StatesGroup):
    waiting_text = State()


def specialty_kb(lang='uz') -> InlineKeyboardMarkup:
    specs = SPECIALTIES.get(lang, SPECIALTIES['uz'])
    rows = []
    # Qidiruv nomi bo'yicha
    search_name = {
        'uz': '🔍 Nomi bo\'yicha qidirish',
        'ru': '🔍 Поиск по названию',
        'en': '🔍 Search by Name'
    }
    rows.append([InlineKeyboardButton(text=search_name.get(lang, search_name['uz']), callback_data='search_by_name')])
    
    for i in range(0, len(specs), 2):
        row = []
        row.append(InlineKeyboardButton(text=specs[i][1], callback_data=f'spec:{specs[i][0]}'))
        if i + 1 < len(specs):
            row.append(InlineKeyboardButton(text=specs[i+1][1], callback_data=f'spec:{specs[i+1][0]}'))
        rows.append(row)
    rows.append([InlineKeyboardButton(text='🔙', callback_data='main_menu')])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def city_kb(spec: str) -> InlineKeyboardMarkup:
    rows = []
    for i in range(0, len(CITIES), 2):
        row = [InlineKeyboardButton(text=CITIES[i], callback_data=f'city:{spec}:{CITIES[i]}')]
        if i+1 < len(CITIES):
            row.append(InlineKeyboardButton(text=CITIES[i+1], callback_data=f'city:{spec}:{CITIES[i+1]}'))
        rows.append(row)
    rows.append([InlineKeyboardButton(text='🔙', callback_data='search_clinic')])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def get_lang(telegram_id: int) -> str:
    try:
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{API}/patients/global/{telegram_id}/", timeout=4)
            if r.status_code == 200:
                return r.json().get('telegram_language', 'uz')
    except Exception:
        pass
    return 'uz'


@router.callback_query(F.data == 'search_clinic')
async def search_menu(callback: CallbackQuery):
    lang = await get_lang(callback.from_user.id)
    titles = {
        'uz': "🔍 <b>Klinika qidirish</b>\n\nQaysi ixtisoslikdagi klinikani qidirmoqchisiz?",
        'ru': "🔍 <b>Поиск клиники</b>\n\nКакую специализацию ищете?",
        'en': "🔍 <b>Find a Clinic</b>\n\nWhat specialty are you looking for?",
    }
    await callback.message.edit_text(titles.get(lang, titles['uz']), reply_markup=specialty_kb(lang))
    await callback.answer()


@router.callback_query(F.data == 'search_by_name')
async def search_by_name(callback: CallbackQuery, state: FSMContext):
    lang = await get_lang(callback.from_user.id)
    prompts = {
        'uz': "⌨️ Klinika nomini kiriting:",
        'ru': "⌨️ Введите название клиники:",
        'en': "⌨️ Type clinic name:"
    }
    await callback.message.edit_text(prompts.get(lang, prompts['uz']), 
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                                         [InlineKeyboardButton(text='🔙', callback_data='search_clinic')]
                                     ]))
    await state.set_state(SearchState.waiting_text)
    await callback.answer()


@router.message(SearchState.waiting_text)
async def process_search_name(message: Message, state: FSMContext):
    query = message.text
    lang = await get_lang(message.from_user.id)
    await state.clear()

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{API}/clinics/?search={query}&is_active=true", timeout=8)
            clinics = r.json().get('results', r.json()) if r.status_code == 200 else []
    except Exception:
        clinics = []

    if not clinics:
        no_res = {
            'uz': f"😔 '{query}' bo'yicha klinika topilmadi.",
            'ru': f"😔 Клиника '{query}' не найдена.",
            'en': f"😔 Clinic '{query}' not found.",
        }
        await message.answer(no_res.get(lang, no_res['uz']), reply_markup=specialty_kb(lang))
        return

    rows = []
    for clinic in clinics[:10]:
        name = clinic.get('name', '—')
        rating = clinic.get('rating', 0)
        city = clinic.get('city', '')
        rows.append([InlineKeyboardButton(text=f"🏥 {name} · {rating}⭐ · {city}", 
                                          callback_data=f"clinic_detail:{clinic.get('id')}")])
    
    rows.append([InlineKeyboardButton(text='🔙', callback_data='search_clinic')])
    
    titles = {
        'uz': f"🔍 <b>Qidiruv natijalari:</b>",
        'ru': f"🔍 <b>Результаты поиска:</b>",
        'en': f"🔍 <b>Search results:</b>",
    }
    await message.answer(titles.get(lang, titles['uz']), reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))


@router.callback_query(F.data.startswith('spec:'))
async def choose_city(callback: CallbackQuery):
    spec = callback.data.split(':')[1]
    lang = await get_lang(callback.from_user.id)
    titles = {
        'uz': "📍 <b>Shaharni tanlang:</b>",
        'ru': "📍 <b>Выберите город:</b>",
        'en': "📍 <b>Choose your city:</b>",
    }
    await callback.message.edit_text(titles.get(lang, titles['uz']), reply_markup=city_kb(spec))
    await callback.answer()


@router.callback_query(F.data.startswith('city:'))
async def show_clinics(callback: CallbackQuery):
    _, spec, city = callback.data.split(':', 2)
    lang = await get_lang(callback.from_user.id)

    params = f"clinic_type={spec}" + (f"&city={city}" if city != 'Barchasi' else "")
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{API}/clinics/?{params}&is_active=true&ordering=-rating", timeout=8)
            clinics = r.json().get('results', r.json()) if r.status_code == 200 else []
    except Exception:
        clinics = []

    if not clinics:
        no_res = {
            'uz': "😔 Bu bo'yicha klinikalar topilmadi. Boshqa shahar yoki ixtisoslik tanlang.",
            'ru': "😔 Клиники не найдены. Попробуйте другой город или специализацию.",
            'en': "😔 No clinics found. Try another city or specialty.",
        }
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='🔙 Orqaga', callback_data='search_clinic')]
        ])
        await callback.message.edit_text(no_res.get(lang, no_res['uz']), reply_markup=kb)
        await callback.answer()
        return

    # Klinikalar ro'yxati
    rows = []
    for clinic in clinics[:10]:  # Max 10 ta
        name = clinic.get('name', '—')
        rating = clinic.get('rating', 0)
        stars = f"{rating}⭐" if rating else "☆"
        city_info = clinic.get('city', '')
        rows.append([InlineKeyboardButton(
            text=f"🏥 {name} · {stars} · {city_info}",
            callback_data=f"clinic_detail:{clinic.get('id')}"
        )])

    rows.append([InlineKeyboardButton(text='🔙', callback_data='search_clinic')])

    titles = {
        'uz': f"🏥 <b>Topilgan klinikalar ({len(clinics)}):</b>",
        'ru': f"🏥 <b>Найдено клиник ({len(clinics)}):</b>",
        'en': f"🏥 <b>Clinics found ({len(clinics)}):</b>",
    }
    await callback.message.edit_text(titles.get(lang, titles['uz']),
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await callback.answer()


@router.callback_query(F.data.startswith('clinic_detail:'))
async def clinic_detail(callback: CallbackQuery):
    clinic_id = callback.data.split(':')[1]
    lang = await get_lang(callback.from_user.id)

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{API}/clinics/{clinic_id}/", timeout=5)
            if r.status_code == 200:
                clinic = r.json()
                from .start import show_clinic_detail
                # Callback → yangi xabar
                await callback.message.delete()
                await show_clinic_detail(callback.message, clinic, lang)
                await callback.answer()
                return
    except Exception:
        pass

    await callback.answer("❌ Xato", show_alert=True)


@router.callback_query(F.data.startswith('rate_clinic:'))
async def rate_clinic(callback: CallbackQuery):
    clinic_id = callback.data.split(':')[1]
    lang = await get_lang(callback.from_user.id)
    titles = {
        'uz': "⭐ <b>Klinikani baholang:</b>",
        'ru': "⭐ <b>Оцените клинику:</b>",
        'en': "⭐ <b>Rate the clinic:</b>",
    }
    rows = [[
        InlineKeyboardButton(text=f"{i}⭐", callback_data=f"give_rating:{clinic_id}:{i}")
        for i in range(1, 6)
    ], [InlineKeyboardButton(text='🔙', callback_data=f'clinic_detail:{clinic_id}')]]
    await callback.message.edit_text(titles.get(lang, titles['uz']),
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await callback.answer()


@router.callback_query(F.data.startswith('give_rating:'))
async def save_rating(callback: CallbackQuery):
    _, clinic_id, rating = callback.data.split(':')
    lang = await get_lang(callback.from_user.id)
    user = callback.from_user

    try:
        async with httpx.AsyncClient() as client:
            await client.post(f"{API}/clinics/{clinic_id}/review/", json={
                'telegram_id': user.id,
                'patient_name': f"{user.first_name or ''} {user.last_name or ''}".strip(),
                'rating': int(rating),
            }, timeout=5)
    except Exception:
        pass

    msgs = {
        'uz': f"✅ Rahmat! {rating}⭐ baho berildi.",
        'ru': f"✅ Спасибо! Вы поставили {rating}⭐.",
        'en': f"✅ Thanks! You rated {rating}⭐.",
    }
    await callback.answer(msgs.get(lang, msgs['uz']), show_alert=True)
