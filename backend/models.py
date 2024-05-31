from typing import Optional

from sqlmodel import Field, SQLModel, Relationship

class User (SQLModel,table=True):
    id: int|None = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    password: str
    icon: Optional[int]

    messages: list["Message"] = Relationship(back_populates="user")

class Message (SQLModel,table=True):
    id: int|None = Field(default=None, primary_key=True)
    sender: str
    content: str
    order: int

    user_id: int = Field(default=None, foreign_key="user.id")
    user:User = Relationship(back_populates="messages")
