@echo off
echo =====================================
echo        WATCH STORE - AUTO SETUP
echo =====================================
echo.

:: 1. Activate virtual environment
call venv\Scripts\activate

:: 2. Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

:: 3. Cai thu vien
echo Installing requirements...
pip install -r requirements.txt

:: 4. Migrate database
echo Running migrations...
python manage.py makemigrations
python manage.py migrate

:: 5. Load data tu fixtures/data.json
if exist fixtures\data.json (
    echo Loading data from fixtures/data.json...
    python manage.py loaddata fixtures/data.json
    echo Data loaded successfully!
) else (
    echo [WARNING] fixtures/data.json not found - no data loaded.
)

:: 6. Chay server
echo.
echo =====================================
echo   SERVER IS RUNNING
echo   Truy cap: http://127.0.0.1:8000/
echo =====================================
echo.
python manage.py runserver

pause