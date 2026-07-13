from flask import render_template, request, redirect, session
from datetime import datetime
from models import db, Trek, User , Booking
from app import app  

def check_staff():
    return 'user_id' in session and session.get('user_role') == 'Staff'

@app.route('/staff/update_trek/<int:trek_id>', methods=['POST'])
def update_trek(trek_id):
    if 'user_id' not in session or session.get('user_role') != 'Staff':
        return redirect('/login')

    trek = Trek.query.get_or_404(trek_id)

    slots_input = int(request.form.get('available_slots', 0))
    status_input = request.form.get('status')
    
    if slots_input == 0:
        status_input = 'Closed'

    trek.available_slots = slots_input
    trek.status = status_input

    db.session.commit()

    return redirect('/dashboard?updated=true')

@app.route('/staff/trek/<int:trek_id>/roster')
def view_roster(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    bookings = Booking.query.filter_by(trek_id=trek_id).all()
    return render_template('roster.html', trek=trek , bookings=bookings)

@app.route('/staff/profile', methods=['GET', 'POST'])
def staff_profile():
    if 'user_id' not in session or session.get('user_role') != 'Staff':
        return "Access Forbidden", 403

    staff_user = User.query.get_or_404(session['user_id'])
    
    if request.method == 'POST':
        staff_user.name = request.form.get('name').strip()
        staff_user.phone = request.form.get('phone').strip()

        db.session.commit()
        
        session['user_name'] = staff_user.name
        
        return redirect('/dashboard?updated=true')
        
    return render_template('staff_profile.html', staff=staff_user)