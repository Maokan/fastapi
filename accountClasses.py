from pydantic import BaseModel

class SetDeposit(BaseModel):
    account_id:int
    amount:float

class GetAccounts(BaseModel):
    user_id:int

class GetAccount(BaseModel):
    id:int

class CloseAccount(BaseModel):
    account_id:int