# user.py
from sqlalchemy import Column, Integer, String, Date
from database.base import Base 

class User(Base):
    __tablename__ = "users"
    __table_args__ = {'extend_existing': True, 'schema': 'tetrascan'}

    id_user = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    avatar = Column(String, nullable=True)
    company = Column(String, nullable=True)
    created_at = Column(Date, nullable=False)
