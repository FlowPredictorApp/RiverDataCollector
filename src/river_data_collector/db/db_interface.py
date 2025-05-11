from abc import ABC, abstractmethod

class DataStorage(ABC):

    @abstractmethod
    def save_data(self, river_name: str, data: dict) -> None:
        """Saves river data to the database."""
        pass
