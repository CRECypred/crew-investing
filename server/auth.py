from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import jwt
import datetime
import sqlite3
import os
from dotenv import load_dotenv
load_dotenv()

auth_bp = Blueprint('auth', __name__)
SECRET_KEY = os.getenv("SECRET_KEY")

UPLOAD_FOLDER = os.path.join(os.getcwd(), "static", "avatars")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

# ----------------------
# Kayıt olma
# ----------------------
@auth_bp.route("/api/register", methods=["POST"])
def register():
    data = request.json
    full_name = data.get("full_name")
    email = data.get("email")
    username = data.get("username")
    password = data.get("password")

    if not all([full_name, email, username, password]):
        return jsonify({"error": "Tüm alanlar gereklidir"}), 400

    conn = get_db_connection()
    existing = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    if existing:
        return jsonify({"error": "Kullanıcı zaten var"}), 409

    hashed_pw = generate_password_hash(password)
    conn.execute(
        "INSERT INTO users (full_name, email, username, password, role) VALUES (?, ?, ?, ?, ?)",
        (full_name, email, username, hashed_pw, "user")
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Kayıt başarılı"}), 201

# ----------------------
# Giriş yapma
# ----------------------
@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    conn.close()

    if not user or not check_password_hash(user["password"], password):
        return jsonify({"error": "Geçersiz giriş"}), 401

    user_role = user["role"] if "role" in user.keys() else "user"

    token = jwt.encode({
        "username": username,
        "role": user_role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }, SECRET_KEY, algorithm="HS256")

    return jsonify({"token": token, "role": user_role})

# ----------------------
# Profil fotoğrafı yükleme
# ----------------------
@auth_bp.route("/api/upload-avatar", methods=["POST"])
def upload_avatar():
    username = request.form.get("username")
    file = request.files.get("file")

    if not username or not file:
        return jsonify({"error": "Eksik bilgi"}), 400

    filename = secure_filename(file.filename)
    ext = filename.rsplit('.', 1)[-1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({"error": "Sadece PNG, JPG ve JPEG destekleniyor"}), 400

    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    new_filename = f"{username}.{ext}"
    save_path = os.path.join(UPLOAD_FOLDER, new_filename)
    file.save(save_path)

    avatar_url = f"/static/avatars/{new_filename}"

    conn = get_db_connection()
    conn.execute("UPDATE users SET avatar_url = ? WHERE username = ?", (avatar_url, username))
    conn.commit()
    conn.close()

    return jsonify({"success": True, "avatar_url": avatar_url})

# ----------------------
# Kullanıcı bilgilerini alma
# ----------------------
@auth_bp.route("/api/user/<username>", methods=["GET"])
def get_user_profile(username):
    conn = get_db_connection()
    user = conn.execute(
        "SELECT full_name, email, username, role, avatar_url FROM users WHERE username = ?",
        (username,)
    ).fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "Kullanıcı bulunamadı"}), 404

    user_data = dict(user)
    # Eğer avatar_url yoksa default tanımla
    if not user_data.get("avatar_url"):
        user_data["avatar_url"] = "/static/avatars/default.png"

    return jsonify(user_data)

@auth_bp.route("/api/update-profile", methods=["POST"])
def update_profile():
    data = request.json
    username = data.get("username")
    full_name = data.get("full_name")
    email = data.get("email")

    if not all([username, full_name, email]):
        return jsonify({"error": "Eksik bilgi gönderildi"}), 400

    conn = get_db_connection()
    conn.execute(
        "UPDATE users SET full_name = ?, email = ? WHERE username = ?",
        (full_name, email, username)
    )
    conn.commit()
    conn.close()

    return jsonify({"message": "Profil bilgileri güncellendi"})
