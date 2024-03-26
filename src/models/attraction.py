from init import db, ma
from marshmallow import fields

class Attraction(db.Model):
    __tablename__ = "attractions"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)
    contact_phone = db.Column(db.String, nullable=False)
    contact_email = db.Column(db.String, nullable=False)
    opening_hours = db.Column(db.String, nullable=False)
    available_slots = db.Column(db.Integer, nullable=False)

    bookings = db.relationship('Booking', back_populates='attraction')

class AttractionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        fields = ('id', 'name', 'description', 'location', 'contact_phone', 'contact_email', 'opening_hours', 'available_slots')

attraction_schema = AttractionSchema()
attractions_schema = AttractionSchema(many=True)