from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///attendance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

class Attendance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subject.id'), nullable=False)
    date = db.Column(db.String(10), nullable=False)
    present = db.Column(db.Boolean, nullable=False)

    # Relationships for easier access
    student = db.relationship('Student', backref='attendances')
    subject = db.relationship('Subject', backref='attendances')

# Create the database tables
with app.app_context():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        student_name = request.form['name']
        new_student = Student(name=student_name)
        db.session.add(new_student)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_student.html')

@app.route('/add_subject', methods=['GET', 'POST'])
def add_subject():
    if request.method == 'POST':
        subject_name = request.form['name']
        new_subject = Subject(name=subject_name)
        db.session.add(new_subject)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('add_subject.html')

@app.route('/mark_attendance', methods=['GET', 'POST'])
def mark_attendance():
    students = Student.query.all()
    subjects = Subject.query.all()
    
    if request.method == 'POST':
        student_ids_present = request.form.getlist('present')
        subject_id = request.form['subject_id']
        date = request.form['date']

        for student in students:
            is_present = str(student.id) in student_ids_present
            attendance_record = Attendance(
                student_id=student.id,
                subject_id=subject_id,
                date=date,
                present=is_present
            )
            db.session.add(attendance_record)

        db.session.commit()
        return redirect(url_for('view_attendance'))

    return render_template('mark_attendance.html', students=students, subjects=subjects)

@app.route('/view_attendance', methods=['GET'])
def view_attendance():
    records = Attendance.query.all()
    return render_template('view_attendance.html', records=records)

# Delete Student
@app.route('/delete_student/<int:student_id>', methods=['POST'])
def delete_student(student_id):
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('index'))

# Delete Subject
@app.route('/delete_subject/<int:subject_id>', methods=['POST'])
def delete_subject(subject_id):
    subject = Subject.query.get_or_404(subject_id)
    db.session.delete(subject)
    db.session.commit()
    return redirect(url_for('index'))

# Delete Attendance
@app.route('/delete_attendance/<int:attendance_id>', methods=['POST'])
def delete_attendance(attendance_id):
    attendance_record = Attendance.query.get_or_404(attendance_id)
    db.session.delete(attendance_record)
    db.session.commit()
    return redirect(url_for('view_attendance'))

if __name__ == "__main__":
    app.run(debug=True)
