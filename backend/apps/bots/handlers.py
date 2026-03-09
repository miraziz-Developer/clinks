"""
Telegram Bot Handler — FSM (Finite State Machine) asosida

Holatlar:
- START → Tilni tanlash
- LANGUAGE_SELECTED → Telefon raqam so'raladi
- PHONE_RECEIVED → Asosiy menyu
- BOOKING:
  - DOCTOR_SELECT
  - DATE_SELECT
  - TIME_SELECT
  - CONFIRM
"""
import logging
from apps.bots.models import TelegramBot, BotUser
from apps.bots.notifications import send_telegram_message

logger = logging.getLogger(__name__)

# Holat konstantalari
class States:
    IDLE = ''
    LANGUAGE = 'language'
    PHONE = 'phone'
    MAIN_MENU = 'main_menu'
    BOOKING_DOCTOR = 'booking_doctor'
    BOOKING_DATE = 'booking_date'
    BOOKING_TIME = 'booking_time'
    BOOKING_CONFIRM = 'booking_confirm'
    BOOKING_COMPLAINT = 'booking_complaint'
    CANCEL_APPOINTMENT = 'cancel_appointment'


# Matnlar (uz/ru)
TEXTS = {
    'uz': {
        'welcome': "🏥 <b>{clinic_name}</b>\n\nAssalomu alaykum! Klinikamizga xush kelibsiz.\n\nTilni tanlang:",
        'choose_language': "🌐 Tilni tanlang:",
        'ask_phone': "📱 Telefon raqamingizni yuboring:\n(Kontakt yuborish tugmasini bosing)",
        'main_menu': "🏠 <b>Asosiy menyu</b>\n\nQuyidagilardan birini tanlang:",
        'choose_doctor': "👨‍⚕️ <b>Shifokorni tanlang:</b>",
        'choose_date': "📅 <b>Sanani kiriting:</b>\n(Masalan: {example_date})",
        'choose_time': "🕐 <b>Vaqtni tanlang:</b>",
        'confirm': (
            "✅ <b>Navbatni tasdiqlang:</b>\n\n"
            "👨‍⚕️ Shifokor: {doctor}\n"
            "📅 Sana: {date}\n"
            "🕐 Vaqt: {time}\n\n"
            "Tasdiqlaysizmi?"
        ),
        'ask_complaint': "📝 Shikoyatingizni kiriting (ixtiyoriy, o'tkazib yuborish uchun /skip):",
        'success': (
            "🎉 <b>Navbat muvaffaqiyatli olindi!</b>\n\n"
            "📅 {date} kuni soat {time} da\n"
            "👨‍⚕️ Dr. {doctor}\n\n"
            "📍 {clinic_name}\n"
            "📞 {clinic_phone}\n\n"
            "⏰ 24 soat oldin eslatma yuboriladi."
        ),
        'no_slots': "😔 Bu kunda bo'sh vaqt yo'q. Boshqa kun tanlang.",
        'invalid_date': "⚠️ Sana noto'g'ri. Iltimos, YYYY-MM-DD formatida kiriting.",
        'cancelled': "✅ Navbat bekor qilindi.",
        'my_appointments': "📋 <b>Mening navbatlarim:</b>",
        'no_appointments': "📭 Hozircha navbatingiz yo'q.",
        'help': "ℹ️ <b>Yordam</b>\n\n/start — Boshlash\n/book — Navbat olish\n/appointments — Navbatlarim\n/cancel — Navbatni bekor qilish",
        'error': "⚠️ Xatolik yuz berdi. Qayta urinib ko'ring: /start",
    },
    'ru': {
        'welcome': "🏥 <b>{clinic_name}</b>\n\nДобро пожаловать в нашу клинику!\n\nВыберите язык:",
        'ask_phone': "📱 Отправьте номер телефона:\n(Нажмите кнопку 'Поделиться контактом')",
        'main_menu': "🏠 <b>Главное меню</b>\n\nВыберите действие:",
        'choose_doctor': "👨‍⚕️ <b>Выберите врача:</b>",
        'choose_date': "📅 <b>Введите дату:</b>\n(Например: {example_date})",
        'choose_time': "🕐 <b>Выберите время:</b>",
        'no_slots': "😔 Нет свободного времени на этот день. Выберите другой день.",
        'success': (
            "🎉 <b>Запись успешно создана!</b>\n\n"
            "📅 {date} в {time}\n"
            "👨‍⚕️ Др. {doctor}\n\n"
            "📍 {clinic_name}\n"
            "📞 {clinic_phone}"
        ),
        'error': "⚠️ Произошла ошибка. Попробуйте снова: /start",
    }
}


