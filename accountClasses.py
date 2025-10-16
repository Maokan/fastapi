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

class GetBeneficiaries(BaseModel):
    user_id: int

class CreateAccount(BaseModel):
    user_id: int
    type: str

class CreateBeneficiary(BaseModel):
    first_name: str
    name: str 
    account_number: str
    account_id: int 