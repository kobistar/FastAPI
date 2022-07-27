from itsdangerous import Serializer
from sqlalchemy import Column, Integer, String

from .database import Base


class Post(Base):
    __tablename__ = "posts"

    userid = Column(Integer, nullable=False)
    id = Column(Integer, primary_key=True, nullable=False)
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)

