from marshmallow import fields
from marshmallow.validate import OneOf

from init import db, ma

class booking_status:
    REQUESTED = 'Requested'
    CONFIRMED = 'Confirmed'
    CANCELLED = 'Cancelled'
    
class Booking(db.Model):
    __tablename__ = "bookings"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    attraction_name = db.Column(db.String, nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False)
    number_of_guests = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, nullable=False, default=booking_status.REQUESTED)

    user = db.relationship('User', back_populates='bookings', cascade='all, delete')

class BookingSchema(ma.Schema):
    status = fields.String(validate=OneOf([booking_status.REQUESTED, booking_status.CONFIRMED, booking_status.CANCELLED]))
    user = fields.Nested('UserSchema', only = ['name', 'email', 'phone'])
    
    class Meta:
        model = Booking

booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)
    