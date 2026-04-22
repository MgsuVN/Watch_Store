# ⌚ Watch Store — Website Bán Đồng Hồ Chính Hãng
<div align="center">
![Framework](https://img.shields.io/badge/Framework-Django-green)
![Language](https://img.shields.io/badge/Language-Python-blue)
![Database](https://img.shields.io/badge/Database-SQLite-lightgrey)
![AI](https://img.shields.io/badge/AI-Groq%20Llama-orange)
![Payment](https://img.shields.io/badge/Payment-VietQR-red)
![Auth](https://img.shields.io/badge/Auth-Allauth-purple)
![Admin](https://img.shields.io/badge/Admin-Jazzmin-darkblue)
</div>
---
## 📌 Giới Thiệu

**Watch Store** là website thương mại điện tử bán đồng hồ chính hãng, được xây dựng bằng **Django (Python)**. Hệ thống hỗ trợ đầy đủ luồng mua hàng từ duyệt sản phẩm → giỏ hàng → thanh toán → theo dõi đơn hàng, tích hợp AI chatbot tư vấn sản phẩm thông minh và dashboard doanh thu cho admin.

---

## 🚀 Tính Năng Chính

### 👤 Người Dùng (Frontend)

#### 🛍️ Sản Phẩm & Danh Mục
- Xem danh sách đồng hồ, phụ kiện (dây đồng hồ, hộp đựng)
- Lọc theo **thương hiệu**, **giới tính** (Nam / Nữ / Unisex), **danh mục**
- Sắp xếp theo: giá tăng dần / giảm dần, giảm giá nhiều nhất, bán chạy nhất
- Phân trang tự động (12 sản phẩm/trang)
- Tìm kiếm sản phẩm với **AJAX autocomplete** (gợi ý tức thì từ 2 ký tự)
- Xem chi tiết sản phẩm: thông số kỹ thuật đầy đủ, **gallery ảnh**, mô tả chi tiết có hỗ trợ ảnh layout trái/phải/full
- Hiển thị giá gốc, giá sau giảm, % giảm giá và trạng thái hàng (còn hàng / hết hàng)
- Trang thương hiệu riêng với bộ lọc giá và sắp xếp
- Xem sản phẩm liên quan cùng thương hiệu

#### 🛒 Giỏ Hàng
- Thêm vào giỏ hàng trực tiếp hoặc qua AJAX (không reload trang)
- Cập nhật số lượng inline với tính toán tổng tiền real-time
- Xoá từng sản phẩm khỏi giỏ
- Hiển thị số lượng sản phẩm trên icon giỏ hàng (cập nhật dynamic)

#### 💳 Thanh Toán & Đơn Hàng
- Nhập thông tin giao hàng: họ tên, số điện thoại, địa chỉ, thành phố, ghi chú
- 2 hình thức thanh toán:
  - **COD** (Thanh toán khi nhận hàng)
  - **Chuyển khoản ngân hàng** qua mã **QR VietQR**
- Tự động điền thông tin từ hồ sơ cá nhân (nếu đã lưu)
- Xem trang hóa đơn với trạng thái thanh toán theo thời gian thực
- Theo dõi trạng thái đơn hàng: Chờ xác nhận → Đã xác nhận → Đang giao → Đã giao
- **Huỷ đơn hàng**: Nếu đã thanh toán → form yêu cầu hoàn tiền (nhập thông tin ngân hàng, lý do)
- Xem lịch sử tất cả đơn hàng

#### ❤️ Danh Sách Yêu Thích
- Toggle yêu thích / bỏ yêu thích bằng AJAX (lưu vào database)
- Xem danh sách sản phẩm đã yêu thích
- Badge hiển thị số lượng yêu thích trên header

#### ⭐ Đánh Giá Sản Phẩm
- Gửi đánh giá sao (1–5) kèm nhận xét
- Đính kèm tối đa 3 ảnh mỗi đánh giá
- Admin có thể ẩn/hiện từng đánh giá

#### 🤖 Chatbot AI Tư Vấn
- Chatbot tích hợp **Groq API** (model llama-3.3-70b-versatile)
- Tư vấn sản phẩm phù hợp dựa theo ngân sách, giới tính, phong cách
- Hiển thị card sản phẩm gợi ý với ảnh, tên, giá ngay trong chat
- Ngữ cảnh động: nhận toàn bộ danh sách sản phẩm thực tế từ database
- Fallback tự động khi model quá tải (thử nhiều model Groq lần lượt)

#### 🔔 Thông Báo
- Nhận thông báo khi đơn hàng thay đổi trạng thái (đặt hàng, xác nhận, vận chuyển, giao hàng, huỷ)
- Dropdown thông báo real-time trên header (load qua AJAX)
- Đánh dấu đã đọc từng thông báo hoặc tất cả cùng lúc
- Badge hiển thị số thông báo chưa đọc

#### 👤 Hồ Sơ Cá Nhân
- Cập nhật: avatar, họ tên, số điện thoại, địa chỉ, giới thiệu bản thân
- Avatar tự động tạo chữ cái đầu + màu sắc nếu chưa upload ảnh

#### 🔐 Xác Thực
- Đăng ký / Đăng nhập bằng **username hoặc email** (qua django-allauth)
- Đổi mật khẩu, đặt lại mật khẩu qua email

---

### 🛠️ Quản Trị (Admin)

#### 📦 Quản Lý Sản Phẩm
- Thêm / sửa / xoá sản phẩm với form đầy đủ thông số kỹ thuật
- **Inline gallery ảnh** sản phẩm (có thể thêm nhiều ảnh, đặt thứ tự)
- **Inline ảnh mô tả chi tiết** với 3 layout: toàn chiều rộng, ảnh trái, ảnh phải
- Quản lý trạng thái hàng (còn hàng / hết hàng), % giảm giá
- Tự động tạo slug từ tên sản phẩm

#### 🏷️ Quản Lý Thương Hiệu
- Thêm / sửa / xoá thương hiệu kèm logo
- Cấu hình **hãng nổi bật** (BrandShowcase) hiển thị trên trang chủ

#### 🧾 Quản Lý Đơn Hàng
- Xem danh sách đơn hàng với **badge màu** theo trạng thái
- Cập nhật trạng thái đơn: Chờ → Xác nhận → Vận chuyển → Giao hàng
- **Xác nhận thanh toán QR** (chuyển `waiting_confirm` → `paid`)
- Gửi thông báo tự động cho khách khi thay đổi trạng thái
- Xem chi tiết từng đơn hàng (inline OrderItem)

#### 💰 Quản Lý Hoàn Tiền
- Xem danh sách yêu cầu hoàn tiền với thông tin ngân hàng
- Cập nhật trạng thái: Chờ xử lý → Đã hoàn tiền

#### 📊 Dashboard Doanh Thu (`/admin/doanh-thu/`)
- Biểu đồ doanh thu theo **ngày / tháng / năm**
- Thống kê tổng đơn hàng, tổng doanh thu, đơn hàng chờ xử lý
- **Top sản phẩm bán chạy** nhất
- Thống kê doanh thu theo **thương hiệu**
- Bộ lọc thời gian linh hoạt (7 ngày, 30 ngày, tùy chọn khoảng ngày)

#### 📢 Quản Lý Thông Báo
- Xem và quản lý thông báo của tất cả người dùng
- **Gửi thông báo khuyến mãi** tới tất cả users cùng lúc
- Đánh dấu đã đọc / chưa đọc

---

## 🛠️ Công Nghệ Sử Dụng

| Thành phần | Công nghệ | Phiên bản |
|---|---|---|
| **Ngôn ngữ** | Python | 3.12 |
| **Framework** | Django | 6.0.2 |
| **Database** | SQLite3 | - |
| **ORM** | Django ORM | - |
| **Xác thực** | django-allauth | 65.14.3 |
| **Admin UI** | django-jazzmin | 3.0.3 |
| **AI Chatbot** | Groq API (llama-3.3-70b-versatile) | - |
| **Xử lý ảnh** | Pillow | 12.1.1 |
| **Template** | Django Template Language + HTML/CSS/JS | - |
| **Form** | django-widget-tweaks | 1.5.1 |
| **Static files** | WhiteNoise | 6.11.0 |
| **WSGI Server** | Gunicorn | 25.1.0 |
| **Biến môi trường** | python-dotenv | 1.2.2 |
| **HTTP Client** | Requests | 2.32.5 |
| **Timezone** | tzdata | 2025.3 |
---
## 📥 Hướng Dẫn Cài Đặt

### 🔹 Cách 1: Chạy Tự Động (Windows) ✅ Khuyến nghị

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

> `run.bat` tự động: kích hoạt venv → cài thư viện → kiểm tra `.env` → migrate → load dữ liệu → chạy server.

---

### 🔹 Cách 2: Chạy Thủ Công

**Bước 1: Clone project**
```bash
git clone https://github.com/MgsuVN/Watch_Store.git
cd Watch_Store
```

**Bước 2: Tạo và kích hoạt môi trường ảo**

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


🍎 macOS / Linux:

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
> Lấy `GROQ_API_KEY` miễn phí tại: https://console.groq.com → API Keys → Create API Key

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

## 🔐 Tài Khoản Quản Trị

Truy cập: http://127.0.0.1:8000/admin

| Username | Password |
|---|---|
| `admin1` | `123456` |

---

## 🔑 Biến Môi Trường (`.env`)

| Biến | Mô tả | Bắt buộc |
|---|---|---|
| `SECRET_KEY` | Django secret key (dùng cho bảo mật session, CSRF) | ✅ |
| `DEBUG` | Chế độ debug (`True` / `False`) | ✅ |
| `GROQ_API_KEY` | API key Groq cho chatbot AI | ✅ (chatbot) |

---

## 🌐 Danh Sách URL Chính

| URL | Mô tả |
|---|---|
| `/` | Trang chủ — danh sách đồng hồ |
| `/nam/` | Đồng hồ Nam |
| `/nu/` | Đồng hồ Nữ |
| `/phu-kien/` | Phụ kiện (dây, hộp đựng) |
| `/brand/<slug>/` | Trang thương hiệu |
| `/watch/<slug>/` | Chi tiết sản phẩm |
| `/search/` | Kết quả tìm kiếm |
| `/cart/` | Giỏ hàng |
| `/checkout/` | Thanh toán |
| `/payment/qr/<id>/` | Thanh toán QR VietQR |
| `/invoice/<id>/` | Hóa đơn đơn hàng |
| `/orders/` | Lịch sử đơn hàng |
| `/wishlist/` | Danh sách yêu thích |
| `/profile/` | Hồ sơ cá nhân |
| `/profile/edit/` | Chỉnh sửa hồ sơ |
| `/accounts/login/` | Đăng nhập (allauth) |
| `/accounts/signup/` | Đăng ký (allauth) |
| `/admin/` | Django Admin (Jazzmin) |
| `/admin/doanh-thu/` | Dashboard doanh thu tùy chỉnh |

---
## 🗄️ Mô Hình Dữ Liệu (Database)

| Model | Mô tả |
|---|---|
| `Brand` | Thương hiệu đồng hồ (tên, slug, logo) |
| `Watch` | Sản phẩm (tên, giá, % giảm, thông số kỹ thuật, danh mục, giới tính) |
| `WatchImage` | Ảnh gallery sản phẩm (quan hệ nhiều với Watch) |
| `WatchDescImage` | Ảnh mô tả chi tiết với layout (full / float_left / float_right) |
| `BrandShowcase` | Hãng nổi bật hiển thị trang chủ |
| `Cart` | Giỏ hàng (1 user – 1 giỏ) |
| `CartItem` | Từng sản phẩm trong giỏ (số lượng, tham chiếu Watch) |
| `Profile` | Hồ sơ mở rộng của user (avatar, phone, địa chỉ) |
| `Order` | Đơn hàng (thông tin giao hàng, trạng thái đơn, trạng thái TT) |
| `OrderItem` | Sản phẩm trong đơn (lưu snapshot tên + giá tại thời điểm mua) |
| `Notification` | Thông báo cho user với 7 loại (đặt hàng, xác nhận, vận chuyển, ...) |
| `Review` | Đánh giá sản phẩm (sao, bình luận, tối đa 3 ảnh) |
| `Wishlist` | Sản phẩm yêu thích (unique user + watch) |
| `Refund` | Yêu cầu hoàn tiền (thông tin ngân hàng, lý do, trạng thái) |

## 💾 Quy Trình Cập Nhật Dữ Liệu (Dev Team)

Sau khi thêm/sửa sản phẩm hoặc có thay đổi dữ liệu, chạy lệnh sau để export và push:

**1. Export data mới nhất (chạy được trên mọi hệ điều hành):**
```bash
python -c "
import os, django
os.environ['DJANGO_SETTINGS_MODULE'] = 'mysite.settings'
django.setup()
from django.core.management import call_command
with open('fixtures/data.json', 'w', encoding='utf-8') as f:
    call_command('dumpdata', '--natural-foreign', '--natural-primary', '--indent', '2',
                 '--exclude', 'contenttypes', '--exclude', 'auth.Permission',
                 '--exclude', 'admin.LogEntry', '--exclude', 'app1.Profile', stdout=f)
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

## 📁 Cấu trúc dự án
"""
Watch_Store/
├── app1/                          # App chính — toàn bộ logic nghiệp vụ
│   ├── models.py                  # Brand, Watch, WatchImage, WatchDescImage,
│   │                              # Cart, CartItem, Profile, Order, OrderItem,
│   │                              # Notification, BrandShowcase, Review,
│   │                              # Refund (yêu cầu hoàn tiền: TK ngân hàng,
│   │                              # lý do, trạng thái pending/completed/rejected)
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
│       ├── gender_watch.html      # Trang lọc theo giới tính (Nam / Nữ)
│       ├── accessory.html         # Trang phụ kiện đồng hồ (dây, hộp đựng...)
│       ├── checkout.html          # Trang thanh toán
│       ├── qr_payment.html        # Thanh toán QR
│       ├── invoice.html           # Hoá đơn
│       ├── refund_form.html       # Form yêu cầu hoàn tiền (nhập TK ngân hàng,
│       │                          # lý do hủy đơn)
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
"""
---
