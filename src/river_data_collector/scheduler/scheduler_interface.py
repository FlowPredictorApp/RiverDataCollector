from abc import ABC, abstractmethod

class TaskScheduler(ABC):

    @abstractmethod
    def schedule_task(self, interval: int, task: callable) -> None:
        """Schedules a task to run periodically."""
        pass
