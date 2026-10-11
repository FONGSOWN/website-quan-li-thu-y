import os
import re
import secrets
import sqlite3
from datetime import date
from functools import wraps

from flask import Flask, abort, flash, g, redirect, render_template, request, session, url_for

SERVICES = ("Khám sức khỏe", "Tiêm phòng", "Tắm và vệ sinh", "Điều trị thú cưng")
STATUSES = ("Chờ xác nhận", "Đã xác nhận", "Đã hoàn thành", "Đã hủy")
DOCTORS = (
    {
        "name": "BS. Nguyễn Minh Anh",
        "role": "Bác sĩ thú y tổng quát",
        "specialty": "Khám sức khỏe · Tư vấn dinh dưỡng",
        "image": "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?auto=format&fit=crop&w=600&q=80",
        "bio": "Bác sĩ Minh Anh có hơn 8 năm kinh nghiệm khám và tư vấn sức khỏe cho chó, mèo và tiểu động vật. Chuyên gia về dinh dưỡng thú cưng và chăm sóc phòng ngừa. (Thông tin minh họa)",
        "skills": ["Khám tổng quát", "Tư vấn dinh dưỡng", "Chăm sóc phòng ngừa", "Nội khoa"],
    },
    {
        "name": "BS. Trần Quốc Bảo",
        "role": "Bác sĩ điều trị và phẫu thuật",
        "specialty": "Chẩn đoán · Phẫu thuật · Theo dõi",
        "image": "https://images.unsplash.com/photo-1612349317150-e413f6a5b16d?auto=format&fit=crop&w=600&q=80",
        "bio": "Bác sĩ Quốc Bảo chuyên về chẩn đoán lâm sàng và can thiệp điều trị. Có kinh nghiệm phẫu thuật các ca tiểu khoa phổ biến và theo dõi hồi phục sau điều trị. (Thông tin minh họa)",
        "skills": ["Chẩn đoán lâm sàng", "Phẫu thuật tiểu khoa", "Điều trị nội khoa", "Theo dõi hồi phục"],
    },
    {
        "name": "BS. Lê Ngọc Hà",
        "role": "Bác sĩ chăm sóc và tiêm phòng",
        "specialty": "Tiêm phòng · Da liễu · Nhi khoa",
        "image": "https://images.unsplash.com/photo-1594824476967-48c8b964273f?auto=format&fit=crop&w=600&q=80",
        "bio": "Bác sĩ Ngọc Hà đặc biệt yêu thích làm việc với thú cưng còn nhỏ tuổi. Chuyên về chương trình tiêm phòng, da liễu và nhi khoa thú y. Được nhiều chủ nuôi tin tưởng với phong cách thăm khám nhẹ nhàng. (Thông tin minh họa)",
        "skills": ["Tiêm phòng", "Da liễu thú y", "Nhi khoa thú y", "Chăm sóc sau sinh"],
    },
)


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY=os.environ.get("PETCARE_SECRET_KEY", "dev-only-change-before-deployment"),
        DATABASE=os.path.join(app.instance_path, "petcare.db"),
        ADMIN_USERNAME=os.environ.get("PETCARE_ADMIN_USER", "admin"),
        ADMIN_PASSWORD=os.environ.get("PETCARE_ADMIN_PASSWORD", "admin123"),
        TESTING=False,
    )
    if test_config:
        app.config.update(test_config)
    os.makedirs(app.instance_path, exist_ok=True)

    def get_db():
        if "db" not in g:
            g.db = sqlite3.connect(app.config["DATABASE"])
            g.db.row_factory = sqlite3.Row
        return g.db

    @app.teardown_appcontext
    def close_db(_error=None):
        db = g.pop("db", None)
        if db:
            db.close()

    def init_db():
        db = get_db()
        db.executescript("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT NOT NULL,
                phone TEXT NOT NULL, pet_name TEXT NOT NULL, appointment_date TEXT NOT NULL,
                service TEXT NOT NULL, note TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'Chờ xác nhận',
                created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT NOT NULL,
                email TEXT NOT NULL, message TEXT NOT NULL, is_read INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT (datetime('now','localtime'))
            );
            CREATE INDEX IF NOT EXISTS idx_appointments_date ON appointments(appointment_date);
            CREATE INDEX IF NOT EXISTS idx_appointments_status ON appointments(status);
            CREATE INDEX IF NOT EXISTS idx_messages_read ON messages(is_read);
        """)
        db.commit()

    @app.context_processor
    def inject_globals():
        token = session.get("csrf_token")
        if not token:
            token = secrets.token_urlsafe(32)
            session["csrf_token"] = token
        return {"current_year": date.today().year, "csrf_token": token, "services": SERVICES}

    @app.before_request
    def csrf_protect():
        if request.method == "POST":
            expected, submitted = session.get("csrf_token"), request.form.get("csrf_token", "")
            if not expected or not secrets.compare_digest(expected, submitted):
                abort(400, description="Phiên làm việc không hợp lệ. Vui lòng tải lại trang và thử lại.")

    def admin_required(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            if not session.get("admin_logged_in"):
                flash("Vui lòng đăng nhập để truy cập trang quản lý.", "error")
                return redirect(url_for("admin_login", next=request.path))
            return view(*args, **kwargs)
        return wrapped

    def valid_appointment(form):
        fields = ("full_name", "phone", "pet_name", "appointment_date", "service", "note")
        values = {key: form.get(key, "").strip() for key in fields}
        if not all(values[key] for key in fields[:-1]): return None, "Vui lòng điền đầy đủ các trường bắt buộc."
        if not re.fullmatch(r"[0-9+ .()\-]{9,30}", values["phone"]): return None, "Số điện thoại chưa đúng định dạng."
        try:
            if date.fromisoformat(values["appointment_date"]) < date.today(): return None, "Ngày khám phải từ hôm nay trở đi."
        except ValueError: return None, "Ngày khám không hợp lệ."
        if values["service"] not in SERVICES: return None, "Vui lòng chọn dịch vụ hợp lệ."
        if len(values["full_name"]) > 120 or len(values["pet_name"]) > 100 or len(values["note"]) > 1000: return None, "Một số thông tin quá dài."
        return values, None

    @app.get("/")
    def index(): return render_template("index.html", doctors=DOCTORS)
    @app.get("/gioi-thieu")
    def about(): return render_template("about.html")
    @app.get("/dich-vu")
    def services(): return render_template("services.html")
    @app.get("/bac-si")
    def doctors(): return render_template("doctors.html", doctors=DOCTORS)

    @app.route("/dat-lich", methods=["GET", "POST"])
    def book_appointment():
        if request.method == "GET": return render_template("booking.html")
        values, error = valid_appointment(request.form)
        if error: flash(error, "error"); return redirect(url_for("book_appointment"))
        db = get_db()
        duplicate = db.execute("SELECT id FROM appointments WHERE phone=? AND pet_name=? AND appointment_date=? AND service=? AND created_at >= datetime('now','-2 minutes')", (values["phone"], values["pet_name"], values["appointment_date"], values["service"])).fetchone()
        if duplicate: flash("Lịch hẹn này vừa được gửi. Vui lòng không gửi lại nhiều lần.", "error"); return redirect(url_for("book_appointment"))
        db.execute("INSERT INTO appointments (full_name,phone,pet_name,appointment_date,service,note) VALUES (?,?,?,?,?,?)", tuple(values[k] for k in ("full_name","phone","pet_name","appointment_date","service","note"))); db.commit()
        flash("Đặt lịch thành công! Trung tâm đã ghi nhận thông tin.", "success"); return redirect(url_for("book_appointment"))

    @app.route("/lien-he", methods=["GET", "POST"])
    def contact():
        if request.method == "GET": return render_template("contact.html")
        full_name, email, message = (request.form.get(k, "").strip() for k in ("full_name", "email", "message"))
        valid_email = re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email)
        if not full_name or not email or not message or len(full_name)>120 or len(email)>200 or len(message)>3000 or not valid_email:
            flash("Thông tin liên hệ chưa hợp lệ. Vui lòng kiểm tra lại.", "error"); return redirect(url_for("contact"))
        db=get_db(); db.execute("INSERT INTO messages (full_name,email,message) VALUES (?,?,?)", (full_name,email,message)); db.commit()
        flash("Cảm ơn bạn! Tin nhắn đã được gửi đến hệ thống.", "success"); return redirect(url_for("contact"))

    @app.route("/admin/login", methods=["GET", "POST"])
    def admin_login():
        if session.get("admin_logged_in"): return redirect(url_for("admin_dashboard"))
        if request.method == "POST":
            good_user = secrets.compare_digest(request.form.get("username", ""), app.config["ADMIN_USERNAME"])
            good_pass = secrets.compare_digest(request.form.get("password", ""), app.config["ADMIN_PASSWORD"])
            if good_user and good_pass:
                session.clear(); session["admin_logged_in"] = True; session["admin_username"] = app.config["ADMIN_USERNAME"]
                flash("Đăng nhập thành công.", "success"); next_url=request.args.get("next", "")
                return redirect(next_url if next_url.startswith("/") and not next_url.startswith("//") else url_for("admin_dashboard"))
            flash("Tên đăng nhập hoặc mật khẩu không đúng.", "error")
        return render_template("admin_login.html")

    @app.post("/admin/logout")
    @admin_required
    def admin_logout(): session.clear(); flash("Bạn đã đăng xuất.", "success"); return redirect(url_for("admin_login"))

    @app.get("/admin")
    @admin_required
    def admin_dashboard():
        status, query, appointment_date = request.args.get("status", "").strip(), request.args.get("q", "").strip(), request.args.get("date", "").strip()
        page=max(request.args.get("page", 1, type=int), 1); where=[]; params=[]
        if status in STATUSES: where.append("status=?"); params.append(status)
        else: status=""
        if appointment_date:
            try: date.fromisoformat(appointment_date); where.append("appointment_date=?"); params.append(appointment_date)
            except ValueError: appointment_date=""
        if query: where.append("(full_name LIKE ? OR phone LIKE ? OR pet_name LIKE ?)"); params.extend([f"%{query}%"]*3)
        clause=" WHERE "+" AND ".join(where) if where else ""; db=get_db(); per_page=10
        filtered=db.execute("SELECT COUNT(*) FROM appointments"+clause, params).fetchone()[0]; pages=max((filtered+per_page-1)//per_page,1); page=min(page,pages)
        appointments=db.execute("SELECT * FROM appointments"+clause+" ORDER BY appointment_date DESC,id DESC LIMIT ? OFFSET ?", params+[per_page,(page-1)*per_page]).fetchall()
        total=db.execute("SELECT COUNT(*) FROM appointments").fetchone()[0]; pending=db.execute("SELECT COUNT(*) FROM appointments WHERE status='Chờ xác nhận'").fetchone()[0]; unread=db.execute("SELECT COUNT(*) FROM messages WHERE is_read=0").fetchone()[0]
        messages=db.execute("SELECT * FROM messages ORDER BY id DESC LIMIT 10").fetchall()
        return render_template("admin_dashboard.html", appointments=appointments,messages=messages,total=total,pending=pending,message_count=unread,statuses=STATUSES,status_filter=status,query=query,appointment_date=appointment_date,page=page,pages=pages)

    @app.route("/admin/appointments/new", methods=["GET", "POST"])
    @admin_required
    def new_appointment(): return appointment_form(None)
    @app.route("/admin/appointments/<int:appointment_id>/edit", methods=["GET", "POST"])
    @admin_required
    def edit_appointment(appointment_id):
        appointment=get_db().execute("SELECT * FROM appointments WHERE id=?",(appointment_id,)).fetchone()
        if not appointment: abort(404)
        return appointment_form(appointment)
    def appointment_form(appointment):
        if request.method == "POST":
            values,error=valid_appointment(request.form)
            if error: flash(error,"error")
            else:
                status=request.form.get("status") if request.form.get("status") in STATUSES else STATUSES[0]; db=get_db()
                columns=("full_name","phone","pet_name","appointment_date","service","note")
                if appointment: db.execute("UPDATE appointments SET full_name=?,phone=?,pet_name=?,appointment_date=?,service=?,note=?,status=? WHERE id=?",tuple(values[k] for k in columns)+(status,appointment["id"]))
                else: db.execute("INSERT INTO appointments (full_name,phone,pet_name,appointment_date,service,note,status) VALUES (?,?,?,?,?,?,?)",tuple(values[k] for k in columns)+(status,))
                db.commit(); flash("Đã lưu lịch hẹn.","success"); return redirect(url_for("admin_dashboard"))
        return render_template("admin_appointment_form.html",appointment=appointment,statuses=STATUSES)

    @app.post("/admin/appointments/<int:appointment_id>/status")
    @admin_required
    def update_appointment_status(appointment_id):
        status=request.form.get("status","")
        if status not in STATUSES: abort(400)
        result=get_db().execute("UPDATE appointments SET status=? WHERE id=?",(status,appointment_id)); get_db().commit()
        if not result.rowcount: abort(404)
        flash("Đã cập nhật trạng thái lịch hẹn.","success"); return redirect(url_for("admin_dashboard"))
    @app.post("/admin/appointments/<int:appointment_id>/delete")
    @admin_required
    def delete_appointment(appointment_id): get_db().execute("DELETE FROM appointments WHERE id=?",(appointment_id,)); get_db().commit(); flash("Đã xóa lịch hẹn.","success"); return redirect(url_for("admin_dashboard"))
    @app.post("/admin/messages/<int:message_id>/read")
    @admin_required
    def mark_message_read(message_id): get_db().execute("UPDATE messages SET is_read=1 WHERE id=?",(message_id,)); get_db().commit(); flash("Đã đánh dấu tin nhắn là đã đọc.","success"); return redirect(url_for("admin_dashboard"))
    @app.post("/admin/messages/<int:message_id>/delete")
    @admin_required
    def delete_message(message_id): get_db().execute("DELETE FROM messages WHERE id=?",(message_id,)); get_db().commit(); flash("Đã xóa tin nhắn.","success"); return redirect(url_for("admin_dashboard"))
    @app.errorhandler(404)
    def not_found(_error): return render_template("error.html",code=404,message="Không tìm thấy trang bạn cần."),404
    @app.errorhandler(400)
    def bad_request(error): return render_template("error.html",code=400,message=getattr(error,"description","Yêu cầu không hợp lệ.")),400
    @app.errorhandler(500)
    def server_error(_error): return render_template("error.html",code=500,message="Hệ thống đang gặp sự cố. Vui lòng thử lại sau."),500
    with app.app_context(): init_db()
    return app

app=create_app()
if __name__=="__main__": app.run(host="127.0.0.1",port=5000,debug=os.environ.get("FLASK_DEBUG")=="1")
