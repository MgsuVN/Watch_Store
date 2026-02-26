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

> `run.bat` sẽ tự động: kích hoạt venv, cài thư viện, migrate, load dữ liệu và chạy server.

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
python manage.py makemigrations
python manage.py migrate
```

**Bước 5: Load dữ liệu mẫu**
```bash
python manage.py loaddata data.json
```

**Bước 6: Cấu hình API keys (tuỳ chọn)**

Mở file `mysite/settings.py`, thêm vào cuối:

```python
# Chatbot AI (Google Gemini - miễn phí)
# Lấy key tại: https://aistudio.google.com/apikey
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
| admin1   | (nhập mật khẩu của bạn) |

> Nếu chưa có tài khoản, tạo bằng lệnh:
> ```bash
> python manage.py createsuperuser
> ```

---

## 💾 Backup & Deploy — Export dữ liệu lên GitHub

Sau khi thêm/sửa sản phẩm hoặc có thay đổi code, chạy lệnh sau để backup và push:

```bash
python manage.py makemigrations
python manage.py migrate
python -c "
import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mysite.settings')
django.setup()
from django.core import serializers
from django.apps import apps
all_objects = []
for model in apps.get_models():
    all_objects.extend(model.objects.all())
data = serializers.serialize('json', all_objects, indent=2)
with open('data.json', 'w', encoding='utf-8') as f:
    f.write(data)
print('Done!')
"
git add .
git commit -m "Update data and code"
git push
```

---

## 📂 Cấu trúc thư mục

```
Watch_Store/
├── app1/            - App chính (Watch, Brand, Cart, Order, Chatbot...)
├── mysite/          - Cấu hình project Django (settings, urls)
├── templates/       - Giao diện HTML
│   ├── base.html
│   ├── checkout.html
│   ├── order_success.html
│   └── includes/
│       └── chatbot_widget.html
├── static/          - CSS, JS, hình ảnh tĩnh
├── media/           - Ảnh sản phẩm upload
├── data.json        - Dữ liệu mẫu (sản phẩm, đơn hàng...)
├── run.bat          - Script chạy tự động (Windows)
└── requirements.txt
```

---

## 👨‍🎓 Thông tin đồ án

- **Sinh viên:** (Điền tên)
- **Môn học:** (Điền môn học)
- **Giảng viên:** (Điền tên GVHD)