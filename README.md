# Media Hub

![Python](https://img.shields.io/badge/Python-3.13-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.0-092E20?logo=django&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-18-4169E1?logo=postgresql&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-2-E92063?logo=pydantic&logoColor=white)
![Tests](https://img.shields.io/badge/tests-pytest-0A9EDC?logo=pytest&logoColor=white)

A JSON API for storing and managing personal media files — images, video and audio.
Each user uploads, views, updates and deletes only their own files.

## Features

- Upload media files with a title, description and type (image / video / audio)
- List and view your own media with absolute file URLs
- Update metadata and replace the file; the old file is removed from storage
- Delete media together with its file
- Strict per-user data isolation, including the files themselves
- The file content must match `media_type`; size is limited to 50 MB
- Brute-force protection on login

## Tech decisions

**Layered architecture: view → service → repository.**
Views only deal with HTTP, services hold the business logic and build response schemas,
repositories are the only place that talks to the ORM. Each layer can be tested on its own,
and the ORM can be replaced without touching the HTTP code.

**Pydantic validation instead of DRF.**
The `@with_payload` decorator (`utils/decorators.py`) reads the Pydantic model from the
`payload` type annotation of a view method, validates the form data and passes a typed object
into the view, or returns `400` with the validation errors. This keeps the views small and the
request contracts explicit, without pulling in a full framework.

**Ownership is enforced in the repository.**
Every query is filtered by `owner_id`, so there is no code path that can load someone else's
object. A request for another user's media returns `404` rather than `403`, which doesn't
reveal that the object exists.

**Files are served only through signed links.**
`MEDIA_ROOT` is never served directly. Files are stored under random names, and `file_path`
in API responses is a link to `/api/media/<id>/file/` with a token signed with `SECRET_KEY`.
The link works without the `Authorization` header, so it can go straight into `<img src>`.
It expires after an hour (`MEDIA_FILE_URL_TTL`) and stops working once the file is replaced.

**File type is checked by content, not by name.**
The upload is accepted only if its signature (`filetype`) matches `media_type`. The stored
extension and the `Content-Type` of the response are taken from the content, so a file
named `evil.html` can't be served as HTML.

**Login attempts are rate limited.**
Failed logins are counted in the Django cache per IP + email (5 per 15 minutes) and per IP
(50 per 15 minutes). After that the API responds with `429` and `Retry-After`. There is no
per-email limit on its own, so nobody can lock another user out of their account.

**Tests run against real PostgreSQL, not SQLite.**
Production uses Postgres, so tests do too. They run in a separate Compose project
(`docker-compose.test.yml`) with data in memory and `fsync` off. It is fast and fully isolated
from the local development database.

## Quick start

Requires Docker.

```bash
cp service.env.example service.env
make up
make migrate
```

The API is now available at http://localhost:8000/api/.

### Running tests

Requires Docker and a Python 3.13 virtual environment:

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
make test
```

`make test` starts the test database if needed and runs pytest. Other commands are in the `Makefile`.

## API

Register or log in to get a token, then send it as `Authorization: Bearer <token>`.
Tokens are valid for 30 days. Only the register and login endpoints, and signed file links,
work without one.

| Method   | Endpoint              | Description                       |
|----------|-----------------------|-----------------------------------|
| `POST`   | `/api/auth/register/` | Create an account and get a token |
| `POST`   | `/api/auth/login/`    | Get a token                       |
| `POST`   | `/api/auth/logout/`   | Revoke the current token          |
| `GET`    | `/api/media/`        | List the current user's media     |
| `POST`   | `/api/media/create/` | Upload a new media file           |
| `GET`    | `/api/media/<id>/`   | Get a media item                  |
| `POST`   | `/api/media/<id>/`   | Update a media item               |
| `DELETE` | `/api/media/<id>/`   | Delete a media item and its file  |
| `GET`    | `/api/media/<id>/file/?token=…` | Download the file by the signed link from `file_path` |

## Project structure

```
api/views/      HTTP layer
core/
  models/       Django models
  schemas/      Pydantic request and response schemas
  services/     Business logic
  repos/        Data access
utils/          @with_payload decorator, token auth mixin
tests/          pytest tests
```

## Roadmap

- [x] Authentication API with tokens (registration, login, logout)
- [ ] Tags, collections, likes and comments (the models already exist)
- [ ] Pagination for the media list
- [ ] Partial updates with `PATCH`
- [x] Validate that the uploaded file matches `media_type`
- [ ] OpenAPI / Swagger documentation
