from init import db, ma
from marshmallow import fields

class User(db.Model):
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False, unique=True)
    is_admin = db.Column(db.Boolean, default=False)
    
    bookings = db.relationship('Booking', back_populates='user', cascade='all, delete')
    
class UserSchema(ma.Schema):
    
    bookings = fields.List(fields.Nested('BookingSchema', exclude=['user']))
    class Meta:
        fields = ('id', 'name', 'email', 'password', 'phone', 'is_admin', 'bookings')

user_schema = UserSchema(exclude=['password'])
users_schema = UserSchema(many=True, exclude=['password'])     