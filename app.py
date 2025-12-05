# app.py – DTA SPACE FINAL VERSION (05/12/2025)
# BOD: Chỉ duyệt + xem toàn bộ đơn | Không gửi đơn | Không thấy "ĐƠN TÔI ĐÃ GỬI"

from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from datetime import datetime
import sqlite3
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(24)
DB_NAME = "off_database.db"

# ==================== DANH SÁCH NGƯỜI DÙNG ====================
USERS = {
    "truongkhuong@dieutuongam.com": {"name": "TRƯƠNG HUỆ KHƯƠNG",       "role": "BOD",      "department": "BOD",                     "password": "123456"},
    "hongtuyet@dieutuongam.com":   {"name": "NGUYỄN THỊ HỒNG TUYẾT",   "role": "BOD",      "department": "BOD",                    "password": "123456"},
    "it@dieutuongam.com":          {"name": "TRẦN CÔNG KHÁNH",         "role": "Employee", "department": "PHÒNG HCNS-IT",           "password": "123456"},
    "anthanh@dieutuongam.com":     {"name": "NGUYỄN THỊ AN THANH",     "role": "Manager",  "department": "PHÒNG HCNS-IT",           "password": "123456"},
    "hcns@dieutuongam.com":        {"name": "NHÂN SỰ DTA",             "role": "Employee", "department": "PHÒNG HCNS-IT",           "password": "123456"},
    "yennhi@dieutuongam.com":      {"name": "TRẦN NGỌC YẾN NHI",       "role": "Employee", "department": "PHÒNG HCNS-IT",           "password": "123456"},
    "ketoan@dieutuongam.com":      {"name": "LÊ THỊ MAI ANH",          "role": "Manager",  "department": "PHÒNG TÀI CHÍNH KẾ TOÁN", "password": "123456"},
    "xuanhoa@dieutuongam.com":     {"name": "LÊ XUÂN HOA",             "role": "Manager",  "department": "PHÒNG KINH DOANH HCM",    "password": "123456"},
    "thoainha@dieutuongam.com":    {"name": "TRẦN THOẠI NHÃ",          "role": "Manager",  "department": "PHÒNG KINH DOANH HCM",    "password": "123456"},
}

# ==================== HELPER FUNCTIONS ====================
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def row_to_dict(row):
    return dict(row) if row else None

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated

# Chỉ Employee & Manager mới được gửi đơn – BOD bị chặn
def employee_only(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if session["user"]["role"] == "BOD":
            flash("Tài khoản BOD không được phép gửi đơn.", "warning")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)
    return decorated

def is_default_password(email):
    return USERS.get(email, {}).get("password") == "123456"

# ==================== KHỞI TẠO DATABASE ====================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
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

# ==================== ROUTES ====================

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        if email in USERS and USERS[email]["password"] == password:
            session["user"] = {
                "email": email,
                "name": USERS[email]["name"],
                "role": USERS[email]["role"],
                "department": USERS[email]["department"]
            }
            if is_default_password(email):
                return redirect(url_for("force_change_password"))
            return redirect(url_for("dashboard"))

        flash("Sai email hoặc mật khẩu!", "danger")
    return render_template("login.html")

@app.route("/force_change_password", methods=["GET", "POST"])
@login_required
def force_change_password():
    email = session["user"]["email"]
    if not is_default_password(email):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        new_password = request.form["new_password"]
        confirm = request.form["confirm_password"]

        if new_password != confirm:
            flash("Mật khẩu mới không khớp!", "danger")
        elif len(new_password) < 6:
            flash("Mật khẩu phải ít nhất 6 ký tự!", "danger")
        else:
            USERS[email]["password"] = new_password
            flash("Đổi mật khẩu thành công! Chào mừng bạn đến với DTA SPACE.", "success")
            return redirect(url_for("dashboard"))

    return render_template("force_change_password.html", user=session["user"])

