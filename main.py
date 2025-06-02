from fastapi import FastAPI, HTTPException, Depends, Response
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from models import get_db, Base, engine
from sqlalchemy.orm import Session
from auth import router as auth_router, get_current_user, optional_current_user
from event_routes import router as event_router
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.requests import Request
from models import User
import models

app = FastAPI()

templates = Jinja2Templates(directory="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(event_router)

app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/logout")
def logout(response: Response):
    response = RedirectResponse(url="/", status_code=302)
    response.delete_cookie("access_token")
    return response


@app.get("/", response_class=HTMLResponse)
def homepage(request: Request, db: Session = Depends(get_db), user: User = Depends(optional_current_user)):
    events = db.query(models.Event).all()
    message = request.query_params.get("message")
    
    context = {
        "request": request,
        "events": events,
        "user": user,
        "message": message
    }
    return templates.TemplateResponse("main_page.html", context)


@app.get("/my-events", response_class=HTMLResponse)
def my_events(request: Request, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    favorite_events = current_user.favorites  # Завдяки relationship, не треба вручну SQL
    message = request.query_params.get("message")
    return templates.TemplateResponse("mojeeventy.html", {
        "request": request,
        "events": favorite_events,
        "user": current_user,
        "message": message
        
        
    })

