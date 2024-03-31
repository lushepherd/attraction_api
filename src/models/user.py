from marshmallow import fields
from marshmallow.validate import Length, Regexp
from sqlalchemy import UniqueConstraint

from init import db, ma
class User(db.Model):
    """
    Represents a user and their details stored in the users table, including their personal and authentication details.
    
    Attributes:
        id: Unique identifier for the user.
        name: Full name of the user.
        email: Email address of the user, must be unique and correct email format.
        password: Hashed password for user authentication, must be a minimum of 8 characters.
        phone: Contact phone number of the user, must be unique and 10 characters (representative of an Australian mobile or landline).
        is_admin: Indicates whether the user has admin privileges.
        booking_attempts: Number of booking attempts made by the user (security fraud measure).
        is_locked: Flag indicating whether the user account is locked - can lock if more than 5 bookings have been made or more than $2500 spent in a 24hr period.
        bookings: Link to the bookings made by the user.
        reviews: Link to the reviews made by the user.
    """
    __tablename__ = "users"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    phone = db.Column(db.String, nullable=False, unique=True)
    is_admin = db.Column(db.Boolean, default=False)
    booking_attempts = db.Column(db.Integer, default=0)
    is_locked = db.Column(db.Boolean, default=False)
    
    bookings = db.relationship('Booking', back_populates='user', cascade='all, delete')
    reviews = db.relationship('Review', back_populates='user', cascade='all, delete')
    
    # Allows me to apply separate error messages on different fields in the same table
    __table_args__ = (
        UniqueConstraint('email', name='uix_email'),
        UniqueConstraint('phone', name='uix_phone'),
    )
    
class UserSchema(ma.Schema):
    """
    Schema for serialising and deserialising user instances.
    
    Fields:
        id: User's unique identifier.
        name: User's full name.
        email: User's email address.
        phone: User's contact phone number.
        password: User's password (excluded in serialised output for security).
        bookings: User's bookings.
        reviews: User's reviews.
        is_locked_out: Method field to determine if user account is locked.
        
        get_lockout_status: Returns a boolean indicating if the user account is locked (True or False).
    """
    
    # Validation applied to fields for data integrity
    name = fields.String(validate=[
        Length(min=1, error="Name cannot be empty."),
        Regexp(regex=r'^[a-zA-Z\s-]+$', error="Name can't contain special characters.")
    ])
    email = fields.Email()
    phone = fields.String(validate=Length(equal=10, error="Phone number must contain 10 characters."))
    password = fields.String(validate=Length(min=8, error="Password must be at least 8 characters long."))

    bookings = fields.List(fields.Nested('BookingSchema', exclude=['user']))
    reviews = fields.List(fields.Nested('ReviewSchema'))
    
    is_locked_out = fields.Method("get_lockout_status")
    
    # Determines if the user is currently locked out of their account.
    def get_lockout_status(self, user):
        if user.is_locked:
            return True
        return False
    
    # Fields that are returned when retrieving user object from database and the order they appear
    class Meta:
        ordered = True
        fields = ('id', 'name', 'email', 'password', 'phone', 'is_locked_out', 'is_admin', 'bookings', 'reviews')      

user_schema = UserSchema(exclude=['password'])
users_schema = UserSchema(many=True, exclude=['password'])     
user_registration_schema = UserSchema()

