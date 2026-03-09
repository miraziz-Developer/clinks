# 🏥 CLinks.uz — Clinic SaaS Platform

A complete management system for private clinics in Uzbekistan.

## 🛠 Tech Stack
- **Backend**: Django 4.2 + Django REST Framework
- **Bot**: python-telegram-bot 20.x
- **Database**: PostgreSQL 15
- **Cache**: Redis
- **Deploy**: Docker + Docker Compose
- **Server**: Hetzner VPS

## 📁 Project Structure
```
CLinks_uz/
├── backend/              # Django project
│   ├── config/           # Core settings
│   ├── apps/
│   │   ├── clinics/      # Clinic model
│   │   ├── patients/     # Patient model
│   │   ├── appointments/ # Appointment model
│   │   ├── doctors/      # Doctor model
│   │   ├── payments/     # Payments (disabled for now)
│   │   └── bots/         # Telegram bot management
│   └── templates/        # Admin panel templates
├── bot/                  # Telegram bot
├── nginx/                # Nginx configuration
└── docker-compose.yml
```

## 🚀 Getting Started
```bash
cp .env.example .env
# Fill in the .env file with your credentials
docker-compose up -d
```

## ✅ Roadmap
- [x] MVP in development
- [ ] Telegram bot integration
- [ ] Admin panel
- [ ] Payment gateway (Payme / Click)

## 📌 About
CLinks.uz is a SaaS platform designed to help private clinics in Uzbekistan manage patients, appointments, doctors, and payments — all in one place.

> Built with Django REST Framework, PostgreSQL, Redis, and Docker.