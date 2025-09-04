from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

class Users(SQLModel, table=True):
    user_id: int = Field(primary_key=True)
    username: str = Field()
    password: str = Field()
    is_blue_team: bool = Field(default=True)
    blue_team_num: int = Field(foreign_key=True)

class BlueTeams(SQLModel, table=True):
    team_num: int = Field(primary_key=True)
    last_check_id: int | None = Field(default=None, foreign_key=True)

class CheckInstance(SQLModel, table=True):
    check_id: int = Field(primary_key=True)
    blue_team_num: int = Field(foreign_key=True)
    timestamp: str = Field()
    score: int = Field()

class IOCCheckResult(SQLModel, table=True):
    ioc_id: int = Field(primary_key=True)
    check_instance_id: int = Field(foreign_key=True)
    box_ip: str = Field()
    ioc_name: str = Field()
    difficulty: int = Field()
    status: int = Field()
    error: str = Field()