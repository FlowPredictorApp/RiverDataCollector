from abc import ABC, abstractmethod
from typing import Dict, List, Optional

class RiverDownloaderInterface(ABC):

    @abstractmethod
    def get_river_data(self, river_name: str) -> Optional[List[Dict]]:
        """Fetches data for a given river."""
        pass
