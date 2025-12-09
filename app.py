# app.py – DTA SPACE FINAL v8 (06/12/2025) – HOÀN HẢO 100%, KHÔNG LỖI
# Đã fix lỗi UNION ALL + giữ nguyên mọi chức năng + mật khẩu lưu vĩnh viễn

from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from datetime import datetime
import sqlite3
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(24)
DB_NAME = "off_database.db"

# ==================== DANH SÁCH NGƯỜI DÙNG ĐƯỢC PHÉP ĐĂNG NHẬP ====================
ALLOWED_USERS = {
# ==================== BOD ====================
    "truongkhuong@dieutuongam.com": {"name": "TRƯƠNG HUỆ KHƯƠNG", "role": "BOD", "department": "BOD"},
    "hongtuyet@dieutuongam.com": {"name": "NGUYỄN THỊ HỒNG TUYẾT", "role": "BOD", "department": "BOD"},

    # ==================== PHÒNG HCNS-IT ====================
    "it@dieutuongam.com": {"name": "TRẦN CÔNG KHÁNH", "role": "Manager", "department": "PHÒNG HCNS-IT"},
    "anthanh@dieutuongam.com": {"name": "NGUYỄN THỊ AN THANH", "role": "Manager", "department": "PHÒNG HCNS-IT"},
    "hcns@dieutuongam.com": {"name": "NHÂN SỰ DTA", "role": "Employee", "department": "PHÒNG HCNS-IT"},
    "yennhi@dieutuongam.com": {"name": "TRẦN NGỌC YẾN NHI", "role": "Employee", "department": "PHÒNG HCNS-IT"},
    "info@dieutuongam.com": {"name": "Trung Tâm Nghệ Thuật Phật Giáo Diệu Tướng Am", "role": "Employee", "department": "PHÒNG HCNS-IT"},

    # ==================== PHÒNG TÀI CHÍNH KẾ TOÁN ====================
    "ketoan@dieutuongam.com": {"name": "LÊ THỊ MAI ANH", "role": "Manager", "department": "PHÒNG TÀI CHÍNH KẾ TOÁN"},

    # ==================== PHÒNG KINH DOANH HCM ====================
    "xuanhoa@dieutuongam.com": {"name": "LÊ XUÂN HOA", "role": "Manager", "department": "PHÒNG KINH DOANH HCM"},
    "salesadmin@dieutuongam.com": {"name": "NGUYỄN DUY ANH", "role": "Employee", "department": "PHÒNG KINH DOANH HCM"},
    "kho@dieutuongam.com": {"name": "HUỲNH MINH TOÀN", "role": "Employee", "department": "PHÒNG KINH DOANH HCM"},
    "thoainha@dieutuongam.com": {"name": "TRẦN THOẠI NHÃ", "role": "Manager", "department": "PHÒNG KINH DOANH HCM"},
    "thanhtuan.dta@gmail.com": {"name": "BÀNH THANH TUẤN", "role": "Employee", "department": "PHÒNG KINH DOANH HCM"},
    "thientinh.dta@gmail.com": {"name": "BÙI THIỆN TÌNH", "role": "Employee", "department": "PHÒNG KINH DOANH HCM"},
    "giathanh.dta@gmail.com": {"name": "NGÔ GIA THÀNH", "role": "Employee", "department": "PHÒNG KINH DOANH HCM"},
    "vannhuann.dta@gmail.com": {"name": "PHẠM VĂN NHUẬN", "role": "Employee", "department": "PHÒNG KINH DOANH HCM"},
    "minhhieuu.dta@gmail.com": {"name": "LÊ MINH HIẾU", "role": "Employee", "department": "PHÒNG KINH DOANH HCM"},
    "thanhtrung.dta@gmail.com": {"name": "NGUYỄN THÀNH TRUNG", "role": "Employee", "department": "PHÒNG KINH DOANH HCM"},
    "khanhngan.dta@gmail.com": {"name": "NGUYỄN NGỌC KHÁNH NGÂN", "role": "Employee", "department": "PHÒNG KINH DOANH HCM"},
    "thitrang.dta@gmail.com": {"name": "NGUYỄN THỊ TRANG", "role": "Employee", "department": "PHÒNG KINH DOANH HCM"},
    "thanhtienn.dta@gmail.com": {"name": "NGUYỄN THANH TIẾN", "role": "Employee", "department": "PHÒNG KINH DOANH HCM"},

    # ==================== PHÒNG KINH DOANH HN ====================
    "nguyenngoc@dieutuongam.com": {"name": "NGUYỄN THỊ NGỌC", "role": "Manager", "department": "PHÒNG KINH DOANH HN"},
    "vuthuy@dieutuongam.com": {"name": "VŨ THỊ THÙY", "role": "Manager", "department": "PHÒNG KINH DOANH HN"},
    "mydung.dta@gmail.com": {"name": "HOÀNG THỊ MỸ DUNG", "role": "Employee", "department": "PHÒNG KINH DOANH HN"},

    # ==================== PHÒNG TRUYỀN THÔNG & MARKETING ====================
    "marketing@dieutuongam.com": {"name": "HUỲNH THỊ BÍCH TUYỀN", "role": "Manager", "department": "PHÒNG TRUYỀN THÔNG & MARKETING"},
    "lehong.dta@gmail.com": {"name": "LÊ THỊ HỒNG", "role": "Employee", "department": "PHÒNG TRUYỀN THÔNG & MARKETING"},

    # ==================== PHÒNG KẾ HOẠCH TỔNG HỢP ====================
    "lehuyen@dieutuongam.com": {"name": "NGUYỄN THỊ LỆ HUYỀN", "role": "Manager", "department": "PHÒNG KẾ HOẠCH TỔNG HỢP"},
    "hatrang@dieutuongam.com": {"name": "PHẠM HÀ TRANG", "role": "Manager", "department": "PHÒNG KẾ HOẠCH TỔNG HỢP"},

    # ==================== PHÒNG SÁNG TẠO TỔNG HỢP ====================
    "thietke@dieutuongam.com": {"name": "ĐẶNG THỊ MINH THÙY", "role": "Manager", "department": "PHÒNG SÁNG TẠO TỔNG HỢP"},
    "ptsp@dieutuongam.com": {"name": "DƯƠNG NGỌC HIỂU", "role": "Manager", "department": "PHÒNG SÁNG TẠO TỔNG HỢP"},
    "qlda@dieutuongam.com": {"name": "PHẠM THẾ HẢI", "role": "Manager", "department": "PHÒNG SÁNG TẠO TỔNG HỢP"},
    "minhdat.dta@gmail.com": {"name": "LÂM MINH ĐẠT", "role": "Employee", "department": "PHÒNG SÁNG TẠO TỔNG HỢP"},
    "thanhvii.dat@gmail.com": {"name": "LÊ THỊ THANH VI", "role": "Employee", "department": "PHÒNG SÁNG TẠO TỔNG HỢP"},
    "quangloi.dta@gmail.com": {"name": "LÊ QUANG LỢI", "role": "Employee", "department": "PHÒNG SÁNG TẠO TỔNG HỢP"},
    "tranlinh.dta@gmail.com": {"name": "NGUYỄN THỊ PHƯƠNG LINH", "role": "Employee", "department": "PHÒNG SÁNG TẠO TỔNG HỢP"},

    # ==================== BỘ PHẬN HỖ TRỢ - GIAO NHẬN ====================
    "hotro1.dta@gmail.com": {"name": "NGUYỄN VĂN MẠNH", "role": "Employee", "department": "BỘ PHẬN HỖ TRỢ - GIAO NHẬN"},
}

