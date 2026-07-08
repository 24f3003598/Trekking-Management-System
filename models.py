from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekking_system.db'

db = SQLAlchemy(app)


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(db.Enum('Admin', 'Staff', 'Trekker', name='user_roles'), nullable=False)
    status = db.Column(db.String(20), nullable=False, default='Approved')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    managed_treks = db.relationship('Trek', backref='assigned_staff', lazy=True)
    bookings = db.relationship('Booking', backref='trekker', lazy=True)


class Trek(db.Model):
    trek_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    trek_name = db.Column(db.String(150), nullable=False)
    location = db.Column(db.String(150), nullable=False)
    difficulty = db.Column(db.Enum('Easy', 'Moderate', 'Hard', name='trek_difficulty'), nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)
    max_slots = db.Column(db.Integer, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum('Pending', 'Started', 'Open', 'Closed', 'Completed', name='trek_status'), nullable=False)
    assigned_staff_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=True)
    cost_per_person = db.Column(db.Float, nullable=False, default=0.0)
    meeting_point = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    # Relationship to access bookings for this trek
    bookings = db.relationship('Booking', backref='trek', lazy=True)


class Booking(db.Model):
    booking_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    trek_id = db.Column(db.Integer, db.ForeignKey('trek.trek_id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum('Confirmed', 'Cancelled', 'Completed', name='booking_status'), nullable=False, default='Confirmed')