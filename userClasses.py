from pydantic import BaseModel

class CreateUser(BaseModel):
    username:str
    adress_mail:str
    password:str
    name:str
    first_name:str

class GetUser(BaseModel):
    adress_mail:str
    password:str

class GetUserInfos(BaseModel):
    username:str
    adress_mail:str
    name:str
    first_name:str