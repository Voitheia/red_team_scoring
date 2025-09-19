import asyncio
import threading
from typing import Optional, Callable
from datetime import datetime, timedelta
import logging

class CheckScheduler:
    """
    Manages periodic execution of IOC checks.
    Runs checks every 5 minutes when competition is active.
    """

    def __init__(self, check_interval_minutes: int = 5):
        self.logger = logging.getLogger(__name__)
        self.check_interval = check_interval_minutes
        self.running = False
        self.task: Optional[asyncio.Task] = None
        self.check_callback: Optional[Callable] = None
        self.last_check_time: Optional[datetime] = None
        self.next_check_time: Optional[datetime] = None

    def set_callback(self, callback: Callable) -> None:
        """Set the callback function to run checks"""
        self.check_callback = callback

    async def start(self) -> None:
        """Start the scheduler"""
        if self.running:
            self.logger.warning("Scheduler already running")
            return

        if not self.check_callback:
            raise RuntimeError("No check callback set")

        self.running = True
        self.task = asyncio.create_task(self._run_scheduler())
        self.logger.info(f"Check scheduler started with {self.check_interval} minute interval")

    async def stop(self) -> None:
        """Stop the scheduler"""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None
        self.logger.info("Check scheduler stopped")

    async def _run_scheduler(self) -> None:
        """Main scheduler loop"""
        # Run initial check immediately
        await self._run_check()

        while self.running:
            try:
                # Calculate next check time
                self.next_check_time = datetime.utcnow() + timedelta(minutes=self.check_interval)

                # Wait for interval
                await asyncio.sleep(self.check_interval * 60)

                if self.running:
                    await self._run_check()

            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Error in scheduler loop: {e}")
                # Continue running but wait a bit before retry
                await asyncio.sleep(30)

    async def _run_check(self) -> None:
        """Execute a check cycle"""
        self.last_check_time = datetime.utcnow()
        self.logger.info(f"Starting scheduled check at {self.last_check_time}")

        try:
            # Run check callback
            if asyncio.iscoroutinefunction(self.check_callback):
                await self.check_callback()
            else:
                # Run synchronous callback in thread pool
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, self.check_callback)

            self.logger.info("Scheduled check completed successfully")

        except Exception as e:
            self.logger.error(f"Error during scheduled check: {e}")

    async def trigger_immediate_check(self) -> None:
        """Trigger an immediate check outside of schedule"""
        if not self.check_callback:
            raise RuntimeError("No check callback set")

        self.logger.info("Triggering immediate check")
        await self._run_check()

    def get_status(self) -> dict:
        """Get scheduler status"""
        return {
            "running": self.running,
            "check_interval_minutes": self.check_interval,
            "last_check_time": self.last_check_time.isoformat() if self.last_check_time else None,
            "next_check_time": self.next_check_time.isoformat() if self.next_check_time else None
        }