import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import Optional, List, Dict
from datetime import datetime
from river_data_collector.river_downloader.river_downloader_interface import RiverDownloaderInterface

class SlovakiaRiverNames:
    JAVORINKA = "Javorinka"

class Shmu(RiverDownloaderInterface):

    url = "https://www.shmu.sk/en/?page=1&id=hydro_vod_all&station_id=7930"
    
    def get_river_data(self, river_name: str) -> Optional[List[Dict]]:
        if river_name == SlovakiaRiverNames.JAVORINKA:
            return self.get_javorinka()
        else:
            print(f"River {river_name} not supported.")
            print (f"Supported rivers: {', '.join([name for name in SlovakiaRiverNames.__dict__.keys() if not name.startswith('__')])}")
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
        response = requests.get(url, headers=headers)
        response.encoding = 'utf-8'
        return response

    def get_javorinka(self) -> Optional[List[Dict]]:
        
        response = self.get_service_data(self.url)
        if response.status_code != 200:
            print(f"Error fetching data: {response.status_code}")
            return None
        soup = BeautifulSoup(response.text, "html.parser")
        table: Optional[BeautifulSoup] = soup.find("table", class_="dynamictable w600 center stripped")

        if table is not None:
            return self.parse_table(table)
        else:
            print("Table not found")
            return None
        
if __name__ == "__main__":
    shmu = Shmu()
    data = shmu.get_river_data(SlovakiaRiverNames.JAVORINKA)
    if data:
        for entry in data:
            print(entry)
    else:
        print("No data found.")