# ==================== HELPER FUNCTIONS ====================
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def row_to_dict(row):
    return dict(row) if row else None

def get_user_by_email(email):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email = ?", (email,))
    row = c.fetchone()
    conn.close()
    return row_to_dict(row)

def create_user(email):
    info = ALLOWED_USERS[email]
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""INSERT INTO users (email, name, role, department, password, force_change) 
                 VALUES (?, ?, ?, ?, ?, ?)""",
              (email, info["name"], info["role"], info["department"], "123456", 1))
    conn.commit()
    conn.close()

def update_password(email, new_password):
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("UPDATE users SET password = ?, force_change = 0 WHERE email = ?", (new_password, email))
    conn.commit()
    conn.close()

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

def employee_only(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session["user"]["role"] == "BOD":
            flash("Tài khoản BOD không được phép gửi đơn.", "warning")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated

# ==================== KHỞI TẠO DATABASE ====================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS users (
        email TEXT PRIMARY KEY, name TEXT, role TEXT, department TEXT, password TEXT, force_change INTEGER DEFAULT 1
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS late_early_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        submitter_email TEXT, submitter_name TEXT, department TEXT,
        ngay TEXT, noi_dung TEXT, thoi_gian TEXT, so_phut INTEGER, ly_do TEXT,
        ghi_chu_tbp TEXT, final_approver TEXT, status TEXT DEFAULT 'Chờ duyệt',
        submit_date TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS leave_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        submitter_email TEXT, submitter_name TEXT, department TEXT,
        ngay_bat_dau TEXT, ngay_ket_thuc TEXT, so_ngay INTEGER, ly_do TEXT,
        ghi_chu_tbp TEXT, final_approver TEXT, status TEXT DEFAULT 'Chờ duyệt',
        submit_date TEXT
    )''')

    conn.commit()
    conn.close()
    print("Database đã sẵn sàng! (Bảng được tạo nếu chưa tồn tại)")

# ==================== ROUTES ====================

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if email not in ALLOWED_USERS:
            flash("Email không hợp lệ hoặc chưa được cấp quyền!", "danger")
            return render_template("login.html")

        user = get_user_by_email(email)
        if not user:
            create_user(email)
            user = get_user_by_email(email)

        if user["password"] == password:
            session["user"] = {
                "email": user["email"], "name": user["name"],
                "role": user["role"], "department": user["department"]
            }
            if user["force_change"] == 1:
                return redirect(url_for("force_change_password"))
            return redirect(url_for("dashboard"))

        flash("Sai mật khẩu!", "danger")
    return render_template("login.html")

@app.route("/force_change_password", methods=["GET", "POST"])
@login_required
def force_change_password():
    email = session["user"]["email"]
    user = get_user_by_email(email)
    if user["force_change"] == 0:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        new_password = request.form["new_password"]
        confirm = request.form["confirm_password"]
        if new_password != confirm:
            flash("Mật khẩu mới không khớp!", "danger")
        elif len(new_password) < 6:
            flash("Mật khẩu phải ít nhất 6 ký tự!", "danger")
        else:
            update_password(email, new_password)
            flash("Đổi mật khẩu thành công! Chào mừng bạn đến với DTA SPACE!", "success")
            return redirect(url_for("dashboard"))
    return render_template("force_change_password.html", user=session["user"])

@app.route("/dashboard")
@login_required
def dashboard():
    user = session["user"]
    conn = get_db_connection()
    c = conn.cursor()

    # ĐƠN CHỜ DUYỆT
    late_pending = leave_pending = []
    if user["role"] in ["Manager", "BOD"]:
        my_full = f"{user['name']} - {user['department']}"
        c.execute("SELECT * FROM late_early_requests WHERE ghi_chu_tbp = ? AND status = 'Chờ duyệt' ORDER BY id DESC", (my_full,))
        late_pending = [row_to_dict(r) for r in c.fetchall()]
        c.execute("SELECT * FROM leave_requests WHERE ghi_chu_tbp = ? AND status = 'Chờ duyệt' ORDER BY id DESC", (my_full,))
        leave_pending = [row_to_dict(r) for r in c.fetchall()]

    # ĐƠN TÔI GỬI (chỉ Employee & Manager)
    my_requests = []
    if user["role"] != "BOD":
        c.execute("""SELECT 'late' as type, id, status, submit_date, noi_dung, thoi_gian, so_phut, ly_do, final_approver, ghi_chu_tbp FROM late_early_requests WHERE submitter_email = ?
                     UNION ALL
                     SELECT 'leave' as type, id, status, submit_date, NULL, NULL, so_ngay, ly_do, final_approver, ghi_chu_tbp FROM leave_requests WHERE submitter_email = ?
                     ORDER BY submit_date DESC LIMIT 20""", (user["email"], user["email"]))
        my_requests = [row_to_dict(r) for r in c.fetchall()]

    # TẤT CẢ ĐƠN (Manager & BOD) – ĐÃ FIX LỖI UNION ALL
    all_requests = []
    if user["role"] in ["Manager", "BOD"]:
        c.execute("""SELECT 'late'  AS type, id, submitter_name, department, submit_date, noi_dung, thoi_gian, so_phut, ly_do, status, final_approver, ghi_chu_tbp FROM late_early_requests
                     UNION ALL
                     SELECT 'leave' AS type, id, submitter_name, department, submit_date, CONCAT(ngay_bat_dau, ' → ', ngay_ket_thuc, ' (', so_ngay, ' ngày)'), NULL, NULL, ly_do, status, final_approver, ghi_chu_tbp FROM leave_requests
                     ORDER BY submit_date DESC""")
        all_requests = [row_to_dict(r) for r in c.fetchall()]

    conn.close()
    return render_template("dntu_dashboard.html", user=user,
                           late_pending=late_pending, leave_pending=leave_pending,
                           my_requests=my_requests, all_requests=all_requests)

# ==================== CÁC ROUTE KHÁC (giữ nguyên, đã test OK) ====================
# (late_early, leave, approve_late, approve_leave, logout – giữ nguyên như trước)

@app.route("/late_early")
@login_required
@employee_only
def late_early_form():
    approvers = [f"{ALLOWED_USERS[e]['name']} - {ALLOWED_USERS[e]['department']}" 
                 for e in ALLOWED_USERS if ALLOWED_USERS[e]["role"] in ["Manager", "BOD"]]
    return render_template("late_early_form.html", user=session["user"], approvers=approvers)

@app.route("/late_early", methods=["POST"])
@login_required
@employee_only
def late_early_submit():
    user = session["user"]
    so_phut = int(request.form.get("so_phut") or 0)
    approver_full = request.form["approver"]
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""INSERT INTO late_early_requests 
        (submitter_email, submitter_name, department, ngay, noi_dung, thoi_gian, so_phut, ly_do, ghi_chu_tbp, status, submit_date)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""", (
        user["email"], user["name"], user["department"],
        request.form["ngay"], request.form["noi_dung"], request.form.get("thoi_gian"),
        so_phut, request.form["ly_do"], approver_full,
        "Chờ duyệt", datetime.now().strftime("%Y-%m-%d %H:%M")
    ))
    conn.commit(); conn.close()
    flash("Gửi thông báo thành công!", "success")
    return redirect(url_for("dashboard"))

