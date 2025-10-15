from fastapi import FastAPI, Depends, Response
from fastapi.responses import JSONResponse
from datetime import date
from typing import Optional, Any
from sqlmodel import *
from accountClasses import *
from transactionClasses import *
from pydantic import BaseModel
from random import *

print("[DEBUG] Début du chargement de main.py")
app = FastAPI()

# ======================
# MODELES DE DONNÉES
# ======================

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
    
# ======================
# SCHEMAS Pydantic
# ======================

class GetAccount(BaseModel):
    id: int

class GetAccounts(BaseModel):
    user_id: int

class GetSendInformation(BaseModel):
    send_account_id: int
    receive_account_id: int
    amount: float

class CreateAccount(BaseModel):
    user_id: int
    type: str

# ======================
# ROUTES GET
# ======================

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur FastAPI!"}

@app.get("/login")
def login():
    return {}

@app.get("/user")
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

@app.get("/transactions")
def transactions():
    return {}

@app.get("/transaction")
def transaction():
    return {}

@app.get("/beneficiaries")
def beneficiaries():
    return {}

# ======================
# ROUTES PUT
# ======================

def CreateTransaction(outAccountId, entryAccountId, transactionType, amount, session):
    transaction = Transaction(
        transactionType=transactionType,
        start_account_id=entryAccountId,
        end_account_id=outAccountId,
        amount=amount
    )
    session.add(transaction)
    session.commit()
    session.refresh(transaction)
    return transaction

@app.put("/send")
def send(body: GetSendInformation, session=Depends(get_session)):
    send_account = session.get(Account, body.send_account_id)
    receive_account = session.get(Account, body.receive_account_id)

    if body.amount <= 0:
        return JSONResponse(content={"ERROR": "Montant négatif ou nul"})
    if body.send_account_id == body.receive_account_id:
        return JSONResponse(content={"ERROR": "Le compte destinataire doit être différent"})
    if send_account.amount < body.amount:
        return JSONResponse(content={"ERROR": "Fonds insuffisants"})

    send_account.amount -= body.amount
    receive_account.amount += body.amount
    session.commit()

    CreateTransaction(body.receive_account_id, body.send_account_id, "Send", body.amount, session)
    return JSONResponse(content={"SUCCESS": "Transaction effectuée"})

@app.put("/deposit")
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
        CreateTransaction(body.receive_account_id,body.send_account_id,"Send",body.amount,session)
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

@app.put("/close-account")
def closeAccount():
    return {}

# ======================
# ROUTES POST
# ======================

def createAccount(user_id: int, type: str, session):
    accountNumber = randint(10000000, 99999999)
    if ( type == "Principal" ):
        startamount = 100
    else:
        startamount = 0
    account = Account(type=type, amount=startamount, user_id=user_id, account_number=str(accountNumber))
    session.add(account)
    session.commit()
    session.refresh(account)
    return account

@app.post("/sign-in") # Story 1
def createUser(session = Depends(get_session)):
    return {"SUCCESS":"Utilisateur créé avec succès"}

@app.post("/open-account")
def openAccount(body: CreateAccount, session=Depends(get_session)):
    if not session.get(User, body.user_id):
        return JSONResponse(content={"ERROR": "L'utilisateur n'existe pas"})
    if body.type not in ["Principal", "Secondaire"]:
        return JSONResponse(content={"ERROR": "Type de compte invalide"})
    if body.type == "Principal":
        existing_account = session.exec(select(Account).where(Account.user_id == body.user_id, Account.type == "Principal")).first()
        if existing_account:
            return JSONResponse(content={"ERROR": "L'utilisateur possède déjà un compte Principal"})
    accounts_count = session.exec(
        select(Account).where(Account.user_id == body.user_id)
    ).all()
    if len(accounts_count) >= 5:
        return JSONResponse(content={"ERROR": "Un utilisateur ne peut pas avoir plus de 5 comptes"})
    account = createAccount(body.user_id, body.type, session)
    return {"SUCCESS": f"Compte ouvert avec l'id : {account.id}"}

@app.post("/beneficiary")
def beneficiary():
    return {}
