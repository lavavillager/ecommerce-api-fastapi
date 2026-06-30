.PHONY: up down build logs migrate seed test fmt

up:            ## Запустить через docker compose
	docker compose up --build

down:          ## Остановить и удалить контейнеры
	docker compose down

logs:          ## Логи API
	docker compose logs -f api

migrate:       ## Применить миграции локально
	alembic upgrade head

revision:      ## Создать миграцию: make revision m="описание"
	alembic revision --autogenerate -m "$(m)"

seed:          ## Загрузить демо-данные локально
	python -m app.seed

test:          ## Запустить тесты
	pytest --cov=app --cov-report=term-missing
