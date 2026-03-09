.PHONY: help build up down restart logs shell migrate createsuperuser setup demo

help:
	@echo "CLinks.uz — Buyruqlar:"
	@echo "  make build      - Docker image'larni build qilish"
	@echo "  make up         - Barcha servislarni ishga tushirish"
	@echo "  make down       - Servislarni to'xtatish"
	@echo "  make restart    - Qayta ishga tushirish"
	@echo "  make logs       - Loglarni ko'rish"
	@echo "  make shell      - Backend shell"
	@echo "  make migrate    - Migratsiyalarni bajarish"
	@echo "  make setup      - Boshlang'ich sozlamalar (admin yaratish)"
	@echo "  make demo       - Demo ma'lumotlar qo'shish"
	@echo "  make test       - Testlarni ishga tushirish"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

logs:
	docker-compose logs -f backend

logs-all:
	docker-compose logs -f

shell:
	docker-compose exec backend python manage.py shell

migrate:
	docker-compose exec backend python manage.py migrate

makemigrations:
	docker-compose exec backend python manage.py makemigrations

setup:
	docker-compose exec backend python manage.py setup_initial_data

demo:
	docker-compose exec backend python manage.py setup_initial_data --with-demo

reminders:
	docker-compose exec backend python manage.py send_reminders

createsuperuser:
	docker-compose exec backend python manage.py createsuperuser

collectstatic:
	docker-compose exec backend python manage.py collectstatic --noinput

test:
	docker-compose exec backend python manage.py test

ps:
	docker-compose ps

# Local development (Docker'siz)
local-install:
	pip install -r backend/requirements.txt

local-run:
	cd backend && python manage.py runserver 0.0.0.0:8000

local-migrate:
	cd backend && python manage.py migrate

local-setup:
	cd backend && python manage.py setup_initial_data --with-demo
