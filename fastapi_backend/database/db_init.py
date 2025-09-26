from sqlmodel import create_engine, SQLModel, Session
from sqlalchemy import text
import logging

from fastapi_backend.database.models import *
from fastapi_backend.utils.auth import *

class DatabaseInitializer:
    """Initialize database schema and views"""
    
    def __init__(self, database_url: str = "sqlite:///db/database.db"):
        self.engine = create_engine(database_url)
        self.logger = logging.getLogger(__name__)
    
    def initialize_database(self):
        """Create all tables and views"""
        
        # Create tables from SQLModel definitions
        self.logger.info("Creating database tables...")
        SQLModel.metadata.create_all(self.engine)
        
        # Create views using raw SQL
        self.logger.info("Creating database views...")
        self.create_scoring_views()
        
        # Initialize blue teams
        self.logger.info("Initializing blue teams...")
        self.initialize_teams()

        self.logger.info("Initializing webpage accounts...")
        self.initialize_accounts()
        
        self.logger.info("Database initialization complete")
    
    def create_scoring_views(self):
        """Create all scoring views"""
        
        views = [
            ("ioc_check_result_with_points", """
                CREATE VIEW IF NOT EXISTS ioc_check_result_with_points AS
                SELECT
                  icr.*,
                  CASE
                      WHEN icr.status = 0 THEN
                          CASE icr.difficulty
                              WHEN 1 THEN 10
                              WHEN 2 THEN 15
                              WHEN 3 THEN 20
                              ELSE 0
                          END
                      ELSE 0
                  END AS points
                FROM ioc_check_result icr
            """),
            
            ("check_instance_with_score", """
                CREATE VIEW IF NOT EXISTS check_instance_with_score AS
                SELECT
                  ci.check_id,
                  ci.blue_team_num,
                  ci.timestamp,
                  COALESCE(SUM(icrp.points), 0) AS score
                FROM check_instance ci
                LEFT JOIN ioc_check_result_with_points icrp ON ci.check_id = icrp.check_instance_id
                GROUP BY ci.check_id, ci.blue_team_num, ci.timestamp
            """),
            
            ("blue_teams_scoreboard", """
                CREATE VIEW IF NOT EXISTS blue_teams_scoreboard AS
                SELECT
                  bt.team_num,
                  bt.last_check_id,
                  COALESCE(
                      (SELECT SUM(score)
                       FROM check_instance_with_score
                       WHERE blue_team_num = bt.team_num),
                  0) AS total_score,
                  COALESCE(last_check.score, 0) AS last_check_score,
                  last_check.timestamp AS last_check_time
                FROM blue_teams bt
                LEFT JOIN check_instance_with_score last_check
                  ON bt.last_check_id = last_check.check_id
            """),
            
            ("team_latest_ioc_details", """
                CREATE VIEW IF NOT EXISTS team_latest_ioc_details AS
                SELECT
                  bt.team_num,
                  icrp.box_ip,
                  icrp.ioc_name,
                  icrp.difficulty,
                  icrp.status,
                  icrp.error,
                  icrp.points
                FROM blue_teams bt
                INNER JOIN ioc_check_result_with_points icrp ON icrp.check_instance_id = bt.last_check_id
                ORDER BY bt.team_num, icrp.box_ip, icrp.ioc_name
            """),
            
            ("score_history", """
                CREATE VIEW IF NOT EXISTS score_history AS
                SELECT
                  ci.blue_team_num AS team_num,
                  ci.timestamp,
                  ci.score AS check_score,
                  (SELECT SUM(score)
                   FROM check_instance_with_score ci2
                   WHERE ci2.blue_team_num = ci.blue_team_num
                     AND ci2.timestamp <= ci.timestamp) AS cumulative_score
                FROM check_instance_with_score ci
                ORDER BY ci.blue_team_num, ci.timestamp
            """)
        ]
        
        with Session(self.engine) as session:
            for view_name, view_sql in views:
                try:
                    # Drop view if it exists (for updates)
                    session.exec(text(f"DROP VIEW IF EXISTS {view_name}"))
                    # Create the view
                    session.exec(text(view_sql))
                    session.commit()
                    self.logger.info(f"Created view: {view_name}")
                except Exception as e:
                    self.logger.error(f"Failed to create view {view_name}: {e}")
                    session.rollback()
                    raise
    
    def initialize_teams(self):
        """Initialize blue team records"""
        
        with Session(self.engine) as session:
            for team_num in range(0, 17):  # Teams 0-16
                existing = session.get(BlueTeams, team_num)
                if not existing:
                    team = BlueTeams(
                        team_num=team_num,
                        last_check_id=None,
                        total_score=0
                    )
                    session.add(team)
            session.commit()

    def initialize_accounts(self):
        """Initialize website accounts"""

        with Session(self.engine) as session:
            # TODO: Are these passwords too insecure? Do we care?
            # add blue team accounts, no 0th account 
            for team_num in range(1,17):
                existing = session.query(Users).filter_by(blue_team_num=team_num).first()
                if not existing:
                    add_user(Users(
                    username=f"blueteam{team_num}",
                    password=f"CDE25Blueteam{team_num}",
                    is_admin=False,
                    is_blue_team=True,
                    blue_team_num=team_num
                ))
            # add red team accounts
            existing = session.query(Users).filter_by(username="redteamlead").first()
            if not existing:
                add_user(Users(
                    username="redteamlead",
                    password="Sqordfish0!",
                    is_admin=True,
                    is_blue_team=False,
                ))
            existing = session.query(Users).filter_by(username="redteamer").first()
            if not existing:
                add_user(Users(
                    username="redteamer",
                    password="Sqordfish0!",
                    is_admin=False,
                    is_blue_team=False,
                ))
            # add black team account
            existing = session.query(Users).filter_by(username="blackteam").first()
            if not existing:
                add_user(Users(
                    username="blackteam",
                    password="BlackTeamIsTheB3st!CDE25",
                    is_admin=False,
                    is_blue_team=False,
                ))
            
            # add white team account
            existing = session.query(Users).filter_by(username="whiteteam").first()
            if not existing:
                add_user(Users(
                    username="whiteteam",
                    password="WhiteTeamIsNumb3r0n3!CDE25",
                    is_admin=False,
                    is_blue_team=False,
                ))