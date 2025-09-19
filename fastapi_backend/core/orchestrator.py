import asyncio
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path

from sqlmodel import Session, select

from fastapi_backend.core.competition_state import CompetitionState, CompetitionStatus
from fastapi_backend.core.scheduler import CheckScheduler
from fastapi_backend.core.inventory_manager import InventoryManager
from fastapi_backend.ansible.ioc_definition import IOCDefinitionLoader
from fastapi_backend.ansible.worker_queue import IOCCheckExecutor, IOCTask
from fastapi_backend.database.db_init import DatabaseInitializer
from fastapi_backend.database.db_writer import engine, create_db_and_tables
from fastapi_backend.database.models import CheckInstance, BlueTeams, IOCCheckResult

class CompetitionOrchestrator:
    """
    Main orchestrator for the competition.
    Manages all components and coordinates operations.
    """

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.state = CompetitionState()

        # Core components
        self.db_init = DatabaseInitializer()
        self.inventory_manager = InventoryManager()
        self.ioc_loader = IOCDefinitionLoader()
        self.executor: Optional[IOCCheckExecutor] = None
        self.scheduler = CheckScheduler()

        # Configuration
        self.ansible_dir = Path("./ansible")
        self.ansible_dir.mkdir(exist_ok=True)

        # Set orchestrator reference in state
        self.state.orchestrator = self

    async def initialize(self) -> None:
        """Initialize all competition components"""
        try:
            self.state.set_status(CompetitionStatus.INITIALIZING)
            self.logger.info("Initializing competition orchestrator...")

            # 1. Initialize database
            self.logger.info("Step 1: Initializing database...")
            await self._initialize_database()

            # 2. Load inventory
            self.logger.info("Step 2: Loading inventory...")
            await self._load_inventory()

            # 3. Load IOC definitions
            self.logger.info("Step 3: Loading IOC definitions...")
            await self._load_iocs()

            # 4. Initialize executor with worker threads
            self.logger.info("Step 4: Initializing check executor...")
            await self._initialize_executor()

            # 5. Set up scheduler
            self.logger.info("Step 5: Setting up scheduler...")
            self.scheduler.set_callback(self.run_checks)

            # Update state
            self.state.num_teams = len(self.inventory_manager.teams)
            self.state.num_boxes = len(self.inventory_manager.all_boxes)
            self.state.num_iocs = len(self.ioc_loader.ioc_definitions)
            self.state.set_status(CompetitionStatus.NOT_STARTED)

            self.logger.info("Orchestrator initialization complete")

        except Exception as e:
            self.logger.error(f"Failed to initialize orchestrator: {e}")
            self.state.set_status(CompetitionStatus.ERROR)
            raise

    async def _initialize_database(self) -> None:
        """Initialize database and create tables/views"""
        try:
            # Create tables
            create_db_and_tables()

            # Initialize views and teams
            self.db_init.initialize_database()

        except Exception as e:
            self.logger.error(f"Database initialization failed: {e}")
            raise

    async def _load_inventory(self) -> None:
        """Load team and box inventory"""
        try:
            # Load from config or use defaults
            self.inventory_manager.load_from_config()

            # Generate Ansible inventory
            inventory_path = self.inventory_manager.generate_ansible_inventory()
            self.logger.info(f"Generated inventory at {inventory_path}")

            # Save config for reference
            self.inventory_manager.save_config()

        except Exception as e:
            self.logger.error(f"Inventory loading failed: {e}")
            raise

    async def _load_iocs(self) -> None:
        """Load IOC definitions from YAML files"""
        try:
            self.ioc_loader.load_ioc_definitions()

            # Validate scripts exist
            self.ioc_loader.validate_ioc_scripts()

        except FileNotFoundError:
            # For MVP, we'll just warn about missing scripts
            self.logger.warning("Some IOC scripts are missing, continuing anyway for MVP")
        except Exception as e:
            self.logger.error(f"IOC loading failed: {e}")
            raise

    async def _initialize_executor(self) -> None:
        """Initialize the check executor with worker threads"""
        try:
            with Session(engine) as session:
                self.executor = IOCCheckExecutor(session, num_workers=16)

            # Pass components to executor
            self.executor.ioc_definitions = self.ioc_loader.ioc_definitions
            self.executor.os_ioc_mapping = self.ioc_loader.os_ioc_mapping
            self.executor.inventory_path = str(self.inventory_manager.inventory_path)

            # Generate playbooks for all IOCs
            await self._generate_playbooks()

            # Start worker threads (they'll wait for tasks)
            # Note: Workers will be started when competition starts

        except Exception as e:
            self.logger.error(f"Executor initialization failed: {e}")
            raise

    async def _generate_playbooks(self) -> None:
        """Pre-generate Ansible playbooks for all box/IOC combinations"""
        playbook_dir = self.ansible_dir / "playbooks"
        playbook_dir.mkdir(exist_ok=True)

        count = 0
        for team in self.inventory_manager.teams.values():
            for box in team.boxes:
                iocs = self.ioc_loader.get_iocs_for_os(box.os)

                for ioc in iocs:
                    # Create unique playbook key
                    playbook_key = f"{box.ip}_{ioc.name}"

                    # Generate playbook content
                    playbook = [{
                        'name': f'Check {ioc.name} on {box.ip}',
                        'hosts': box.ip,
                        'gather_facts': False,
                        'tasks': [{
                            'name': f'Execute {ioc.name} check',
                            'script': f'../../iocs/{ioc.check_script}',
                            'register': 'check_result',
                            'failed_when': False,
                            'changed_when': False
                        }, {
                            'name': 'Display result',
                            'debug': {
                                'var': 'check_result.stdout'
                            }
                        }]
                    }]

                    # Save playbook
                    import yaml
                    playbook_path = playbook_dir / f'{playbook_key}.yml'
                    with open(playbook_path, 'w') as f:
                        yaml.dump(playbook, f)

                    # Cache the path
                    if self.executor:
                        self.executor.playbook_cache[playbook_key] = str(playbook_path)

                    count += 1

        self.logger.info(f"Generated {count} playbooks")

    async def start_competition(self) -> None:
        """Start the competition"""
        if self.state.status != CompetitionStatus.NOT_STARTED:
            raise RuntimeError(f"Cannot start competition from status: {self.state.status}")

        self.logger.info("Starting competition...")
        self.state.set_status(CompetitionStatus.RUNNING)

        # Start worker threads in executor
        if self.executor:
            self.executor.start_workers()

        # Start scheduler for periodic checks
        await self.scheduler.start()

        # Run initial check
        await self.run_checks()

        self.logger.info("Competition started successfully")

    async def stop_competition(self) -> None:
        """Stop the competition"""
        self.logger.info("Stopping competition...")

        # Stop scheduler
        await self.scheduler.stop()

        # Stop workers
        if self.executor:
            self.executor.stop_workers()

        self.state.set_status(CompetitionStatus.STOPPED)
        self.logger.info("Competition stopped")

    async def run_checks(self) -> None:
        """Run checks for all teams and boxes"""
        if not self.state.can_run_checks():
            self.logger.warning(f"Cannot run checks in state: {self.state.status}")
            return

        self.logger.info("Starting check cycle...")
        start_time = datetime.utcnow()

        try:
            # Create new check instance
            with Session(engine) as session:
                check_id = await self._create_check_instance(session)

            # Queue all IOC checks
            task_count = await self._queue_all_checks(check_id)

            # Wait for completion (with timeout)
            # Note: In production, this would be async monitoring
            self.logger.info(f"Queued {task_count} IOC checks")

            # Update state
            self.state.increment_checks()
            self.state.update_check_times(
                last=start_time,
                next=datetime.utcnow() + timedelta(minutes=self.state.check_interval_minutes)
            )

        except Exception as e:
            self.logger.error(f"Check cycle failed: {e}")

    async def _create_check_instance(self, session: Session) -> int:
        """Create a new check instance for all teams"""
        check_instances = []

        for team_num in self.inventory_manager.teams:
            check = CheckInstance(
                blue_team_num=team_num,
                timestamp=datetime.utcnow(),
                score=0
            )
            session.add(check)
            check_instances.append(check)

        session.commit()

        # Update team last_check_id
        for check in check_instances:
            team = session.get(BlueTeams, check.blue_team_num)
            if team:
                team.last_check_id = check.check_id
                session.add(team)

        session.commit()

        # Return first check_id (they're sequential)
        return check_instances[0].check_id if check_instances else 0

    async def _queue_all_checks(self, check_id: int) -> int:
        """Queue all IOC checks for all teams and boxes"""
        if not self.executor:
            raise RuntimeError("Executor not initialized")

        task_count = 0

        for team in self.inventory_manager.teams.values():
            for box in team.boxes:
                iocs = self.ioc_loader.get_iocs_for_os(box.os)

                for ioc in iocs:
                    # Create task
                    task = IOCTask(
                        team_num=team.team_num,
                        box_ip=box.ip,
                        box_os=box.os,
                        ioc_name=ioc.name,
                        ioc_script=ioc.check_script,
                        check_id=check_id + team.team_num,  # Offset by team number
                        playbook_path=self.executor.playbook_cache.get(f"{box.ip}_{ioc.name}", ""),
                        difficulty=ioc.difficulty,  # Add difficulty from IOC definition
                        attempt=1
                    )

                    # Add to queue
                    self.executor.task_queue.put(task)
                    task_count += 1

        return task_count

    async def deploy_iocs(self) -> Dict[str, Any]:
        """Deploy all IOCs to target systems"""
        self.logger.info("Deploying IOCs to all systems...")

        results = {
            "total": 0,
            "successful": 0,
            "failed": 0,
            "errors": []
        }

        for team in self.inventory_manager.teams.values():
            for box in team.boxes:
                iocs = self.ioc_loader.get_iocs_for_os(box.os)

                for ioc in iocs:
                    if not ioc.deploy_script:
                        continue

                    results["total"] += 1

                    try:
                        # Run deploy script via Ansible
                        # For MVP, we'll simulate this
                        self.logger.info(f"Deploying {ioc.name} to {box.ip}")
                        results["successful"] += 1

                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append(f"{box.ip}/{ioc.name}: {str(e)}")

        self.state.total_iocs_deployed = results["successful"]
        return results

    async def shutdown(self) -> None:
        """Shutdown orchestrator and cleanup"""
        self.logger.info("Shutting down orchestrator...")

        try:
            # Stop competition if running
            if self.state.is_active():
                await self.stop_competition()
            elif self.executor:
                # If competition wasn't running but executor exists, still stop workers
                self.executor.stop_workers()

            self.logger.info("Orchestrator shutdown complete")

        except Exception as e:
            self.logger.error(f"Error during shutdown: {e}")

    def get_status(self) -> Dict[str, Any]:
        """Get comprehensive status information"""
        status = self.state.get_status_info()

        # Add component status
        status["components"] = {
            "database": "ready",
            "inventory": self.inventory_manager.get_inventory_summary(),
            "iocs": {
                "loaded": len(self.ioc_loader.ioc_definitions),
                "by_os": {
                    os: len(iocs)
                    for os, iocs in self.ioc_loader.os_ioc_mapping.items()
                }
            },
            "scheduler": self.scheduler.get_status() if self.scheduler else {},
            "executor": {
                "workers": self.executor.num_workers if self.executor else 0,
                "queue_size": self.executor.task_queue.qsize() if self.executor else 0
            }
        }

        return status