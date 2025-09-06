from typing import Annotated, Optional

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select


class Users(SQLModel, table=True):
    user_id: int = Field(primary_key=True)
    username: str
    password: str
    is_blue_team: bool = Field(default=True)
    blue_team_num: int = Field(foreign_key="blueteams.team_num")


class BlueTeams(SQLModel, table=True):
    team_num: int = Field(primary_key=True)
    last_check_id: Optional[int] = Field(default=None, foreign_key="checkinstance.check_id")


class CheckInstance(SQLModel, table=True):
    check_id: int = Field(primary_key=True)
    blue_team_num: int = Field(foreign_key="blueteams.team_num")
    timestamp: str
    score: int


class IOCCheckResult(SQLModel, table=True):
    ioc_id: int = Field(primary_key=True)
    check_instance_id: int = Field(foreign_key="checkinstance.check_id")
    box_ip: str
    ioc_name: str
    difficulty: int
    status: int
    error: str