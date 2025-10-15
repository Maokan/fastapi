from pydantic import BaseModel

class SetDeposit(BaseModel):
    account_id:int
    amount:float

class CloseAccount(BaseModel):
    account_id:int

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