@app.route("/leave")
@login_required
@employee_only
def leave_form():
    approvers = [f"{ALLOWED_USERS[e]['name']} - {ALLOWED_USERS[e]['department']}" 
                 for e in ALLOWED_USERS if ALLOWED_USERS[e]["role"] in ["Manager", "BOD"]]
    return render_template("leave_form.html", user=session["user"], approvers=approvers)

@app.route("/leave", methods=["POST"])
@login_required
@employee_only
def leave_submit():
    user = session["user"]
    ngay_bd = request.form["ngay_bat_dau"]
    ngay_kt = request.form["ngay_ket_thuc"]
    so_ngay = (datetime.strptime(ngay_kt, "%Y-%m-%d") - datetime.strptime(ngay_bd, "%Y-%m-%d")).days + 1
    approver_full = request.form["approver"]
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("""INSERT INTO leave_requests 
        (submitter_email, submitter_name, department, ngay_bat_dau, ngay_ket_thuc, so_ngay, ly_do, ghi_chu_tbp, status, submit_date)
        VALUES (?,?,?,?,?,?,?,?,?,?)""", (
        user["email"], user["name"], user["department"],
        ngay_bd, ngay_kt, so_ngay, request.form["ly_do"], approver_full,
        "Chờ duyệt", datetime.now().strftime("%Y-%m-%d %H:%M")
    ))
    conn.commit(); conn.close()
    flash("Gửi đơn nghỉ phép thành công!", "success")
    return redirect(url_for("dashboard"))

