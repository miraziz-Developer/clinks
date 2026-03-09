"""
CLinks.uz — Central Telegram Bot
Barcha klinikalar uchun bitta bot.
Bemor klinikani qidiradi, navbat oladi.
"""
import os
import asyncio
import logging
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(name)s] %(levelname)s: %(message)s'
)
logger = logging.getLogger('clinks_bot')

BOT_TOKEN = os.getenv('CENTRAL_BOT_TOKEN', '')
DJANGO_API = os.getenv('DJANGO_API_URL', 'http://backend:8000/api/v1')
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')  # https://your-domain.com


async def wait_for_backend():
    """Backend tayyor bo'lgucha kutish"""
    import httpx
    for i in range(30):
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{DJANGO_API}/health/", timeout=5)
                if r.status_code < 500:
                    logger.info("✅ Backend tayyor!")
                    return True
        except Exception:
            pass
        logger.info(f"⏳ Backend kutilmoqda... ({i+1}/30)")
        await asyncio.sleep(5)
    logger.warning("⚠️ Backend 150s ichida javob bermadi")
    return False


async def main():
    if not BOT_TOKEN:
        logger.error("❌ CENTRAL_BOT_TOKEN .env da topilmadi!")
        logger.info("📋 Bot token olish uchun:")
        logger.info("   1. Telegram: @BotFather")
        logger.info("   2. /newbot → nom bering")
        logger.info("   3. Tokenni .env ga qo'shing: CENTRAL_BOT_TOKEN=xxx")
        # Servisni tirik saqlash
        while True:
            await asyncio.sleep(60)

    await wait_for_backend()

    try:
        from aiogram import Bot, Dispatcher
        from aiogram.enums import ParseMode
        from aiogram.client.default import DefaultBotProperties

        from handlers import register_all_handlers

        bot = Bot(
            token=BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        dp = Dispatcher()
        register_all_handlers(dp)

        bot_info = await bot.get_me()
        logger.info(f"🤖 Bot: @{bot_info.username} ({bot_info.full_name})")
        logger.info(f"🔗 Deep link: t.me/{bot_info.username}?start=clinic_TOKEN")

        if WEBHOOK_URL:
            # Production: webhook
            webhook_path = f"/webhook/{BOT_TOKEN}"
            await bot.set_webhook(f"{WEBHOOK_URL}{webhook_path}")
            logger.info(f"🌐 Webhook: {WEBHOOK_URL}{webhook_path}")
            # Webhook mode — aiohttp server boshlanadi
            from webhook_server import start_webhook_server
            await start_webhook_server(bot, dp, webhook_path)
        else:
            # Development: polling
            logger.info("📡 Polling rejimida ishlamoqda...")
            await bot.delete_webhook(drop_pending_updates=True)
            await dp.start_polling(bot)

    except ImportError:
        logger.error("❌ aiogram o'rnatilmagan! pip install aiogram")
        while True:
            await asyncio.sleep(60)
    except Exception as e:
        logger.error(f"❌ Bot xatosi: {e}")
        raise


if __name__ == '__main__':
    asyncio.run(main())
