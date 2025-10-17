from fastapi import FastAPI, Depends
from fastapi.responses import JSONResponse
from datetime import date, datetime, timedelta
from typing import Optional
from sqlmodel import *
from accountClasses import *
from transactionClasses import *
from userClasses import *
from random import *
import asyncio
import bcrypt
from fastapi.security import HTTPBearer

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
    type: str = Field(index=True)
    transaction_date: Optional[datetime] = Field(sa_column=Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP"),
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

secret_key = "SLVM"
Algorithm = "HS256"
security = HTTPBearer(auto_error=False)
global user_id

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    asyncio.create_task(batch())
    
async def batch():
    while True:
        await validateTransactions()
        await asyncio.sleep(10)

async def validateTransactions():
    with Session(engine) as session:
        five_seconds_ago = datetime.now() - timedelta(seconds=5)
        transactions = session.exec(
            select(Transaction).where(
                Transaction.status == "En cours",
                Transaction.type == "Send",
                Transaction.transaction_date < five_seconds_ago
            )
        ).all()
        for transaction in transactions:
            transaction.status = "Validée"
            account = session.get(Account, transaction.end_account_id)
            account.amount += transaction.amount
            session.commit()
            session.refresh(account)
            session.refresh(transaction)
        print(f"[DEBUG] Batch exécuté à {datetime.now()}, {len(transactions)} transactions validées.")
        pass

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

def createBeneficiary(first_name: str, name: str, account_number: str, account_id: int , session):
    beneficiary = Beneficiary(first_name = first_name, name = name, account_number = account_number, account_id = account_id)
    session.add(beneficiary)
    session.commit()
    session.refresh(beneficiary)
    return beneficiary

# ======================
# ROUTES GET
# ======================

@app.get("/")
def read_root():
    return {"message": "Bienvenue sur FastAPI!"}

@app.get("/users")
def users(session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

@app.get("/infos", response_model=GetUserInfos)
def infos(session:Session = Depends(get_session)):
        user = session.get(User, user_id)

        return user

@app.get("/account") # Story 5
def account(body: GetAccount, session = Depends(get_session)) -> Account:
    account = session.get(Account,body.id)
    if account.open:
        return account
    return {"ERROR":"Compte innexistant"}


@app.get("/accounts") # Story 9
def accounts(body: GetAccounts, session = Depends(get_session)) -> list[Account]:
    accounts = session.exec(select(Account).where(Account.user_id == body.user_id,Account.open == True).order_by(col(Account.id).desc())).all()
    return accounts

@app.get("/transactions")
def transactions(body: GetTransactions, session = Depends(get_session)):
    transactions = session.exec(select(Transaction).where((Transaction.start_account_id == body.account_id) | (Transaction.end_account_id == body.account_id)).order_by(col(Transaction.id).desc())).all()
    return transactions

@app.get("/transaction")
def transaction(body: GetTransaction, session = Depends(get_session)):
    transaction = session.get(Transaction,body.transaction_id)
    if transaction:
        return transaction
    return {"ERROR":"Transaction innexistante"}

@app.get("/beneficiaries")
def beneficiaries(body : GetBeneficiaries, session = Depends(get_session)) -> list[Beneficiary]:
    beneficiaries = session.exec(select(Beneficiary).join(Account).where(Account.user_id == body.user_id)).all()
    return beneficiaries

# ======================
# ROUTES PUT
# ======================

@app.put("/deposit")
def deposit(body: SetDeposit, session = Depends(get_session)):
    if body.amount > 0 and body.amount <= 2000:
        account = session.get(Account,body.account_id)
        if account.open == False or account is None:
            return {"ERROR":"Le compte doit être ouvert pour effectuer un dépôt"}
        account.amount += body.amount
        session.commit()
        session.refresh(account)
        CreateTransaction(body.receive_account_id,0,"Deposit",body.amount)
        return {"Nouveau Solde":account.amount}
    elif body.amount > 0:
        return {"ERROR":"Montant supérieur à 2000"}
    else:
        return {"ERROR":"Montant négatif"}

@app.put("/send") # Story 7
async def send(body: GetSendInformation, session = Depends(get_session)):
    send_account = session.get(Account,body.send_account_id)
    if send_account.amount >= body.amount and body.amount > 0 and body.send_account_id != body.receive_account_id and send_account.open == True:
        send_account.amount -= body.amount
        session.commit()
        session.refresh(send_account)
        CreateTransaction(body.receive_account_id,body.send_account_id,"Send",body.amount,session)
        return JSONResponse(content={"SUCCESS":"Transaction effectuée"})
    elif send_account.amount < body.amount:
        return JSONResponse(content={"ERROR":"Fonds insuffisant"})
    elif body.send_account_id != body.receive_account_id:
        return JSONResponse(content={"ERROR":"Le compte destinataire doit être différent du compte d'envoi"})
    elif body.amount <= 0:
        return JSONResponse(content={"ERROR":"Montant Négatif ou nul"})
    else:
        return JSONResponse(content={"ERROR":"Le compte doit être ouvert pour effectuer un virement"})

@app.put("/close-account") # Story 12
def closeAccount(body: CloseAccount, session = Depends(get_session)):
    account = session.get(Account,body.account_id)
    if account is None or account.open == False:
        return JSONResponse(content={"ERROR":"Le compte n'existe pas ou est déjà fermé"})
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
async def cancel(body: CancelTransaction,session = Depends(get_session)):
    transaction = session.get(Transaction,body.transaction_id)
    transaction.status = "Annulée"
    account = session.get(Account,transaction.start_account_id)
    account.amount+=transaction.amount
    session.commit()
    session.refresh(account)
    session.refresh(transaction)
    return {"SUCCESS":"Transaction annulée"}

# ======================
# ROUTES POST
# ======================

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
    return {"SUCCESS": f"Compte ouvert avec l'id : {account.id}, Numéro de compte : {account.account_number}"}

@app.post("/add-beneficiary")
def beneficiary(body: CreateBeneficiary, session=Depends(get_session)):
    if not session.get(Account, body.account_id):
        return JSONResponse(content={"ERROR": "Le compte n'existe pas"})
    if not session.exec(select(Account).where(Account.account_number == body.account_number)).first():
        return JSONResponse(content={"ERROR": "Le numéro de compte est incorrect"})
    if not session.get(Account, body.account_id).open:
        return JSONResponse(content={"ERROR": "Le compte doit être ouvert pour ajouter un bénéficiaire"})
    if session.exec(select(Beneficiary).where(Beneficiary.account_id == body.account_id, Beneficiary.account_number == body.account_number, Beneficiary.name == body.name, Beneficiary.first_name == body.first_name )).first():
        return JSONResponse(content={"ERROR": "Le bénéficiaire existe déjà"})
    if not session.exec(select(User).where(User.name == body.name, User.first_name == body.first_name)).first():
        return JSONResponse(content={"ERROR": "Le nom ou le prénom est incorrect"})
    if session.exec(select(User).where(User.name == body.name, User.first_name == body.first_name)).first().id == session.get(Account, body.account_id).user_id:
        return JSONResponse(content={"ERROR": "Vous ne pouvez pas vous ajouter en bénéficiaire à un compte qui vous appartient"})
    beneficiary = createBeneficiary(body.first_name, body.name, body.account_number, body.account_id, session)
    return {"SUCCESS": f"Bénéficiaire ajouté avec succès avec l'id : {beneficiary.id}"}


@app.post("/login")
def login(body:GetUser, session:Session = Depends(get_session)):
    # Recherche de l'utilisateur
    statement = select(User).where(User.adress_mail == body.adress_mail)
    mail = session.exec(statement).first()
    if not mail:
        return {"ERROR":"Adresse mail incorrecte"}
    # Vérifie le mot de passe
    if not bcrypt.checkpw(body.password.encode('utf-8'), mail.password):
        return {"ERROR":"Mot de passe incorrect"}

    global user_id
    user_id = mail.id
    return {"message": f"Welcome back, {mail.username} !"}

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
        return JSONResponse(content={"ERROR":"Utilisateur déjà existant"})
    else:
        print(chiffrement)
        session.add(user)
        session.commit()
        session.refresh(user)
        createAccount(user.id, "Principal", session)
    return user