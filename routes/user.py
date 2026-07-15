from flask import Flask, render_template, request, redirect, session,url_for
from datetime import datetime
from models import db, User, Trek, Booking
from app import app 

def check_trekker():
    return 'user_id' not in session and session['user_role'] == 'Trekker'

@app.route('/explore-treks')
def explore_treks():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    booked_bookings = Booking.query.filter_by(user_id=user_id, status='Confirmed').all()
    booked_trek_ids = [b.trek_id for b in booked_bookings]

    open_treks = Trek.query.filter_by(status='Open').all()
    return render_template('explore.html', treks=open_treks, booked_trek_ids=booked_trek_ids)

@app.route('/book/<int:trek_id>', methods=['GET', 'POST'])
def book_trek(trek_id):
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    trek = Trek.query.get_or_404(trek_id)
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        if trek.status != 'Open' or trek.available_slots <= 0:
            return "Trek is not available", 400

        trek.available_slots -= 1
        new_booking = Booking(user_id=user_id, trek_id=trek_id, status='Confirmed')
        db.session.add(new_booking)
        db.session.commit()

        return redirect(url_for('booking_success', trek_id=trek_id))

    return render_template('booking_trek.html', trek=trek, user=user)

@app.route('/booking-success/<int:trek_id>')
def booking_success(trek_id):
    trek = Trek.query.get_or_404(trek_id)
    return render_template('booking_success.html', trek=trek)

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

@app.route('/my-bookings')
def my_bookings():
    user_id = session['user_id']
    if not user_id:
        return redirect('/login')
    user_bookings = Booking.query.filter_by(user_id=user_id).all()
    return render_template('my_bookings.html', bookings=user_bookings )

@app.route('/booking/delete/<int:booking_id>', methods=['POST'])
def delete_booked_trek(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != session['user_id']:
        return "Unauthorized Operation", 401

    db.session.delete(booking)
    db.session.commit()
    
    return redirect('/my-bookings')