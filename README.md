# 🐾 PetCare – Website Trung tâm Thú y

Website đặt lịch khám thú cưng, xây dựng bằng Python Flask + SQLite, dành cho môn Lập trình Web.

---

## Yêu cầu hệ thống

| Thành phần | Phiên bản tối thiểu |
|---|---|
| Python | 3.10 trở lên |
| pip | kèm theo Python |
| Hệ điều hành | Windows 10/11, macOS, Linux |

> **Khuyến nghị**: Dùng Python 3.11 hoặc 3.12 để đảm bảo tương thích tốt nhất.

---

## Cài đặt và chạy (Windows / VS Code)

### Bước 1 – Mở dự án trong VS Code

```
File → Open Folder → chọn thư mục WEBSITE_TRUNG_TAM_THU_Y_FLASK
```

### Bước 2 – Mở Terminal trong VS Code

```
Terminal → New Terminal (Ctrl + `)
```

### Bước 3 – Tạo Virtual Environment

```powershell
python -m venv venv
```

### Bước 4 – Kích hoạt Virtual Environment

```powershell
venv\Scripts\activate
```

Sau khi kích hoạt, terminal sẽ hiển thị `(venv)` ở đầu dòng.

### Bước 5 – Cài dependencies

```powershell
pip install -r requirements.txt
```

### Bước 6 – Thiết lập biến môi trường (tuỳ chọn)

Sao chép file `.env.example` thành `.env` và chỉnh sửa:

```powershell
copy .env.example .env
```

> Nếu không làm bước này, hệ thống sẽ dùng giá trị mặc định cho demo.

### Bước 7 – Chạy server

```powershell
python app.py
```

Hoặc với chế độ debug:

```powershell
set FLASK_DEBUG=1
python app.py
```

---

## Địa chỉ truy cập

| Trang | URL |
|---|---|
| Trang chủ | http://127.0.0.1:5000 |
| Giới thiệu | http://127.0.0.1:5000/gioi-thieu |
| Dịch vụ | http://127.0.0.1:5000/dich-vu |
| Bác sĩ | http://127.0.0.1:5000/bac-si |
| Đặt lịch | http://127.0.0.1:5000/dat-lich |
| Liên hệ | http://127.0.0.1:5000/lien-he |
| **Trang Admin** | **http://127.0.0.1:5000/admin** |

---

## Tài khoản demo Admin

| Trường | Giá trị |
|---|---|
| Tên đăng nhập | `admin` |
| Mật khẩu | `admin123` |

> ⚠️ **Quan trọng**: Đây là tài khoản demo. Thay đổi mật khẩu qua biến môi trường `PETCARE_ADMIN_PASSWORD` trước khi triển khai thực tế.

---

## Cơ sở dữ liệu

- **Vị trí**: `instance/petcare.db` (được tạo tự động khi chạy lần đầu)
- **Loại**: SQLite (không cần cài đặt thêm)
- **Dữ liệu**: Lưu tất cả lịch hẹn và tin nhắn liên hệ
- **Không mất dữ liệu** khi restart server

### Xem dữ liệu trực tiếp (tuỳ chọn)

Cài [DB Browser for SQLite](https://sqlitebrowser.org/) và mở file `instance/petcare.db`.

---

## Kiểm thử

### Chạy toàn bộ test

```powershell
python -m pytest tests/ -v
```

### Chạy một test cụ thể

```powershell
python -m pytest tests/test_app.py::test_booking_valid_saved_to_db -v
```

### Kết quả mong đợi

```
tests/test_app.py::test_public_pages_return_200          PASSED
tests/test_app.py::test_admin_requires_login             PASSED
tests/test_app.py::test_404_returns_html                 PASSED
tests/test_app.py::test_booking_past_date_rejected       PASSED
tests/test_app.py::test_booking_missing_fields_rejected  PASSED
tests/test_app.py::test_booking_invalid_phone_rejected   PASSED
tests/test_app.py::test_booking_valid_saved_to_db        PASSED
tests/test_app.py::test_booking_invalid_service_rejected PASSED
tests/test_app.py::test_contact_valid_message_saved      PASSED
tests/test_app.py::test_contact_invalid_email_rejected   PASSED
tests/test_app.py::test_admin_login_success              PASSED
tests/test_app.py::test_admin_login_wrong_password       PASSED
tests/test_app.py::test_admin_csrf_protection            PASSED
tests/test_app.py::test_admin_logout                     PASSED
tests/test_app.py::test_admin_create_appointment         PASSED
tests/test_app.py::test_admin_update_status              PASSED
tests/test_app.py::test_admin_delete_appointment         PASSED
tests/test_app.py::test_admin_mark_message_read_and_delete PASSED
tests/test_app.py::test_data_persists                    PASSED
```

---

## Chức năng chính

### Website công khai
- **Trang chủ**: Hero section, giới thiệu, dịch vụ, quy trình, đội ngũ, đánh giá
- **Giới thiệu**: Sứ mệnh, tầm nhìn, giá trị, thống kê, thông tin liên hệ
- **Dịch vụ**: 4 dịch vụ với mô tả chi tiết, hình ảnh, danh sách tính năng, FAQ
- **Bác sĩ**: Hồ sơ đầy đủ với bio và chuyên môn
- **Đặt lịch**: Form đặt lịch với kiểm tra ngày, dịch vụ, số điện thoại
- **Liên hệ**: Form gửi tin nhắn, thông tin trung tâm

### Trang quản trị Admin
- Đăng nhập/đăng xuất với session bảo vệ
- Dashboard thống kê (tổng lịch, chờ xác nhận, tin nhắn chưa đọc)
- Tìm kiếm lịch hẹn theo tên, SĐT, tên thú cưng
- Lọc theo trạng thái và ngày khám
- Thêm/Sửa/Xóa lịch hẹn (có xác nhận trước khi xóa)
- Cập nhật trạng thái: Chờ xác nhận → Đã xác nhận → Đã hoàn thành / Đã hủy
- Phân trang lịch hẹn (10 lịch/trang)
- Xem/đánh dấu đọc/xóa tin nhắn liên hệ

---

## Cấu trúc dự án

```
WEBSITE_TRUNG_TAM_THU_Y_FLASK/
├── app.py                    # Flask app, routes, logic
├── requirements.txt          # Dependencies
├── README.md                 # Hướng dẫn này
├── .gitignore
├── .env.example              # Mẫu biến môi trường
├── instance/
│   └── petcare.db            # SQLite (tự tạo)
├── templates/
│   ├── base.html             # HTML base với head/body
│   ├── site.html             # Layout site (header + footer)
│   ├── index.html            # Trang chủ
│   ├── about.html            # Giới thiệu
│   ├── services.html         # Dịch vụ
│   ├── doctors.html          # Bác sĩ
│   ├── booking.html          # Đặt lịch
│   ├── booking_form.html     # Form đặt lịch (include)
│   ├── contact.html          # Liên hệ
│   ├── flashes.html          # Flash messages (include)
│   ├── error.html            # Trang lỗi
│   ├── admin_login.html      # Đăng nhập admin
│   ├── admin_dashboard.html  # Dashboard admin
│   └── admin_appointment_form.html  # Form thêm/sửa lịch
├── static/
│   ├── css/style.css         # CSS toàn bộ website
│   ├── js/main.js            # JavaScript
│   └── images/               # Ảnh nội bộ (nếu có)
└── tests/
    └── test_app.py           # Bộ kiểm thử pytest
