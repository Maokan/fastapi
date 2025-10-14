from fastapi import FastAPI
from datetime import date
from typing import Optional
from sqlmodel import Column, Field, SQLModel, TIMESTAMP, text

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
def account():
    return {}

@app.get("/accounts") # Story 9
def accounts():
    return {}

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

@app.put("/send") # Story 7
def send():
    return {}

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

@app.post("/open-account") # Story 4 / 11
def openAccount():
    return {}

@app.post("/beneficiary") # Story 14
def beneficiary():
    return {}