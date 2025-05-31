import os

from fastapi import APIRouter, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from datetime import datetime, timedelta
from passlib.context import CryptContext
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import models, schemas
from models import get_db
from dotenv import load_dotenv
from models import User

templates = Jinja2Templates(directory="static")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
router = APIRouter()


def optional_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            return None
        # Отримуємо об'єкт користувача з бази
        return db.query(User).filter(User.username == username).first()
    except JWTError:
        return None
# def optional_current_user(request: Request):
#     token = request.cookies.get("access_token")
#     if not token:
#         return None
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         return payload.get("sub")
#     except JWTError:
#         return None


def hash_password(password: str):
    return pwd_context.hash(password)


def check_password(plain, hashed):
    return pwd_context.verify(plain, hashed)


def create_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(request: Request, db: Session = Depends(get_db)) -> models.User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authorized")
    
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user

# def get_current_user(request: Request):
#     token = request.cookies.get("access_token")
#     if not token:
#         raise HTTPException(status_code=401, detail="Not authorised")
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         return payload.get("sub")
#     except JWTError:
#         raise HTTPException(status_code=401, detail="Invalid token")


@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register", response_model=schemas.UserOut)
def register(request: Request,
             username: str = Form(),
             password: str = Form(),
             db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.username == username).first()
    if existing_user:
        return templates.TemplateResponse("register.html", {"request": request, "error": "Username already taken"})

    hashed = pwd_context.hash(password)
    new_user = models.User(username=username, password=hashed)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    token = create_token({"sub": username})
    response = RedirectResponse(url='/', status_code=302)
    response.set_cookie("access_token", token)
    return response


@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login", response_model=schemas.Token)
def login(request: Request,
          username: str = Form(),
          password: str = Form(),
          db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.username == username).first()
    if not db_user or not pwd_context.verify(password, db_user.password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})

    token = create_token(data={"sub": db_user.username})
    response = RedirectResponse(url='/', status_code=302)
    response.set_cookie("access_token", token)
    return response
