from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import date

class RiverDownloaderInterface(ABC):

    @abstractmethod
    def get_river_data(self, river_name: str, since: date, till: date) -> Optional[List[Dict[str, any]]]:
        """Fetches data for a given river between specified dates.
        
        Args:
            river_name (str): The name of the river to fetch data for. River names should be defined in a separate class.
            since (date): The start date for data collection. 
            till (date): The end date for data collection.
        
        Returns:
            Optional[List[Dict[str, any]]]: A list of data records, or None if data retrieval fails.
        """
        pass
