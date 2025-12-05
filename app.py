# app.py – DTA SPACE FINAL VERSION (05/12/2025) – ĐÃ THÊM BẮT BUỘC ĐỔI MẬT KHẨU LẦN ĐẦU
# Tính năng: Đi trễ/Về sớm + Nghỉ phép + Đổi mật khẩu + BẮT BUỘC đổi mật khẩu lần đầu

from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from datetime import datetime
import sqlite3
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
DB_NAME = "off_database.db"

# ==================== DANH SÁCH USER ====================
USERS = {
    "truongkhuong@dieutuongam.com": {"name": "TRƯƠNG HUỆ KHƯƠNG",       "role": "BOD",      "department": "BOD",                     "password": "123456"},
    "hongtuyet@dieutuongam.com":   {"name": "NGUYỄN THỊ HỒNG TUYẾT",   "role": "BOD",      "department": "BOD",                    "password": "123456"},
    "it@dieutuongam.com":          {"name": "TRẦN CÔNG KHÁNH",         "role": "Employee", "department": "PHÒNG HCNS-IT",           "password": "123456"},
    "anthanh@dieutuongam.com":     {"name": "NGUYỄN THỊ AN THANH",       "role": "Manager",  "department": "PHÒNG HCNS-IT",           "password": "123456"},
    "hcns@dieutuongam.com":        {"name": "NHÂN SỰ DTA",             "role": "Employee", "department": "PHÒNG HCNS-IT",           "password": "123456"},
    "yennhi@dieutuongam.com":      {"name": "TRẦN NGỌC YẾN NHI",       "role": "Employee", "department": "PHÒNG HCNS-IT",           "password": "123456"},
    "ketoan@dieutuongam.com":      {"name": "LÊ THỊ MAI ANH",           "role": "Manager",  "department": "PHÒNG TÀI CHÍNH KẾ TOÁN",  "password": "123456"},
    "xuanhoa@dieutuongam.com":     {"name": "LÊ XUÂN HOA",              "role": "Manager",  "department": "PHÒNG KINH DOANH HCM",    "password": "123456"},
    "thoainha@dieutuongam.com":    {"name": "TRẦN THOẠI NHÃ",           "role": "Manager",  "department": "PHÒNG KINH DOANH HCM",    "password": "123456"},
}

# ==================== HELPER ====================
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

def is_default_password(email):
    """Kiểm tra xem user còn dùng mật khẩu mặc định không"""
    return USERS.get(email, {}).get("password") == "123456"

# ==================== TẠO DATABASE ====================
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS late_early_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        submitter_email TEXT,
        submitter_name TEXT,
        department TEXT,
        ngay TEXT,
        noi_dung TEXT,
        thoi_gian TEXT,
        so_phut INTEGER,
        ly_do TEXT,
        ghi_chu_tbp TEXT,
        final_approver TEXT,
        status TEXT DEFAULT 'Chờ duyệt',
        submit_date TEXT
    )''')

    c.execute('''CREATE TABLE IF NOT EXISTS leave_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        submitter_email TEXT,
        submitter_name TEXT,
        department TEXT,
        ngay_bat_dau TEXT,
        ngay_ket_thuc TEXT,
        so_ngay INTEGER,
        ly_do TEXT,
        ghi_chu_tbp TEXT,
        final_approver TEXT,
        status TEXT DEFAULT 'Chờ duyệt',
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

            # BẮT BUỘC đổi mật khẩu lần đầu nếu còn 123456
            if is_default_password(email):
                flash("Đây là lần đăng nhập đầu tiên. Bạn bắt buộc phải đổi mật khẩu để tiếp tục!", "warning")
                return redirect(url_for("force_change_password"))

            return redirect(url_for("dashboard"))

        flash("Sai email hoặc mật khẩu!", "danger")
    return render_template("login.html")

# ==================== BẮT BUỘC ĐỔI MẬT KHẨU LẦN ĐẦU ====================
@app.route("/force_change_password", methods=["GET", "POST"])
@login_required
def force_change_password():
    user_email = session["user"]["email"]

    # Nếu đã đổi rồi thì không cho vào trang này nữa
    if not is_default_password(user_email):
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        new_pass = request.form["new_password"]
        confirm_pass = request.form["confirm_password"]

        if new_pass != confirm_pass:
            flash("Mật khẩu xác nhận không khớp!", "danger")
        elif len(new_pass) < 6:
            flash("Mật khẩu mới phải có ít nhất 6 ký tự!", "danger")
        else:
            USERS[user_email]["password"] = new_pass
            flash("Đổi mật khẩu thành công! Chào mừng bạn đến với DTA SPACE!", "success")
            return redirect(url_for("dashboard"))

    return render_template("force_change_password.html", user=session["user"])

# ==================== ĐỔI MẬT KHẨU THƯỜNG (các lần sau) ====================
@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    user_email = session["user"]["email"]

    if request.method == "POST":
        new_pass = request.form["new_password"]
        confirm_pass = request.form["confirm_password"]

        if new_pass != confirm_pass:
            flash("Mật khẩu xác nhận không khớp!", "danger")
        elif len(new_pass) < 6:
            flash("Mật khẩu mới phải có ít nhất 6 ký tự!", "danger")
        else:
            USERS[user_email]["password"] = new_pass
            flash("Đổi mật khẩu thành công!", "success")
            return redirect(url_for("dashboard"))

    return render_template("change_password.html", user=session["user"])

