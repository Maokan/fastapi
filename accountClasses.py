from pydantic import BaseModel

class GetAccounts(BaseModel):
    user_id:int

class GetAccount(BaseModel):
    id:int