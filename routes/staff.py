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
def staff_update_trek(trek_id):
    if 'user_id' not in session or session.get('user_role') != 'Staff':
        return "Access Forbidden", 403

    trek = Trek.query.get_or_404(trek_id)
    
    if trek.assigned_staff_id != session['user_id']:
        return "Unauthorized action on this trek layout", 403

    try:
        updated_slots = int(request.form.get('available_slots'))
        updated_status = request.form.get('status')

        
        if 0 <= updated_slots <= trek.max_slots:
            trek.available_slots = updated_slots
        
        if updated_status in ['Open', 'Closed', 'Pending', 'Completed']:
            trek.status = updated_status

        db.session.commit()
        print(f"[SUCCESS] Trek ID #{trek_id} updated by Staff ID #{session['user_id']}.")
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Failed to save staff updates: {e}")

    return redirect('/staff/dashboard?updated=true')

@app.route('/staff/trek/<int:trek_id>/roster')
def view_roster(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    return render_template('roster.html', trek=trek)