@app.route("/dashboard")
@login_required
def dashboard():
    user = session["user"]
    conn = get_db_connection()
    c = conn.cursor()

    # Tên đầy đủ để so sánh người duyệt
    my_full = f"{user['name']} - {user['department']}"

    # 1. ĐƠN CHỜ DUYỆT (gửi cho mình)
    c.execute("""SELECT * FROM late_early_requests 
                 WHERE ghi_chu_tbp = ? AND status = 'Chờ duyệt' 
                 ORDER BY id DESC""", (my_full,))
    late_pending = [dict(row) for row in c.fetchall()]

    c.execute("""SELECT * FROM leave_requests 
                 WHERE ghi_chu_tbp = ? AND status = 'Chờ duyệt' 
                 ORDER BY id DESC""", (my_full,))
    leave_pending = [dict(row) for row in c.fetchall()]

    # 2. ĐƠN TÔI ĐÃ GỬI (gộp 2 bảng, có submit_date thống nhất)
    c.execute("""SELECT 
                    id, 
                    'late' as type,
                    submit_date,
                    noi_dung,
                    thoi_gian,
                    so_phut,
                    ly_do,
                    status,
                    ghi_chu_tbp,
                    final_approver
                 FROM late_early_requests 
                 WHERE submitter_email = ? 
                 ORDER BY submit_date DESC LIMIT 20""", (user["email"],))
    my_late = [dict(row) for row in c.fetchall()]

    c.execute("""SELECT 
                    id,
                    'leave' as type,
                    submit_date,
                    ngay_bat_dau,
                    ngay_ket_thuc,
                    so_ngay,
                    ly_do,
                    status,
                    ghi_chu_tbp,
                    final_approver
                 FROM leave_requests 
                 WHERE submitter_email = ? 
                 ORDER BY submit_date DESC LIMIT 20""", (user["email"],))
    my_leave = [dict(row) for row in c.fetchall()]

    my_requests = my_late + my_leave
    my_requests.sort(key=lambda x: x.get('submit_date', ''), reverse=True)

    # 3. TẤT CẢ ĐƠN (chỉ Manager & BOD thấy)
    all_requests = []
    if user["role"] in ["Manager", "BOD"]:
        c.execute("SELECT *, 'late' as type FROM late_early_requests ORDER BY submit_date DESC")
        all_late = [dict(row) for row in c.fetchall()]
        c.execute("SELECT *, 'leave' as type FROM leave_requests ORDER BY submit_date DESC")
        all_leave = [dict(row) for row in c.fetchall()]
        all_requests = all_late + all_leave
        all_requests.sort(key=lambda x: x.get('submit_date', ''), reverse=True)

    conn.close()

    return render_template("dntu_dashboard.html",
                           user=user,
                           late_pending=late_pending,
                           leave_pending=leave_pending,
                           my_requests=my_requests,
                           all_requests=all_requests)
# ==================== GỬI ĐƠN (CHỈ EMPLOYEE & MANAGER) ====================
@app.route("/late_early", methods=["GET", "POST"])
@login_required
@employee_only
def late_early_form():
    if request.method == "GET":
        approvers = [f"{v['name']} - {v['department']}" for k, v in USERS.items() if v["role"] in ["Manager", "BOD"]]
        return render_template("late_early_form.html", user=session["user"], approvers=approvers)

    # POST – Gửi đơn
    user = session["user"]
    approver_full = request.form["approver"]
    so_phut = int(request.form.get("so_phut") or 0)

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
    conn.commit()
    conn.close()
    flash("Gửi thông báo đi trễ/về sớm thành công!", "success")
    return redirect(url_for("dashboard"))

@app.route("/leave")
@login_required
@employee_only
def leave_form():
    approvers = [f"{v['name']} - {v['department']}" for k, v in USERS.items() if v["role"] in ["Manager", "BOD"]]
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
    conn.commit()
    conn.close()
    flash("Gửi đơn nghỉ phép thành công!", "success")
    return redirect(url_for("dashboard"))

# ==================== DUYỆT ĐƠN (Manager & BOD đều được duyệt) ====================
@app.route("/approve_late/<int:req_id>", methods=["GET", "POST"])
@login_required
def approve_late(req_id):
    user = session["user"]
    conn = get_db_connection()
    c = conn.cursor()
    c.execute("SELECT * FROM late_early_requests WHERE id=?", (req_id,))
    req = row_to_dict(c.fetchone())
    conn.close()
    if not req:
        flash("Không tìm thấy đơn!", "danger")
        return redirect(url_for("dashboard"))

    my_full = f"{user['name']} - {user['department']}"
    if req["ghi_chu_tbp"] != my_full and user["role"] not in ["Manager", "BOD"]:
        flash("Bạn không có quyền duyệt đơn này!", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        decision = request.form["decision"]
        status = "Đã duyệt" if decision == "approve" else "Từ chối"
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE late_early_requests SET status=?, final_approver=? WHERE id=?", 
                  (status, user["name"], req_id))
        conn.commit()
        conn.close()
        flash(f"Đã {status.lower()} thông báo!", "success" if decision == "approve" else "danger")
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
    if not req:
        flash("Không tìm thấy đơn!", "danger")
        return redirect(url_for("dashboard"))

    my_full = f"{user['name']} - {user['department']}"
    if req["ghi_chu_tbp"] != my_full and user["role"] not in ["Manager", "BOD"]:
        flash("Bạn không có quyền duyệt đơn này!", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        decision = request.form["decision"]
        status = "Đã duyệt" if decision == "approve" else "Từ chối"
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE leave_requests SET status=?, final_approver=? WHERE id=?", 
                  (status, user["name"], req_id))
        conn.commit()
        conn.close()
        flash(f"Đã {status.lower()} đơn nghỉ phép!", "success" if decision == "approve" else "danger")
        return redirect(url_for("dashboard"))

    return render_template("approve_leave.html", req=req, user=user)

@app.route("/logout")
def logout():
    session.clear()
    flash("Đăng xuất thành công!", "info")
    return redirect(url_for("login"))

# ==================== CHẠY ỨNG DỤNG ====================
if __name__ == "__main__":
    init_db()
    print("="*80)
    print("DTA SPACE – PHIÊN BẢN HOÀN CHỈNH CUỐI CÙNG (05/12/2025)")
    print("BOD: Chỉ duyệt + xem toàn bộ | Không gửi đơn | Không thấy 'ĐƠN TÔI ĐÃ GỬI'")
    print("http://127.0.0.1:5000")
    print("="*80)
    app.run(host="0.0.0.0", port=5000, debug=True)