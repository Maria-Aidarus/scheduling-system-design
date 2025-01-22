from app import db
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

class Tutor(db.Model):
    __tablename__ = 'tutors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    subject = db.Column(db.String(255), nullable=False)  # Changed from list to string
    bookings = db.relationship('Booking', backref='tutor', lazy=True)
    
class Student(db.Model):
    __tablename__ = 'students'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    timezone = db.Column(db.String(50), nullable=False)
    bookings = db.relationship('Booking', backref='student', lazy=True)

class Availability(db.Model):
    __tablename__ = 'availability'
    id = db.Column(db.Integer, primary_key=True)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutors.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    time_zone = db.Column(db.String(50), nullable=False)
    is_booked = db.Column(db.Boolean, default=False, nullable=False)

class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable=False)
    tutor_id = db.Column(db.Integer, db.ForeignKey('tutors.id'), nullable=False)
    availability_id = db.Column(db.Integer, db.ForeignKey('availability.id'), nullable=True)
    booking_time = db.Column(db.DateTime, nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    time_zone = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(50), default="confirmed")

class Notification(db.Model):
    __tablename__ = 'notifications'
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(50), nullable=False)  # e.g., 'conflict'
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)