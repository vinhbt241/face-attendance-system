from db import db


class Img(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    img = db.Column(db.Text, nullable=False)
    name = db.Column(db.Text, nullable=False)
    mimetype = db.Column(db.Text, nullable=False)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'))


subject_student = db.Table('subject_student',
                           db.Column('subject_id', db.Integer, db.ForeignKey('subject.id')),
                           db.Column('student_id', db.Integer, db.ForeignKey('student.id')))

subject_teacher = db.Table('subject_teacher',
                           db.Column('subject_id', db.Integer, db.ForeignKey('subject.id')),
                           db.Column('teacher_id', db.Integer, db.ForeignKey('teacher.id')))


class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String, nullable=False)
    subject_school_id = db.Column(db.String, nullable=False, unique=True)
    start_at = db.Column(db.Time, nullable=False)
    end_at = db.Column(db.Time, nullable=False)
    students = db.relationship("Student",
                               secondary=subject_student,
                               backref="subjects")
    teachers = db.relationship("Teacher",
                               secondary=subject_teacher,
                               backref="subjects")


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_name = db.Column(db.String, nullable=False)
    student_school_id = db.Column(db.String, nullable=False, unique=True)
    images_uploaded = db.Column(db.Boolean, nullable=False)
    images = db.relationship('Img', backref='student')


class Teacher(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    teacher_school_id = db.Column(db.String, nullable=False, unique=True)
    teacher_name = db.Column(db.String, nullable=False)
    teacher_email = db.Column(db.String, nullable=False, unique=True)
