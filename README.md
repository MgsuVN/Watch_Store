# ⌚ Watch Store - Website bán đồng hồ

## 📌 Giới thiệu

Watch Store là website thương mại điện tử bán đồng hồ chính hãng, xây dựng bằng Django.
Hệ thống hỗ trợ đầy đủ luồng mua hàng từ duyệt sản phẩm đến thanh toán và theo dõi đơn hàng.

**Tính năng người dùng:**
- Xem danh sách sản phẩm theo hãng, tìm kiếm (có AJAX)
- Xem chi tiết sản phẩm: thông số kỹ thuật, gallery ảnh, mô tả chi tiết
- Xem giá gốc, giá sau giảm, trạng thái còn hàng / hết hàng
- Đánh giá sản phẩm bằng sao kèm ảnh (tối đa 3 ảnh/đánh giá)
- Thêm vào giỏ hàng, cập nhật số lượng, xoá sản phẩm
- Thêm vào danh sách yêu thích
- Đặt hàng với 2 hình thức thanh toán: COD, chuyển khoản QR
- Theo dõi trạng thái đơn hàng, huỷ đơn, xem hoá đơn
- Nhận thông báo real-time khi đơn hàng thay đổi trạng thái
- Chatbot tư vấn sản phẩm bằng AI (Groq)
- Quản lý hồ sơ cá nhân: avatar, số điện thoại, địa chỉ, giới thiệu

**Tính năng quản trị (Admin):**
- Quản lý sản phẩm với inline gallery ảnh và ảnh mô tả chi tiết (hỗ trợ layout trái/phải/full), có thể thêm sửa xóa sản phẩm
- Quản lý hãng sản phẩm: Có thể thêm sửa xóa các hãng sản phẩm
- Quản lý đơn hàng: xem nhãn màu trạng thái, xác nhận thanh toán QR, gửi thông báo cho khách
- Quản lý thông báo: đánh dấu đã đọc, gửi khuyến mãi tới tất cả người dùng
- Dashboard doanh thu tùy chỉnh tại `/admin/doanh-thu/`: biểu đồ theo ngày/tháng, top sản phẩm bán chạy, thống kê theo thương hiệu, bộ lọc thời gian linh hoạt

---

## 🛠 Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Backend | Python 3.12, Django 6.x |
| Database | SQLite3 |
| Xác thực | django-allauth (đăng nhập bằng username hoặc email) |
| Admin UI | django-jazzmin |
| Template | HTML, CSS, JavaScript, django-widget-tweaks |
| AI Chatbot | Groq API (llama-3.3-70b-versatile) |
| Media | Pillow |
| Deploy | Whitenoise (static), Gunicorn (WSGI) |

---

## 📥 Hướng dẫn cài đặt và chạy dự án

### 🔹 Cách 1: Chạy tự động (Windows) ✅ Khuyến nghị

**Bước 1: Clone project**
```bash
git clone https://github.com/MgsuVN/Watch_Store.git
cd Watch_Store
```

**Bước 2: Tạo môi trường ảo**
```bash
python -m venv venv
```

**Bước 3: Tạo file `.env`**
```bash
copy .env.example .env
```

Mở file `.env` vừa tạo, điền các giá trị:
```env
# Tạo SECRET_KEY mới bằng lệnh bên dưới rồi dán vào đây
SECRET_KEY=your-secret-key-here

DEBUG=True

# Lấy miễn phí tại: https://console.groq.com → API Keys → Create API Key
GROQ_API_KEY=your-groq-api-key-here
```

Tạo `SECRET_KEY` mới:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**Bước 4: Chạy**
```bash
run.bat
```

> `run.bat` sẽ tự động: kích hoạt venv, cài thư viện, kiểm tra `.env`, migrate, load dữ liệu và chạy server.

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

**Bước 4: Tạo file `.env`**

🪟 Windows:
```bash
copy .env.example .env
```

🍎 macOS / Linux:
```bash
cp .env.example .env
```

Mở file `.env`, điền các giá trị:
```env
SECRET_KEY=your-secret-key-here
DEBUG=True
GROQ_API_KEY=your-groq-api-key-here
```

Tạo `SECRET_KEY` mới:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Lấy `GROQ_API_KEY` miễn phí tại: https://console.groq.com → API Keys → Create API Key

**Bước 5: Migrate database**
```bash
python manage.py migrate
```

**Bước 6: Load dữ liệu mẫu**
```bash
python manage.py loaddata fixtures/data.json
```

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

Sau khi thêm/sửa sản phẩm hoặc có thay đổi dữ liệu, chạy lệnh sau để export và push:

**1. Export data mới nhất (chạy được trên mọi hệ điều hành):**
```bash
python -c "
import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
django.setup()
from django.core.management import call_command
with open('fixtures/data.json', 'w', encoding='utf-8') as f:
    call_command('dumpdata', '--natural-foreign', '--natural-primary', '--indent', '2', '--exclude', 'contenttypes', '--exclude', 'auth.Permission', '--exclude', 'admin.LogEntry', '--exclude', 'app1.Profile', stdout=f)
print('Done!')
"
```

**2. Commit và push bằng VS Code:**

Nhấn `Ctrl+Shift+G` → Stage `fixtures/data.json` → nhập commit message → **Commit** → **Sync Changes**

**3. Các thành viên còn lại sau khi pull:**
```bash
git pull
run.bat
```

