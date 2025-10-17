from pydantic import BaseModel

class GetSendInformation(BaseModel):
    send_account_id:int
    receive_account_id:int
    amount:float

class CancelTransaction(BaseModel):
    transaction_id:int

class GetTransactions(BaseModel):
    account_id:int

class GetTransaction(BaseModel):
    transaction_id:int