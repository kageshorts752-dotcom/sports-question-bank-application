from flask import Flask, render_template, request, redirect, url_for, flash, Response
import sqlite3, csv, io, os, shutil

app = Flask(__name__)
# Use an env secret in production; the demo fallback is only for local use.
app.secret_key = os.environ.get("SECRET_KEY", "sports-question-bank-demo")

# Vercel's deployment filesystem is read-only except /tmp, and serverless
# instances are ephemeral, so writes to a bundled questions.db would fail.
# On Vercel, seed a writable copy in /tmp on first load; locally, use the
# bundled file next to app.py. Note: adds/edits on the live site therefore
# last only for that serverless instance's lifetime — a hosted database
# (e.g. Vercel Postgres / Turso) is needed for permanent shared storage.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BUNDLED_DB = os.path.join(BASE_DIR, "questions.db")
if os.environ.get("VERCEL"):
    DB = "/tmp/questions.db"
    if not os.path.exists(DB) and os.path.exists(BUNDLED_DB):
        shutil.copyfile(BUNDLED_DB, DB)
else:
    DB = BUNDLED_DB

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            course TEXT NOT NULL,
            semester TEXT NOT NULL,
            subject TEXT NOT NULL,
            unit TEXT NOT NULL,
            topic TEXT NOT NULL,
            question_type TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            marks INTEGER NOT NULL,
            bloom TEXT NOT NULL,
            tags TEXT,
            question TEXT NOT NULL,
            answer TEXT
        )
    """)
    count = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    if count == 0:
        sample = [
            ("BCA Sports Technology","VI","Sports Analytics","Unit 1","Introduction to Sports Analytics","MCQ","Easy",2,"Remember","analytics,basic","What is sports analytics?","Use of data to understand and improve sports performance."),
            ("BCA Sports Technology","VI","Kinesiology","Unit 2","Planes and Axes","Short Answer","Easy",2,"Understand","kinesiology,planes","Name the three anatomical planes.","Sagittal, frontal and transverse planes."),
            ("BCA Sports Technology","VI","Sports Biomechanics","Unit 3","Force","Long Answer","Medium",5,"Analyze","force,biomechanics","Explain the role of force in sports performance.","Force can change motion and is analysed using magnitude and direction."),
            ("BCA Sports Technology","VI","Sports Management","Unit 4","Tournament Management","MCQ","Medium",2,"Apply","tournament,management","Which module stores match results?","Result management module.")
        ]
        conn.executemany("""INSERT INTO questions
            (course,semester,subject,unit,topic,question_type,difficulty,marks,bloom,tags,question,answer)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""", sample)
    conn.commit()
    conn.close()

@app.route("/")
def index():
    conn = get_db()
    q = request.args.get("q","").strip()
    subject = request.args.get("subject","").strip()
    difficulty = request.args.get("difficulty","").strip()
    qtype = request.args.get("question_type","").strip()
    bloom = request.args.get("bloom","").strip()

    sql = "SELECT * FROM questions WHERE 1=1"
    params = []
    if q:
        sql += " AND (question LIKE ? OR topic LIKE ? OR tags LIKE ?)"
        params += [f"%{q}%", f"%{q}%", f"%{q}%"]
    if subject:
        sql += " AND subject=?"; params.append(subject)
    if difficulty:
        sql += " AND difficulty=?"; params.append(difficulty)
    if qtype:
        sql += " AND question_type=?"; params.append(qtype)
    if bloom:
        sql += " AND bloom=?"; params.append(bloom)
    sql += " ORDER BY id DESC"
    rows = conn.execute(sql, params).fetchall()
    subjects = [r[0] for r in conn.execute("SELECT DISTINCT subject FROM questions ORDER BY subject")]
    conn.close()
    return render_template("index.html", questions=rows, subjects=subjects,
                           filters=request.args)

@app.route("/add", methods=["GET","POST"])
def add():
    if request.method == "POST":
        data = request.form
        conn = get_db()
        conn.execute("""INSERT INTO questions
            (course,semester,subject,unit,topic,question_type,difficulty,marks,bloom,tags,question,answer)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?)""",
            (data["course"],data["semester"],data["subject"],data["unit"],data["topic"],
             data["question_type"],data["difficulty"],int(data["marks"]),data["bloom"],
             data["tags"],data["question"],data["answer"]))
        conn.commit(); conn.close()
        flash("Question added successfully.")
        return redirect(url_for("index"))
    return render_template("form.html", title="Add Question", question=None)

@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id):
    conn = get_db()
    if request.method == "POST":
        data = request.form
        conn.execute("""UPDATE questions SET course=?,semester=?,subject=?,unit=?,topic=?,
            question_type=?,difficulty=?,marks=?,bloom=?,tags=?,question=?,answer=? WHERE id=?""",
            (data["course"],data["semester"],data["subject"],data["unit"],data["topic"],
             data["question_type"],data["difficulty"],int(data["marks"]),data["bloom"],
             data["tags"],data["question"],data["answer"],id))
        conn.commit(); conn.close()
        flash("Question updated successfully.")
        return redirect(url_for("index"))
    row = conn.execute("SELECT * FROM questions WHERE id=?", (id,)).fetchone()
    conn.close()
    return render_template("form.html", title="Edit Question", question=row)

@app.route("/delete/<int:id>", methods=["POST"])
def delete(id):
    conn = get_db()
    conn.execute("DELETE FROM questions WHERE id=?", (id,))
    conn.commit(); conn.close()
    flash("Question deleted.")
    return redirect(url_for("index"))

@app.route("/export")
def export():
    conn = get_db()
    rows = conn.execute("SELECT * FROM questions ORDER BY id").fetchall()
    conn.close()
    out = io.StringIO()
    writer = csv.writer(out)
    writer.writerow(["ID","Course","Semester","Subject","Unit","Topic","Type","Difficulty","Marks","Bloom","Tags","Question","Answer"])
    for r in rows:
        writer.writerow(list(r))
    return Response(out.getvalue(), mimetype="text/csv",
                    headers={"Content-Disposition":"attachment;filename=question_bank.csv"})

@app.route("/question-set")
def question_set():
    conn = get_db()
    rows = conn.execute("SELECT * FROM questions ORDER BY RANDOM() LIMIT 10").fetchall()
    conn.close()
    return render_template("question_set.html", questions=rows)

# Initialise on import too, not only under __main__: Vercel imports the
# app via api/index.py and never runs the __main__ block, so without this
# a fresh database would have no questions table at all.
init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)),
            debug=not os.environ.get("VERCEL"))
