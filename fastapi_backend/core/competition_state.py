from enum import Enum
from typing import Optional, Dict, Any
from datetime import datetime
import threading
import logging

class CompetitionStatus(Enum):
    """Competition status states"""
    NOT_STARTED = "not_started"
    INITIALIZING = "initializing"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"
    ERROR = "error"

class CompetitionState:
    """
    Manages global competition state and metadata.
    Thread-safe singleton for accessing competition information.
    """

    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.logger = logging.getLogger(__name__)
        self.status = CompetitionStatus.NOT_STARTED
        self.start_time: Optional[datetime] = None
        self.end_time: Optional[datetime] = None
        self.last_check_time: Optional[datetime] = None
        self.next_check_time: Optional[datetime] = None

        # Competition configuration
        self.check_interval_minutes = 5
        self.num_teams = 0
        self.num_boxes = 0
        self.num_iocs = 0

        # Runtime statistics
        self.total_checks_run = 0
        self.total_iocs_deployed = 0
        self.current_check_id: Optional[int] = None

        # Component references (set during initialization)
        self.orchestrator = None
        self.executor = None
        self.scheduler = None

        self._initialized = True

    def set_status(self, status: CompetitionStatus) -> None:
        """Update competition status with logging"""
        old_status = self.status
        self.status = status
        self.logger.info(f"Competition status changed: {old_status.value} -> {status.value}")

        if status == CompetitionStatus.RUNNING and self.start_time is None:
            self.start_time = datetime.utcnow()
        elif status == CompetitionStatus.STOPPED:
            self.end_time = datetime.utcnow()

    def is_active(self) -> bool:
        """Check if competition is currently active"""
        return self.status == CompetitionStatus.RUNNING

    def can_run_checks(self) -> bool:
        """Check if system can run checks"""
        return self.status in [CompetitionStatus.RUNNING, CompetitionStatus.INITIALIZING]

    def update_check_times(self, last: datetime, next: datetime) -> None:
        """Update check timing information"""
        self.last_check_time = last
        self.next_check_time = next

    def increment_checks(self) -> None:
        """Increment total checks counter"""
        with self._lock:
            self.total_checks_run += 1

    def get_status_info(self) -> Dict[str, Any]:
        """Get current status information for API"""
        return {
            "status": self.status.value,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "last_check_time": self.last_check_time.isoformat() if self.last_check_time else None,
            "next_check_time": self.next_check_time.isoformat() if self.next_check_time else None,
            "total_checks_run": self.total_checks_run,
            "total_iocs_deployed": self.total_iocs_deployed,
            "check_interval_minutes": self.check_interval_minutes,
            "configuration": {
                "num_teams": self.num_teams,
                "num_boxes": self.num_boxes,
                "num_iocs": self.num_iocs
            }
        }

    def reset(self) -> None:
        """Reset state for new competition"""
        self.status = CompetitionStatus.NOT_STARTED
        self.start_time = None
        self.end_time = None
        self.last_check_time = None
        self.next_check_time = None
        self.total_checks_run = 0
        self.total_iocs_deployed = 0
        self.current_check_id = None
        self.logger.info("Competition state reset")