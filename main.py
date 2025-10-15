from fastapi import FastAPI, Depends, Response
from fastapi.responses import JSONResponse
from datetime import date
from typing import Optional, Any
from sqlmodel import *
from accountClasses import *
from transactionClasses import *
from random import *
import asyncio

print("[DEBUG] Début du chargement de main.py")
app = FastAPI()
interrupt_event = asyncio.Event()

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
    type: str = Field(index=True)
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
    accounts = session.exec(select(Account).where(Account.user_id == body.user_id).order_by(col(Account.id).desc())).all()
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
def deposit(body: SetDeposit, session = Depends(get_session)):
    if body.amount > 0 and body.amount <= 2000:
        account = session.get(Account,body.account_id)
        account.amount += body.amount
        session.commit()
        session.refresh(account)
        CreateTransaction(body.receive_account_id,0,"Deposit",body.amount)
        return {"Nouveau Solde":account.amount}
    elif body.amount > 0:
        return {"ERROR":"Montant supérieur à 2000"}
    else:
        return {"ERROR":"Montant négatif"}

def CreateTransaction(outAccountId,entryAccountId,transactionType,amount, session):
    if entryAccountId == 0:
        transaction = Transaction(type=transactionType,end_account_id=outAccountId,amount=amount)
    else:
        transaction = Transaction(type=transactionType,start_account_id=entryAccountId,end_account_id=outAccountId,
                              amount=amount)
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction

def confirmTransaction(transactionId, session):
    transaction = session.get(Transaction,transactionId)
    transaction.status = "Validée"
    session.commit()
    session.refresh(transaction)
    return transaction

def cancelTransaction(transactionId, session):
    transaction = session.get(Transaction,transactionId)
    transaction.status = "Annulée"
    session.commit()
    session.refresh(transaction)
    return transaction

# Dictionnaire pour stocker les events d'attente par compte
pending_send_events = {}

@app.put("/send") # Story 7
async def send(body: GetSendInformation, session = Depends(get_session)):
    # Crée un event pour ce compte
    event = asyncio.Event()
    pending_send_events[body.send_account_id] = event
    transaction = CreateTransaction(body.receive_account_id,body.send_account_id,"Send",body.amount,session)
    try:
        # Attente de 5 secondes ou annulation
        await asyncio.wait_for(event.wait(), timeout=5)
        confirmTransaction(transaction.id, session)
        send_account = session.get(Account,body.send_account_id)
        if send_account.amount >= body.amount and body.amount > 0 and body.send_account_id != body.receive_account_id:
            send_account.amount -= body.amount
            receive_account = session.get(Account,body.receive_account_id)
            receive_account.amount += body.amount
            session.commit()
            session.refresh(send_account)
            session.refresh(receive_account)
            return JSONResponse(content={"SUCCESS":"Transaction effectuée"})
        elif send_account.amount < body.amount:
            return JSONResponse(content={"ERROR":"Fonds insuffisant"})
        elif body.send_account_id != body.receive_account_id:
            return JSONResponse(content={"ERROR":"Le compte destinataire doit être différent du compte d'envoi"})
        else:
            return JSONResponse(content={"ERROR":"Montant Négatif"})
    except asyncio.TimeoutError:
        cancelTransaction(transaction.id, session)
        return {"message": f"Envoi annulé pour le compte {body.send_account_id}"}
    finally:
        # Nettoyage de l'event
        pending_send_events.pop(body.send_account_id, None)

@app.put("/close-account") # Story 12
def closeAccount(body: CloseAccount, session = Depends(get_session)):
    account = session.get(Account,body.account_id)
    if account.type == "Principal":
        return JSONResponse(content={"ERROR":"Vous ne pouvez pas fermer un compte principal"})
    transactions = session.exec(select(Transaction).where((Transaction.start_account_id == account.id) 
                                                          | (Transaction.end_account_id == account.id)
                                                          , Transaction.status == "En cours")).all()
    if len(transactions) > 0:
        return JSONResponse(content={"ERROR":"Vous ne pouvez pas fermer un compte avec des transactions associées"})
    account.open = False
    if account.amount != 0:
        user = session.get(User,account.user_id)
        mainAccount = session.exec(select(Account).where(Account.user_id == user.id,Account.type == "Principal",Account.open == True)).first()
        if mainAccount is None:
            return JSONResponse(content={"ERROR":"Vous devez posséder un compte principal ouvert pour fermer ce compte"})
        else:
            mainAccount.amount += account.amount
            session.commit()
            session.refresh(mainAccount)
            CreateTransaction(mainAccount.id,account.id,"Transfer",account.amount,session)
    session.commit()
    session.refresh(account)
    return {"SUCCESS":"Compte fermé"}

@app.put("/cancel") # Story 10
async def cancel(body: CancelTransaction):
    event = pending_send_events.get(body.account_id)
    if event:
        event.set()
        return {"message": f"Annulation reçue pour le compte {body.account_id}"}
    else:
        return {"message": f"Aucune opération d'envoi en attente pour le compte {body.account_id}"}

# Requêtes POST

@app.post("/sign-in") # Story 1
def createUser(session = Depends(get_session)):
    return {"SUCCESS":"Utilisateur créé avec succès"}

@app.post("/open-account") # Story 4 / 11
def openAccount(session = Depends(get_session)):
    return {"SUCCESS":"Compte ouvert"}

@app.post("/beneficiary") # Story 14
def beneficiary():
    return {}