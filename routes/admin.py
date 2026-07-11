from flask import Flask,render_template,request,redirect,session
from models import db, User ,Trek , Booking
from datetime import datetime
from app import app

@app.route('/admin/staff-details')
def admin_staff_details():
    if 'user_id' not in session or session['user_role'] != 'Admin':
        return "Access Forbidden: Administrator clearance required.", 403

    search_query = request.args.get('search', '').strip()

    query = User.query.filter_by(role='Staff')

    if search_query:
        clean_id = search_query.replace('#', '').strip()

        if clean_id.isdigit():
            query = query.filter(User.user_id == int(clean_id))
                
        else:
            query = query.filter(User.name.like(f"%{search_query}%"))

    all_staff = query.all()
    return render_template('adminstaffdetails.html', staff_list=all_staff)

@app.route('/admin/staff/approve/<int:staff_id>')
def admin_approve_staff(staff_id):
    if 'user_id' not in session or session['user_role'] != 'Admin':
        return "Access Forbidden", 403
        
    staff_user = User.query.get_or_404(staff_id)
    
    staff_user.status = 'Approved'
    db.session.commit() 
    all_staff = User.query.filter_by(role='Staff').all()
    return render_template('adminstaffdetails.html', staff_list=all_staff)
                        
                       
@app.route('/admin/staff/blacklist/<int:staff_id>')
def admin_blacklist_staff(staff_id):
    if 'user_id' not in session or session.get('user_role') != 'Admin':
        return "Access Forbidden", 403
        
    staff_user = User.query.get_or_404(staff_id)
    staff_user.status = 'Blacklisted'
    db.session.commit()
    return redirect('/admin/staff-details')

@app.route('/admin/trekker-details')
def admin_user_details():
    if 'user_id' not in session or session['user_role'] != 'Admin':
        return "Access Forbidden: Administrator clearance required.", 403

    search_query = request.args.get('search', '').strip()
 
    query = User.query.filter_by(role='Trekker')

    if search_query:
        clean_id = search_query.replace('#', '').strip()
        if clean_id.isdigit():
            query = query.filter(User.user_id == int(clean_id))
        else:
            query = query.filter(User.name.like(f"%{search_query}%"))

    all_trekkers = query.all()
 
    return render_template('adminusers.html', user_list=all_trekkers, search_query=search_query)

@app.route('/admin/user/toggle/<int:user_id>')
def admin_user_toggle(user_id):
    if 'user_id' not in session or session['user_role'] != 'Admin':
        return "Access Forbidden: Administrator clearance required.", 403
    
    traveler = User.query.get_or_404(user_id)
    
    if traveler.status == 'Approved':
        traveler.status = 'Blacklisted'
    else:
        traveler.status = 'Approved'
        
    db.session.commit()

    return redirect('/admin/user-details')

@app.route('/admin/treks')
def admin_trek_list():
    if 'user_id' not in session or session['user_role'] != 'Admin':
        return "Access Forbidden", 403

    search_query = request.args.get('search', '').strip()
    
    # 2. Start with a base query selecting all treks
    query = Trek.query
    
    # 3. Apply dynamic filtering if the admin typed something
    if search_query:
        clean_id = search_query.replace('#', '').strip()
        if clean_id.isdigit():
            query = query.filter(Trek.trek_id == int(clean_id))
        else:
            query = query.filter(Trek.trek_name.like(f"%{search_query}%"))
        
    all_treks = query.all()

    return render_template('admintreks.html', treks=all_treks, search_query=search_query)

@app.route('/admin/trek/create', methods=['GET', 'POST'])
def admin_create_trek():
    if 'user_id' not in session or session['user_role'] != 'Admin':
        return "Access Forbidden", 403

    if request.method == 'POST':
        start_dt = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        end_dt = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()
        
        staff_id = request.form.get('assigned_staff_id')
        staff_id = int(staff_id) if staff_id and staff_id.isdigit() else None

        new_trek = Trek(
            trek_name=request.form.get('trek_name'),
            location=request.form.get('location'),
            difficulty=request.form.get('difficulty'), 
            duration_days=int(request.form.get('duration_days')),
            max_slots=int(request.form.get('max_slots')),
            available_slots=int(request.form.get('max_slots')), 
            start_date=start_dt,
            end_date=end_dt,
            status=request.form.get('status', 'Pending'), 
            assigned_staff_id=staff_id,
            cost_per_person=float(request.form.get('cost_per_person', 0)),
            meeting_point=request.form.get('meeting_point'),
            description=request.form.get('description')
        )
        
        db.session.add(new_trek)
        db.session.commit()
        return redirect('/admin/treks')

    staff_members = User.query.filter_by(role='Staff', status='Approved').all()
    return render_template('admincreatetrek.html', staff=staff_members)


@app.route('/admin/trek/edit/<int:trek_id>', methods=['GET', 'POST'])
def admin_edit_trek(trek_id):
    if 'user_id' not in session or session['user_role'] != 'Admin':
        return "Access Forbidden", 403

    trek = Trek.query.get_or_404(trek_id)

    if request.method == 'POST':
        trek.trek_name = request.form.get('trek_name')
        trek.location = request.form.get('location')
        trek.difficulty = request.form.get('difficulty')
        trek.duration_days = int(request.form.get('duration_days'))
        trek.max_slots = int(request.form.get('max_slots'))
        trek.status = request.form.get('status')
        
        trek.start_date = datetime.strptime(request.form.get('start_date'), '%Y-%m-%d').date()
        trek.end_date = datetime.strptime(request.form.get('end_date'), '%Y-%m-%d').date()

        staff_id = request.form.get('assigned_staff_id')
        trek.assigned_staff_id = int(staff_id) if staff_id and staff_id.isdigit() else None
        trek.cost_per_person = float(request.form.get('cost_per_person', 0))
        trek.meeting_point = request.form.get('meeting_point')
        trek.description = request.form.get('description')
        
        db.session.commit()
        return redirect('/admin/treks')

    staff_members = User.query.filter_by(role='Staff', status='Approved').all()
    return render_template('adminedittrek.html', trek=trek, staff=staff_members)

@app.route('/admin/trek/delete/<int:trek_id>', methods=['POST'])
def admin_delete_trek(trek_id):
    if 'user_id' not in session or session['user_role'] != 'Admin':
        return "Access Forbidden", 403

    trek = Trek.query.get_or_404(trek_id)
    trek_name = trek.trek_name

    if trek.bookings:
        return redirect('/admin/treks')

    db.session.delete(trek)
    db.session.commit()

    return redirect('/admin/treks')

@app.route('/logout')
def logout():
    return render_template('home.html')

@app.route('/admin/history')
def admin_trekking_history():
    if 'user_id' not in session or session['user_role'] != 'Admin':
        return "Access Forbidden", 403

    all_history = Booking.query.all()
    
    return render_template('adminhistory.html', history=all_history)