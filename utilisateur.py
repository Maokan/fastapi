#fastapi dev utilisateur.py

from datetime import datetime, timedelta
from fastapi import Depends, FastAPI, HTTPException, Security
from pydantic import BaseModel
from sqlmodel import SQLModel, Session, create_engine, select
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from main import User
import bcrypt
import jwt

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)
secret_key = "SLVM"
Algorithm = "HS256"
security = HTTPBearer(auto_error=False)
global user_id
def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

app = FastAPI()
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

class CreateUser(BaseModel):
    username:str
    adress_mail:str
    password:str
    name:str
    first_name:str

class GetUser(BaseModel):
    adress_mail:str
    password:str

class GetUserInfos(BaseModel):
    username:str
    adress_mail:str
    name:str
    first_name:str

@app.post("/users/")
def create_user(body: CreateUser, session = Depends(get_session)) -> User:
    user = User(name=body.name)
    session.add(user)
    session.commit()
    session.refresh(user)
    return user



@app.post("/getUser/")
def create_item (getUser:GetUser)-> GetUser:
    return GetUser
    
@app.post("/register")
def register(body: CreateUser, session: Session = Depends(get_session)):
    print(body.password)
    chiffrement = bcrypt.hashpw(body.password.encode('utf-8'), bcrypt.gensalt())
    user = User(name=body.name,username=body.username,adress_mail=body.adress_mail,password=chiffrement,first_name=body.first_name)
         # Vérifie si l'utilisateur existe déjà
    statement = select(User).where(User.adress_mail == body.adress_mail)
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Un utilisateur ayant cette adresse email est déjà enrengistré")
    else:
        print(chiffrement)
        session.add(user)
        session.commit()
        session.refresh(user)
    return user
@app.get("/users")
def users(session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

@app.post("/login")
def login(body:GetUser, session:Session = Depends(get_session)):
    # Recherche de l'utilisateur
    statement = select(User).where(User.adress_mail == body.adress_mail)
    mail = session.exec(statement).first()
    if not mail:
        raise HTTPException(status_code=404, detail="Adresse mail incorrecte")
    # Vérifie le mot de passe
    if not bcrypt.checkpw(body.password.encode('utf-8'), mail.password):
        raise HTTPException(status_code=401, detail="Mot de passe incorrecte")

    global user_id
    user_id = mail.id
    return {"message": f"Welcome back, {mail.username} !"}

@app.get("/infos", response_model=GetUserInfos)
def infos(session:Session = Depends(get_session)):
        user = session.get(User, user_id)

        return user