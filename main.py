
from fastapi import FastAPI
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi import HTTPException
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
import logging

from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowPassword
from fastapi.openapi.models import SecuritySchemeType
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2

from database import create_db_and_tables

from sqlmodel import Session, select
from models import ToDo
from database import engine

app = FastAPI()

logging.basicConfig(level=logging.DEBUG)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

  

users_db = []

class UserIn(BaseModel):
  username: str
  password: str
  
class UserOut(BaseModel):
  username: str
  
  
def get_password_hash(password):
  return pwd_context.hash(password)




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


SECRET_KEY = "secret-key-should-be-long-and-random"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: timedelta = None):
  print("Generating token for:", data)
  to_encode = data.copy()
  expire = datetime.now(tz=timezone.utc) + (expires_delta or timedelta(minutes=15))
  print("Expire at:", expire)
  to_encode.update({"exp": expire})
  token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
  print("Generated token:", token)
  return token


@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
  print("Recieved login form data:")
  print("Username:", form_data.username)
  print("Password:", form_data.password)
  
  user = None
  for u in users_db:
    print("Checking user:", u["username"])
    if u["username"] == form_data.username:
      user = u
      break
    
  
  if user is None:
    print("User not found!")
    raise HTTPException(status_code=401, detail="Incorrect username or password")
  
  print("User found:", user)
  print("Comparing password...")
  
  if not pwd_context.verify(form_data.password, user["hashed_password"]):
    print("Password incorrect!")
    raise HTTPException(status_code=401, detail="Incorrect username or password")
  
  print("Password correct. Creating token...")
  
  token = create_access_token(data={"sub": user["username"]})
  print("Token created:", token)
  return {"access_token": token, "token_type": "bearer"}


def get_current_user(token: str = Depends(oauth2_scheme)):
  credentials_exception = HTTPException(status_code=401, detail="Invalid credentials")
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload.get("sub")
    if username is None:
      raise credentials_exception
  except JWTError:
    raise credentials_exception
  
  user = None
  for u in users_db:
    if u["username"] == username:
      user = u
      break
    
  if user is None:
    raise credentials_exception
  return user

print("Current users_db:", users_db)


@app.on_event("startup")
def on_startup():
  create_db_and_tables()





@app.post("/todos")
def create_todo(todo: ToDo, user=Depends(get_current_user)):
  todo.user = user["username"]
  with Session(engine) as session:
    session.add(todo)
    session.commit()
    session.refresh(todo)
    return todo
  
@app.get("/todos")
def read_todos(user=Depends(get_current_user)):
  with Session(engine) as session:
    statement = select(ToDo).where(ToDo.user == user["username"])
    results = session.exec(statement).all()
    return results

  
  @app.get("/me")
  def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"]}
  
  
