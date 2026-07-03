from flask import Flask,render_template,request,redirect,session
from models import db, User
from app import app

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
            session.clear()
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
            msg = "Email already registered! Try another one."
            return render_template('restricted.html' , error_message= msg)

        if input_role == 'Staff':
            user_status = 'Pending'
        else :
            user_status = 'Approved'
            
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