# 🏥 CLinks.uz — Klinika SaaS Platformasi

O'zbekistondagi xususiy klinikalar uchun to'liq boshqaruv tizimi.

## Texnologiyalar
- **Backend**: Django 4.2 + DRF
- **Bot**: python-telegram-bot 20.x
- **Database**: PostgreSQL 15
- **Cache**: Redis
- **Deploy**: Docker + Docker Compose
- **Server**: Hetzner VPS

## Loyiha Strukturasi
```
CLinks_uz/
├── backend/          # Django loyihasi
│   ├── config/       # Asosiy sozlamalar
│   ├── apps/
│   │   ├── clinics/  # Klinika modeli
│   │   ├── patients/ # Bemor modeli
│   │   ├── appointments/ # Navbat modeli
│   │   ├── doctors/  # Shifokor modeli
│   │   ├── payments/ # To'lov (hozircha o'chirilgan)
│   │   └── bots/     # Telegram bot boshqaruvi
│   └── templates/    # Admin panel shablonlar
├── bot/              # Telegram bot
├── nginx/            # Nginx konfiguratsiya
└── docker-compose.yml
```

## Ishga tushirish
```bash
cp .env.example .env
# .env faylini to'ldiring
docker-compose up -d
```

## Statuslar
- [x] MVP qurilmoqda
- [ ] Telegram bot
- [ ] Admin panel
- [ ] To'lov tizimi (Payme/Click)
