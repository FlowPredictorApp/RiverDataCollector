import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import Optional, List, Dict
from datetime import datetime


def main() -> Optional[List[Dict]]:
    url = "https://www.shmu.sk/en/?page=1&id=hydro_vod_all&station_id=7930"
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'

    soup = BeautifulSoup(response.text, "html.parser")
    table: Optional[BeautifulSoup] = soup.find("table", class_="dynamictable w600 center stripped")

    if table is not None:
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
    else:
        print("No Table on the site")
        return None


if __name__ == "__main__":
    print("Collecting data from Javorinka")
    data = main()