"""
CLinks.uz Bot — Barcha Handler'lar Registratsiyasi
"""
from aiogram import Dispatcher

from .start import router as start_router
from .search import router as search_router
from .booking import router as booking_router
from .my_appointments import router as my_appts_router
from .profile import router as profile_router
from .admin_notify import router as admin_router


def register_all_handlers(dp: Dispatcher):
    dp.include_router(start_router)
    dp.include_router(search_router)
    dp.include_router(booking_router)
    dp.include_router(my_appts_router)
    dp.include_router(profile_router)
    dp.include_router(admin_router)
