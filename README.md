# ⌚ Watch Store - Website bán đồng hồ

## 📌 Giới thiệu

Watch Store là website bán đồng hồ được xây dựng bằng Django.  
Hệ thống cho phép:

- Xem danh sách sản phẩm theo hãng
- Xem chi tiết sản phẩm và thông số kỹ thuật
- Tính giá sau khi giảm
- Đánh giá sản phẩm bằng sao
- Quản lý sản phẩm qua trang Admin

---

## 🛠 Công nghệ sử dụng

- Python 3.x
- Django 6.x
- SQLite3
- HTML, CSS, Bootstrap

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
python manage.py migrate
```

**Bước 5: Load dữ liệu mẫu**
```bash
python manage.py loaddata data.json
```

**Bước 6: Chạy server**
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

## 💾 Lưu ý quan trọng - Backup dữ liệu

Sau khi thêm/sửa sản phẩm, **luôn export và push lên GitHub**:

```bash
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
git add data.json media/
git commit -m "Update data.json"
git push
```

---

## 📂 Cấu trúc thư mục

```
Watch_Store/
├── app1/        - Ứng dụng quản lý sản phẩm (Watch, Brand, Cart)
├── home/        - Trang chủ
├── mysite/      - Cấu hình project Django
├── templates/   - Giao diện HTML
├── static/      - CSS, JS, hình ảnh tĩnh
├── media/       - Ảnh sản phẩm upload
├── data.json    - Dữ liệu mẫu
├── run.bat      - Script chạy tự động (Windows)
└── requirements.txt
```

---

## 👨‍🎓 Thông tin đồ án

- **Sinh viên:** (Điền tên)
- **Môn học:** (Điền môn học)
- **Giảng viên:** (Điền tên GVHD)