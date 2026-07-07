from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash

from database import init_db, get_connection
from agents.time_management_agent import allocate_hours
from agents.planning_agent import generate_schedule
from agents.revision_agent import apply_revision
from agents.motivation_agent import get_daily_tip

app = Flask(__name__)
app.secret_key = "change-this-secret-key-in-production"


# ---------------------------------------------------------------
# Helper
# ---------------------------------------------------------------
def login_required(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please log in first.", "warning")
            return redirect(url_for("login"))
        return func(*args, **kwargs)
    return wrapper


# ---------------------------------------------------------------
# Auth Routes
# ---------------------------------------------------------------
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        conn = get_connection()
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            flash("An account with this email already exists.", "danger")
            conn.close()
            return redirect(url_for("register"))

        password_hash = generate_password_hash(password)
        conn.execute(
            "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
            (name, email, password_hash),
        )
        conn.commit()
        conn.close()

        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        conn = get_connection()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["user_name"] = user["name"]
            return redirect(url_for("dashboard"))

        flash("Invalid email or password.", "danger")
        return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("index"))


# ---------------------------------------------------------------
# Dashboard + Plan Generation
# ---------------------------------------------------------------
@app.route("/dashboard", methods=["GET", "POST"])
@login_required
def dashboard():
    if request.method == "POST":
        exam_date = request.form["exam_date"]
        daily_hours = float(request.form["daily_hours"])

        subject_names = request.form.getlist("subject_name[]")
        subject_priorities = request.form.getlist("subject_priority[]")

        subjects_with_priority = [
            {"name": name.strip(), "priority": int(priority)}
            for name, priority in zip(subject_names, subject_priorities)
            if name.strip()
        ]

        if not subjects_with_priority:
            flash("Please add at least one subject.", "warning")
            return redirect(url_for("dashboard"))

        # ---- Multi-agent pipeline ----
        # 1) Time Management Agent -> per-subject daily hour allocation
        hours_per_subject = allocate_hours(subjects_with_priority, daily_hours)

        # 2) Planning Agent -> day-wise schedule
        schedule, total_days = generate_schedule(
            subjects_with_priority, exam_date, hours_per_subject
        )

        # 3) Revision Agent -> mark revision days near the exam
        schedule = apply_revision(schedule, total_days)

        # 4) Motivation Agent -> daily tip
        for day in schedule:
            day["tip"] = get_daily_tip(day["day_number"])

        # ---- Save to DB ----
        conn = get_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO plans (user_id, exam_date, daily_hours) VALUES (?, ?, ?)",
            (session["user_id"], exam_date, daily_hours),
        )
        plan_id = cur.lastrowid

        for day in schedule:
            for sess in day["sessions"]:
                cur.execute(
                    """INSERT INTO plan_days
                       (plan_id, day_number, date, subject, hours, session_type, tip)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        plan_id, day["day_number"], day["date"],
                        sess["subject"], sess["hours"], day["session_type"], day["tip"],
                    ),
                )
        conn.commit()
        conn.close()

        return redirect(url_for("view_plan", plan_id=plan_id))

    conn = get_connection()
    past_plans = conn.execute(
        "SELECT * FROM plans WHERE user_id = ? ORDER BY created_at DESC",
        (session["user_id"],),
    ).fetchall()
    conn.close()

    return render_template("dashboard.html", past_plans=past_plans)


@app.route("/plan/<int:plan_id>")
@login_required
def view_plan(plan_id):
    conn = get_connection()
    plan = conn.execute("SELECT * FROM plans WHERE id = ?", (plan_id,)).fetchone()

    if plan is None or plan["user_id"] != session["user_id"]:
        conn.close()
        flash("Plan not found.", "danger")
        return redirect(url_for("dashboard"))

    rows = conn.execute(
        "SELECT * FROM plan_days WHERE plan_id = ? ORDER BY day_number",
        (plan_id,),
    ).fetchall()
    conn.close()

    # Group rows day-wise for the template
    days = {}
    for row in rows:
        d = days.setdefault(row["day_number"], {
            "date": row["date"],
            "session_type": row["session_type"],
            "tip": row["tip"],
            "sessions": [],
        })
        d["sessions"].append({"subject": row["subject"], "hours": row["hours"]})

    ordered_days = [
        {"day_number": num, **info} for num, info in sorted(days.items())
    ]

    return render_template("plan.html", plan=plan, days=ordered_days)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
