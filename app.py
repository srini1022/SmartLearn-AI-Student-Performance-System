from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, make_response, send_file
)
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, Student, Grade, AIReport, StudentFile, Admin  # ✅ Added Admin
from ai_helper.ai_model import predict_performance
from fpdf import FPDF
import os
import time

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'

# ---------- MySQL Configuration ----------
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:root@localhost/smartlearn_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ---------- File Upload Configuration ----------
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db.init_app(app)

# ---------- Create Tables Automatically ----------
with app.app_context():
    db.create_all()

# ---------- STUDENT MODULE ----------
@app.route('/')
def index():
    if 'student_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        if Student.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('register'))
        new_student = Student(name=name, email=email, password=password)
        db.session.add(new_student)
        db.session.commit()
        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Student.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['student_id'] = user.id
            session['student_name'] = user.name
            return redirect(url_for('dashboard'))
        flash('Invalid credentials', 'danger')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@app.route('/dashboard')
def dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    student = Student.query.get(session['student_id'])
    grades = Grade.query.filter_by(student_id=student.id).all()
    files = StudentFile.query.filter_by(student_id=student.id).all()
    reports = AIReport.query.filter_by(student_id=student.id).all()

    # ✅ Calculate average marks
    avg_marks = None
    if grades:
        total = sum(g.marks for g in grades)
        avg_marks = round(total / len(grades), 2)

    # ✅ Notification for new uploads
    new_upload = session.pop('new_upload', None)

    return render_template(
        'dashboard.html',
        student=student,
        grades=grades,
        files=files,
        reports=reports,
        avg_marks=avg_marks,
        new_upload=new_upload
    )


# ---------- AI STUDY HELPER ----------
@app.route('/ai-helper', methods=['GET', 'POST'])
def ai_helper():
    result = suggestion = avg_marks = score = None
    if request.method == 'POST':
        try:
            subjects = request.form.getlist('subjects[]')
            marks = list(map(int, request.form.getlist('marks[]')))
            attendance = float(request.form['attendance'])
            assignments_done = int(request.form['assignments_done'])

            if not subjects or not marks:
                flash("Please enter at least one subject and marks.", "danger")
                return redirect(url_for('ai_helper'))

            avg_marks = sum(marks) / len(marks)
            data = {
                'avg_marks': avg_marks,
                'attendance': attendance,
                'assignments_done': assignments_done
            }

            result, suggestion, avg_marks, score = predict_performance(data)

        except Exception as e:
            flash(f"Error: {str(e)}", "danger")

    return render_template('ai_helper.html', result=result, suggestion=suggestion,
                           avg_marks=avg_marks, score=score)

# ---------- ADMIN MODULE ----------
@app.route('/admin/register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']

        if Admin.query.filter_by(email=email).first():
            flash('Email already exists!', 'danger')
            return redirect(url_for('admin_register'))

        new_admin = Admin(name=name, email=email, password=password, role=role)
        db.session.add(new_admin)
        db.session.commit()
        flash('Admin registered successfully!', 'success')
        return redirect(url_for('admin_login'))

    return render_template('admin_register.html')


@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        admin = Admin.query.filter_by(email=email).first()

        if admin and check_password_hash(admin.password, password):
            session['admin'] = admin.id
            session['admin_role'] = admin.role
            session['admin_name'] = admin.name
            flash(f"Welcome, {admin.name} ({admin.role})!", "success")
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin credentials', 'danger')

    return render_template('admin_login.html')


@app.route('/admin/logout')
def admin_logout():
    session.pop('admin', None)
    return redirect(url_for('admin_login'))


@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('admin_login'))
    students = Student.query.all()
    return render_template('admin_dashboard.html', students=students)


