from app import db
from models.user import User


def populate():
    try:
        print("Trying to insert data...")
        user = User("smart", "admin")
        db.session.add(user)
        db.session.commit()
        print("Successfully inserted data!")
    except Exception as e:
        #print(e)
        print("Error inserting data, rolling back!")
        db.session.rollback()
