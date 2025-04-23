import requests
from bs4 import BeautifulSoup
import pandas as pd
from typing import Optional

url = "https://www.shmu.sk/en/?page=1&id=hydro_vod_all&station_id=7930"
headers = {'User-Agent': 'Mozilla/5.0'}
response = requests.get(url, headers=headers)
response.encoding = 'utf-8'
fileName = "javorinkaToCSV/hydro_data.csv"

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
        print(f"Saved to {fileName}")
        df.to_csv(fileName, index=False)
    else:
        print("Table is empty")
else:
    print("No Table on the site")
