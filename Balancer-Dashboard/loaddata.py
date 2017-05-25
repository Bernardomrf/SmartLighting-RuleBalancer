from app import db
from models.User import User


def populate():
    try:
        print("Trying to insert data...")
        user = User("admin", "admin")
        db.session.add(user)
        db.session.commit()
        print("Successfully inserted data!")
    except:
        print("Error inserting data, rolling back!")
        db.session.rollback()
