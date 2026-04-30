import sqlite3
from flask import Blueprint, render_template, redirect, url_for, session, flash, request

admin = Blueprint("admin", __name__)

def get_db():
    conn = sqlite3.connect("scams.db")
    conn.row_factory = sqlite3.Row
    return conn

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_id") or not session.get("is_admin"):
            flash("Admin access required.", "error")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@admin.route("/admin")
@admin_required
def dashboard():
    db = get_db()
    pending = db.execute("""
        SELECT reports.*, users.username
        FROM reports
        JOIN users ON reports.user_id = users.id
        WHERE reports.status = 'pending'
        ORDER BY reports.created_at DESC
    """).fetchall()

    approved = db.execute("""
        SELECT reports.*, users.username
        FROM reports
        JOIN users ON reports.user_id = users.id
        WHERE reports.status = 'approved'
        ORDER BY reports.created_at DESC
    """).fetchall()

    rejected = db.execute("""
        SELECT reports.*, users.username
        FROM reports
        JOIN users ON reports.user_id = users.id
        WHERE reports.status = 'rejected'
        ORDER BY reports.created_at DESC
    """).fetchall()

    db.close()
    return render_template("admin.html", pending=pending, approved=approved, rejected=rejected)


@admin.route("/admin/approve/<int:report_id>", methods=["POST"])
@admin_required
def approve(report_id):
    admin_note = request.form.get("admin_note", "").strip()
    db = get_db()
    db.execute("""
        UPDATE reports SET status = 'approved', admin_note = ? WHERE id = ?
    """, (admin_note, report_id))
    db.commit()
    db.close()
    flash("Report approved and published.", "success")
    return redirect(url_for("admin.dashboard"))


@admin.route("/admin/reject/<int:report_id>", methods=["POST"])
@admin_required
def reject(report_id):
    admin_note = request.form.get("admin_note", "").strip()
    db = get_db()
    db.execute("""
        UPDATE reports SET status = 'rejected', admin_note = ? WHERE id = ?
    """, (admin_note, report_id))
    db.commit()
    db.close()
    flash("Report rejected.", "success")
    return redirect(url_for("admin.dashboard"))


@admin.route("/admin/toggle/<int:report_id>", methods=["POST"])
@admin_required
def toggle_active(report_id):
    db = get_db()
    report = db.execute("SELECT is_active FROM reports WHERE id = ?", (report_id,)).fetchone()
    new_status = 0 if report["is_active"] else 1
    db.execute("UPDATE reports SET is_active = ? WHERE id = ?", (new_status, report_id))
    db.commit()
    db.close()
    flash("Report status updated.", "success")
    return redirect(url_for("admin.dashboard"))


@admin.route("/admin/edit/<int:report_id>", methods=["GET", "POST"])
@admin_required
def edit_report(report_id):
    db = get_db()
    report = db.execute("SELECT * FROM reports WHERE id = ?", (report_id,)).fetchone()

    if not report:
        flash("Report not found.", "error")
        return redirect(url_for("admin.dashboard"))

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        description = request.form.get("description", "").strip()
        admin_note = request.form.get("admin_note", "").strip()

        db.execute("""
            UPDATE reports SET title = ?, description = ?, admin_note = ? WHERE id = ?
        """, (title, description, admin_note, report_id))
        db.commit()
        db.close()
        flash("Report updated successfully.", "success")
        return redirect(url_for("admin.dashboard"))

    db.close()
    return render_template("edit_report.html", report=report)