from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime, timezone

class ToDo(SQLModel, table=True):
  id: Optional[int] = Field(default=None, primary_key=True)
  title: str
  done: bool = False
  created_at: datetime = Field(default_factory=datetime.now(tz=timezone.utc))
  user: str
  