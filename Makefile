up:
	docker compose up -d

down:
	docker compose down

logs:
	docker compose logs -f

test:
	docker compose exec web pytest

test-v:
	docker compose exec web pytest -v

test-create-db:
	docker compose exec web pytest --create-db -v

shell:
	docker compose exec web bash

django-shell:
	docker compose exec web python manage.py shell
