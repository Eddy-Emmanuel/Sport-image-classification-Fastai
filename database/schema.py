from pydantic import BaseModel

class RegistrationResponse(BaseModel):
    message : dict
    
    class Config:
        orm_mode = True
        
class Token(BaseModel):
    access_token : str
    token_type : str
    
class RegistrationForm(BaseModel):
    username : str
    email : str
    password : str
    
class TargetClass(BaseModel):
    class_ : list
    
    
class DeleteResponse(BaseModel):
    message : str
    
class Prediction(BaseModel):
    prediction : str