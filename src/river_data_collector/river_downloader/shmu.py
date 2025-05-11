from enum import Enum
import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import Optional, List, Dict
from datetime import date, datetime
from river_data_collector.river_downloader.models.measurement import *
from river_data_collector.river_downloader.models.river import River
from river_data_collector.river_downloader.models.station import Station
from river_data_collector.river_downloader.river_downloader_interface import RiverDownloaderInterface

class SlovakiaRiverNames(Enum):
    JAVORINKA = "Javorinka"

class StationsNames(Enum):
    ZIDAR = "Ždiar - Podspády"
    
class ShmuMeasurementsNames(Enum):
    TIMESTAMP = 'Čas merania'
    WATER_LEVEL = 'Vodný stav [cm]'
    WATER_TEMPERATURE = 'Teplota vody [°C]'

class ShmuDownloader(RiverDownloaderInterface):

    BASE_URL = "https://www.shmu.sk/en/?page=1&id=hydro_vod_all&station_id=7930"
    SHMU_TIMESTAMP_FORMAT = "%d.%m.%Y %H:%M"

    MEASUREMENTS_COLLECTIONS = {
        RiverMeasurementsNames.WATER_LEVEL.value: MeasurementsCollection(RiverMesaurements[RiverMeasurementsNames.FLOW.value], []),
        RiverMeasurementsNames.WATER_TEMPERATURE.value: MeasurementsCollection(RiverMeasurementsNames.WATER_TEMPERATURE.value, []),
}

    SLOVAKIA_RIVERS = {
        SlovakiaRiverNames.JAVORINKA.value: River(SlovakiaRiverNames.JAVORINKA.value, {
            StationsNames.ZIDAR.value: Station(StationsNames.ZIDAR.value, "7930")
        })
    }

    def get_river_data(self, river_name: str, station_name: str, since: date, till: date) -> Optional[Dict[str, MeasurementsCollection]]:
        print(f"Fetching data for river: {river_name}, station: {station_name}")
        if river_name == SlovakiaRiverNames.JAVORINKA.value:
            return self.get_javorinka_data()
        else:
            print(f"River {river_name} not supported.")
            print(f"Supported rivers: {', '.join([name for name in SlovakiaRiverNames.__dict__.keys() if not name.startswith('__')])}")
            return None

    def get_table_data(self, table: BeautifulSoup) -> Optional[List[Dict]]:
        rows = []
        for row in table.find_all("tr"):
            cols = [col.get_text(strip=True) for col in row.find_all(["th", "td"])]
            if cols:
                rows.append(cols)

        if len(rows) > 1:
            df = pd.DataFrame(rows[1:], columns=rows[0])
            print(f"Retrieved data at {datetime.datetime.now()}")

            data = df.to_dict(orient="records")
            return data
        else:
            print("Table is empty")
            return None

    def get_service_data(self, url: str) -> requests.Response:
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            response.encoding = 'utf-8'
            return response
        except requests.RequestException as error:
            print(f"Request failed: {error}")
            return None

    def get_javorinka_data(self) -> Optional[Dict[str, MeasurementsCollection]]:
        response = self.get_service_data(self.BASE_URL)
        if response and response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            table: Optional[BeautifulSoup] = soup.find("table", class_="dynamictable w600 center stripped")

            if table is not None:
                table_data = self.get_table_data(table)
                self.MEASUREMENTS_COLLECTIONS = self.parse_table_data(table_data)
            else:
                print("Table not found")
                return None
        else:
            print(f"Error fetching data: {response.status_code if response else 'No response'}")
            return None
        print("Data collection complete.")
        return self.MEASUREMENTS_COLLECTIONS
        
    def parse_table_data(self, table_data: List[Dict]) -> Optional[Dict[str, MeasurementsCollection]]:
        for row in table_data:
            timestamp = datetime.datetime.strptime(row[ShmuMeasurementsNames.TIMESTAMP.value], self.SHMU_TIMESTAMP_FORMAT)
            water_level = row[ShmuMeasurementsNames.WATER_LEVEL.value]
            water_temperature = row[ShmuMeasurementsNames.WATER_TEMPERATURE.value]
            self.MEASUREMENTS_COLLECTIONS[ShmuMeasurementsNames.WATER_LEVEL.name].measurements.append(
                BasicMeasurement(timestamp, water_level) )
            self.MEASUREMENTS_COLLECTIONS[ShmuMeasurementsNames.WATER_TEMPERATURE.name].measurements.append(
                 BasicMeasurement(timestamp, water_temperature)
            )
        return self.MEASUREMENTS_COLLECTIONS

if __name__ == "__main__":
    # Example usage
    downloader = ShmuDownloader()
    data = downloader.get_river_data(SlovakiaRiverNames.JAVORINKA.value, StationsNames.ZIDAR.value, date(2023, 1, 1), date(2023, 1, 2))