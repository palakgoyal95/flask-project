from flask import Flask, render_template, request, redirect,session,Response,jsonify
import csv
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = "superecretkey"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
# ✅ STEP 1: DEFINE get_db FIRST
def get_db():
    return sqlite3.connect(DB_PATH)


# ✅ STEP 2: CREATE TABLE
def create_table():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            rating INTEGER,
            comments TEXT,
            date_submitted TEXT
        );
    """)
    conn.commit()
    conn.close()


create_table()

# ✅ STEP 3: ROUTES
@app.route("/")
def home():
    return render_template("index.html")

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form["name"]
    email = request.form["email"]
    rating = request.form["rating"]
    comments = request.form["comments"]
    date = datetime.now().strftime("%Y-%m-%d %H:%M")

    conn = get_db()
    conn.execute(
        "INSERT INTO feedback (name, email, rating, comments, date_submitted) VALUES (?, ?, ?, ?, ?)",
        (name, email, rating, comments, date)
    )
    conn.commit()
    conn.close()

    return redirect("/")



@app.route("/admin")
def admin():
    if not session.get("admin"):
        return redirect("/login")
    conn = get_db()
    data = conn.execute("SELECT * FROM feedback").fetchall()
    total = len(data)
    avg_rating = conn.execute("SELECT AVG(rating) FROM feedback").fetchone()[0]
    ratings = conn.execute("""
        SELECT rating, COUNT(*) 
        FROM feedback 
        GROUP BY rating
    """).fetchall()
    conn.close()
     # Prepare data for chart
    rating_labels = [str(r[0]) for r in ratings]
    rating_counts = [r[1] for r in ratings]
    return render_template("admin.html", 
                           feedbacks=data, total=total, 
                           avg_rating=round(avg_rating, 2) if avg_rating else 0,
                           labels=rating_labels,
                           counts=rating_counts)
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Simple hardcoded admin credentials
        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect("/admin")
        else:
            return render_template("login.html", error="Invalid credentials")

    return render_template("login.html")
@app.route("/logout")
def logout():
    session.pop("admin", None)
    return redirect("/login")
@app.route("/export-csv")
def export_csv():
    if not session.get("admin"):
        return redirect("/login")

    conn = get_db()
    feedbacks = conn.execute("SELECT * FROM feedback").fetchall()
    conn.close()

    def generate():
        data = []
        header = ["ID", "Name", "Email", "Rating", "Comments", "Date"]
        data.append(header)

        for f in feedbacks:
            data.append([
                f[0], f[1], f[2], f[3], f[4], f[5]
            ])

        for row in data:
            yield ",".join(map(str, row)) + "\n"

    return Response(
        generate(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": "attachment;filename=feedback.csv"
        }
    )
@app.route("/api/feedback", methods=["GET"])
def api_feedback():
    conn = get_db()
    rows = conn.execute("SELECT * FROM feedback").fetchall()
    conn.close()

    data = []
    for r in rows:
        data.append({
            "id": r[0],
            "name": r[1],
            "email": r[2],
            "rating": r[3],
            "comments": r[4],
            "date_submitted": r[5]
        })

    return jsonify(data)
   


if __name__ == "__main__":
    app.run()
