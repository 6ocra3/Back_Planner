from sqlalchemy import Column, Integer, ForeignKey, VARCHAR, UniqueConstraint, SMALLINT, ARRAY, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Tasks(Base):
    __tablename__="tasks"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    task = Column(VARCHAR(50), nullable=False)
    status = Column(SMALLINT,  nullable=False)
    days = Column(ARRAY(Integer, dimensions=1), nullable=False, default=[0,0,0,0,0,0,0])

class TrackerOrder(Base):
    __tablename__="tracker_order"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    order = Column(ARRAY(Integer, dimensions=1), nullable=False)

class ListOrder(Base):
    __tablename__="list_order"
    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    order = Column(JSON, nullable = False)

class User(Base):
    __tablename__="users"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    username = Column(VARCHAR(50), nullable=True)
    password = Column(VARCHAR(300), nullable=False)
    email = Column(VARCHAR(40))

    UniqueConstraint(username, name="username")
    UniqueConstraint(email, name="email")


class MusicalComposition(Base):

    __tablename__="musical_compositions"

    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey(f'{User.__tablename__}.{User.id.name}'), nullable=False)
    url = Column(VARCHAR(60), nullable=True)
    user = relationship("User", backref="musical_composition")
