from flask import render_template, request, redirect, session
from datetime import datetime
from models import db, Trek, User
from app import app  

@app.route('/staff/dashboard')
def staff_dashboard():
    if 'user_id' not in session or session.get('user_role') != 'Staff':
        return "Access Forbidden: Staff Only", 403

    current_staff_id = session['user_id']

    print(f"\n--- [DEBUG] Staff Dashboard Access ---")
    print(f"Logged-in Staff User ID: {current_staff_id}")

    assigned_treks = Trek.query.filter_by(assigned_staff_id=current_staff_id).all()
    
    print(f"Number of treks retrieved from SQLite: {len(assigned_treks)}")
    for trek in assigned_treks:
        print(f" -> Assigned Trek found: ID #{trek.trek_id} - {trek.trek_name}")
    print("---------------------------------------\n")

    return render_template('staffhomepage.html', treks=assigned_treks)

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

    return redirect('/staff/dashboard?updated=true')

@app.route('/staff/trek/<int:trek_id>/roster')
def view_roster(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    return render_template('roster.html', trek=trek)

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
        
        return redirect('/staff/dashboard?updated=true')
        
    return render_template('staff_profile.html', staff=staff_user)