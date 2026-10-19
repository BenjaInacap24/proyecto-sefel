@echo off
cd /d "%~dp0"
py -m venv .venv
call .venv\Scripts\activate
python -m pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
pause
