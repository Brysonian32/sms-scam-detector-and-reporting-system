import sqlite3
from flask import Blueprint, request, render_template, redirect, url_for, session, flash

reports = Blueprint("reports", __name__)

def get_db():
    conn = sqlite3.connect("scams.db")
    conn.row_factory = sqlite3.Row
    return conn

SCAM_TYPES = {
    "device": [
        "SMS Fraud",
        "Phishing (Email/Link)",
        "Romance Scam",
        "Fake Investment",
        "Impersonation",
        "Fake Job Offer"
    ],
    "in_person": [
        "Con Artist",
        "Fake Product/Service",
        "Impersonation",
        "Fake Emergency"
    ]
}

@reports.route("/community")
def community():
    db = get_db()
    all_reports = db.execute("""
        SELECT reports.*, users.username
        FROM reports
        JOIN users ON reports.user_id = users.id
        WHERE reports.status = 'approved'
        ORDER BY reports.created_at DESC
    """).fetchall()

    # Get comment counts per report
    comment_counts = {}
    for report in all_reports:
        count = db.execute(
            "SELECT COUNT(*) as cnt FROM comments WHERE report_id = ?",
            (report["id"],)
        ).fetchone()["cnt"]
        comment_counts[report["id"]] = count

    db.close()
    return render_template("community.html",
                           reports=all_reports,
                           comment_counts=comment_counts)


@reports.route("/report", methods=["GET", "POST"])
def report():
    if not session.get("user_id"):
        flash("You must be logged in to report a scam.", "error")
        return redirect(url_for("auth.login"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        delivery_method = request.form.get("delivery_method", "").strip()
        scam_type = request.form.get("scam_type", "").strip()
        description = request.form.get("description", "").strip()
        date_occurred = request.form.get("date_occurred", "").strip()
        scammer_contact = request.form.get("scammer_contact", "").strip()
        location = request.form.get("location", "").strip()

        if not all([title, delivery_method, scam_type, description, date_occurred]):
            flash("All fields are required.", "error")
            return render_template("report.html", scam_types=SCAM_TYPES)

        db = get_db()
        
        db.execute("""
            INSERT INTO reports (user_id, title, delivery_method, scam_type, description, date_occurred, scammer_contact, location)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (session["user_id"], title, delivery_method, scam_type, description, date_occurred, scammer_contact, location))
        db.commit()
        db.close()

        flash("Scam reported successfully. It will appear after admin approval.", "success")
        return redirect(url_for("reports.community"))

    return render_template("report.html", scam_types=SCAM_TYPES)


@reports.route("/scam/<int:report_id>")
def scam_detail(report_id):
    db = get_db()
    report = db.execute("""
        SELECT reports.*, users.username
        FROM reports
        JOIN users ON reports.user_id = users.id
        WHERE reports.id = ? AND reports.status = 'approved'
    """, (report_id,)).fetchone()

    if not report:
        flash("Report not found.", "error")
        return redirect(url_for("reports.community"))

    comments = db.execute("""
        SELECT comments.*, users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.report_id = ?
        ORDER BY comments.created_at DESC
    """, (report_id,)).fetchall()

    db.close()
    return render_template("scam_detail.html", report=report, comments=comments)


@reports.route("/scam/<int:report_id>/comment", methods=["POST"])
def add_comment(report_id):
    if not session.get("user_id"):
        flash("You must be logged in to comment.", "error")
        return redirect(url_for("auth.login"))

    date_encountered = request.form.get("date_encountered", "").strip()

    if not date_encountered:
        flash("Please provide the date you encountered this scam.", "error")
        return redirect(url_for("reports.scam_detail", report_id=report_id))

    db = get_db()
    db.execute("""
        INSERT INTO comments (report_id, user_id, date_encountered)
        VALUES (?, ?, ?)
    """, (report_id, session["user_id"], date_encountered))
    db.commit()
    db.close()

    flash("Comment added successfully.", "success")
    return redirect(url_for("reports.scam_detail", report_id=report_id))