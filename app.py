from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from database import get_connection
from sha_utils import generate_hash

app = Flask(__name__)
# Fixed secret key (prevents login sessions from dropping)
app.secret_key = "secure_document_key_123" 
ADMIN_PASSWORD = "admin" 

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/team")
def team():
    return render_template("team.html")

# --- LOGIN / LOGOUT ---
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        password = request.form.get("password")
        if password == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for("dashboard"))
        else:
            return render_template("login.html", error="❌ Incorrect Password")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("is_admin", None)
    return redirect(url_for("index"))

# --- ADMIN DASHBOARD ---
@app.route("/dashboard")
def dashboard():
    if not session.get("is_admin"):
        return redirect(url_for("login"))
    return render_template("dashboard.html")

# --- REGISTER ---
@app.route("/register", methods=["GET", "POST"])
def register():
    if not session.get("is_admin"):
        return redirect(url_for("login"))

    if request.method == "POST":
        reg_no = request.form.get("reg_no")
        doc_type = request.form.get("document_type")
        file = request.files.get("file")

        if not (reg_no and doc_type and file and allowed_file(file.filename)):
            return render_template("result.html", message="❌ Invalid input or file type.", status="error", back_url=url_for('register'))

        try:
            file_hash = generate_hash(file)
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute("SELECT reg_no FROM documents WHERE hash=%s", (file_hash,))
            if cursor.fetchone():
                return render_template("result.html", message="⚠️ This document content is already registered.", status="warning", back_url=url_for('register'))

            cursor.execute("SELECT * FROM documents WHERE reg_no=%s AND doc_type=%s", (reg_no, doc_type))
            if cursor.fetchone():
                return render_template("result.html", message="⚠️ An entry for this Register Number already exists.", status="warning", back_url=url_for('register'))

            cursor.execute("INSERT INTO documents (reg_no, doc_type, hash) VALUES (%s, %s, %s)", (reg_no, doc_type, file_hash))
            conn.commit()
            return render_template("result.html", message="✅ Document Registered Successfully!", status="success", back_url=url_for('register'))
        except Exception as e:
            return render_template("result.html", message=f"❌ Error: {e}", status="error", back_url=url_for('register'))
        finally:
            if 'conn' in locals(): conn.close()
            
    return render_template("register.html")

# --- DELETE ---
@app.route("/delete", methods=["GET", "POST"])
def delete_record():
    if not session.get("is_admin"): 
        return redirect(url_for("login"))
    
    if request.method == "POST":
        reg_no = request.form.get("reg_no")
        doc_type = request.form.get("document_type")
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("DELETE FROM documents WHERE reg_no=%s AND doc_type=%s", (reg_no, doc_type))
            conn.commit()
            if cursor.rowcount > 0:
                return render_template("result.html", message=f"✅ Record for {reg_no} deleted.", status="success", back_url=url_for('delete_record'))
            return render_template("result.html", message="⚠️ No matching record found.", status="warning", back_url=url_for('delete_record'))
        finally:
            if 'conn' in locals(): conn.close()
            
    return render_template("delete.html")

# --- VERIFY ---
@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        reg_no = request.form.get("reg_no")
        doc_type = request.form.get("document_type")
        file = request.files.get("file")
        if not (reg_no and doc_type and file):
             return render_template("result.html", message="❌ Missing data.", status="error", back_url=url_for('verify'))
        try:
            u_hash = generate_hash(file)
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT hash FROM documents WHERE reg_no=%s AND doc_type=%s", (reg_no, doc_type))
            res = cursor.fetchone()
            if res and res[0] == u_hash:
                return render_template("result.html", message="✅ Authentic Document. No tampering detected.", status="success", back_url=url_for('verify'))
            return render_template("result.html", message="❌ Verification Failed.", status="error", back_url=url_for('verify'))
        finally:
            if 'conn' in locals(): conn.close()
    return render_template("verify.html")

if __name__ == "__main__":
    app.run(debug=True)