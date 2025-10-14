from pydantic import BaseModel

class CreateAccount(BaseModel):
    user_id:int

class GetAccounts(BaseModel):
    user_id:int

class GetAccount(BaseModel):
    id:int