from flask import Blueprint
from init import db, bcrypt
from models.user import User

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
    print("Tables seeded")