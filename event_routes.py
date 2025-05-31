from fastapi import APIRouter, Depends, HTTPException ,Request
from fastapi.responses import RedirectResponse  
from sqlalchemy.orm import Session
from models import get_db, favourites_table,User, Event
import models, schemas
from auth import get_current_user

router = APIRouter()


@router.get("/events", response_model=list[schemas.EventOut])
def get_all_events(db: Session = Depends(get_db)):
    return db.query(models.Event).all()


@router.get("/events/{event_id}", response_model=schemas.EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    event = db.query(models.Event).get(event_id)
    if not event:
        raise HTTPException(404, detail="Event not found")
    return event


@router.post("/events", response_model=schemas.EventOut)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    new_event = models.Event(**event.dict())
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


@router.post("/tickets", response_model=schemas.TicketOut)
def buy_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    new_ticket = models.Ticket(**ticket.dict())
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)
    return new_ticket


@router.get("/events/{event_id}/tickets", response_model=list[schemas.TicketOut])
def get_tickets_for_event(event_id: int, db: Session = Depends(get_db)):
    return db.query(models.Ticket).filter(models.Ticket.event_id == event_id).all()


@router.post("/feedbacks", response_model=schemas.FeedbackOut)
def add_feedback(feedback: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    new_feedback = models.Feedback(**feedback.dict())
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return new_feedback


@router.get("/events/{event_id}/feedbacks", response_model=list[schemas.FeedbackOut])
def get_feedbacks_for_event(event_id: int, db: Session = Depends(get_db)):
    return db.query(models.Feedback).filter(models.Feedback.event_id == event_id).all()


@router.post("/sponsors", response_model=schemas.SponsorOut)
def add_sponsor(sponsor: schemas.SponsorCreate, db: Session = Depends(get_db)):
    new_sponsor = models.Sponsor(**sponsor.dict())
    db.add(new_sponsor)
    db.commit()
    db.refresh(new_sponsor)
    return new_sponsor


@router.get("/events/{event_id}/sponsors", response_model=list[schemas.SponsorOut])
def get_sponsors(event_id: int, db: Session = Depends(get_db)):
    return db.query(models.Sponsor).filter(models.Sponsor.event_id == event_id).all()


@router.post("/speakers", response_model=schemas.SpeakerOut)
def add_speaker(speaker: schemas.SpeakerCreate, db: Session = Depends(get_db)):
    new_speaker = models.Speaker(**speaker.dict())
    db.add(new_speaker)
    db.commit()
    db.refresh(new_speaker)
    return new_speaker


@router.get("/events/{event_id}/speakers", response_model=list[schemas.SpeakerOut])
def get_speaker(event_id: int, db: Session = Depends(get_db)):
    return db.query(models.Speaker).filter(models.Speaker.event_id == event_id).all()

# @router.post("/add-to-favorites")
# async def add_to_favorites(
#     request: Request,
#     db: Session = Depends(get_db),
#     current_user: User = Depends(get_current_user),
#     event_id: int = Form(...)
# ):
#     event = db.query(Event).filter(Event.id == event_id).first()
#     if not event:
#         request.session["message"] = "Event do not found!"
#         return RedirectResponse("/", status_code=HTTP_302_FOUND)

#     already = db.query(favourites_table).filter(
#         favourites_table.c.user_id == current_user.id,
#         favourites_table.c.event_id == event_id
#     ).first()

#     if already:
#         request.session["message"] = "Event in favourites"
#     else:
#         db.execute(favourites_table.insert().values(user_id=current_user.id, event_id=event_id))
#         db.commit()
#         request.session["message"] = "Event added to favourites"

#     return RedirectResponse("/", status_code=HTTP_302_FOUND)


@router.post("/add-to-favorites")
async def add_to_favorites(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):

    form = await request.form()
    event_id = int(form.get('event_id'))


    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="event not found")

    if db.query(favourites_table).filter(favourites_table.c.user_id == current_user.id, favourites_table.c.event_id == event_id).first():
        raise HTTPException(status_code=400, detail="event already in favorites")

    db.execute(favourites_table.insert().values(user_id=current_user.id, event_id=event_id))
    db.commit()

    return {"success": True, "message": "event added to favorites!"}


# @router.post("/favorite/{event_id}")
# def add_favorite(event_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
#     event = db.query(models.event).filter(models.event.id == event_id).first()
#     if not event:
#         raise HTTPException(status_code=404, detail="event not found")
#     if event in current_user.favorites:
#         raise HTTPException(status_code=400, detail="Already in favorites")

#     current_user.favorites.append(event)
#     db.commit()
#     return RedirectResponse(url="/", status_code=303) 
