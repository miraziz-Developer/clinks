"""
Booking Handler — Navbat olish flow
Clinic → Doctor → Date → Time → Confirm → Payment
"""
import httpx
from datetime import date, timedelta
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

router = Router()
API = __import__('os').getenv('DJANGO_API_URL', 'http://backend:8000/api/v1')


class BookingState(StatesGroup):
    choosing_doctor = State()
    choosing_date = State()
    choosing_time = State()
    confirming = State()


async def get_lang(telegram_id: int) -> str:
    try:
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{API}/patients/global/{telegram_id}/", timeout=4)
            if r.status_code == 200:
                return r.json().get('telegram_language', 'uz')
    except Exception:
        pass
    return 'uz'


async def ensure_patient(tg_user, clinic_id: str) -> dict | None:
    """Bemor klinikada ro'yxatda bo'lmasa yaratish"""
    try:
        async with httpx.AsyncClient() as c:
            r = await c.post(f"{API}/patients/ensure_in_clinic/", json={
                'telegram_id': tg_user.id,
                'telegram_first_name': tg_user.first_name or '',
                'telegram_last_name': tg_user.last_name or '',
                'telegram_username': tg_user.username or '',
                'clinic_id': clinic_id,
            }, timeout=5)
            if r.status_code in (200, 201):
                return r.json()
    except Exception:
        pass
    return None


@router.callback_query(F.data.startswith('book_clinic:'))
async def show_doctors(callback: CallbackQuery, state: FSMContext):
    clinic_id = callback.data.split(':')[1]
    lang = await get_lang(callback.from_user.id)

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{API}/doctors/?clinic={clinic_id}&is_active=true", timeout=6)
            if r.status_code == 200:
                data = r.json()
                if isinstance(data, dict):
                    doctors = data.get('results', [])
                elif isinstance(data, list):
                    doctors = data
                else:
                    doctors = []
            else:
                doctors = []
    except Exception as e:
        import logging
        logging.getLogger(__name__).error(f"Error fetching doctors: {e}", exc_info=True)
        doctors = []


    if not doctors:
        msgs = {
            'uz': "😔 Hozircha faol shifokorlar yo'q.",
            'ru': "😔 Сейчас нет доступных врачей.",
            'en': "😔 No doctors available right now.",
        }
        await callback.answer(msgs.get(lang, msgs['uz']), show_alert=True)
        return

    await state.update_data(clinic_id=clinic_id)

    titles = {
        'uz': "👨‍⚕️ <b>Shifokorni tanlang:</b>",
        'ru': "👨‍⚕️ <b>Выберите врача:</b>",
        'en': "👨‍⚕️ <b>Choose a doctor:</b>",
    }

    rows = []
    for d in doctors:
        name = f"{d.get('first_name','')} {d.get('last_name','')}".strip()
        spec = d.get('specialty', '')
        exp = d.get('experience_years', 0)
        fee = d.get('consultation_price') or 0
        try:
            fee_int = int(float(fee))
        except (ValueError, TypeError):
            fee_int = 0
        label = f"👤 {name} · {spec} · {exp}y · {fee_int:,} so'm"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"book_doctor:{d['id']}")])

    rows.append([InlineKeyboardButton(text='🔙', callback_data=f'clinic_detail:{clinic_id}')])
    await callback.message.edit_text(titles.get(lang, titles['uz']),
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await callback.answer()


@router.callback_query(F.data.startswith('book_doctor:'))
async def show_dates(callback: CallbackQuery, state: FSMContext):
    doctor_id = callback.data.split(':')[1]
    lang = await get_lang(callback.from_user.id)
    await state.update_data(doctor_id=doctor_id)

    # Keyingi 7 kunlik sanalar
    today = date.today()
    rows = []
    row = []
    for i in range(7):
        d = today + timedelta(days=i)
        day_name = d.strftime('%a')
        label = f"{d.strftime('%d.%m')} {day_name}"
        row.append(InlineKeyboardButton(text=label, callback_data=f"book_date:{d.isoformat()}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)

    data = await state.get_data()
    clinic_id = data.get('clinic_id', '')
    rows.append([InlineKeyboardButton(text='🔙', callback_data=f'book_clinic:{clinic_id}')])

    titles = {
        'uz': "📅 <b>Sanani tanlang:</b>",
        'ru': "📅 <b>Выберите дату:</b>",
        'en': "📅 <b>Choose a date:</b>",
    }
    await callback.message.edit_text(titles.get(lang, titles['uz']),
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await callback.answer()


@router.callback_query(F.data.startswith('book_date:'))
async def show_time_slots(callback: CallbackQuery, state: FSMContext):
    chosen_date = callback.data.split(':')[1]
    lang = await get_lang(callback.from_user.id)
    await state.update_data(chosen_date=chosen_date)

    data = await state.get_data()
    doctor_id = data.get('doctor_id', '')

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{API}/doctors/{doctor_id}/available_slots/?date={chosen_date}", timeout=6
            )
            slots = r.json().get('slots', []) if r.status_code == 200 else []
    except Exception:
        slots = []

    if not slots:
        msgs = {
            'uz': "😔 Bu kunda bo'sh vaqt yo'q. Boshqa kun tanlang.",
            'ru': "😔 На этот день нет свободного времени.",
            'en': "😔 No available slots for this day.",
        }
        await callback.answer(msgs.get(lang, msgs['uz']), show_alert=True)
        return

    rows = []
    row = []
    for slot in slots:
        row.append(InlineKeyboardButton(text=f"🕐 {slot}", callback_data=f"book_time:{slot}"))
        if len(row) == 3:
            rows.append(row)
            row = []
    if row:
        rows.append(row)
    rows.append([InlineKeyboardButton(text='🔙', callback_data=f'book_doctor:{doctor_id}')])

    titles = {
        'uz': f"🕐 <b>{chosen_date} — bo'sh vaqtlar:</b>",
        'ru': f"🕐 <b>{chosen_date} — свободное время:</b>",
        'en': f"🕐 <b>{chosen_date} — available slots:</b>",
    }
    await callback.message.edit_text(titles.get(lang, titles['uz']),
                                     reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await callback.answer()


@router.callback_query(F.data.startswith('book_time:'))
async def confirm_booking(callback: CallbackQuery, state: FSMContext):
    chosen_time = callback.data.split(':')[1]
    lang = await get_lang(callback.from_user.id)
    await state.update_data(chosen_time=chosen_time)

    data = await state.get_data()
    clinic_id = data.get('clinic_id', '')
    doctor_id = data.get('doctor_id', '')
    chosen_date = data.get('chosen_date', '')

    # Doctor ma'lumotlari
    doctor_name = '—'
    fee = 0
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{API}/doctors/{doctor_id}/", timeout=4)
            if r.status_code == 200:
                d = r.json()
                doctor_name = f"{d.get('first_name','')} {d.get('last_name','')}".strip()
                fee = d.get('consultation_price', 0)
    except Exception:
        pass

    texts = {
        'uz': (
            f"✅ <b>Navbatni tasdiqlang:</b>\n\n"
            f"👨‍⚕️ Shifokor: <b>{doctor_name}</b>\n"
            f"📅 Sana: <b>{chosen_date}</b>\n"
            f"🕐 Vaqt: <b>{chosen_time}</b>\n"
            f"💰 Narxi: <b>{int(fee):,} so'm</b>"
        ),
        'ru': (
            f"✅ <b>Подтвердите запись:</b>\n\n"
            f"👨‍⚕️ Врач: <b>{doctor_name}</b>\n"
            f"📅 Дата: <b>{chosen_date}</b>\n"
            f"🕐 Время: <b>{chosen_time}</b>\n"
            f"💰 Стоимость: <b>{int(fee):,} сум</b>"
        ),
        'en': (
            f"✅ <b>Confirm your booking:</b>\n\n"
            f"👨‍⚕️ Doctor: <b>{doctor_name}</b>\n"
            f"📅 Date: <b>{chosen_date}</b>\n"
            f"🕐 Time: <b>{chosen_time}</b>\n"
            f"💰 Fee: <b>{int(fee):,} UZS</b>"
        ),
    }

    btn = {
        'uz': ['✅ Tasdiqlash', '❌ Bekor qilish'],
        'ru': ['✅ Подтвердить', '❌ Отмена'],
        'en': ['✅ Confirm', '❌ Cancel'],
    }
    t = btn.get(lang, btn['uz'])

    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t[0], callback_data='confirm_final')],
        [InlineKeyboardButton(text=t[1], callback_data=f'book_clinic:{clinic_id}')],
    ])
    await callback.message.edit_text(texts.get(lang, texts['uz']), reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data == 'confirm_final')
