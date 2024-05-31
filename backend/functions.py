from database import create_db_and_tables, engine
from models import User, Message
from chatController import ChatController

from sqlmodel import Session, select
from passlib.context import CryptContext

from loguru import logger
import logging
from datetime import datetime, UTC

setup = logger.level("SETUP", no=26, color="<magenta>", icon="💻")
conv = logger.level("CONV", no=27, color="\u001b[30;1m", icon="💬")
utctime = datetime.now(UTC).strftime("%Y-%m-%d_%H-%M-%S")
logger.add("log/" + utctime + "/debug_" + utctime + ".log",
           format="{time} {level} {message}", level="DEBUG")
logger.add("log/" + utctime + "/info_" + utctime + ".log",
           format="{time} {level} {message}", level="INFO")
logger.add("log/" + utctime + "/conv_" + utctime + ".log",
           format="{level} {message}", level="SETUP")


create_db_and_tables()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


openaikey = "sk-proj-vfjH4tydJOk1A9tdxqQKT3BlbkFJWOVNXRpawSijxmRszr8H"

def messageNumber(user_id: int):
    with Session(engine) as session:
        statement = select(Message).where(Message.user_id == user_id)
        return len(session.exec(statement).all())

def messageByNumber(user_id: int, message_n:int):
    with Session(engine) as session:
        statement = select(Message).where(Message.user_id == user_id).where(Message.order == message_n)
        return session.exec(statement).one()
    
def userById(user_id: int):
    with Session(engine) as session:
        statement = select(User).where(User.id == user_id)
        return session.exec(statement).one()
    
def userByUsername(username: str):
    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        return session.exec(statement).one()

def messageSend(user_id: int, message:str):
    u = userById(user_id)
    n = messageNumber(user_id)
    chat = ChatController(openaikey, messageByNumber(user_id, 0).content, "Assistant")
    for x in range(n):
        if x != 0:
            messageDB = messageByNumber(user_id, x)
            if messageDB.sender == "user":
                chat.join_context(messageDB.sender, messageDB.content, u.username)
            elif messageDB.sender == "assistant":
                chat.join_context(messageDB.sender, messageDB.content, "Assistant")
            else:
                Exception()
            chat.reduce_context()
    answer = chat.answer_request(message, u.username)
    with Session(engine) as session:
        uM = Message(sender="user", content=message, order=n, user_id=user_id)
        uA = Message(sender="assistant", content=answer, order=n+1, user_id=user_id)
        session.add(uM)
        session.add(uA)
        session.commit()
    return answer
    
def authenticate_user(username: str, password: str):
    try:
        user = userByUsername(username)
    except Exception:
        user = False
    if not user:
        return False
    if not pwd_context.verify(password, user.password):
        return False
    return user

from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta, timezone
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from pydantic import BaseModel

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "12b3fb373fa05c0594a335415abaf37a627bc38259e3165cc36798501a09e305"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class TokenData(BaseModel):
    username: str | None = None

class UserNONRECURSIVE(BaseModel):
    id: int
    username: str


def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except InvalidTokenError:
        raise credentials_exception
    user = UserNONRECURSIVE(username=userByUsername(token_data.username).username, id=userByUsername(token_data.username).id)
    if user is None:
        raise credentials_exception
    return user