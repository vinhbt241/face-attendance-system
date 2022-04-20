from flask import Flask, request, render_template, url_for, Response, redirect, flash, jsonify
from db import db_init, db
from models import Subject, Student, Img, Teacher
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = "some thing fishy"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db_init(app)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/subject/index')
def subject_index():
    return render_template('subject_index.html', subjects=Subject.query.all())


@app.route('/subject/new')
def subject_new():
    return render_template('subject_new.html')


@app.route('/subject/create', methods=["POST"])
def subject_create():
    subject = Subject(subject_name=request.form.get('subject_name'),
                      subject_school_id=request.form.get('subject_school_id'),
                      start_at=datetime.strptime(request.form.get('start_at'), "%H:%M").time(),
                      end_at=datetime.strptime(request.form.get('end_at'), "%H:%M").time())
    subject_school_id_exists = db.session.query(Subject.id).filter_by(subject_school_id=subject.subject_school_id).scalar() is not None

    if subject_school_id_exists:
        flash('Subject ID must be unique!')
        return render_template('subject_new.html')

    db.session.add(subject)
    db.session.commit()
    flash('Subject Added!')

    return redirect(url_for('subject_index'))


@app.route('/subject/teachers_and_students/<int:subject_id>')
def subject_teachers_and_students(subject_id):
    subject = db.session.query(Subject).filter_by(id=subject_id).scalar()
    students = subject.students
    teachers = subject.teachers
    return render_template('subject_teachers_and_students.html', subject=subject, students=students, teachers=teachers)


@app.route('/subject/add_student', methods=["POST"])
def subject_add_student():
    subject = db.session.query(Subject).filter_by(id=request.form.get('subject_id')).scalar()
    student = db.session.query(Student).filter_by(student_school_id=request.form.get('student_school_id')).scalar()

    if student is None:
        flash("Student School ID don't exists!")
        return redirect(url_for('subject_teachers_and_students', subject_id=subject.id))
    elif not student.images_uploaded:
        flash("Student must have images before add to class!")
        return redirect(url_for('subject_teachers_and_students', subject_id=subject.id))

    subject.students.append(student)
    db.session.commit()
    flash("Student Added To Subject!")
    return redirect(url_for('subject_teachers_and_students', subject_id=subject.id))


@app.route('/subject/add_teacher', methods=["POST"])
def subject_add_teacher():
    subject = db.session.query(Subject).filter_by(id=request.form.get('subject_id')).scalar()
    teacher = db.session.query(Teacher).filter_by(teacher_school_id=request.form.get('teacher_school_id')).scalar()

    if teacher is None:
        flash("Student ID don't exists!")
        return redirect(url_for('subject_teachers_and_students', subject_id=subject.id))

    subject.teachers.append(teacher)
    db.session.commit()
    flash("Teacher Added To Subject!")
    return redirect(url_for('subject_teachers_and_students', subject_id=subject.id))


@app.route('/teacher/index')
def teacher_index():
    return render_template('teacher_index.html', teachers=Teacher.query.all())


@app.route('/teacher/new')
def teacher_new():
    return render_template('teacher_new.html')


@app.route('/teacher/create', methods=["POST"])
def teacher_create():
    teacher = Teacher(teacher_name=request.form.get('teacher_name'),
                      teacher_email=request.form.get('teacher_email'),
                      teacher_school_id=request.form.get('teacher_school_id'))
    teacher_school_id_exists = db.session.query(Teacher.id).filter_by(teacher_school_id=teacher.teacher_school_id).scalar() is not None

    if teacher_school_id_exists:
        flash('Teacher School ID must be unique!')
        return render_template('teacher_new.html')

    db.session.add(teacher)
    db.session.commit()
    flash('Teacher Added!')

    return redirect(url_for('teacher_index'))


@app.route('/student/index')
def student_index():
    return render_template('student_index.html', students=Student.query.all())


@app.route('/student/new')
def student_new():
    return render_template('student_new.html')


@app.route('/student/create', methods=["POST"])
def student_create():
    student = Student(student_name=request.form.get('student_name'),
                      student_school_id=request.form.get('student_school_id'),
                      images_uploaded=False)
    student_school_id_exists = db.session.query(Student.id).filter_by(student_school_id=student.student_school_id).scalar() is not None

    if student_school_id_exists:
        flash('Student ID must be unique!')
        return render_template('student_new.html')

    db.session.add(student)
    db.session.commit()
    flash('Student Added!')

    return redirect(url_for('student_index'))


@app.route('/student/collect_images/<int:student_id>')
def student_collect_images(student_id):
    return render_template('student_collect_images.html', student_id=student_id)


@app.route('/student/upload_imgs', methods=["POST"])
def student_upload_imgs():
    student_id = request.form.get('student_id')
    student = db.session.query(Student).filter_by(id=student_id).scalar()

    images = request.files.getlist('student_imgs')

    error = False

    if len(images) != 10:
        flash('Must submit 10 images!')
        error = True

    if error:
        return render_template('student_collect_images.html')

    for image in images:
        filename = secure_filename(image.filename)

        img = Img(img=image.read(), mimetype=image.mimetype, name=filename)

        student.images.append(img)
        student.images_uploaded = True

    db.session.commit()

    flash('Images Upload Successfully!')
    return redirect(url_for('student_index'))


@app.route('/student/download_images/<string:student_school_id>/<int:offset>')
def get_img(student_school_id, offset):
    student = db.session.query(Student).filter_by(student_school_id=student_school_id).scalar()

    if len(student.images) == 0:
        return 'Student have no image!', 404

    image = student.images[int(offset)]

    return Response(image.img, mimetype=image.mimetype)


@app.route('/get_student_school_id_in_subject/<string:subject_school_id>')
def get_student_school_id_in_subject(subject_school_id):
    subject = db.session.query(Subject).filter_by(subject_school_id=subject_school_id).scalar()
    students = subject.students

    id_list = []
    for student in students:
        student_school_id = student.student_school_id
        id_list.append(student_school_id)

    return jsonify({"all_school_id": id_list})


# Write route to get teacher's emails in chosen subject
@app.route('/get_teacher_email_list_in_subject/<string:subject_school_id>')
def get_teacher_mail_list_in_subject(subject_school_id):
    subject = db.session.query(Subject).filter_by(subject_school_id=subject_school_id).scalar()
    teachers = subject.teachers

    mail_list = []
    for teacher in teachers:
        teacher_email = teacher.teacher_email
        mail_list.append(teacher_email)

    return jsonify({"teacher_email_list": mail_list})


@app.route('/get_subjects')
def get_subjects():
    subjects = db.session.query(Subject).all()

    subject_list = []

    for subject in subjects:
        subject_list.append({"subject_name": subject.subject_name,
                             "subject_school_id": subject.subject_school_id,
                             "start_at": subject.start_at.strftime("%H:%M"),
                             "end_at": subject.end_at.strftime("%H:%M")})

    return jsonify({"subjects": subject_list})


if __name__ == "__main__":
    app.run(debug=False)