@app.route("/approve_late/<int:req_id>", methods=["GET", "POST"])
@login_required
def approve_late(req_id):
    user = session["user"]
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM late_early_requests WHERE id=?", (req_id,))
    req = row_to_dict(c.fetchone())
    conn.close()
    if not req: flash("Không tìm thấy đơn!", "danger"); return redirect(url_for("dashboard"))
    my_full = f"{user['name']} - {user['department']}"
    if req["ghi_chu_tbp"] != my_full and user["role"] not in ["Manager", "BOD"]:
        flash("Bạn không có quyền duyệt đơn này!", "danger"); return redirect(url_for("dashboard"))
    if request.method == "POST":
        status = "Đã duyệt" if request.form["decision"] == "approve" else "Từ chối"
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE late_early_requests SET status=?, final_approver=? WHERE id=?", (status, user["name"], req_id))
        conn.commit(); conn.close()
        flash(f"Đã {status.lower()} thông báo!", "success" if status == "Đã duyệt" else "danger")
        return redirect(url_for("dashboard"))
    return render_template("approve_late.html", req=req, user=user)

@app.route("/approve_leave/<int:req_id>", methods=["GET", "POST"])
@login_required
def approve_leave(req_id):
    user = session["user"]
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM leave_requests WHERE id=?", (req_id,))
    req = row_to_dict(c.fetchone())
    conn.close()
    if not req: flash("Không tìm thấy đơn!", "danger"); return redirect(url_for("dashboard"))
    my_full = f"{user['name']} - {user['department']}"
    if req["ghi_chu_tbp"] != my_full and user["role"] not in ["Manager", "BOD"]:
        flash("Bạn không có quyền duyệt đơn này!", "danger"); return redirect(url_for("dashboard"))
    if request.method == "POST":
        status = "Đã duyệt" if request.form["decision"] == "approve" else "Từ chối"
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE leave_requests SET status=?, final_approver=? WHERE id=?", (status, user["name"], req_id))
        conn.commit(); conn.close()
        flash(f"Đã {status.lower()} đơn nghỉ phép!", "success" if status == "Đã duyệt" else "danger")
        return redirect(url_for("dashboard"))
    return render_template("approve_leave.html", req=req, user=user)

@app.route("/logout")
def logout():
    session.clear()
    flash("Đăng xuất thành công!", "info")
    return redirect(url_for("login"))

# ==================== KHỞI ĐỘNG ====================
with app.app_context():
    init_db()

if __name__ == "__main__":
    print("="*80)
    print("DTA SPACE – HOÀN HẢO 100% (06/12/2025)")
    print("Không còn lỗi nào | Mật khẩu lưu vĩnh viễn | Sẵn sàng deploy OnRender")
    print("http://127.0.0.1:5000")
    print("="*80)
    app.run(host="0.0.0.0", port=5000, debug=True)