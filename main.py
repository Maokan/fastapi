from fastapi import FastAPI, Depends, Response
from fastapi.responses import JSONResponse
from datetime import date
from typing import Optional, Any
from sqlmodel import *
from accountClasses import *
from transactionClasses import *
from random import *

app = FastAPI()

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True)
    adress_mail: str = Field(index=True)
    password: str = Field(index=True)
    name: str = Field(index=True)
    first_name: str = Field(index=True)

class Account(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    type: str = Field(index=True)
    created_date: Optional[date] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_DATE"),
        index=True
    ))
    amount: float = Field(index=True)
    user_id: int = Field(index=True, foreign_key="user.id")
    open: bool = Field(index=True, default=True)
    account_number: str = Field(index=True)

class Transaction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    transactionType: str = Field(index=True)
    transaction_date: Optional[date] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_DATE"),
        index=True
    ))
    amount: float = Field(index=True)
    start_account_id: int = Field(index=True, foreign_key="account.id")
    end_account_id: int = Field(index=True, foreign_key="account.id")
    status: str = Field(index=True, default="En cours")

class Beneficiary(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    first_name: str = Field(index=True)
    name: str = Field(index=True)
    creation_date: Optional[date] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_DATE"),
        index=True
    ))
    account_number: str = Field(index=True)
    account_id: int = Field(index=True, foreign_key="account.id")

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    
# Requêtes GET

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur FastAPI!"}

@app.get("/login") # Story 2
def login():
    return {}

@app.get("/user") # Story 3
def user():
    return {}

@app.get("/account") # Story 5
def account(body: GetAccount, session = Depends(get_session)) -> Account:
    account = session.get(Account,body.id)
    return account


@app.get("/accounts") # Story 9
def accounts(body: GetAccounts, session = Depends(get_session)) -> list[Account]:
    accounts = session.exec(select(Account)).where(Account.user_id == body.user_id)
    return accounts

@app.get("/transactions") # Story 8
def transactions():
    return {}

@app.get("/transaction") # Story 13
def transaction():
    return {}

@app.get("/beneficiaries") # Story 15
def beneficiaries():
    return {}

# Requêtes PUT

@app.put("/deposit") # Story 6
def deposit():
    return {}

def CreateTransaction(outAccountId,entryAccountId,transactionType,amount, session = Depends(get_session)):
    transaction = Transaction(transactionType=transactionType,start_account_id=entryAccountId,end_account_id=outAccountId,
                              amount=amount)
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction

@app.put("/send") # Story 7
def send(body: GetSendInformation, session = Depends(get_session)):
    send_account = session.get(Account,body.send_account_id)
    if send_account.amount >= body.amount and body.amount > 0 and body.send_account_id != body.receive_account_id:
        send_account.amount -= body.amount
        receive_account = session.get(Account,body.receive_account_id)
        receive_account.amount += body.amount
        session.commit()
        session.refresh(send_account)
        session.refresh(receive_account)
        CreateTransaction(body.receive_account_id,body.send_account_id,"Send",body.amount)
        return JSONResponse(content={"SUCCESS":"Transaction effectuée"})
    elif send_account.amount < body.amount:
        return JSONResponse(content={"ERROR":"Fonds insuffisant"})
    elif body.send_account_id != body.receive_account_id:
        return JSONResponse(content={"ERROR":"Le compte destinataire doit être différent du compte d'envoi"})
    else:
        return JSONResponse(content={"ERROR":"Montant Négatif"})

@app.put("/cancel") # Story 10
def cancel():
    return {}

@app.put("/close-account") # Story 12
def closeAccount():
    return {}

# Requêtes POST

@app.post("/sign-in") # Story 1
def createUser():
    return {}

def createAccount(user_id,type,amount, session = Depends(get_session)):
    accountNumber = randint(10000000)
    account = Account(type=type,amount=amount,user_id=user_id,account_number=accountNumber)
    session.add(account)
    session.commit()
    session.refresh(account)

@app.post("/open-account") # Story 4 / 11
def openAccount(body: CreateAccount, session = Depends(get_session)):
    CreateAccount(body.user_id,"Secondaire",0)
    return {"SUCCESS":"Compte ouvert"}

@app.post("/beneficiary") # Story 14
def beneficiary():
    return {}