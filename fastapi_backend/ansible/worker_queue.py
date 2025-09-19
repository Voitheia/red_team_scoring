import queue
import threading
import ansible_runner
import time
import logging
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path
import yaml
import json
from sqlmodel import Session

from fastapi_backend.ansible.worker import worker
from fastapi_backend.database.db_writer import engine

@dataclass
class IOCTask:
    """Single IOC check task"""
    team_num: int
    box_ip: str
    box_os: str
    ioc_name: str
    ioc_script: str
    check_id: int
    playbook_path: str
    difficulty: int = 2  # Default to medium difficulty
    attempt: int = 1

class IOCCheckExecutor:
    def __init__(self, db_session, num_workers: int = 32):
        self.logger = logging.getLogger(__name__)
        self.db = db_session
        self.num_workers = num_workers
        
        # Queues
        self.task_queue = queue.Queue()
        self.retry_queue = []  # Store failed tasks for retry after initial run
        
        # Threading
        self.workers = []
        self.shutdown = threading.Event()
        
        # Statistics
        self.stats = {
            'total': 0,
            'completed': 0,
            'failed': 0,
            'timeouts': 0,
            'in_progress': 0,
            'queue_size': 0,
            'retries': 0
        }
        self.stats_lock = threading.Lock()
        
        # Pre-generated components
        self.inventory_path = None
        self.playbook_cache = {}  # Cache of pre-generated playbooks
        
        # IOC definitions
        self.ioc_definitions = {}  # All loaded IOC definitions
        self.os_ioc_mapping = {    # IOCs grouped by OS
            'windows': [],
            'linux': [],
            'firewall': []
        }
        self.difficulty_points = {  # Points per difficulty level
            1: 10,  # Easy
            2: 15,  # Medium
            3: 20   # Hard
        }

    def start_workers(self):
        """Start worker threads"""
        self.logger.info(f"Starting {self.num_workers} worker threads...")

        for i in range(self.num_workers):
            # Pass engine instead of session - each worker will create its own session
            # This avoids SQLite threading issues
            t = threading.Thread(
                target=worker,
                args=(
                    self.task_queue,
                    self.retry_queue,
                    self.shutdown,
                    self.stats,
                    self.stats_lock,
                    self.inventory_path,
                    self.ioc_definitions,
                    engine  # Pass engine, not session
                ),
                daemon=True,
                name=f"IOCWorker-{i+1}"
            )
            t.start()
            self.workers.append(t)

        self.logger.info(f"Started {len(self.workers)} worker threads")

    def stop_workers(self, timeout: int = 30):
        """Stop all worker threads gracefully"""
        self.logger.info("Stopping worker threads...")

        # Signal all workers to stop
        self.shutdown.set()

        # Wait for all workers to finish
        for worker_thread in self.workers:
            worker_thread.join(timeout=timeout)
            if worker_thread.is_alive():
                self.logger.warning(f"Worker {worker_thread.name} did not stop within timeout")

        # Clear the worker list
        self.workers.clear()
        self.logger.info("All worker threads stopped")

    def get_stats(self) -> Dict:
        """Get current statistics"""
        with self.stats_lock:
            return self.stats.copy()