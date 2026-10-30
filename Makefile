up:
	docker compose up -d

down:
	docker compose down

migrate:
	docker compose exec web python manage.py migrate

logs:
	docker compose logs -f

TEST_DB_PORT ?= 5434
export TEST_DB_PORT
TEST_ENV = POSTGRES_HOST=localhost POSTGRES_PORT=$(TEST_DB_PORT)

test-db-up:
	docker compose -f docker-compose.test.yml up -d --wait

test-db-down:
	docker compose -f docker-compose.test.yml down

test: test-db-up
	$(TEST_ENV) pytest

test-v: test-db-up
	$(TEST_ENV) pytest -v

test-create-db: test-db-up
	$(TEST_ENV) pytest --create-db -v

shell:
	docker compose exec web bash

django-shell:
	docker compose exec web python manage.py shell
