"""Mening navbatlarim handler"""
import httpx
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()
API = __import__('os').getenv('DJANGO_API_URL', 'http://backend:8000/api/v1')


async def get_lang(tid): 
    try:
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{API}/patients/global/{tid}/", timeout=4)
            if r.status_code==200: return r.json().get('telegram_language','uz')
    except: pass
    return 'uz'


@router.callback_query(F.data == 'my_appointments')
async def my_appointments(callback: CallbackQuery):
    lang = await get_lang(callback.from_user.id)
    tid = callback.from_user.id

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{API}/appointments/?telegram_id={tid}&ordering=-appointment_date", timeout=6)
            appts = (r.json().get('results') or r.json()) if r.status_code==200 else []
    except:
        appts = []

    if not appts:
        msgs = {
            'uz': "📅 <b>Mening navbatlarim</b>\n\nSizda hali navbat yo'q.\n\n/start → Klinika topish",
            'ru': "📅 <b>Мои записи</b>\n\nУ вас нет записей.\n\n/start → Найти клинику",
            'en': "📅 <b>My Appointments</b>\n\nNo appointments yet.\n\n/start → Find clinic",
        }
        await callback.message.edit_text(msgs.get(lang,msgs['uz']),
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text='🏠',callback_data='main_menu')]]))
        await callback.answer(); return

    status_emoji = {'pending':'⏳','confirmed':'✅','completed':'🏁','cancelled':'❌','no_show':'🚫'}
    rows = []
    for a in appts[:10]:
        emoji = status_emoji.get(a.get('status',''),'📅')
        label = f"{emoji} {a.get('appointment_date','?')} {a.get('appointment_time','?')} — {a.get('doctor_name','?')}"
        rows.append([InlineKeyboardButton(text=label, callback_data=f"appt_detail:{a['id']}")])

    rows.append([InlineKeyboardButton(text='🏠',callback_data='main_menu')])
    titles = {'uz':f"📅 <b>Navbatlarim ({len(appts)}):</b>",'ru':f"📅 <b>Мои записи ({len(appts)}):</b>",'en':f"📅 <b>My Appointments ({len(appts)}):</b>"}
    await callback.message.edit_text(titles.get(lang,titles['uz']), reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await callback.answer()


@router.callback_query(F.data.startswith('appt_detail:'))
async def appt_detail(callback: CallbackQuery):
    appt_id = callback.data.split(':')[1]
    lang = await get_lang(callback.from_user.id)

    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{API}/appointments/{appt_id}/", timeout=5)
            a = r.json() if r.status_code==200 else {}
    except: a = {}

    status_map = {
        'uz':{'pending':'⏳ Kutilmoqda','confirmed':'✅ Tasdiqlangan','completed':'🏁 Tugallangan','cancelled':'❌ Bekor qilingan'},
        'ru':{'pending':'⏳ Ожидание','confirmed':'✅ Подтверждено','completed':'🏁 Завершено','cancelled':'❌ Отменено'},
        'en':{'pending':'⏳ Pending','confirmed':'✅ Confirmed','completed':'🏁 Completed','cancelled':'❌ Cancelled'},
    }

    status = a.get('status','')
    status_text = status_map.get(lang,status_map['uz']).get(status,'❓')
    paid = a.get('is_paid', False)
    
    paid_uz = "✅ To'langan" if paid else "⏳ To'lanmagan"

    texts = {
        'uz': (f"📋 <b>Navbat tafsilotlari</b>\n\n"
               f"🏥 {a.get('clinic_name','—')}\n"
               f"👨‍⚕️ {a.get('doctor_name','—')}\n"
               f"📅 {a.get('date','—')}\n"
               f"🕐 {a.get('time','—')}\n"
               f"📊 {status_text}\n"
               f"💳 {paid_uz}"),
        'ru': (f"📋 <b>Детали записи</b>\n\n"
               f"🏥 {a.get('clinic_name','—')}\n"
               f"👨‍⚕️ {a.get('doctor_name','—')}\n"
               f"📅 {a.get('date','—')}\n"
               f"🕐 {a.get('time','—')}\n"
               f"📊 {status_text}\n"
               f"💳 {'✅ Оплачено' if paid else '⏳ Не оплачено'}"),
        'en': (f"📋 <b>Appointment Details</b>\n\n"
               f"🏥 {a.get('clinic_name','—')}\n"
               f"👨‍⚕️ {a.get('doctor_name','—')}\n"
               f"📅 {a.get('date','—')}\n"
               f"🕐 {a.get('time','—')}\n"
               f"📊 {status_text}\n"
               f"💳 {'✅ Paid' if paid else '⏳ Unpaid'}"),
    }

    rows = []
    if status in ('pending','confirmed'):
        cancel_btn = {'uz':'❌ Bekor qilish','ru':'❌ Отменить','en':'❌ Cancel'}
        rows.append([InlineKeyboardButton(text=cancel_btn.get(lang,cancel_btn['uz']),
                                          callback_data=f'cancel_appt:{appt_id}')])
    rows.append([InlineKeyboardButton(text='🔙', callback_data='my_appointments')])
    await callback.message.edit_text(texts.get(lang,texts['uz']), reply_markup=InlineKeyboardMarkup(inline_keyboard=rows))
    await callback.answer()


@router.callback_query(F.data.startswith('cancel_appt:'))
async def cancel_appointment(callback: CallbackQuery):
    appt_id = callback.data.split(':')[1]
    lang = await get_lang(callback.from_user.id)

    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(f"{API}/appointments/{appt_id}/update_status/",
                                  json={'status':'cancelled'}, timeout=5)
            ok = r.status_code in (200,204)
    except: ok = False

    msgs = {
        True: {'uz':'✅ Navbat bekor qilindi.','ru':'✅ Запись отменена.','en':'✅ Appointment cancelled.'},
        False: {'uz':'❌ Bekor qilib bo\'lmadi.','ru':'❌ Не удалось отменить.','en':'❌ Could not cancel.'},
    }
    await callback.answer(msgs[ok].get(lang, msgs[ok]['uz']), show_alert=True)
    if ok: await my_appointments(callback)
