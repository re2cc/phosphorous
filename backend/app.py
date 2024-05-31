from functions import *
from models import Message

from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import  OAuth2PasswordRequestForm
from pydantic import BaseModel

# to get a string like this run:
# openssl rand -hex 32
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class Token(BaseModel):
    access_token: str
    token_type: str

class UserNonRecursive(BaseModel):
    id: int
    username: str


app = FastAPI()


@app.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return Token(access_token=access_token, token_type="bearer")


@app.get("/user/", response_model=UserNonRecursive)
async def read_users_me(
    current_user: Annotated[UserNonRecursive, Depends(get_current_user)],
):
    return current_user

@app.post("/user/register")
async def registerUser(
    username: str,
    password: str
):
    createUser(username, password)

    
@app.post("/chat/sys")
async def changeSysPmt(
    current_user: Annotated[UserNonRecursive, Depends(get_current_user)],
    message: str
):
    editPrompt(current_user.id, 0, message)

@app.get("/chat/number/")
async def nmessages(
    current_user: Annotated[UserNonRecursive, Depends(get_current_user)],
):
    return messageNumber(current_user.id)

@app.get("/chat/message/{n_message}")
async def nmessage(
    current_user: Annotated[UserNonRecursive, Depends(get_current_user)],
    n_message: int
):
    return messageByNumber(current_user.id, n_message)

@app.get("/chat/send")
async def smessage(
    current_user: Annotated[UserNonRecursive, Depends(get_current_user)],
    message: str
):
    return messageSend(current_user.id, message)