@app.route('/admin/add_grade/<int:student_id>', methods=['GET', 'POST'])
def admin_add_grade(student_id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    student = Student.query.get_or_404(student_id)
    if request.method == 'POST':
        subject = request.form['subject']
        marks = request.form['score']
        new_grade = Grade(subject=subject, marks=marks, student_id=student.id)
        db.session.add(new_grade)
        db.session.commit()
        flash('Grade added successfully!', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_add_grade.html', student=student)


@app.route('/admin/delete/<int:id>')
def admin_delete_student(id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    # Restrict staff admins
    if session.get('admin_role') != 'superadmin':
        flash('Access denied. Only Super Admins can delete students.', 'danger')
        return redirect(url_for('admin_dashboard'))

    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    flash('Student deleted successfully', 'success')
    return redirect(url_for('admin_dashboard'))


# ---------- ADMIN: Update Attendance & Assignments ----------
@app.route('/admin/update/<int:id>', methods=['POST'])
def admin_update_student(id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    # Restrict staff admins
    if session.get('admin_role') != 'superadmin':
        flash('Access denied. Only Super Admins can update student data.', 'danger')
        return redirect(url_for('admin_dashboard'))

    student = Student.query.get_or_404(id)
    student.attendance = request.form.get('attendance', type=float)
    student.assignments_done = request.form.get('assignments_done', type=int)
    db.session.commit()
    flash(f"{student.name}'s details updated successfully!", 'success')
    return redirect(url_for('admin_dashboard'))


# ---------- ADMIN FILE UPLOAD ----------
@app.route('/admin/upload/<int:student_id>', methods=['GET', 'POST'])
def admin_upload(student_id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    student = Student.query.get_or_404(student_id)
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filename = secure_filename(file.filename)
            safe_name = f"{student.id}_{int(time.time())}_{filename}"
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], safe_name)
            file.save(filepath)

            new_file = StudentFile(student_id=student.id, filename=filename, filepath=filepath)
            db.session.add(new_file)
            db.session.commit()

            session['new_upload'] = f"📂 New file uploaded by admin: {filename}"
            flash('File uploaded successfully!', 'success')
            return redirect(url_for('admin_dashboard'))

    return render_template('admin_upload.html', student=student)

@app.route('/admin/delete_files/<int:student_id>')
def admin_delete_files(student_id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    student = Student.query.get_or_404(student_id)
    deleted_count = 0

    for f in student.files:
        try:
            if os.path.exists(f.filepath):
                os.remove(f.filepath)
            db.session.delete(f)
            deleted_count += 1
        except Exception as e:
            print(f"⚠️ Error deleting {f.filename}: {e}")

    db.session.commit()
    flash(f"🗑️ Deleted {deleted_count} uploaded file(s) for {student.name}.", "info")
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/delete_file/<int:file_id>')
def admin_delete_file(file_id):
    if 'admin' not in session:
        return redirect(url_for('admin_login'))

    file_entry = StudentFile.query.get_or_404(file_id)
    student = Student.query.get(file_entry.student_id)

    try:
        if os.path.exists(file_entry.filepath):
            os.remove(file_entry.filepath)
        db.session.delete(file_entry)
        db.session.commit()
        flash(f"🗑️ Deleted file: {file_entry.filename}", "info")
    except Exception as e:
        flash(f"⚠️ Error deleting file: {e}", "danger")

    return redirect(url_for('admin_upload', student_id=student.id))


# ---------- STUDENT FILE DOWNLOAD ----------
@app.route('/download/<int:file_id>')
def download_file(file_id):
    if 'student_id' not in session:
        return redirect(url_for('login'))
    file_entry = StudentFile.query.get_or_404(file_id)
    return send_file(file_entry.filepath, as_attachment=True)


# ---------- PDF DOWNLOAD ----------
@app.route('/download_report')
def download_report():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    student = Student.query.get(session['student_id'])
    grades = Grade.query.filter_by(student_id=student.id).all()
    reports = AIReport.query.filter_by(student_id=student.id).all()

    avg_marks = None
    if grades:
        total = sum(g.marks for g in grades)
        avg_marks = round(total / len(grades), 2)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "SmartLearn Student Report", ln=True, align="C")
    pdf.ln(10)
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Name: {student.name}", ln=True)
    pdf.cell(0, 10, f"Email: {student.email}", ln=True)
    pdf.cell(0, 10, f"Attendance: {student.attendance}%", ln=True)
    pdf.cell(0, 10, f"Assignments Completed: {student.assignments_done}", ln=True)
    if avg_marks:
        pdf.cell(0, 10, f"Overall Performance: {avg_marks}%", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(90, 10, "Subject", 1)
    pdf.cell(50, 10, "Marks", 1, ln=True)
    pdf.set_font("Arial", '', 12)
    for g in grades:
        pdf.cell(90, 10, g.subject, 1)
        pdf.cell(50, 10, str(g.marks), 1, ln=True)
    pdf.ln(10)
    if reports:
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, "AI Study Helper Insights", ln=True)
        pdf.ln(5)
        pdf.set_font("Arial", '', 12)
        for r in reports:
            pdf.multi_cell(0, 8, f"📊 Result: {r.result}\n💡 Suggestion: {r.suggestion}")
            pdf.ln(5)
    else:
        pdf.set_font("Arial", 'I', 12)
        pdf.cell(0, 10, "No AI study helper analysis available.", ln=True)
    pdf.ln(10)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, "Generated by SmartLearn © 2025", align="C")
    response = make_response(pdf.output(dest='S').encode('latin1'))
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename={student.name}_report.pdf'
    return response


# ---------- RUN APP ----------
if __name__ == '__main__':
    app.run(debug=True)
