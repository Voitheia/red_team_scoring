import queue
import threading
import ansible_runner
import time
from dataclasses import dataclass
from typing import Dict, List, Optional
from pathlib import Path
import yaml
import json

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
    attempt: int = 1

class IOCCheckExecutor:
    def __init__(self, db_session, num_workers: int = 32):
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