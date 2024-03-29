from init import db, ma
from marshmallow import fields
from sqlalchemy import UniqueConstraint

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
    bookings = fields.List(fields.Nested('BookingSchema', exclude=['user']))
    reviews = fields.List(fields.Nested('ReviewSchema', only=('rating', 'comment', 'created_at')))
    class Meta:
        ordered = True
        fields = ('id', 'name', 'email', 'password', 'phone', 'is_admin', 'bookings', 'reviews')      

user_schema = UserSchema(exclude=['password'])
users_schema = UserSchema(many=True, exclude=['password'])     