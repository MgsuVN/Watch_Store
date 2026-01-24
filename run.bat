@echo off
echo =====================================
echo DJANGO PROJECT
echo =====================================

if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing required packages...
pip install -r requirements.txt

echo Applying migrations...
python manage.py migrate

echo =====================================
echo RUNNING SERVER
echo =====================================
python manage.py runserver
