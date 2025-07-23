from sqlmodel import SQLModel,Field
from typing import Optional
from datetime import datetime, timezone
from pydantic import BaseModel


class User(SQLModel, table=True):
  id: Optional[int] = Field(default=None, primary_key=True)
  username: str = Field(index=True, unique=True)
  hashed_password: str
  created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))

class UserCreate(BaseModel):
  username: str
  password: str
  
class UserRead(BaseModel):
  id: int
  username: str
  



class ToDo(SQLModel, table=True):
  id: Optional[int] = Field(default=None, primary_key=True)
  title: str
  description: Optional[str] = None
  done: bool = False
  created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
  user: str
  
  
class ToDoCreate(BaseModel):
  title: str
  description: Optional[str] = None
  done: Optional[bool] = False
  
  
class ToDoRead(BaseModel):
  id: int
  title: str
  description: Optional[str]
  done: bool
  created_at: datetime
  user: str
  
  