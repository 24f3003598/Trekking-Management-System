from flask import Flask, render_template, request, redirect, session,url_for
from models import db, User, Trek, Booking

from app import app 

@app.route('/explore-treks')
def explore_treks():
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']

    booked_bookings = Booking.query.filter_by(user_id=user_id, status='Confirmed').all()
    booked_trek_ids = [b.trek_id for b in booked_bookings]

    open_treks = Trek.query.filter_by(status='Open').all()
    return render_template('explore.html', treks=open_treks, booked_trek_ids=booked_trek_ids)

@app.route('/book/<int:trek_id>', methods=['POST'])
def book_trek(trek_id):
    if 'user_id' not in session:
        return redirect('/login')

    user_id = session['user_id']
    trek = Trek.query.get_or_404(trek_id)

    existing_booking = Booking.query.filter_by(user_id=user_id, trek_id=trek_id).first()
    if existing_booking and existing_booking.status != 'Cancelled':
        return render_template('booking_failed.html', trek=trek, reason="You have already booked this trek route.")

    if trek.status != 'Open' or trek.available_slots <= 0:
        return render_template('booking_failed.html', trek=trek, reason="This trek is fully booked or closed.")

    trek.available_slots -= 1

    new_booking = Booking(
        user_id=user_id,
        trek_id=trek_id,
        status='Confirmed'
    )
    
    db.session.add(new_booking)
    db.session.commit()

    current_user = User.query.get(user_id)
    return render_template('booking_success.html', trek=trek, user=current_user)

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
    if 'user_id' not in session or session['user_role'] != 'Trekker':
        return redirect('/login')
        
    user_id = session['user_id']
    user_bookings = Booking.query.filter_by(user_id=user_id).all()
    return render_template('my_bookings.html', bookings=user_bookings)

@app.route('/booking/delete/<int:booking_id>', methods=['POST'])
def delete_booked_trek(booking_id):
    if 'user_id' not in session or session['user_role'] != 'Trekker':
        return "Access Forbidden", 403

    booking = Booking.query.get_or_404(booking_id)

    if booking.user_id != session['user_id']:
        return "Unauthorized Operation", 401

    db.session.delete(booking)
    db.session.commit()
    
    return redirect('/my-bookings')