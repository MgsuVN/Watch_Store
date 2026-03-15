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

:: 4. Xoa db cu de tranh conflict khi load fixtures
if exist db.sqlite3 (
    echo Removing old database...
    del db.sqlite3
)

:: 5. Migrate database
echo Running migrations...
python manage.py makemigrations
python manage.py migrate

:: 6. Load data tu fixtures/data.json
if exist fixtures\data.json (
    echo Loading data from fixtures/data.json...
    python manage.py loaddata fixtures/data.json
    if errorlevel 1 (
        echo.
        echo [ERROR] Load data that bai! Kiem tra app1/migrations/ da duoc commit chua.
        pause
        exit /b 1
    )
    echo Data loaded successfully!
) else (
    echo [WARNING] fixtures/data.json not found - no data loaded.
)

:: 7. Chay server
echo.
echo =====================================
echo   SERVER IS RUNNING
echo   Truy cap: http://127.0.0.1:8000/
echo =====================================
echo.
python manage.py runserver

pause