```

---

## Biến môi trường

Tạo file `.env` từ `.env.example` và điền giá trị:

| Biến | Mô tả | Mặc định demo |
|---|---|---|
| `PETCARE_SECRET_KEY` | Secret key cho Flask session | `dev-only-change-before-deployment` |
| `PETCARE_ADMIN_USER` | Tên đăng nhập admin | `admin` |
| `PETCARE_ADMIN_PASSWORD` | Mật khẩu admin | `admin123` |
| `FLASK_DEBUG` | Bật debug mode (`1` = bật) | `0` |

---

## Tuỳ chỉnh nội dung

### Đổi thông tin trung tâm

Chỉnh sửa trực tiếp trong các file template:
- Địa chỉ, SĐT, email: `templates/about.html`, `templates/contact.html`, `templates/site.html` (footer)
- Giờ làm việc: `templates/about.html`, `templates/contact.html`

### Đổi thông tin bác sĩ

Sửa biến `DOCTORS` trong `app.py` (dòng 12–40).

### Thêm/bớt dịch vụ

Sửa tuple `SERVICES` trong `app.py` (dòng 10). Tên dịch vụ phải khớp với các lựa chọn trong form đặt lịch.

### Thay hình ảnh

1. Đặt file ảnh vào `static/images/`
2. Thay URL Unsplash trong template bằng `{{ url_for('static', filename='images/ten-anh.jpg') }}`

---

## Bảo mật

- CSRF protection trên tất cả form POST
- Admin route bảo vệ bằng session
- Truy vấn SQL dùng tham số (chống SQL injection)
- Jinja2 auto-escaping (chống XSS)
- Mật khẩu admin không lưu trong DB (cấu hình môi trường)
- Trang lỗi thân thiện không lộ traceback

---

## Giới hạn của bản demo

1. Mật khẩu admin không được hash vì lưu qua biến môi trường (không phải trong DB)
2. Không có email xác nhận tự động sau khi đặt lịch
3. Bản đồ trên trang liên hệ là placeholder (cần địa chỉ thực tế để nhúng Google Maps)
4. Hình ảnh dùng từ Unsplash (cần thay bằng ảnh thực khi triển khai)
5. Thông tin bác sĩ và số liệu thống kê là dữ liệu minh họa
6. Chưa có hệ thống phân quyền nhiều admin

---

## Kiểm tra chức năng thủ công

1. Mở http://127.0.0.1:5000 – xem trang chủ
2. Vào /dat-lich – thử đặt lịch với ngày hôm nay
3. Vào /admin – đăng nhập với admin/admin123
4. Xem lịch vừa đặt, thay đổi trạng thái, sửa, xóa
5. Vào /lien-he – gửi tin nhắn
6. Trong admin: xem tin nhắn, đánh dấu đọc, xóa
7. Thử /trang-khong-ton-tai – xem trang 404

---

*Website được xây dựng phục vụ mục đích học tập. Dữ liệu bác sĩ, địa chỉ và số điện thoại là thông tin minh họa.*
# website-quan-li-thu-y
