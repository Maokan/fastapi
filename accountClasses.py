from pydantic import BaseModel

class CreateAccount(BaseModel):
    user_id:int

class SetDeposit(BaseModel):
    account_id:int
    amount:float

class GetAccounts(BaseModel):
    user_id:int

class GetAccount(BaseModel):
    id:int