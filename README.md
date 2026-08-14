# Media Hub

Project "Media Hub" for keeping, viewing and handling mediafiles (photo, video, audio).

Quick local start:

1. Create virtual environment and install dependencies
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Environment settings
- Copy `service.env.example` to `service.env` and define variables.

3. Run migrations and run server
```bash
python manage.py migrate
python manage.py runserver
```

4. Run tests
```bash
pytest -q
```