---

## 📁 Cấu trúc dự án

```
Watch_Store/
├── app1/                          # App chính — toàn bộ logic nghiệp vụ
│   ├── models.py                  # Brand, Watch, WatchImage, WatchDescImage,
│   │                              # Cart, CartItem, Profile, Order, OrderItem,
│   │                              # Notification, BrandShowcase, Review
│   ├── views.py                   # Sản phẩm, giỏ hàng, checkout, đơn hàng,
│   │                              # wishlist, chatbot AI, thông báo, QR payment, invoice
│   ├── forms.py                   # WatchForm, ProfileForm
│   ├── urls.py                    # 30+ routes: /, brand, watch, cart, checkout,
│   │                              # orders, wishlist, chatbot, notifications,
│   │                              # payment/qr, invoice, profile
│   ├── admin.py                   # Admin tùy chỉnh: BrandAdmin, WatchAdmin (inline
│   │                              # gallery + mô tả), OrderAdmin (badge trạng thái,
│   │                              # gửi thông báo), NotificationAdmin (gửi promo tới tất cả users),
│   │                              # Dashboard doanh thu /admin/doanh-thu/
│   ├── templatetags/
│   │   └── custom_filters.py      # Custom template filters
│   └── migrations/                # 23 migration files (lịch sử thay đổi DB)
│
├── home/                          # App phụ — trang chủ & profile người dùng
│   ├── models.py                  # Brand, Product, Profile (model khởi tạo ban đầu,
│   │                              # logic chính đã chuyển sang app1)
│   ├── views.py                   # home() — danh sách sản phẩm,
│   │                              # profile_view(), profile_edit()
│   ├── forms.py                   # ProfileForm (views dùng app1.forms thay thế)
│   ├── admin.py                   # ProfileAdmin — hiển thị (user, phone)
│   ├── urls.py                    # '' → profile, edit/ → profile_edit
│   │                              # (mount tại /profile/ trong mysite/urls.py)
│   └── Templates/                 # Template riêng của app home
│       ├── home.html              # Trang chủ
│       ├── brand_detail.html      # Trang thương hiệu
│       ├── watch_detail.html      # Chi tiết sản phẩm
│       ├── checkout.html          # Trang thanh toán
│       ├── qr_payment.html        # Thanh toán QR
│       ├── invoice.html           # Hoá đơn
│       ├── Order_success.html     # Đặt hàng thành công
│       └── includes/
│           ├── product_card.html  # Component card sản phẩm
│           └── product_list.html  # Component danh sách sản phẩm
│
├── mysite/                        # Cấu hình project Django
│   ├── settings.py                # Cài đặt: SQLite3, Jazzmin admin, allauth
│   │                              # (đăng nhập bằng username + email), widget_tweaks,
│   │                              # ngôn ngữ vi / múi giờ Asia/Ho_Chi_Minh,
│   │                              # GROQ_API_KEY, STATIC + MEDIA config
│   │                              # Đọc cấu hình từ file .env
│   ├── urls.py                    # URL gốc: admin/, accounts/ (allauth),
│   │                              # profile/ (home), '' (app1)
│   ├── wsgi.py                    # WSGI config (deploy truyền thống)
│   └── asgi.py                    # ASGI config (deploy async)
│
├── templates/                     # Template dùng chung toàn project
│   ├── base.html                  # Layout chính (header, footer, chatbot widget)
│   ├── cart.html                  # Trang giỏ hàng
│   ├── orders.html                # Lịch sử đơn hàng
│   ├── search_results.html        # Kết quả tìm kiếm
│   ├── wishlist.html              # Danh sách yêu thích
│   ├── account/                   # Template xác thực & hồ sơ
│   │   ├── login.html
│   │   ├── signup.html
│   │   ├── profile.html
│   │   └── profile_edit.html
│   ├── admin/
│   │   └── revenue.html           # Dashboard doanh thu tùy chỉnh
│   └── includes/                  # Components tái sử dụng
│       ├── header.html
│       ├── footer.html
│       └── chatbot_widget.html    # Widget chatbot AI (Groq)
│
├── static/                        # File tĩnh
│   ├── images/                    # Ảnh sản phẩm, thương hiệu, banner
│   └── video/                     # Video nền trang chủ (hero.mp4, craft.mp4, ...)
│
├── media/                         # File upload từ người dùng (tự sinh khi chạy)
│   ├── avatars/                   # Ảnh đại diện người dùng
│   ├── brands/                    # Logo thương hiệu
│   ├── products/                  # Ảnh sản phẩm chính
│   │   └── gallery/               # Ảnh gallery sản phẩm
│   ├── reviews/                   # Ảnh đính kèm đánh giá (tối đa 3 ảnh/review)
│   └── watch_desc/                # Ảnh mô tả chi tiết sản phẩm
│
├── fixtures/
│   └── data.json                  # Dữ liệu mẫu (loaddata khi setup)
│
├── manage.py                      # Django management CLI
├── requirements.txt               # Thư viện Python cần thiết
├── run.bat                        # Script chạy project tự động (Windows)
├── .env                           # ⚠️ Biến môi trường (SECRET_KEY, GROQ_API_KEY) — KHÔNG commit
├── .env.example                   # File mẫu .env — commit lên Git
└── README.md                      # Tài liệu hướng dẫn
```