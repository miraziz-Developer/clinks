"""
Telegram bildirishnomalar moduli
Bemor Telegram ID bo'lsa — to'g'ridan-to'g'ri xabar yuboradi
"""
import logging
import httpx
from django.conf import settings

logger = logging.getLogger(__name__)


def send_telegram_message(bot_token: str, chat_id: int, text: str, parse_mode='HTML',
                           reply_markup=None) -> dict | None:
    """Telegram API orqali xabar yuborish"""
    if not bot_token or not chat_id:
        return None

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': parse_mode,
    }
    if reply_markup:
        import json
        payload['reply_markup'] = json.dumps(reply_markup)

    try:
        with httpx.Client(timeout=10) as client:
            resp = client.post(url, json=payload)
            if resp.status_code == 200:
                return resp.json()
            else:
                logger.warning(f"Telegram API error: {resp.status_code} — {resp.text}")
    except Exception as e:
        logger.error(f"Telegram send error: {e}")
    return None


def get_clinic_bot_token(clinic) -> str | None:
    """Klinikaning bot tokenini olish — Central bot fallback bilan"""
    try:
        if hasattr(clinic, 'telegram_bot') and clinic.telegram_bot.is_active:
            return clinic.telegram_bot.token
    except Exception:
        pass
    
    # Central bot token setting'dan olinadi
    from django.conf import settings
    return getattr(settings, 'CENTRAL_BOT_TOKEN', None)


def send_appointment_confirmation(appointment):
    """Navbat tasdiqlash xabari"""
    patient = appointment.patient
    if not patient.telegram_id:
        return

    token = get_clinic_bot_token(appointment.clinic)
    if not token:
        return

    text = (
        f"✅ <b>Navbat tasdiqlandi!</b>\n\n"
        f"🏥 <b>Klinika:</b> {appointment.clinic.name}\n"
        f"👨‍⚕️ <b>Shifokor:</b> Dr. {appointment.doctor.full_name}\n"
        f"📅 <b>Sana:</b> {appointment.date.strftime('%d.%m.%Y')}\n"
        f"🕐 <b>Vaqt:</b> {appointment.time.strftime('%H:%M')}\n"
        f"📍 <b>Manzil:</b> {appointment.clinic.address}\n\n"
        f"ℹ️ Bekor qilish uchun /cancel_{appointment.id} buyrug'ini yuboring"
    )
    result = send_telegram_message(token, patient.telegram_id, text)
    if result:
        msg_id = result.get('result', {}).get('message_id')
        if msg_id:
            appointment.telegram_message_id = msg_id
            appointment.save(update_fields=['telegram_message_id'])


def send_appointment_cancellation(appointment):
    """Navbat bekor qilish xabari"""
    patient = appointment.patient
    if not patient.telegram_id:
        return

    token = get_clinic_bot_token(appointment.clinic)
    if not token:
        return

    reason_text = f"\n📝 <b>Sabab:</b> {appointment.cancellation_reason}" if appointment.cancellation_reason else ""

    text = (
        f"❌ <b>Navbat bekor qilindi</b>\n\n"
        f"🏥 <b>Klinika:</b> {appointment.clinic.name}\n"
        f"👨‍⚕️ <b>Shifokor:</b> Dr. {appointment.doctor.full_name}\n"
        f"📅 <b>Sana:</b> {appointment.date.strftime('%d.%m.%Y')}\n"
        f"🕐 <b>Vaqt:</b> {appointment.time.strftime('%H:%M')}"
        f"{reason_text}\n\n"
        f"🔄 Yangi navbat olish uchun /start buyrug'ini yuboring"
    )
    send_telegram_message(token, patient.telegram_id, text)


def send_appointment_reminder(appointment):
    """Navbat eslatmasi (24 soat oldin)"""
    patient = appointment.patient
    if not patient.telegram_id:
        return

    token = get_clinic_bot_token(appointment.clinic)
    if not token:
        return

    text = (
        f"⏰ <b>Eslatma!</b>\n\n"
        f"Ertaga sizning navbatingiz bor:\n\n"
        f"🏥 <b>Klinika:</b> {appointment.clinic.name}\n"
        f"👨‍⚕️ <b>Shifokor:</b> Dr. {appointment.doctor.full_name}\n"
        f"📅 <b>Sana:</b> {appointment.date.strftime('%d.%m.%Y')}\n"
        f"🕐 <b>Vaqt:</b> {appointment.time.strftime('%H:%M')}\n"
        f"📍 <b>Manzil:</b> {appointment.clinic.address}\n\n"
        f"📞 Klinika: {appointment.clinic.phone}"
    )

    result = send_telegram_message(token, patient.telegram_id, text)
    if result:
        appointment.reminder_sent = True
        appointment.save(update_fields=['reminder_sent'])


def send_new_appointment_to_clinic(appointment):
    """Yangi navbat haqida klinikaga xabar"""
    try:
        clinic = appointment.clinic
        # Admin paneli uchun super bot ishlatish
        super_token = settings.SUPER_BOT_TOKEN
        # Klinikaning adminiga xabar yuborish
        owner = clinic.owner
        if not owner.telegram_id or not super_token:
            return

        text = (
            f"🆕 <b>Yangi navbat!</b>\n\n"
            f"👤 <b>Bemor:</b> {appointment.patient.full_name}\n"
            f"📞 <b>Tel:</b> {appointment.patient.phone}\n"
            f"👨‍⚕️ <b>Shifokor:</b> Dr. {appointment.doctor.full_name}\n"
            f"📅 <b>Sana:</b> {appointment.date.strftime('%d.%m.%Y')}\n"
            f"🕐 <b>Vaqt:</b> {appointment.time.strftime('%H:%M')}\n"
            f"📝 <b>Shikoyat:</b> {appointment.complaint or 'Ko\'rsatilmagan'}"
        )
        send_telegram_message(super_token, owner.telegram_id, text)
    except Exception as e:
        logger.error(f"Clinic notification error: {e}")
