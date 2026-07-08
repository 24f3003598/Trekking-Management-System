from flask import Flask,render_template,request,redirect,session
from models import db, User ,Trek ,Booking
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekking_system.db'
app.secret_key = "super_secret_viva_safeguard_key"

db.init_app(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')

    role = session['user_role']
    user_id = session['user_id']

    if role == 'Admin':
        pending_staff = User.query.filter_by(role='Staff', status='Pending').all()
        all_treks = Trek.query.all()
        all_users = User.query.all()
        return render_template('adminhomepage.html', 
                               staff_requests=pending_staff, 
                               total_treks=all_treks, 
                               total_users=all_users)

    elif role == 'Staff':
        assigned_treks = Trek.query.filter_by(assigned_staff_id=user_id).all()
        return render_template('staffhomepage.html' , treks=assigned_treks)

    elif role == 'Trekker':
        location_query = request.args.get('location', '').strip()
        difficulty_query = request.args.get('difficulty', '').strip()

        query = Trek.query.filter_by(status='Open')

        if location_query:
            query = query.filter(Trek.location.like(f"%{location_query}%"))
                
        if difficulty_query:
            query = query.filter(Trek.difficulty == difficulty_query)

        filtered_treks = query.all()
  
        user_bookings = Booking.query.filter_by(user_id=user_id).all()
        booked_trek_ids = [b.trek_id for b in user_bookings if b.status != 'Cancelled']

        return render_template(
            'explore.html',
            treks=filtered_treks,
            bookings=user_bookings,
            selected_location=location_query,
            selected_difficulty=difficulty_query,
            booked_trek_ids=booked_trek_ids,
        )

    return redirect('/login')

with app.app_context():
    db.create_all() 
    existing_admin = User.query.filter_by(email='admin@gmail.com').first()

    if not existing_admin:
        hashed_admin_password = generate_password_hash('admin123')
        admin = User(
                name='Admin',
                email='admin@gmail.com',
                password=hashed_admin_password,     
                phone='1234789000',
                role='Admin',
                status='Approved'
            )
        db.session.add(admin)
        db.session.commit()
        print("Database synced successfully without init_db.py!")

from routes.auth import *
from routes.admin import *
from routes.staff import *
from routes.user import *

if __name__ == '__main__':
    app.run(debug=True)