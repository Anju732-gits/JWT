import os
from datetime import datetime, timedelta
import token
from dotenv import load_dotenv
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, FastAPI, Request, Depends
from fastapi.security import OAuth2PasswordBearer

load_dotenv()

JWT_SECRET_KEY = os.getenv("JWT_SECRET")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")      #to protect the owner's password, we are not storing thr password as it is, we are encrypting it
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

def hash_password(password: str):
    return pwd_context.hash(password)           #to hash the password

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_token(data: dict) -> str:        #creating the token during login
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=2)
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY)
        algorithms=[JWT_ALGORITHM]
        user_id: str = payload.get("user_id")       #extracting user id from the token
        if user_id is None:  #if user id is empty
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    