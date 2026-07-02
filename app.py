from flask import Flask,render_template,request,redirect,session,flash
from models import db, User ,Trek ,Booking
from sqlalchemy import or_

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///trekking_system.db'
app.secret_key = "super_secret_viva_safeguard_key"

db.init_app(app)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        input_email = request.form.get('email')
        input_password = request.form.get('password')

        existing_user = User.query.filter_by(email=input_email,password=input_password).first()
        if existing_user:

            if existing_user.role=='Staff' and existing_user.status=='Pending':
                session.clear()
                msg = "Your account is pending Admin approval."
                return render_template('restricted.html', error_message=msg)

            if existing_user.status=='Blacklisted':
                session.clear()
                msg = '"Your account profile has been deactivated by the System Administrator.'
                return render_template('restricted.html' , error_message= msg)

            session['user_id'] = existing_user.user_id
            session['user_role'] = existing_user.role
            session['user_name'] = existing_user.name

            return redirect('/dashboard')

        else:
            msg = 'Invalid email or password.Try again!'
            return render_template('restricted.html' , error_message= msg)
        
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        input_name = request.form.get('name')
        input_email = request.form.get('email')
        input_password = request.form.get('password')
        input_contact = request.form.get('contact')
        input_role = request.form.get('role')

        if input_role not in ['Admin', 'Staff', 'Trekker']:
            return "Invalid role selected!", 400
        
        existing_user = User.query.filter_by(email=input_email).first()
        if existing_user:
            return "Email already registered! Try another one."

        user_status = 'Pending' if input_role == 'Staff' else 'Approved'
            
        new_user = User(
            name=input_name,
            email=input_email,
            password=input_password,     
            phone=input_contact,
            role=input_role,
            status=user_status
        )
        
        db.session.add(new_user)
        
        db.session.commit()
        
        return redirect('/login')

    return render_template('register.html')

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
        return f"Welcome, Staff member {session['user_name']}. Your portal is coming next!"

    elif role == 'Trekker':
        return f"Welcome, Explorer {session['user_name']}. Your booking feed is coming next!"

    return redirect('/login')

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
    
    flash(f"Successfully activated employee profile for {staff_user.name}!", "success")
    return redirect('/admin/staff-details')



@app.route('/admin/staff/blacklist/<int:staff_id>')
def admin_blacklist_staff(staff_id):
    if 'user_id' not in session or session.get('user_role') != 'Admin':
        return "Access Forbidden", 403
        
    staff_user = User.query.get_or_404(staff_id)
    staff_user.status = 'Blacklisted'
    db.session.commit()
    
    flash(f"Account access revoked for {staff_user.name}.", "warning")
    return redirect('/admin/staff-details')

@app.route('/admin/user-details')
def admin_user_details():
    # 1. Security Check: Block anyone who isn't a logged-in Admin
    if 'user_id' not in session or session['user_role'] != 'Admin':
        return "Access Forbidden: Administrator clearance required.", 403
    
    # 2. Capture the GET search parameter from your template form
    search_query = request.args.get('search', '').strip()
    
    # Base query: Target ONLY users who are Trekkers
    query = User.query.filter_by(role='Trekker')
    
    # 3. Dynamic Search Logic (If admin typed something)
    if search_query:
        # Check if the query matches name OR email using standard strings
        query = query.filter(
            or_(
                User.name.like(f"%{search_query}%"),
                User.email.like(f"%{search_query}%")
            )
        )
    
    # Execute lookup and order results by user_id
    all_trekkers = query.order_by(User.user_id.desc()).all()
    
    # Render your new template with the matching data variables
    return render_template('adminusers.html', user_list=all_trekkers, search_query=search_query)


@app.route('/admin/user/toggle/<int:user_id>')
def admin_user_toggle(user_id):
    if 'user_id' not in session or session['user_role'] != 'Admin':
        return "Access Forbidden: Administrator clearance required.", 403
    
    traveler = User.query.get_or_404(user_id)
    
    # Toggle logic: if Active/Approved -> Blacklist them. If already Blacklisted -> Approve them.
    if traveler.status == 'Approved':
        traveler.status = 'Blacklisted'
    else:
        traveler.status = 'Approved'
        
    db.session.commit()
    
    # Redirect cleanly back to the customer directory view layout
    return redirect('/admin/user-details')

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


if __name__ == '__main__':
    app.run(debug=True)