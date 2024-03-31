from datetime import datetime

from flask import Blueprint

from init import db, bcrypt
from models.user import User
from models.booking import Booking, booking_status
from models.attraction import Attraction
from models.review import Review

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
            email="admin@email.com",
            password=bcrypt.generate_password_hash('password').decode('utf-8'),
            phone="0455555555",
            is_admin=True
        ),
        User(
            name="User One",
            email="user1@email.com",
            password=bcrypt.generate_password_hash('password').decode('utf-8'),
            phone="0466666666",
            is_admin=False
        )
    ]
    db.session.add_all(users)
    db.session.commit()
    
    attractions = [
        Attraction(
            name="The Wheel of Brisbane",
            ticket_price=40,
            description="Iconic landmark on South Bank.",
            location="Brisbane",
            contact_phone="0756789011",
            contact_email="brisbanewheel@email.com",
            opening_hours="10:00 - 21:00",
            available_slots=30
        ),
        Attraction(
            name="Story Bridge Adventure Climb",
            ticket_price=70,
            description="Panoramic group walks in safety harnesses across Brisbane's cantilever bridge.",
            location="Brisbane",
            contact_phone="0755736631",
            contact_email="brisbanebridge@email.com",
            opening_hours="06:00 - 15:00",
            available_slots=100
        )
    ]
    db.session.add_all(attractions)
    db.session.commit()

    bookings = [
        Booking(
            user=users[1],
            attraction=attractions[0],  
            booking_date=datetime(2023, 5, 20),
            number_of_guests=2,
            total_cost=80,
            status=booking_status.CONFIRMED
        ),
        Booking(
            user=users[0],
            attraction=attractions[1],  
            booking_date=datetime(2024, 7, 25),
            number_of_guests=4,
            total_cost=280,
            status=booking_status.REQUESTED
        )
    ]

    db.session.add_all(bookings)
    db.session.commit()
    
    reviews = [
        Review(
            user=users[1],
            attraction=attractions[0],  
            rating=7,
            comment="Was really busy, long queues",
        ),
        Review(
            user=users[0],
            attraction=attractions[1],  
            rating=10,
            comment="Best day of my life!",
        ),      
    ]

    db.session.add_all(reviews)
    db.session.commit()
    
    print("Tables seeded")