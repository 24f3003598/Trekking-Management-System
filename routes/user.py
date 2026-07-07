from flask import Flask, render_template, request, redirect, session
from models import db, User, Trek, Booking

from app import app 

@app.route('/explore-treks')
def explore_treks():
    open_treks = Trek.query.filter_by(status='Open').all()
    return render_template('explore.html', treks=open_treks)



@app.route('/book/<int:trek_id>', methods=['POST'])
def book_trek(trek_id):
    if 'user_id' not in session:
        return redirect('/login')

    trek = Trek.query.get_or_404(trek_id)

    if request.method == 'POST':
        logged_in_user_id = session['user_id']
        current_trekker = User.query.get(logged_in_user_id)

        if not current_trekker or session.get('user_role') != 'Trekker':
            return render_template('booking_failed.html', error_message="Authentication Error: Please log in as a Trekker.")

        existing_booking = Booking.query.filter_by(
            user_id=logged_in_user_id, 
            trek_id=trek_id
        ).first()
        
        if existing_booking:
            return render_template('booking_failed.html', error_message="You have already secured a booking for this journey!")

        try:
            num_persons = int(request.form.get('num_persons', 1))
        except ValueError:
            return render_template('booking_failed.html', error_message="Invalid input data format.")

        if trek.status != 'Open' or num_persons < 1 or num_persons > trek.available_slots:
            return render_template('booking_failed.html', error_message=f"Cannot book {num_persons} slots. Only {trek.available_slots} available.")

        try:
            new_booking = Booking(
                user_id=current_trekker.user_id,
                trek_id=trek.trek_id,
                status='Booked'
            )

            trek.available_slots -= num_persons
            db.session.add(new_booking)
            db.session.commit()

            return render_template('booking_success.html', trek=trek, user=current_trekker)
            
        except Exception as e:
            db.session.rollback()
            return render_template('booking_failed.html', error_message="A backend database error occurred while processing your slot request.")

@app.route('/my-bookings')
def booking_history():
    if 'user_id' not in session:
        return redirect('/login')
        
    logged_in_user_id = session['user_id']
    current_user = User.query.get(logged_in_user_id)

    if not current_user or session.get('user_role') != 'Trekker':
        return "Access Forbidden", 403

    user_bookings = Booking.query.filter_by(user_id=logged_in_user_id).all()

    return render_template('booking_history.html', bookings=user_bookings, user=current_user)

@app.route('/cancel-booking/<int:booking_id>', methods=['POST'])
def cancel_booking(booking_id):
    if 'user_id' not in session:
        return redirect('/login')

    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != session['user_id']:
        return "Access Forbidden: You do not own this booking.", 403

    if booking.status == 'Cancelled':
        return redirect('/my-bookings')

    try:
        booking.status = 'Cancelled'
        
        booking.trek.available_slots += 1 
        
        db.session.commit()
        return redirect('/my-bookings')
        
    except Exception as e:
        db.session.rollback()
        return "A backend database error occurred while cancelling your journey.", 500

@app.route('/user/profile', methods=['GET', 'POST'])
def user_profile():
    user_id = session.get('user_id')
    if not user_id:
        return redirect('/login')

    current_user = User.query.get_or_404(user_id)
    
    if request.method == 'POST':
        current_user.username = request.form.get('username')
        current_user.phone = request.form.get('phone')

        db.session.commit()

        return redirect('/dashboard?success=true')

    return render_template('user_profile.html', user=current_user)