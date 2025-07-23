
from sqlmodel import SQLModel, create_engine, Session
from models import User, ToDo


DATABASE_URL = "sqlite:///sqlite.db"
engine = create_engine(DATABASE_URL, echo=True)

def get_session():
  with Session(engine) as session:
    yield session

def create_db_and_tables():
  from models import SQLModel
  SQLModel.metadata.create_all(engine)
  
  