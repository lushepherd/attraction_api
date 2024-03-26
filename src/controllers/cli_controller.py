from datetime import datetime

from flask import Blueprint

from init import db, bcrypt
from models.user import User
from models.booking import Booking, booking_status
from models.attraction import Attraction

db_commands = Blueprint('db', __name__)

@db_commands.cli.command('create')
def create_tables():
    db.create_all()
    print("Tables created")

@db_commands.cli.command('drop')
def drop_tables():
    db.drop_all()
    print("Tables dropped")

@db_commands.cli.command('seed')
def seed_tables():
    users = [
        User(
            name="Admin One",
            email="admin1@gmail.com",
            password=bcrypt.generate_password_hash('password').decode('utf-8'),
            phone="0455555555",
            is_admin=True
        ),
        User(
            name="User One",
            email="userone@email.com",
            password=bcrypt.generate_password_hash('password').decode('utf-8'),
            phone="0466666666",
            is_admin=False
        )
    ]
    db.session.add_all(users)
    db.session.commit()
    
    attractions = [
        Attraction(
            name="The Great Wall of China",
            description="Built to protect the Chinese states against invasions",
            location="China",
            contact_phone="0456789011",
            contact_email="greatwall@email.com",
            opening_hours="09:00 - 17:00",
            available_slots=500
        ),
        Attraction(
            name="The Colosseum",
            description="Oval amphitheatre in the centre of Rome, Italy.",
            location="Rome, Italy",
            contact_phone="0456733331",
            contact_email="colosseum@email.com",
            opening_hours="10:00 - 23:00",
            available_slots=100
        )
    ]
    db.session.add_all(attractions)
    db.session.commit()

    bookings = [
        Booking(
            user=users[1],
            attraction=attractions[0],  
            booking_date=datetime(2024, 5, 20),
            number_of_guests=2,
            status=booking_status.CONFIRMED
        ),
        Booking(
            user=users[1],
            attraction=attractions[1],  
            booking_date=datetime(2024, 7, 25),
            number_of_guests=4,
            status=booking_status.REQUESTED
        )
    ]

    db.session.add_all(bookings)
    db.session.commit()
    
    print("Tables seeded")