# ==================== DASHBOARD ====================
@app.route("/dashboard")
@login_required
def dashboard():
    user = session["user"]
    my_full = f"{user['name']} - {user['department']}"

    conn = get_db_connection()
    c = conn.cursor()

    # 1. ĐƠN CHỜ DUYỆT CỦA MÌNH
    c.execute("SELECT * FROM late_early_requests WHERE ghi_chu_tbp=? AND status='Chờ duyệt'", (my_full,))
    late_pending = [row_to_dict(r) for r in c.fetchall()]

    c.execute("SELECT * FROM leave_requests WHERE ghi_chu_tbp=? AND status='Chờ duyệt'", (my_full,))
    leave_pending = [row_to_dict(r) for r in c.fetchall()]

    # 2. ĐƠN CỦA TÔI ĐÃ GỬI (20 đơn gần nhất)
    c.execute("""
        SELECT 'late' AS type, id, submit_date AS ngay_gui, noi_dung, thoi_gian, so_phut, ly_do,
               status, final_approver, ghi_chu_tbp,
               NULL AS ngay_bat_dau, NULL AS ngay_ket_thuc, NULL AS so_ngay
        FROM late_early_requests WHERE submitter_email = ?
        UNION ALL
        SELECT 'leave' AS type, id, submit_date AS ngay_gui, NULL, NULL, NULL, ly_do,
               status, final_approver, ghi_chu_tbp,
               ngay_bat_dau, ngay_ket_thuc, so_ngay
        FROM leave_requests WHERE submitter_email = ?
        ORDER BY ngay_gui DESC LIMIT 20
    """, (user["email"], user["email"]))
    my_requests = [row_to_dict(r) for r in c.fetchall()]

    # 3. TẤT CẢ ĐƠN TRONG CÔNG TY (Manager & BOD)
    all_requests = []
    if user["role"] in ["Manager", "BOD"]:
        c.execute("""
            SELECT 'late' AS type, 
                   id, submitter_name, department, submit_date,
                   ngay AS ngay, noi_dung, thoi_gian, so_phut, ly_do,
                   status, final_approver, ghi_chu_tbp
            FROM late_early_requests
            UNION ALL
            SELECT 'leave' AS type,
                   id, submitter_name, department, submit_date,
                   ngay_bat_dau || ' → ' || ngay_ket_thuc AS ngay, 
                   'Nghỉ phép ' || so_ngay || ' ngày' AS noi_dung,
                                     NULL, so_ngay, ly_do,
                   status, final_approver, ghi_chu_tbp
            FROM leave_requests
            ORDER BY submit_date DESC
        """)
        all_requests = [row_to_dict(r) for r in c.fetchall()]

    conn.close()

    return render_template("dntu_dashboard.html",
                           user=user,
                           late_pending=late_pending,
                           leave_pending=leave_pending,
                           my_requests=my_requests,
                           all_requests=all_requests)

# ==================== CÁC ROUTE KHÁC (giữ nguyên, đã test ổn định) ====================
@app.route("/late_early")
@login_required
def late_early_form():
    approvers = [f"{v['name']} - {v['department']}" for k, v in USERS.items() if v["role"] in ["Manager", "BOD"]]
    return render_template("late_early_form.html", user=session["user"], approvers=approvers)

@app.route("/late_early", methods=["POST"])
@login_required
def late_early_submit():
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
    flash("Gửi thông báo thành công!", "success")
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
    if not req:
        flash("Không tìm thấy!", "danger")
        return redirect(url_for("dashboard"))

    my_full = f"{user['name']} - {user['department']}"
    if req["ghi_chu_tbp"] != my_full and user["role"] not in ["Manager", "BOD"]:
        flash("Không có quyền!", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        decision = request.form["decision"]
        new_status = "Đã duyệt" if decision == "approve" else "Từ chối"
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE late_early_requests SET status=?, final_approver=? WHERE id=?", 
                  (new_status, user["name"], req_id))
        conn.commit()
        conn.close()
        flash(f"Đã {new_status.lower()}!", "success" if decision == "approve" else "danger")
        return redirect(url_for("dashboard"))

    return render_template("approve_late.html", req=req, user=user)

@app.route("/leave")
@login_required
def leave_form():
    approvers = [f"{v['name']} - {v['department']}" for k, v in USERS.items() if v["role"] in ["Manager", "BOD"]]
    return render_template("leave_form.html", user=session["user"], approvers=approvers)

@app.route("/leave", methods=["POST"])
@login_required
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
        flash("Không tìm thấy!", "danger")
        return redirect(url_for("dashboard"))

    my_full = f"{user['name']} - {user['department']}"
    if req["ghi_chu_tbp"] != my_full and user["role"] not in ["Manager", "BOD"]:
        flash("Không có quyền!", "danger")
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        decision = request.form["decision"]
        new_status = "Đã duyệt" if decision == "approve" else "Từ chối"
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("UPDATE leave_requests SET status=?, final_approver=? WHERE id=?", 
                  (new_status, user["name"], req_id))
        conn.commit()
        conn.close()
        flash(f"Đã {new_status.lower()} đơn nghỉ phép!", "success" if decision == "approve" else "danger")
        return redirect(url_for("dashboard"))

    return render_template("approve_leave.html", req=req, user=user)

@app.route("/logout")
def logout():
    session.clear()
    flash("Đã đăng xuất thành công!", "info")
    return redirect(url_for("login"))

# ==================== CHẠY APP ====================
if __name__ == "__main__":
    init_db()
    print("="*80)
    print("DTA SPACE – PHIÊN BẢN HOÀN CHỈNH MỚI NHẤT (05/12/2025)")
    print("→ ĐÃ THÊM: BẮT BUỘC ĐỔI MẬT KHẨU LẦN ĐẦU TIÊN")
    print("→ http://127.0.0.1:5000")
    print("="*80)
    app.run(host="0.0.0.0", port=5000, debug=True)