def get_or_create_bot_user(bot: TelegramBot, tg_user: dict) -> BotUser:
    """Bot foydalanuvchisini olish yoki yaratish"""
    telegram_id = tg_user['id']
    bot_user, created = BotUser.objects.get_or_create(
        bot=bot,
        telegram_id=telegram_id,
        defaults={
            'first_name': tg_user.get('first_name', ''),
            'last_name': tg_user.get('last_name', ''),
            'telegram_username': tg_user.get('username', ''),
            'language': 'uz',
        }
    )
    if not created:
        # Ma'lumotlarni yangilash
        bot_user.first_name = tg_user.get('first_name', bot_user.first_name)
        bot_user.telegram_username = tg_user.get('username', bot_user.telegram_username)
        bot_user.save(update_fields=['first_name', 'telegram_username'])
    return bot_user


def t(bot_user: BotUser, key: str, **kwargs) -> str:
    """Matn tarjimasi"""
    lang = bot_user.language or 'uz'
    texts = TEXTS.get(lang, TEXTS['uz'])
    text = texts.get(key, TEXTS['uz'].get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text


def send(bot: TelegramBot, chat_id: int, text: str, keyboard=None) -> dict | None:
    """Xabar yuborish"""
    markup = None
    if keyboard:
        markup = {'inline_keyboard': keyboard}
    return send_telegram_message(bot.token, chat_id, text, reply_markup=markup)


def send_reply_keyboard(bot: TelegramBot, chat_id: int, text: str, buttons: list):
    """Reply keyboard bilan xabar yuborish"""
    markup = {
        'keyboard': buttons,
        'resize_keyboard': True,
        'one_time_keyboard': True,
    }
    return send_telegram_message(bot.token, chat_id, text, reply_markup=markup)


def handle_update(bot: TelegramBot, data: dict):
    """Barcha update'larni boshqarish"""
    try:
        if 'message' in data:
            handle_message(bot, data['message'])
        elif 'callback_query' in data:
            handle_callback(bot, data['callback_query'])
    except Exception as e:
        logger.error(f"Update handling error: {e}", exc_info=True)


def handle_message(bot: TelegramBot, message: dict):
    """Xabar handleri"""
    tg_user = message.get('from', {})
    chat_id = message.get('chat', {}).get('id')
    text = message.get('text', '')
    contact = message.get('contact')

    bot_user = get_or_create_bot_user(bot, tg_user)
    state = bot_user.state

    # /start
    if text == '/start' or text.startswith('/start'):
        handle_start(bot, bot_user, chat_id)
        return

    # /book
    if text == '/book':
        handle_book_start(bot, bot_user, chat_id)
        return

    # /appointments
    if text == '/appointments' or text == 'Navbatlarim 📋' or text == 'Мои записи 📋':
        handle_my_appointments(bot, bot_user, chat_id)
        return

    # /help
    if text == '/help':
        send(bot, chat_id, t(bot_user, 'help'))
        return

    # Holat bo'yicha qayta ishlash
    if state == States.LANGUAGE:
        handle_language_select(bot, bot_user, chat_id, text)
    elif state == States.PHONE:
        handle_phone(bot, bot_user, chat_id, text, contact)
    elif state == States.BOOKING_DATE:
        handle_date_input(bot, bot_user, chat_id, text)
    elif state == States.BOOKING_COMPLAINT:
        handle_complaint_input(bot, bot_user, chat_id, text)
    else:
        # Asosiy menyu tugmalari
        if text in ['Navbat olish 🗓', 'Записаться 🗓']:
            handle_book_start(bot, bot_user, chat_id)
        elif text in ['Navbatlarim 📋', 'Мои записи 📋']:
            handle_my_appointments(bot, bot_user, chat_id)
        elif text in ['Klinika haqida ℹ️', 'О клинике ℹ️']:
            handle_clinic_info(bot, bot_user, chat_id)
        else:
            send_main_menu(bot, bot_user, chat_id)


def handle_callback(bot: TelegramBot, callback: dict):
    """Inline keyboard callback handleri"""
    tg_user = callback.get('from', {})
    chat_id = callback.get('message', {}).get('chat', {}).get('id')
    data = callback.get('data', '')
    callback_id = callback.get('id')

    bot_user = get_or_create_bot_user(bot, tg_user)

    # Callback'ni tasdiqlash
    answer_callback(bot, callback_id)

    if data.startswith('doctor:'):
        doctor_id = data.split(':')[1]
        handle_doctor_selected(bot, bot_user, chat_id, doctor_id)

    elif data.startswith('time:'):
        time_str = data.split(':')[1]
        handle_time_selected(bot, bot_user, chat_id, time_str)

    elif data == 'confirm_yes':
        handle_booking_confirm(bot, bot_user, chat_id)

    elif data == 'confirm_no':
        reset_state(bot_user)
        send_main_menu(bot, bot_user, chat_id)

    elif data.startswith('cancel:'):
        appointment_id = data.split(':')[1]
        handle_cancel_appointment(bot, bot_user, chat_id, appointment_id)

    elif data.startswith('lang:'):
        lang = data.split(':')[1]
        bot_user.language = lang
        bot_user.state = States.PHONE
        bot_user.save()
        send_phone_request(bot, bot_user, chat_id)


def answer_callback(bot: TelegramBot, callback_id: str):
    """Callback javob berish"""
    import httpx
    try:
        httpx.post(
            f"https://api.telegram.org/bot{bot.token}/answerCallbackQuery",
            json={'callback_query_id': callback_id},
            timeout=5
        )
    except Exception:
        pass


def handle_start(bot: TelegramBot, bot_user: BotUser, chat_id: int):
    """Start handleri"""
    text = t(bot_user, 'welcome', clinic_name=bot.clinic.name)
    keyboard = [
        [
            {'text': "🇺🇿 O'zbek", 'callback_data': 'lang:uz'},
            {'text': '🇷🇺 Русский', 'callback_data': 'lang:ru'},
        ]
    ]
    send(bot, chat_id, text, keyboard)
    bot_user.state = States.LANGUAGE
    bot_user.save()


def handle_language_select(bot: TelegramBot, bot_user: BotUser, chat_id: int, text: str):
    lang = 'uz' if 'O\'zbek' in text or 'uz' in text else 'ru'
    bot_user.language = lang
    bot_user.state = States.PHONE
    bot_user.save()
    send_phone_request(bot, bot_user, chat_id)


def send_phone_request(bot: TelegramBot, bot_user: BotUser, chat_id: int):
    """Telefon raqam so'rash"""
    keyboard = {
        'keyboard': [[{'text': '📱 Raqamni yuborish', 'request_contact': True}]],
        'resize_keyboard': True,
        'one_time_keyboard': True,
    }
    send_telegram_message(
        bot.token, chat_id,
        t(bot_user, 'ask_phone'),
        reply_markup=keyboard
    )


def handle_phone(bot: TelegramBot, bot_user: BotUser, chat_id: int, text: str, contact: dict = None):
    """Telefon raqamni qabul qilish"""
    phone = None
    if contact:
        phone = contact.get('phone_number', '')
        # Bemorni tekshirish/yaratish
        bot_user.phone = phone
        bot_user.state = States.MAIN_MENU
        bot_user.save()
        # Patient yaratish
        create_or_link_patient(bot, bot_user)
        send_main_menu(bot, bot_user, chat_id)
    elif text and (text.startswith('+') or text.isdigit()):
        phone = text
        bot_user.phone = phone
        bot_user.state = States.MAIN_MENU
        bot_user.save()
        create_or_link_patient(bot, bot_user)
        send_main_menu(bot, bot_user, chat_id)
    else:
        send_phone_request(bot, bot_user, chat_id)


def create_or_link_patient(bot: TelegramBot, bot_user: BotUser):
    """Bot foydalanuvchisini bemor bilan bog'lash"""
    from apps.patients.models import Patient
    try:
        patient, created = Patient.objects.get_or_create(
            clinic=bot.clinic,
            phone=bot_user.phone,
            defaults={
                'first_name': bot_user.first_name,
                'last_name': bot_user.last_name,
                'telegram_id': bot_user.telegram_id,
                'telegram_username': bot_user.telegram_username,
            }
        )
        if not created and not patient.telegram_id:
            patient.telegram_id = bot_user.telegram_id
            patient.save()
        bot_user.patient = patient
        bot_user.save()
    except Exception as e:
        logger.error(f"Patient create error: {e}")


def send_main_menu(bot: TelegramBot, bot_user: BotUser, chat_id: int):
    """Asosiy menyu"""
    if bot_user.language == 'ru':
        buttons = [
            ['Записаться 🗓', 'Мои записи 📋'],
            ['О клинике ℹ️']
        ]
        text = t(bot_user, 'main_menu')
    else:
        buttons = [
            ['Navbat olish 🗓', 'Navbatlarim 📋'],
            ['Klinika haqida ℹ️']
        ]
        text = t(bot_user, 'main_menu')

    send_reply_keyboard(bot, chat_id, text, buttons)


def handle_book_start(bot: TelegramBot, bot_user: BotUser, chat_id: int):
    """Navbat olish boshlash — shifokor tanlash"""
    doctors = bot.clinic.doctors.filter(is_active=True)
    if not doctors.exists():
        send(bot, chat_id, "😔 Hozircha shifokorlar mavjud emas.")
        return

    keyboard = []
    for doc in doctors:
        price_text = f" — {int(doc.consultation_price):,} so'm" if doc.consultation_price else ""
        keyboard.append([{
            'text': f"👨‍⚕️ {doc.full_name} ({doc.specialty}){price_text}",
            'callback_data': f"doctor:{doc.id}"
        }])

    send(bot, chat_id, t(bot_user, 'choose_doctor'), keyboard)
    bot_user.state = States.BOOKING_DOCTOR
    bot_user.state_data = {}
    bot_user.save()


def handle_doctor_selected(bot: TelegramBot, bot_user: BotUser, chat_id: int, doctor_id: str):
    """Shifokor tanlandi — sana so'rash"""
    from apps.doctors.models import Doctor
    try:
        doctor = Doctor.objects.get(id=doctor_id, clinic=bot.clinic, is_active=True)
    except Doctor.DoesNotExist:
        send(bot, chat_id, "⚠️ Shifokor topilmadi.")
        return

    bot_user.state_data['doctor_id'] = str(doctor.id)
    bot_user.state_data['doctor_name'] = doctor.full_name
    bot_user.state = States.BOOKING_DATE
    bot_user.save()

    from datetime import date
    example = date.today().strftime('%Y-%m-%d')
    send(bot, chat_id, t(bot_user, 'choose_date', example_date=example))


def handle_date_input(bot: TelegramBot, bot_user: BotUser, chat_id: int, text: str):
    """Sana kiritildi — bo'sh vaqtlarni ko'rsatish"""
    from datetime import date
    try:
        target_date = date.fromisoformat(text.strip())
    except ValueError:
        send(bot, chat_id, t(bot_user, 'invalid_date'))
        return

    if target_date < date.today():
        send(bot, chat_id, "⚠️ O'tgan sanani tanlab bo'lmaydi. Bugundan keyin sana kiriting.")
        return

    from apps.doctors.models import Doctor
    doctor_id = bot_user.state_data.get('doctor_id')
    try:
        doctor = Doctor.objects.get(id=doctor_id)
    except Doctor.DoesNotExist:
        send(bot, chat_id, t(bot_user, 'error'))
        return

    slots = doctor.get_available_slots(target_date)
    if not slots:
        send(bot, chat_id, t(bot_user, 'no_slots'))
        return

    bot_user.state_data['date'] = str(target_date)
    bot_user.state = States.BOOKING_TIME
    bot_user.save()

    # Vaqtlarni inline keyboard sifatida ko'rsatish (3 ustun)
    keyboard = []
    row = []
    for i, slot in enumerate(slots[:24]):  # Max 24 ta slot
        row.append({
            'text': slot.strftime('%H:%M'),
            'callback_data': f"time:{slot.strftime('%H:%M')}"
        })
        if len(row) == 3:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    send(bot, chat_id, t(bot_user, 'choose_time'), keyboard)


def handle_time_selected(bot: TelegramBot, bot_user: BotUser, chat_id: int, time_str: str):
    """Vaqt tanlandi — tasdiqlash"""
    bot_user.state_data['time'] = time_str
    bot_user.state = States.BOOKING_COMPLAINT
    bot_user.save()

    send(bot, chat_id, t(bot_user, 'ask_complaint'))


def handle_complaint_input(bot: TelegramBot, bot_user: BotUser, chat_id: int, text: str):
    """Shikoyat kiritildi — yakuniy tasdiqlash"""
    if text != '/skip':
        bot_user.state_data['complaint'] = text
    bot_user.state = States.BOOKING_CONFIRM
    bot_user.save()

    data = bot_user.state_data
    keyboard = [
        [
            {'text': '✅ Tasdiqlash', 'callback_data': 'confirm_yes'},
            {'text': '❌ Bekor qilish', 'callback_data': 'confirm_no'},
        ]
    ]
    send(
        bot, chat_id,
        t(
            bot_user, 'confirm',
            doctor=data.get('doctor_name', ''),
            date=data.get('date', ''),
            time=data.get('time', ''),
        ),
        keyboard
    )


def handle_booking_confirm(bot: TelegramBot, bot_user: BotUser, chat_id: int):
    """Navbatni yaratish"""
    from apps.appointments.models import Appointment
    from apps.doctors.models import Doctor
    from datetime import date, time as dtime

    data = bot_user.state_data
    patient = bot_user.patient

    if not patient:
        create_or_link_patient(bot, bot_user)
        patient = bot_user.patient

    if not patient:
        send(bot, chat_id, t(bot_user, 'error'))
        return

    try:
        doctor = Doctor.objects.get(id=data['doctor_id'])
        target_date = date.fromisoformat(data['date'])
        time_parts = data['time'].split(':')
        target_time = dtime(int(time_parts[0]), int(time_parts[1]))

        appointment = Appointment.objects.create(
            clinic=bot.clinic,
            doctor=doctor,
            patient=patient,
            date=target_date,
            time=target_time,
            complaint=data.get('complaint', ''),
            duration=bot.clinic.appointment_duration,
        )

        # Bot statistikasini yangilash
        bot.total_appointments_via_bot += 1
        bot.save()

        # Klinikaga xabar berish
        from apps.bots.notifications import send_new_appointment_to_clinic
        send_new_appointment_to_clinic(appointment)

        reset_state(bot_user)

        send(
            bot, chat_id,
            t(
                bot_user, 'success',
                date=target_date.strftime('%d.%m.%Y'),
                time=target_time.strftime('%H:%M'),
                doctor=doctor.full_name,
                clinic_name=bot.clinic.name,
                clinic_phone=bot.clinic.phone,
            )
        )
        send_main_menu(bot, bot_user, chat_id)

    except Exception as e:
        logger.error(f"Booking error: {e}", exc_info=True)
        reset_state(bot_user)
        if 'unique' in str(e).lower():
            send(bot, chat_id, "⚠️ Bu vaqt allaqachon band. Boshqa vaqt tanlang.")
            handle_book_start(bot, bot_user, chat_id)
        else:
            send(bot, chat_id, t(bot_user, 'error'))


def handle_my_appointments(bot: TelegramBot, bot_user: BotUser, chat_id: int):
    """Bemorning navbatlari"""
    from apps.appointments.models import Appointment
    from django.utils import timezone

    patient = bot_user.patient
    if not patient:
        send(bot, chat_id, t(bot_user, 'no_appointments'))
        return

    appointments = Appointment.objects.filter(
        patient=patient,
        date__gte=timezone.now().date(),
        status__in=['pending', 'confirmed']
    ).order_by('date', 'time')[:5]

    if not appointments.exists():
        send(bot, chat_id, t(bot_user, 'no_appointments'))
        return

    text = t(bot_user, 'my_appointments') + '\n\n'
    keyboard = []
    for appt in appointments:
        text += (
            f"📅 {appt.date.strftime('%d.%m.%Y')} — {appt.time.strftime('%H:%M')}\n"
            f"👨‍⚕️ Dr. {appt.doctor.full_name}\n"
            f"📌 Status: {appt.get_status_display()}\n\n"
        )
        keyboard.append([{
            'text': f"❌ Bekor qilish ({appt.date.strftime('%d.%m')} {appt.time.strftime('%H:%M')})",
            'callback_data': f"cancel:{appt.id}"
        }])

    send(bot, chat_id, text, keyboard)


def handle_cancel_appointment(bot: TelegramBot, bot_user: BotUser, chat_id: int, appointment_id: str):
    """Navbatni bekor qilish"""
    from apps.appointments.models import Appointment

    try:
        appointment = Appointment.objects.get(
            id=appointment_id,
            patient=bot_user.patient,
            status__in=['pending', 'confirmed']
        )
        appointment.cancel(reason='Bemor tomonidan bekor qilindi', cancelled_by='patient')
        send(bot, chat_id, t(bot_user, 'cancelled'))
        send_main_menu(bot, bot_user, chat_id)
    except Appointment.DoesNotExist:
        send(bot, chat_id, "⚠️ Navbat topilmadi yoki allaqachon bekor qilingan.")


def handle_clinic_info(bot: TelegramBot, bot_user: BotUser, chat_id: int):
    """Klinika haqida ma'lumot"""
    clinic = bot.clinic
    text = (
        f"🏥 <b>{clinic.name}</b>\n\n"
        f"📍 {clinic.address}\n"
        f"📞 {clinic.phone}\n"
    )
    if clinic.phone2:
        text += f"📞 {clinic.phone2}\n"
    if clinic.email:
        text += f"📧 {clinic.email}\n"

    text += f"\n⏰ Ish vaqti: {clinic.work_start.strftime('%H:%M')} — {clinic.work_end.strftime('%H:%M')}"

    working_days = clinic.get_working_days_display()
    if working_days:
        text += f"\n📅 Ish kunlari: {', '.join(working_days)}"

    send(bot, chat_id, text)


def reset_state(bot_user: BotUser):
    """Holatni tozalash"""
    bot_user.state = States.MAIN_MENU
    bot_user.state_data = {}
    bot_user.save()
