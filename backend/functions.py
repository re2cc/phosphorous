from database import create_db_and_tables, engine
from models import User, Message
from chatController import ChatController

from sqlmodel import Session, select


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
    return uM
    

print(messageNumber(1))
print(messageByNumber(1, 1))
messageSend(1, "And that + 11?")