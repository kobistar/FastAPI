from datetime import datetime
from pydantic import BaseModel

class PostBase(BaseModel):
    title: str
    body: str
    userid: int

class PostCreate(PostBase):
    pass 
    
class Post(PostBase):
    id: int
    
    class Config:
        orm_mode = True