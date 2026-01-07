from app.database import engine, Base
from app.models import MonitoredAccount
from sqlalchemy.exc import SQLAlchemyError

try:
    print("Attempting to create all tables...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")
except SQLAlchemyError as e:
    print(f"Error creating tables: {e}")
