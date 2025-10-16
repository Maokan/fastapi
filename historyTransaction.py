from fastapi import FastAPI, Depends, HTTPException, Query
from datetime import date
from typing import Optional, List
from sqlmodel import SQLModel, Session, select
from main import Account, Transaction, get_session

app = FastAPI()


# Class that represents the history of a transaction
class historyTransaction(SQLModel):
    id: int
    type: str
    transaction_date: date
    amount: float
    start_account_id: int
    end_account_id: int
    status: str
    start_account_number: Optional[str] = None
    end_account_number: Optional[str] = None

# Get the history of a transaction of an account
def get_account_transaction_history(
        account_id: int,
        session: Session = Depends(get_session),
        transaction_type: Optional [str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        status: Optional[str] = None,
        limit: int = Query(default=100, le=1000),
):

    # See if the account exists
    account = session.get (Account, account_id)
    if not account:
        raise HTTPException(status_code=404, detail="Compte inexistant")

    # Base Request
    query = select(Transaction).where(
        (Transaction.start_account_id == account_id)
        | (Transaction.end_account_id == account_id)
    )

    # Optional Request
    if start_date:
        query = query.where(Transaction.transaction_date >= start_date)

    if end_date:
        query = query.where(Transaction.transaction_date <= end_date)

    if transaction_type:
        query = query.where(Transaction.type == transaction_type)

    if status:
        query = query.where(Transaction.status == status)

    # Limit and sort by date
    query = query.order_by(Transaction.transaction_date.desc()).limit(limit)

    # Execute the query
    transactions = session.exec(query).all()

    result = []
    #
    for trans in transactions:
        start_account = session.get(Account, trans.start_account_id)
        end_account = session.get(Account, trans.end_account_id)

        trans_response = historyTransaction(
            id=trans.id,
            type=trans.type,
            transaction_date=trans.transaction_date,
            amount=trans.amount,
            start_account_id=trans.start_account.id,
            end_account_id=trans.end_account.id,
            status=trans.status,
            start_account_number=start_account.account_number if start_account else None,
            end_account_number=end_account.account_number if end_account else None,
        )
        result.append(trans_response)

    return result

## Get the transaction history of a user
@app.get("/user/{user_id}/user_transaction") # Story 8
def get_user_transaction(
        userid : int,
        session: Session = Depends(get_session),
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
):

    account = session.exec(
        select(Account).where(Account.user_id == userid)
    ).all()

    if not account:
        raise HTTPException(status_code=404, detail="Compte inexistant")

    account_ids = [account.id for account in account]

    query = select(Transaction).where(
        (Transaction.start_account_id.in_(account_ids)) |
        (Transaction.end_account_id.in_(account_ids))
    )

    if start_date:
        query = query.where(Transaction.transaction_date >= start_date)

    if end_date:
        query = query.where(Transaction.transaction_date <= end_date)

    query = query.order_by(Transaction.transaction_date.desc())

    transaction_list = session.exec(query).all()

    return transaction_list

# Get the details of a transaction
@app.get("/transaction_details") # Story 13
def get_transaction_details (
        transaction_id: int,
        session: Session = Depends(get_session),
):
    trans = session.get(Transaction, transaction_id)

    if not trans:
        raise HTTPException(status_code=404, detail="Transaction inexistant")

    start_account = session.get(Account, trans.start_account_id)
    end_account = session.get(Account, trans.end_account_id)

    return {
        "transaction": trans,
        "start_account": start_account,
        "end_account": end_account,
    }
