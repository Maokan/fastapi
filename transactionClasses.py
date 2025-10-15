from pydantic import BaseModel

class GetSendInformation(BaseModel):
    send_account_id:int
    receive_account_id:int
    amount:float

class CancelTransaction(BaseModel):
    transaction_id:int