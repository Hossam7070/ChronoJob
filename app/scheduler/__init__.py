"""Scheduler module initialization."""

from app.scheduler.scheduler_manager import SchedulerManager

# Global scheduler manager instance
scheduler_manager = SchedulerManager()

__all__ = ['scheduler_manager', 'SchedulerManager']
