from enum import Enum
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

class imgwMesaurementsNames:
    Flow = "Flow"
    OperationalWaterLevel = "Operational Water Level"
    ControlWaterLevel = "Control Water Level"

class PolishRiversNames(Enum):
    Bialka = "Bialka"

class StationsNames(Enum):
    Trybsz2 = "Trybsz2"

class ImgWDownloader(RiverDownloaderInterface):

    base_url = "https://danepubliczne.imgw.pl/pl/datastore/getfiledown"
    year_url = "/Arch/Telemetria/Hydro/"
    zip_files_path = "downloads/"
    unzipped_files_path = "unzipped_files/"
    month_url_prefix = "Hydro_"
    ImgwMeasurements = {
        imgwMesaurementsNames.Flow : ImgwMeasurementMetadata(imgwMesaurementsNames.Flow ,"m3/s", MeasurementType.Hydrological, "B00050S"),
        imgwMesaurementsNames.OperationalWaterLevel : ImgwMeasurementMetadata(imgwMesaurementsNames.OperationalWaterLevel,"cm", MeasurementType.Hydrological, "B00020S"),
        imgwMesaurementsNames.ControlWaterLevel : ImgwMeasurementMetadata(imgwMesaurementsNames.ControlWaterLevel,"cm", MeasurementType.Hydrological, "B00014A"),
        # Temperature = MeasurementMetadata("Temperature", "B00101A", "°C", MeasurementType.Hydrological),
    }
    measurements_collections = {
        imgwMesaurementsNames.Flow : MeasurementsCollection(ImgwMeasurements[imgwMesaurementsNames.Flow], []),
        imgwMesaurementsNames.OperationalWaterLevel : MeasurementsCollection(ImgwMeasurements[imgwMesaurementsNames.OperationalWaterLevel], []),
        imgwMesaurementsNames.ControlWaterLevel : MeasurementsCollection(ImgwMeasurements[imgwMesaurementsNames.ControlWaterLevel], []),
    }

    polishRivers = {
        PolishRiversNames.Bialka.value : River(PolishRiversNames.Bialka.value, {
            StationsNames.Trybsz2.value : Station(StationsNames.Trybsz2.value,"149200110")
            })}

    def get_river_data(self, river_name: str, station_name: str, since: date, till: date) -> Optional[Dict[str, MeasurementsCollection]]:
        try:
            river, station = self.validate_parameters(river_name, station_name, since, till)
            print(f"Fetching data for river: {river.river_name}, station: {station.name}, from {since} to {till}")
        except ValueError as e:
            print(e)
            return None
        start_year = since.year
        end_year = till.year
        for year in range(start_year, end_year + 1):
            start_month = since.month if year == start_year else 1
            end_month = till.month if year == end_year else 12

            for month in range(start_month, end_month + 1):
                file_name = f"{self.month_url_prefix}{year}-{month:02d}.zip"
                url = f"{self.base_url}{self.year_url}{year}/{file_name}"
                print(f"Attempting to download data from: {url}")
                downloaded_zip = self.download_zip(url, self.zip_files_path + file_name)
                if downloaded_zip:
                    measurements_files = self.unzip(downloaded_zip)
                    if measurements_files is None:
                        continue
                    for measuementType_metaData in self.ImgwMeasurements.values():
                        measurement_type_file_name = f"{measuementType_metaData.measurement_id}_{year}_{month:02d}.csv"
                        if measurement_type_file_name in measurements_files:
                            self.measurements_collections[measuementType_metaData.measurement_name].measurements.extend(
                                self.read_measurements_collection(measurement_type_file_name, station)
                            )
                        else:
                            print(f"Measurement type file {measurement_type_file_name} not found in {file_name}")
                else:
                    print(f"Data not available for {year}-{month:02d}")
        print("Data collection complete.")
        print("Collected measurements:")
        for measurement_name, collection in self.measurements_collections.items():
            print(f"{measurement_name}: {len(collection.measurements)} measurements")
        self.clear_directories()
        return self.measurements_collections

    def get_imgw_data(self, url: str) -> requests.Response:
        headers = {'User-Agent': 'Mozilla/5.0'}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            return response
        except requests.RequestException as e:
            print(f"Request failed: {e}")
            return None

    def download_zip(self, url: str, filename: str) -> Optional[str]:
        #TODO make it return file with name as given in the url as default
        response = self.get_imgw_data(url)
        if response and response.status_code == 200:
            if not os.path.exists(self.zip_files_path):
                os.makedirs(self.zip_files_path)
            with open(filename, "wb") as f:
                f.write(response.content)
            print(f"Downloaded: {filename}")
            return filename
        else:
            print(f"Failed to download {url}")
            return None

    def unzip(self, file: str) -> List[str]:
        try:
            with zipfile.ZipFile(file, 'r') as zip_ref:
                zip_ref.extractall(self.unzipped_files_path)
        except Exception as e:
            print(f"Failed to unzip {file}: {e}")
            return None
        print(f"Unzipped: {file}")
        return zip_ref.namelist()
        
    def read_measurements_collection( self, file_name: str, station: Station) -> List[BasicMeasurement]:
        file_path = self.unzipped_files_path + file_name
        if not os.path.exists(file_path):
            print(f"File {file_path} does not exist.")
            return None
        measurements = []
        with open(file_path, "r") as f:
            lines = f.readlines()
            for line in lines:
                data = line.strip().split(";")
                if station.id in data[0]:
                    basic_measurement = BasicMeasurement(data[3],  datetime.datetime.strptime(data[2], '%Y-%m-%d %H:%M'))
                    measurements.append(basic_measurement)
                #if date is last day of the month stop this loop
        if measurements:
            print(f"Read {len(measurements)} measurements from {file_name} for station {station.name}")
            return measurements
        else:
            print(f"No data found for station {station.name} in {file_name}")
            return None

    def validate_parameters(self, river_name: str, station_id: str, since: date, till: date) -> tuple[River, Station]:
        """
        Throws ValueError if any of the parameters are invalid."""
        river = self.validate_river_name(river_name)
        self.validate_station_name(station_id)
        station = self.validate_station_on_river(river_name, station_id)
        self.validate_date_range(since, till)
        return river, station

    def validate_river_name(self, river_name: str) -> River:
        if river_name not in PolishRiversNames.__members__:
            raise ValueError(f"Invalid river name: {river_name}. Supported rivers: {', '.join([river.value for river in PolishRiversNames])}")
        return self.polishRivers[river_name]

    def validate_station_name(self, station_name: str) -> Station:
        valid_station_names = [station.value for station in StationsNames]
        if station_name not in valid_station_names:
            raise ValueError(f"Invalid station name: {station_name}. Supported stations: {', '.join(valid_station_names)}")

    def validate_station_on_river(self, river_name: str, station_name: str):
        # stations_names_on_river = [station.name for station in self.polishRivers[river_name].stations]
        stations_names_on_river = self.polishRivers[river_name].stations
        if station_name not in stations_names_on_river:
            raise ValueError(f"Station {station_name} is not on river {river_name}. Supported stations on the river: {', '.join([station.name for station in self.polishRivers[river_name].stations])}")
        return self.polishRivers[river_name].stations[station_name]
    
    def validate_date_range(self, since: date, till: date):
        if since > till:
            raise ValueError(f"Invalid date range: {since} to {till}. 'since' must be earlier than 'till'.")
        if since.year < 2008 or till.year > datetime.date.today().year:
            raise ValueError(f"Invalid date range: {since} to {till}. Data is only available from 2008 to the current year.")

    def clear_directories(self):
        for file in os.listdir(self.zip_files_path):
            print(f"Removing {file} from {self.zip_files_path}")
            os.remove(os.path.join(self.zip_files_path, file))
        for file in os.listdir(self.unzipped_files_path):
            print(f"Clearing {file}")
            os.remove(os.path.join(self.unzipped_files_path, file))
        print("Cleared directories.")

if __name__ == "__main__":
    # Example usage
    downloader = ImgWDownloader()
    river_name = "Bialka"
    station_name = "Trybsz2"
    since_date = date(2023, 1, 1)
    till_date = date(2023, 2, 1)
    downloader.get_river_data(river_name, station_name, since_date, till_date)