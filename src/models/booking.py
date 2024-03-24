from marshmallow import fields
from marshmallow.validate import OneOf

from init import db, ma

BookingStatus = ('Requested', 'Confirmed', 'Cancelled')

class Booking(db.Model):
    __tablename__ = "bookings"
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    attraction_id = db.Column(db.Integer, db.ForeignKey('attractions.id'), nullable=False)
    booking_date = db.Column(db.DateTime, nullable=False)
    number_of_guests = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String, nullable=False, default='Requested')

    user = db.relationship('User', back_populates='bookings', cascade='all, delete')

class BookingSchema(ma.Schema):
    status = fields.String(validate=OneOf(BookingStatus))
    user = fields.Nested('UserSchema', only = ['name', 'email', 'phone'])
    
    class Meta:
        fields = ('id', 'booking date', 'number of guests', 'status', 'attraction', 'user')

booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)
    