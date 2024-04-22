import sys
sys.path.append("./")

from jose import jwt, JWTError
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import datetime, timedelta
from fastapi import HTTPException, status

from database.create_table import DB_TABLE
from backend_configuration.configuration import Config

configuration = Config()
PASSWORD_HASHER = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Service:
    def __init__(self, db:Session, username=None, email=None, password=None):
        self.username = username
        self.email = email
        self.password = password
        self.db = db
        
    async def UserInDB(self):
        user = self.db.query(DB_TABLE).filter(DB_TABLE.username == self.username, DB_TABLE.email == self.email).first()
        
        if not user:
            return False
        
        else:
            return True
        
    async def Login(self):
        user = self.db.query(DB_TABLE).filter(DB_TABLE.username == self.username).first()
        
        if not user:
            raise HTTPException(status_code=400, detail={"message":"Username not in database"})
        
        if not PASSWORD_HASHER.verify(secret=self.password, hash=user.hashed_password):
            raise HTTPException(status_code=400, detail={"message":"Incorrect password"})
        
        token_expr_time = datetime.utcnow() + timedelta(minutes=60)
        
        return {"access_token":jwt.encode({"username":user.username, "exp":token_expr_time}, 
                                          key=configuration.SECRET_KEY, 
                                          algorithm=configuration.ALGORITHM), 
                "token_type":"bearer"}
        
    async def VerifyUser(self, token:str):
        try:
            decoded_token = jwt.decode(token=token, key=configuration.SECRET_KEY, algorithms=configuration.ALGORITHM)
            username = decoded_token.get("username", None)
            user = self.db.query(DB_TABLE).filter(DB_TABLE.username == username).first()
    
            if (user is None) or (username is None):
                return False
            else:
                return True
            
        except JWTError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message":"Could not validate credintials"})
        
    async def DeleteUser(self, token:str):
        try:
            decoded_token = jwt.decode(token=token, key=configuration.SECRET_KEY, algorithms=configuration.ALGORITHM)
            username = decoded_token.get("username", None)
            user = self.db.query(DB_TABLE).filter(DB_TABLE.username == username).first()
    
            if (user is None) or (username is None):
                return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message":"User not in database"})
            else:
                self.db.delete(user)
                self.db.commit()
                return {"message":"User sucessfully deleted"}
            
        except JWTError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message":"Could not validate credintials"})
        