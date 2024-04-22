import sys
sys.path.append("./")

import pathlib
import numpy as np
from typing import Annotated
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from fastapi.responses import JSONResponse
from fastapi import APIRouter, status, Depends, HTTPException, UploadFile
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# For reading image
import io

# Reading model
from fastai.vision.all import *

from database.session import get_db
from database.create_table import DB_TABLE
from backend_configuration.service import Service
from database.schema import RegistrationResponse, RegistrationForm, Token, TargetClass, DeleteResponse, Prediction


router = APIRouter()
PASSWORD_HASHER = CryptContext(schemes=["bcrypt"], deprecated="auto")
o2pb = OAuth2PasswordBearer(tokenUrl="/token")

@router.post("/registration", tags=["User Registration"], response_model=RegistrationResponse, status_code=status.HTTP_200_OK)
async def UserRegistration(form:RegistrationForm, db:Annotated[Session, Depends(get_db)]):
    backend_service = await Service(username=form.username, email=form.email, password=form.password, db=db).UserInDB()
    
    if not backend_service:
        new_user = DB_TABLE(**form.dict(exclude="password"), hashed_password=PASSWORD_HASHER.hash(form.password))
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return JSONResponse(content={"message":"Registration Successful"}, status_code=status.HTTP_201_CREATED)
    
    else:
        raise HTTPException(status_code=400, detail={"message":"User already in database."})
    
@router.post("/token", tags=["User Login"], status_code=status.HTTP_200_OK, response_model=Token)
async def UserLogin(form:Annotated[OAuth2PasswordRequestForm, Depends()], db:Annotated[Session, Depends(get_db)]) :
    token = await Service(username=form.username, password=form.password, db=db).Login()
    return token

@router.get("/get_class", tags=["Get Prediction Class"], status_code=status.HTTP_200_OK)  
async def GetClasses(token: Annotated[str, Depends(o2pb)], db:Annotated[Session, Depends(get_db)])->TargetClass:
    if not await Service(db=db).VerifyUser(token=token):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message":"Unauthorised Access"})
    else:
        return TargetClass(class_=['Badminton', 'Cricket', 'Karate', 'Soccer', 'Swimming', 'Tennis', 'Wrestling'])
                                        
@router.delete("/delete", tags=["Delete User"], status_code=status.HTTP_200_OK)
async def DeleteUser(token:Annotated[str, Depends(o2pb)], db:Annotated[Session, Depends(get_db)]):
    if not await Service(db=db).VerifyUser(token=token):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message":"Unauthorised Access"})
    else:
        return await Service(db=db).DeleteUser(token=token)
    
@router.post("/get_prediction", tags=["Predict Celebrity"], status_code=status.HTTP_200_OK)
async def GetPrediction(image:UploadFile, token:Annotated[str, Depends(o2pb)], db:Annotated[Session, Depends(get_db)]): 
    if not await Service(db=db).VerifyUser(token=token):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message":"Unauthorised Access"})
    else:
        try:
            # Loads the binary form of the image
            byte_image = await image.read()
            # Convert the binary image to PIL image
            pil_image = PILImage.create(io.BytesIO(initial_bytes=byte_image))
            
            pil_image = pil_image.convert("RGB")
            
            # Resize the image 
            pil_image = pil_image.resize((224, 224)) 
            
            # Convert image to numpy array
            pil_image = np.array(pil_image)
            
            posix_backup = pathlib.PosixPath
            try:
                pathlib.PosixPath = pathlib.WindowsPath
                learner = load_learner("model\learner_2.pkl")
            finally:
                pathlib.PosixPath = posix_backup
            
            model_prediction = learner.predict(pil_image)
            
            return {"prediction":model_prediction[0]}
        
        except:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail={"message":"Uploaded file must be a jpg or png format"})