from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class EventOut(BaseModel):
    id: int
    name: str
    description: str

    class Config:
        from_attributes = True


class EventCreate(BaseModel):
    name: str
    description: str


class TicketCreate(BaseModel):
    event_id: int
    user_id: int


class TicketOut(BaseModel):
    id: int
    event_id: int
    user_id: int

    class Config:
        from_attributes = True


class FeedbackCreate(BaseModel):
    event_id: int
    user_id: int
    comment: str


class FeedbackOut(BaseModel):
    id: int
    event_id: int
    user_id: int
    comment: str

    class Config:
        from_attributes = True


class SponsorCreate(BaseModel):
    event_id: int
    firm_name: str


class SponsorOut(BaseModel):
    id: int
    event_id: int
    firm_name: str

    class Config:
        from_attributes = True


class SpeakerCreate(BaseModel):
    event_id: int   
    name: str


class SpeakerOut(BaseModel):
    id: int
    event_id: int
    name: str

    class Config:
        from_attributes = True
