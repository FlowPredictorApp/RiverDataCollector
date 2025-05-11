from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import date

from river_data_collector.river_downloader.models.measurement import MeasurementsCollection

class RiverDownloaderInterface(ABC):

    @abstractmethod
    def get_river_data(self, river_name: str, station_id: str, since: date, till: date) -> Optional[Dict[str, MeasurementsCollection]]:
        """Fetches data for a given river between specified dates.
        
        Args:
            river_name (str): The name of the river to fetch data for. River names should be defined in a separate class.
            since (date): The start date for data collection. 
            till (date): The end date for data collection.
        
        Returns:
            Collection of all RiverMesaurements that are avaiable for the river. None if data retrieval fails or data is not present.
        """
        pass
