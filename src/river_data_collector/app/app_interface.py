from abc import ABC, abstractmethod

class AppInterface(ABC):
    """Interface for the main application logic"""

    @abstractmethod
    def initialize(self) -> None:
        """Sets up application components."""
        pass

    @abstractmethod
    def start(self) -> None:
        """Starts the application process."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Stops the application process gracefully."""
        pass
