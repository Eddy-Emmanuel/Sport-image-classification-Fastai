import sys
sys.path.append("./")

from database.session import Base

from sqlalchemy import Column, Integer, String

class DB_TABLE(Base):
    __tablename__ = "UserDB"
    
    id =  Column(Integer, primary_key=True, autoincrement=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String, unique=True)
    
    