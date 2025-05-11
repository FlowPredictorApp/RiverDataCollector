from enum import Enum
import json
import os
import requests
from typing import Optional, List, Dict
import zipfile
from datetime import datetime, date
from river_data_collector.river_downloader.models.measurement import *
from river_data_collector.river_downloader.models.river import *
from river_data_collector.river_downloader.models.station import Station
from river_data_collector.river_downloader.river_downloader_interface import RiverDownloaderInterface

class ImgwMeasurementMetadata(MeasurementMetadata):
    def __init__(self, measurement_name: str, unit: str, measurement_type: str, measurement_id: str):
        super().__init__(measurement_name, unit, measurement_type)
        self.measurement_id = measurement_id

class PolishRiversNames(Enum):
    BIALKA = "Bialka"

class StationsNames(Enum):
    TRYBSZ2 = "Trybsz2"

class ImgwDownloader(RiverDownloaderInterface):

    BASE_URL = "https://danepubliczne.imgw.pl/pl/datastore/getfiledown"
    IMGW_TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M"
    YEAR_URL = "/Arch/Telemetria/Hydro/"
    ZIP_FILES_PATH = "downloads/"
    UNZIPPED_FILES_PATH = "unzipped_files/"
    MONTH_URL_PREFIX = "Hydro_"

    IMGW_MEASUREMENTS = {
        RiverMeasurementsNames.FLOW.value : ImgwMeasurementMetadata(RiverMeasurementsNames.FLOW.value, "m3/s", MeasurementType.Hydrological, "B00050S"),
        RiverMeasurementsNames.WATER_LEVEL.value: ImgwMeasurementMetadata(RiverMeasurementsNames.WATER_LEVEL.value, "cm", MeasurementType.Hydrological, "B00020S"),
    }

    MEASUREMENTS_COLLECTIONS = {
        RiverMeasurementsNames.FLOW.value: MeasurementsCollection(RiverMesaurements[RiverMeasurementsNames.FLOW.value], []),
        RiverMeasurementsNames.WATER_LEVEL.value: MeasurementsCollection(RiverMesaurements[RiverMeasurementsNames.WATER_LEVEL.value], []),
    }


    POLISH_RIVERS = {
        PolishRiversNames.BIALKA.value: River(PolishRiversNames.BIALKA.value, {
            StationsNames.TRYBSZ2.value: Station(StationsNames.TRYBSZ2.value, "149200110")
        })
    }


    def get_river_data(self, river_name: str, station_name: str, since: date, till: date, clear_files = True) -> Optional[Dict[str, MeasurementsCollection]]:
        """Fetches data for a given river between specified dates.
        Args:
            river_name (str): The name of the river to fetch data for. River names should be defined in a separate class.
            station_name (str): The name of the station to fetch data for.
            since (date): The start date for data collection. 
            till (date): The end date for data collection.
            clear_files (bool): If True, downloaded files will be removed after processing.
            Returns:
                Collection of all RiverMesaurements that are available for the river. None if data retrieval fails or data is not present.
                """
        try:
            river, station = self.validate_parameters(river_name, station_name, since, till)
            print(f"Fetching data for river: {river.name}, station: {station.name}, from {since} to {till}")
        except ValueError as error:
            print(error)
            return None

        start_year = since.year
        end_year = till.year

        for year in range(start_year, end_year + 1):
            start_month = since.month if year == start_year else 1
            end_month = till.month if year == end_year else 12

            for month in range(start_month, end_month + 1):
                file_name = f"{self.MONTH_URL_PREFIX}{year}-{month:02d}.zip"
                url = f"{self.BASE_URL}{self.YEAR_URL}{year}/{file_name}"
                print(f"Attempting to download data from: {url}")
                downloaded_zip = self.download_zip(url, self.ZIP_FILES_PATH + file_name)
                if downloaded_zip:
                    measurements_files = self.unzip(downloaded_zip)
                    if measurements_files is None:
                        continue
                    for metadata in self.IMGW_MEASUREMENTS.values():
                        measurement_type_file_name = f"{metadata.measurement_id}_{year}_{month:02d}.csv"
                        if measurement_type_file_name in measurements_files:
                            self.MEASUREMENTS_COLLECTIONS[metadata.name].measurements.extend(
                                self.read_measurements_collection(measurement_type_file_name, station)
                            )
                        else:
                            print(f"Measurement type file {measurement_type_file_name} not found in {file_name}")
                else:
                    print(f"Data not available for {year}-{month:02d}")

        print("Data collection complete.")
        print("Collected measurements:")
        for measurement_name, collection in self.MEASUREMENTS_COLLECTIONS.items():
            print(f"{measurement_name}: {len(collection.measurements)} measurements")
        if clear_files:
            self.clear_directories()
        return self.MEASUREMENTS_COLLECTIONS

    def get_imgw_data(self, url: str) -> requests.Response:
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response
        except requests.RequestException as error:
            print(f"Request failed: {error}")
            return None

    def download_zip(self, url: str, filename: str) -> Optional[str]:
        response = self.get_imgw_data(url)
        if response and response.status_code == 200:
            if not os.path.exists(self.ZIP_FILES_PATH):
                os.makedirs(self.ZIP_FILES_PATH)
            with open(filename, "wb") as file:
                file.write(response.content)
            print(f"Downloaded: {filename}")
            return filename
        else:
            print(f"Failed to download {url}")
            return None

    def unzip(self, file: str) -> List[str]:
        try:
            with zipfile.ZipFile(file, 'r') as zip_ref:
                zip_ref.extractall(self.UNZIPPED_FILES_PATH)
        except Exception as error:
            print(f"Failed to unzip {file}: {error}")
            return None
        print(f"Unzipped: {file}")
        return zip_ref.namelist()

    def read_measurements_collection(self, file_name: str, station: Station) -> List[BasicMeasurement]:
        file_path = self.UNZIPPED_FILES_PATH + file_name
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            return None
        measurements = []
        with open(file_path, "r") as file:
            lines = file.readlines()
            for line in lines:
                data = line.strip().split(";")
                if station.id in data[0]:
                    basic_measurement = BasicMeasurement(data[3], datetime.datetime.strptime(data[2], self.IMGW_TIMESTAMP_FORMAT))
                    measurements.append(basic_measurement)
        if measurements:
            print(f"Read {len(measurements)} measurements from {file_name} for station {station.name}")
            return measurements
        else:
            print(f"No data found for station {station.name} in {file_name}")
            return None

    def validate_parameters(self, river_name: str, station_id: str, since: date, till: date) -> tuple[River, Station]:
        """
        Throws ValueError if any of the parameters are invalid.
        """
        river = self.validate_river_name(river_name)
        self.validate_station_name(station_id)
        station = self.validate_station_on_river(river_name, station_id)
        self.validate_date_range(since, till)
        return river, station

    def validate_river_name(self, river_name: str) -> River:
        if river_name not in [river.value for river in PolishRiversNames]:
            raise ValueError(f"Invalid river name: {river_name}. Supported rivers: {', '.join([river.value for river in PolishRiversNames])}")
        return self.POLISH_RIVERS[river_name]

    def validate_station_name(self, station_name: str) -> Station:
        valid_station_names = [station.value for station in StationsNames]
        if station_name not in valid_station_names:
            raise ValueError(f"Invalid station name: {station_name}. Supported stations: {', '.join(valid_station_names)}")

    def validate_station_on_river(self, river_name: str, station_name: str):
        stations_names_on_river = self.POLISH_RIVERS[river_name].stations
        if station_name not in stations_names_on_river:
            raise ValueError(f"Station {station_name} is not on river {river_name}. Supported stations on the river: {', '.join([station.name for station in self.POLISH_RIVERS[river_name].stations])}")
        return self.POLISH_RIVERS[river_name].stations[station_name]

    def validate_date_range(self, since: date, till: date):
        if since > till:
            raise ValueError(f"Invalid date range: {since} to {till}. 'since' must be earlier than 'till'.")
        if since.year < 2008 or till.year > date.today().year:
            raise ValueError(f"Invalid date range: {since} to {till}. Data is only available from 2008 to the current year.")

    def clear_directories(self):
        for file in os.listdir(self.ZIP_FILES_PATH):
            os.remove(os.path.join(self.ZIP_FILES_PATH, file))
        for file in os.listdir(self.UNZIPPED_FILES_PATH):
            os.remove(os.path.join(self.UNZIPPED_FILES_PATH, file))
        if os.path.exists(self.ZIP_FILES_PATH) and not os.listdir(self.ZIP_FILES_PATH):
            os.rmdir(self.ZIP_FILES_PATH)
        if os.path.exists(self.UNZIPPED_FILES_PATH) and not os.listdir(self.UNZIPPED_FILES_PATH):
            os.rmdir(self.UNZIPPED_FILES_PATH)
        print("Removed downloaded files")

if __name__ == "__main__":
    # Example usage
    downloader = ImgwDownloader()
    river_name = PolishRiversNames.BIALKA.value
    station_name = StationsNames.TRYBSZ2.value
    since_date = date(2023, 1, 1)
    till_date = date(2023, 2, 1)
    data = downloader.get_river_data(river_name, station_name, since_date, till_date, clear_files=False)
    #save data to json file
    if data:
        output_dir = "output/"
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for measurement_name, collection in data.items():
            with open(f"{output_dir}{measurement_name}.json", "w") as file:
                json.dump([measurement.__dict__ for measurement in collection.measurements], file, default=str)
        print(f"Data saved to {measurement_name}.json")
    else:
        print("No data collected.")