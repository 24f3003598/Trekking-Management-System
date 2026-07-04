from flask import Flask, render_template, request, redirect, session
from models import db, User, Trek, Booking

from app import app 

@app.route('/explore-treks')
def explore_treks():
    open_treks = Trek.query.filter_by(status='Open').all()
    return render_template('explore.html', treks=open_treks)


@app.route('/book-trek/<int:trek_id>', methods=['POST'])
def book_trek(trek_id):
    current_trekker = User.query.filter_by(role='Trekker').first()
    if not current_trekker:
        return "Authentication Error: Please register/log in as a Trekker first.", 403

    trek = Trek.query.get_or_404(trek_id)

    if trek.status != 'Open':
        return "Booking Failed: This trek is currently closed or unavailable.", 400

    if trek.available_slots <= 0:
        return "Booking Failed: Sorry, no available slots left!", 400

    try:
        new_booking = Booking(
            user_id=current_trekker.user_id,
            trek_id=trek.trek_id,
            status='Booked'
        )

        trek.available_slots -= 1

        db.session.add(new_booking)
        db.session.commit()

        return redirect('/dashboard')

    except Exception as e:
        db.session.rollback()
        return f"An unexpected system database error occurred: {str(e)}", 500