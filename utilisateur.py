    from fastapi import FastAPI
    app = FastAPI()
    @app.get("/")
    def read_root():
        return {"message": "Bienvenue sur FastAPI!"}
def register():
    names=[]
    usernames=[]
    passwords=[]
    names.append(input("Enter your name:"))
    usernames.append(input("choose your username:"))
    passwords.append(input("choose your password:"))
    return usernames
def login(usernames,passwords):
    usernames=[]
    passwords=[]
    password=""
    username=""
    username=input("Enter your username:")
    password=input("Enter your Password:")
    if password==passwords:#[usernames.index(username)]:
       print("welcome")
    else:
       print("incorrect!")

account_ans=""
while True:
    account_ans=input("choose:  a)Sign Up     b)login and shop     c)quit")
    if account_ans=="a":
       register()
    if account_ans=="b":
       password=""
       username=""
       usernames=[]
       passwords=[]
       login(usernames,passwords)
    if account_ans=="c":break