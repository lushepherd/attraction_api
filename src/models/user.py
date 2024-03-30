from marshmallow import fields
from marshmallow.validate import Length, Email, Regexp
from sqlalchemy import UniqueConstraint

from init import db, ma
class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False, unique=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    bookings = db.relationship('Booking', back_populates='user', cascade='all, delete')
    reviews = db.relationship('Review', back_populates='user', cascade='all, delete')
    
    __table_args__ = (
        UniqueConstraint('email', name='uix_email'),
        UniqueConstraint('phone', name='uix_phone'),
    )
    
class UserSchema(ma.Schema):
    name = fields.String(validate=[
        Length(min=1, error="Name cannot be empty."),
        Regexp(regex=r'^[a-zA-Z\s-]+$', error="Name can't contain special characters.")
    ])
    email = fields.Email()
    phone = fields.String(validate=Length(equal=10, error="Phone number must contain 10 characters."))
    password = fields.String(validate=Length(min=8, error="Password must be at least 8 characters long."))

    bookings = fields.List(fields.Nested('BookingSchema', exclude=['user']))
    reviews = fields.List(fields.Nested('ReviewSchema', only=('attraction', 'rating', 'comment', 'created_at')))
    
    class Meta:
        ordered = True
        fields = ('id', 'name', 'email', 'password', 'phone', 'is_admin', 'bookings', 'reviews')      

user_schema = UserSchema(exclude=['password'])
users_schema = UserSchema(many=True, exclude=['password'])     
user_registration_schema = UserSchema()