@echo off
echo =====================================
echo        WATCH STORE - AUTO SETUP
echo =====================================
echo.

:: 1. Activate virtual environment 
call venv\Scripts\activate

:: 2. Upgrade pip (tránh lỗi cài thư viện)
echo Upgrading pip...
python -m pip install --upgrade pip

:: 3. Cài thư viện
echo Installing requirements...
pip install -r requirements.txt

:: 4. Chạy migrate
echo Running migrations...
python manage.py migrate

:: 5. Load data nếu có file data.json (KHÔNG flush - tránh mất dữ liệu)
if exist data.json (
    echo Loading data...
    python manage.py loaddata data.json
)

:: 6. Chạy server
echo.
echo =====================================
echo        SERVER IS RUNNING
echo =====================================
echo.
python manage.py runserver

pause