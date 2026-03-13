# ⌚ Watch Store - Website bán đồng hồ

## 📌 Giới thiệu

Watch Store là website bán đồng hồ được xây dựng bằng Django.
Hệ thống cho phép:

- Xem danh sách sản phẩm theo hãng
- Xem chi tiết sản phẩm và thông số kỹ thuật
- Tính giá sau khi giảm
- Đánh giá sản phẩm bằng sao
- Thêm vào giỏ hàng, thanh toán đặt hàng
- Chatbot tư vấn sản phẩm bằng AI
- Quản lý sản phẩm và đơn hàng qua trang Admin

---

## 🛠 Công nghệ sử dụng

- Python 3.x
- Django 5.x
- SQLite3
- HTML, CSS, JavaScript
- Google Gemini API (chatbot AI)

---

## 📥 Hướng dẫn cài đặt và chạy dự án

### 🔹 Cách 1: Chạy tự động (Windows) ✅ Khuyến nghị

```bash
git clone https://github.com/MgsuVN/Watch_Store.git
cd Watch_Store
python -m venv venv
run.bat
```

> `run.bat` sẽ tự động: kích hoạt venv, cài thư viện, migrate, load dữ liệu từ `fixtures/data.json` và chạy server.

---

### 🔹 Cách 2: Chạy thủ công

**Bước 1: Clone project**
```bash
git clone https://github.com/MgsuVN/Watch_Store.git
cd Watch_Store
```

**Bước 2: Tạo môi trường ảo**

🪟 Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

🍎 macOS / Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

**Bước 3: Cài thư viện**
```bash
pip install -r requirements.txt
```

**Bước 4: Migrate database**
```bash
python manage.py migrate
```

**Bước 5: Load dữ liệu mẫu**
```bash
python manage.py loaddata fixtures/data.json
```

**Bước 6: Cấu hình API keys (tuỳ chọn)**

Mở file `mysite/settings.py`, tìm dòng `GEMINI_API_KEY` và thay bằng key của bạn:

```python
# Lấy key miễn phí tại: https://aistudio.google.com/apikey
GEMINI_API_KEY = 'AIzaSy...'
```

> Không cấu hình vẫn chạy bình thường, chỉ chatbot sẽ không hoạt động.

**Bước 7: Chạy server**
```bash
python manage.py runserver
```

Truy cập: http://127.0.0.1:8000/

---

## 🔐 Tài khoản quản trị (Admin)

Truy cập: http://127.0.0.1:8000/admin

| Username | Password |
|----------|----------|
| admin1   | 123456 |

---

## 💾 Quy trình cập nhật data (dành cho team dev)

Sau khi thêm/sửa sản phẩm hoặc có thay đổi, chạy lệnh sau để export và push:

**1. Export data mới nhất:**
```bash
python -c "
import os, django, io
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
django.setup()
from django.core.management import call_command
with io.open('fixtures/data.json', 'w', encoding='utf-8') as f:
    call_command('dumpdata', '--natural-foreign', '--natural-primary',
        exclude=['contenttypes', 'auth.permission', 'socialaccount'],
        indent=2, stdout=f)
print('Done!')
"
```

**2. Commit và push:**
```bash
git add fixtures/data.json
git add media/
git commit -m "Update data"
git push
```

**3. Các thành viên còn lại sau khi pull:**
```bash
git pull
python manage.py migrate
python manage.py loaddata fixtures/data.json
```

---

## 📂 Cấu trúc thư mục

```
Watch_Store/
├── app1/            - App chính (Watch, Brand, Cart, Order, Chatbot...)
├── mysite/          - Cấu hình project Django (settings, urls)
├── templates/       - Giao diện HTML
│   ├── base.html
│   └── includes/
├── static/          - CSS, JS, hình ảnh tĩnh
├── media/           - Ảnh sản phẩm upload
├── fixtures/
│   └── data.json    - Dữ liệu mẫu (sản phẩm, tài khoản...)
├── run.bat          - Script chạy tự động (Windows)
└── requirements.txt
```