async def save_appointment(callback: CallbackQuery, state: FSMContext):
    lang = await get_lang(callback.from_user.id)
    data = await state.get_data()

    # Bemorni klinikada ro'yxatdan o'tkazish
    patient = await ensure_patient(callback.from_user, data.get('clinic_id', ''))

    try:
        async with httpx.AsyncClient() as client:
            payload = {
                'clinic': data.get('clinic_id'),
                'doctor': data.get('doctor_id'),
                'patient': patient['id'] if patient else None,
                'date': data.get('chosen_date'),
                'time': data.get('chosen_time'),
            }
            r = await client.post(f"{API}/appointments/", json=payload, timeout=8)

            if r.status_code in (200, 201):
                appt = r.json()
                msgs = {
                    'uz': (
                        f"🎉 <b>Navbat muvaffaqiyatli olindi!</b>\n\n"
                        f"📅 {data.get('chosen_date')} soat {data.get('chosen_time')}\n"
                        f"🆔 Navbat raqami: <code>#{appt.get('id','')[:8]}</code>\n\n"
                        f"⏰ Navbatdan 24 soat va 2 soat oldin eslatma yuboriladi.\n"
                        f"❌ Bekor qilish uchun /cancel dan foydalaning."
                    ),
                    'ru': (
                        f"🎉 <b>Запись успешно создана!</b>\n\n"
                        f"📅 {data.get('chosen_date')} в {data.get('chosen_time')}\n"
                        f"🆔 Номер: <code>#{appt.get('id','')[:8]}</code>\n\n"
                        f"⏰ Напоминания за 24 часа и 2 часа."
                    ),
                    'en': (
                        f"🎉 <b>Appointment booked!</b>\n\n"
                        f"📅 {data.get('chosen_date')} at {data.get('chosen_time')}\n"
                        f"🆔 ID: <code>#{appt.get('id','')[:8]}</code>\n\n"
                        f"⏰ Reminders will be sent 24h and 2h before."
                    ),
                }
                kb = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text='📅 Navbatlarim', callback_data='my_appointments'),
                     InlineKeyboardButton(text='🏠 Menyu', callback_data='main_menu')]
                ])
                await callback.message.edit_text(msgs.get(lang, msgs['uz']), reply_markup=kb)
                await state.clear()
                await callback.answer()
                return
    except Exception:
        pass

    err = {'uz': '❌ Xato yuz berdi. Qayta urinib ko\'ring.',
           'ru': '❌ Ошибка. Попробуйте снова.', 'en': '❌ Error. Please try again.'}
    await callback.answer(err.get(lang, err['uz']), show_alert=True)
