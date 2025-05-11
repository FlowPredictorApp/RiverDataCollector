import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import Optional, List, Dict
from datetime import datetime
from river_data_collector.river_downloader.river_downloader_interface import RiverDownloaderInterface

class SlovakiaRiverNames:
    JAVORINKA = "Javorinka"

class ShmuDownloader(RiverDownloaderInterface):

    BASE_URL = "https://www.shmu.sk/en/?page=1&id=hydro_vod_all&station_id=7930"

    def get_river_data(self, river_name: str) -> Optional[List[Dict]]:
        if river_name == SlovakiaRiverNames.JAVORINKA:
            return self.get_javorinka_data()
        else:
            print(f"River {river_name} not supported.")
            print(f"Supported rivers: {', '.join([name for name in SlovakiaRiverNames.__dict__.keys() if not name.startswith('__')])}")
            return None

    def parse_table(self, table: BeautifulSoup) -> Optional[List[Dict]]:
        rows = []
        for row in table.find_all("tr"):
            cols = [col.get_text(strip=True) for col in row.find_all(["th", "td"])]
            if cols:
                rows.append(cols)

        if len(rows) > 1:
            df = pd.DataFrame(rows[1:], columns=rows[0])
            print(f"Retrieved data at {datetime.now()}")

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

    def get_javorinka_data(self) -> Optional[List[Dict]]:
        response = self.get_service_data(self.BASE_URL)
        if response and response.status_code == 200:
            soup = BeautifulSoup(response.text, "html.parser")
            table: Optional[BeautifulSoup] = soup.find("table", class_="dynamictable w600 center stripped")

            if table is not None:
                return self.parse_table(table)
            else:
                print("Table not found")
                return None
        else:
            print(f"Error fetching data: {response.status_code if response else 'No response'}")
            return None

if __name__ == "__main__":
    downloader = ShmuDownloader()
    data = downloader.get_river_data(SlovakiaRiverNames.JAVORINKA)
    if data:
        for entry in data:
            print(entry)
    else:
        print("No data found.")