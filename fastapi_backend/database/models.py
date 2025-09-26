from datetime import datetime
from typing import List, Optional
from sqlmodel import Field, Relationship, SQLModel


class Users(SQLModel, table=True):
    user_id: int = Field(primary_key=True)
    username: str
    password: str
    is_blue_team: bool = Field(default=True)
    blue_team_num: int = Field(default=0, foreign_key="blue_teams.team_num")
    is_admin: bool = Field(default=False)


class BlueTeams(SQLModel, table=True):
    __tablename__ = "blue_teams"

    team_num: int = Field(primary_key=True)
    last_check_id: Optional[int] = Field(default=None, foreign_key="check_instance.check_id")
    total_score: int = Field(default=0)


class CheckInstance(SQLModel, table=True):
    __tablename__ = "check_instance"

    check_id: int = Field(primary_key=True)
    blue_team_num: int = Field(foreign_key="blue_teams.team_num")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    score: int = Field(default=0)

    results: List["IOCCheckResult"] = Relationship(back_populates="check")

class IOCCheckResult(SQLModel, table=True):
    __tablename__ = "ioc_check_result"

    ioc_id: int = Field(primary_key=True)
    check_instance_id: int = Field(foreign_key="check_instance.check_id")
    box_ip: str
    ioc_name: str
    difficulty: int # 1=Easy, 2=Medium, 3=Hard
    status: int
    error: Optional[str] = Field(default=None)

    check: CheckInstance = Relationship(back_populates="results")


class BlueTeamsScoreboard(SQLModel, table=True):
    __tablename__ = "blue_teams_scoreboard"
    __table_args__ = {"extend_existing": True}

    # Columns exposed by your view
    team_num: int = Field(primary_key=True)  # pick a PK (team_num works fine here)
    last_check_id: Optional[int] = None
    total_score: int
    last_check_score: int
    last_check_time: Optional[datetime] = None

class TeamLatestIocDetails(SQLModel, table=True):
    __tablename__ = "team_latest_ioc_details"
    __table_args__ = {"extend_existing": True}

    team_num: int = Field(primary_key=True)
    box_ip: str = Field(primary_key=True)
    ioc_name: str = Field(primary_key=True)

    difficulty: int
    status: int
    error: Optional[str]
    points: int