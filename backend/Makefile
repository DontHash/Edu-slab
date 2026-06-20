.PHONY: help build up down restart logs shell test clean seed init

help:
	@echo "EduAssess Backend - Docker Commands"
	@echo "===================================="
	@echo "make build     - Build Docker images"
	@echo "make up        - Start all services"
	@echo "make down      - Stop all services"
	@echo "make restart   - Restart all services"
	@echo "make logs      - View backend logs"
	@echo "make shell     - Access backend shell"
	@echo "make test      - Run tests"
	@echo "make init      - Initialize database"
	@echo "make seed      - Seed database with sample data"
	@echo "make clean     - Remove all containers and volumes"
	@echo "make prod      - Start production stack"

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart backend

logs:
	docker-compose logs -f backend

shell:
	docker-compose exec backend /bin/bash

test:
	docker-compose exec backend pytest tests/ -v

init:
	docker-compose exec backend python -m app.db.init_db

seed:
	docker-compose exec backend python -m app.db.seed

clean:
	docker-compose down -v --remove-orphans
	docker system prune -f

prod:
	docker-compose -f docker-compose.prod.yml up -d --build

prod-down:
	docker-compose -f docker-compose.prod.yml down

backup-db:
	docker-compose exec postgres pg_dump -U eduassess eduassess > backup_$(shell date +%Y%m%d_%H%M%S).sql

psql:
	docker-compose exec postgres psql -U eduassess eduassess
