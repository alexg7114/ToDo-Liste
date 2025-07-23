
from fastapi import FastAPI
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi import HTTPException
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordRequestForm
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging

from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowPassword
from fastapi.openapi.models import SecuritySchemeType
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2

from database import create_db_and_tables

from sqlmodel import Session, select

from models import ToDo, ToDoCreate, ToDoRead
from database import engine
from database import get_session
from models import User, UserCreate, UserRead

security = HTTPBearer()


logging.basicConfig(level=logging.DEBUG)

oauth2_scheme = HTTPBearer()

app = FastAPI()

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
def register(user: UserCreate, session: Session = Depends(get_session)):
  existing_user = session.exec(select(User).where(User.username == user.username)).first()
  if existing_user:
    raise HTTPException(status_code=400, detail="Username already exists")
    
  hashed_pw = get_password_hash(user.password)
  db_user = User(username=user.username, hashed_password=hashed_pw)
  session.add(db_user)
  session.commit()
  session.refresh(db_user)
      
  return db_user


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
def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    
  user = session.exec(select(User).where(User.username == form_data.username)).first()
  if user is None:
    raise HTTPException(status_code=401, detail="Incorrect username or passwort")
  
  if not pwd_context.verify(form_data.password, user.hashed_password):
    raise HTTPException(status_code=401, detail="Incorrect username or password")
  
    
  token = create_access_token(data={"sub": user.username})
  print("Token created:", token)
  return {"access_token": token, "token_type": "bearer"}





def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), session: Session = Depends(get_session)):
  token = credentials.credentials
  
  try:
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    username = payload.get("sub")
    if username is None:
      raise HTTPException(status_code=401, detail="Invalid token")
  except JWTError:
    raise HTTPException(status_code=401, detail="Token decoding failed")
  
  user = session.exec(select(User).where(User.username == username)).first()
  if user is None:
    raise HTTPException(status_code=401, detail="User not found")
  return user
  
  
 


@app.on_event("startup")
def on_startup():
  create_db_and_tables()



  
@app.get("/todos")
def read_todos(user=Depends(get_current_user)):
  with Session(engine) as session:
    statement = select(ToDo).where(ToDo.user == user.username)
    results = session.exec(statement).all()
    return results

      
  
@app.post("/todos", response_model=ToDo)
def create_todo(
  todo: ToDoCreate,
  session: Session = Depends(get_session),
  current_user: dict = Depends(get_current_user),
):
  print("current_user:", current_user)
  print("todo input:", todo)
  try:
    
    new_todo = ToDo(
      title=todo.title,
      description=todo.description,
      done=todo.done or False,
      user=current_user.username,
    )
    session.add(new_todo)
    session.commit()
    session.refresh(new_todo)
    return new_todo
  except Exception as e:
    print("Fehler with create todo:", e)
    raise HTTPException(status_code=500, detail=str(e))
  


@app.get("/me")
def read_users_me(current_user: dict = Depends(get_current_user)):
  return {"username": current_user.username}

@app.get("/ping")
def ping():
    return {"message": "pong"}


