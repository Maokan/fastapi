from pydantic import BaseModel

class GetSendInformation():
    send_account_id:int
    receive_account_id:int
    amount:float