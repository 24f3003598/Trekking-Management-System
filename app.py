from flask import Flask,render_template,request,redirect,session
from models import db, User ,Trek ,Booking


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
        return render_template('staffhomepage.html')

    elif role == 'Trekker':
        return f"Welcome, Explorer {session['user_name']}. Your booking feed is coming next!"

    return redirect('/login')

with app.app_context():
    db.create_all() 
    existing_admin = User.query.filter_by(email='admin@gmail.com').first()

    if not existing_admin:
        admin = User(
                name='Admin',
                email='admin@gmail.com',
                password='admin123',     
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

if __name__ == '__main__':
    app.run(debug=True)