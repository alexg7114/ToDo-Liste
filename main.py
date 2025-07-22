
from fastapi import FastAPI
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi import HTTPException


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

users_db = []

class UserIn(BaseModel):
  username: str
  password: str
  
class UserOut(BaseModel):
  username: str
  
  
def get_password_hash(password):
  return pwd_context.hash(password)


app = FastAPI()

@app.get("/")
def read_root():
  return {"message": "Hello World!"}


@app.post("/register", response_model=UserOut)
def register(user: UserIn):
  if any(u["username"] == user.username for u in users_db):
    raise HTTPException(status_code=400, detail="Username already exists")
  
  hashed_pw = get_password_hash(user.password)
  new_user = {"username": user.username, "hashed_password": hashed_pw}
  users_db.append(new_user)
  
  return {"username": user.username}


