from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from models import get_db, favourites_table, User, Event
import models, schemas
from auth import get_current_user
from fastapi.templating import Jinja2Templates

router = APIRouter()

templates = Jinja2Templates(directory="static")


@router.get("/events", response_model=list[schemas.EventOut])
def get_all_events(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """
    Retrieve a list of all events.

    Returns all available events from the database.

    Returns:
        List[eventOut]: A list of event objects.
    """
    
    return db.query(models.Event).all()


@router.get("/events/{event_id}", response_model=schemas.EventOut)
def get_event(event_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a single event by its ID.

    Args:
        event_id (int): The ID of the event to retrieve.

    Returns:
        eventOut: The event object if found.

    Raises:
        HTTPException: If the event with the specified ID is not found.
    """
    event = db.query(models.Event).get(event_id)
    if not event:
        raise HTTPException(404, detail="Event not found")
    return event


@router.post("/events", response_model=schemas.EventOut)
def create_event(event: schemas.EventCreate, db: Session = Depends(get_db)):
    """
    Create a new event.

    Args:
        event (eventCreate): Data required to create a new event.

    Returns:
        eventOut: The newly created event object.
    """
    new_event = models.Event(**event.dict())
    db.add(new_event)
    db.commit()
    db.refresh(new_event)
    return new_event


@router.post("/tickets")
async def buy_ticket(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Purchase a ticket for a event.

    Creates a new ticket based on the provided event and user details.

    After successful purchase, redirects the user to the 'my-events' page.
    """
    form = await request.form()
    event_id = int(form.get("event_id"))

    new_ticket = models.Ticket(user_id=current_user.id, event_id=event_id)
    db.add(new_ticket)
    db.commit()
    db.refresh(new_ticket)

    # Виконуємо редірект на сторінку "my-events"
    return RedirectResponse(url="/my-events?message=Ticket+successfully+purchased", status_code=303)


@router.get("/events/{event_id}/tickets", response_model=list[schemas.TicketOut])
def get_tickets_for_event(event_id: int, db: Session = Depends(get_db)):
    """
    Get all tickets for a specific event.

    Retrieves all purchased tickets for the specified event ID.

    Returns:
        List[TicketOut]: A list of ticket objects.
    """
    
    return db.query(models.Ticket).filter(models.Ticket.event_id == event_id).all()


@router.post("/feedbacks", response_model=schemas.FeedbackOut)
def add_feedback(feedback: schemas.FeedbackCreate, db: Session = Depends(get_db)):
    """
    Submit feedback for a event.

    Adds user feedback to the database for the specified event.

    Returns:
        FeedbackOut: The newly created feedback entry.
    """
    new_feedback = models.Feedback(**feedback.dict())
    db.add(new_feedback)
    db.commit()
    db.refresh(new_feedback)
    return new_feedback


@router.get("/events/{event_id}/feedbacks", response_model=list[schemas.FeedbackOut])
def get_feedbacks_for_event(event_id: int, db: Session = Depends(get_db)):
    """
    Retrieve feedbacks for a specific event.

    Returns all user feedback entries related to the given event.

    Returns:
        List[FeedbackOut]: A list of feedback objects.
    """
    return db.query(models.Feedback).filter(models.Feedback.event_id == event_id).all()


@router.post("/sponsors", response_model=schemas.SponsorOut)
def add_sponsor(sponsor: schemas.SponsorCreate, db: Session = Depends(get_db)):
    """
    Register a new sponsor.

    Adds a sponsor to the system based on the provided details.

    Returns:
        SponsorOut: The newly added sponsor.
    """
    new_sponsor = models.Sponsor(**sponsor.dict())
    db.add(new_sponsor)
    db.commit()
    db.refresh(new_sponsor)
    return new_sponsor


@router.get("/events/{event_id}/sponsors", response_model=list[schemas.SponsorOut])
def get_sponsors(event_id: int, db: Session = Depends(get_db)):
    """
    Retrieve sponsors for a specific event.

    Returns a list of sponsors who support the given event.

    Args:
        event_id (int): The ID of the event.

    Returns:
        List[SponsorOut]: A list of sponsor objects related to the event.
    """
    return db.query(models.Sponsor).filter(models.Sponsor.event_id == event_id).all()


@router.post("/speakers", response_model=schemas.SpeakerOut)
def add_speaker(speaker: schemas.SpeakerCreate, db: Session = Depends(get_db)):
    """
    Add a new speaker.

    Creates and stores a new speaker with the provided information.

    Args:
        speaker (SpeakerCreate): The speaker data to add.

    Returns:
        SpeakerOut: The newly created speaker object.
    """
    new_speaker = models.Speaker(**speaker.dict())
    db.add(new_speaker)
    db.commit()
    db.refresh(new_speaker)
    return new_speaker


@router.get("/events/{event_id}/speakers", response_model=list[schemas.SpeakerOut])
def get_speaker(event_id: int, db: Session = Depends(get_db)):
    """
    Retrieve speakers for a specific event.

    Returns a list of speakers associated with the specified event.

    Args:
        event_id (int): The ID of the event.

    Returns:
        List[SpeakerOut]: A list of speaker objects.
    """
    return db.query(models.Speaker).filter(models.Speaker.event_id == event_id).all()


@router.post("/add-to-favorites")
async def add_to_favorites(request: Request, db: Session = Depends(get_db),
                           current_user: User = Depends(get_current_user)):
    """
    Add a event to the user's favorites.

    Takes the event ID from a submitted form and adds it to the authenticated user's favorites list.

    Raises:
        HTTPException: If the event does not exist or is already in favorites.

    Returns:
        dict: A success message indicating the event was added.
    """

    form = await request.form()
    event_id = int(form.get('event_id'))

    event = db.query(Event).filter(Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="event not found")

    if db.query(favourites_table).filter(favourites_table.c.user_id == current_user.id,
                                         favourites_table.c.event_id == event_id).first():
        raise HTTPException(status_code=400, detail="event already in favorites")

    db.execute(favourites_table.insert().values(user_id=current_user.id, event_id=event_id))
    db.commit()

    # Перенаправлення на сторінку з параметром message
    url = "/?message=event+added+to+favorites"
    return RedirectResponse(url=url, status_code=303)

@router.post("/remove-from-favorites")
async def remove_from_favorites(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Remove a event from the user's favorites.

    This endpoint allows an authenticated user to remove a previously added event 
    from their list of favorite events. The user must be logged in. The event ID 
    must be submitted through a form as part of the request.

    Args:
        request (Request): The HTTP request object containing form data.
        db (Session): The SQLAlchemy database session.
        current_user (User): The currently authenticated user (automatically injected).

    Returns:
        RedirectResponse: Redirects the user to the "/my-events" page after successful removal.

    """
    form = await request.form()
    event_id = int(form.get("event_id"))

    db.execute(
        favourites_table.delete().where(
            (favourites_table.c.user_id == current_user.id) &
            (favourites_table.c.event_id == event_id)
        )
    )
    db.commit()
    return RedirectResponse(url="/my-events", status_code=303)

