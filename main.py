from fastapi import FastAPI

app = FastAPI()

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