from sqlalchemy import Column, Integer, String, Date, ForeignKey
from pydantic import BaseModel
from datetime import date
from database.base import Base  
from models.user import User  
from typing import Optional
from pydantic import BaseModel

class Project(Base):
    __tablename__ = "project"
    __table_args__ = {'extend_existing': True, 'schema': 'tetrascan'}

    id_project = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String)
    companies = Column(String)
    crop_type = Column(String)
    cultivar = Column(String)
    description = Column(String)
    start_date = Column(Date)
    update_date = Column(Date)
    status = Column(String)
    user_id = Column(Integer, ForeignKey("tetrascan.users.id_user"), nullable=False)

class ProjectCreate(BaseModel):
    name: str
    companies: str
    crop_type: str
    cultivar: str
    description: Optional[str] = None  # Tornando opcional
    start_date: Optional[date] = None  # Tornando opcional
    update_date: Optional[date] = None  # Tornando opcional
    status: Optional[str] = "active"   # Valor padrão
    user_id: int

class ProjectUpdate(BaseModel):
    name: str
    companies: str
    crop_type: str
    cultivar: str
    description: str
    start_date: date
    update_date: date
    status: str