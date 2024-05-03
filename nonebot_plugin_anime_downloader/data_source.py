from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


ACGRIPBase = declarative_base()
UserBase = declarative_base()
VideoBase = declarative_base()


class ACGRIPData(ACGRIPBase):
    __tablename__ = "acgrip"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String)
    size = Column(String)


class User(UserBase):
    __tablename__ = "users"

    id = Column(String, primary_key=True) # group/private_id
    tags = Column(String) # json : list[list[str]]


class Video(VideoBase):
    __tablename__ = "videos"

    id = Column(Integer, primary_key=True)
    title = Column(String)
    path = Column(String)
