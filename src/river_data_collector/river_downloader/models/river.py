from typing import List

from river_data_collector.river_downloader.models.station import Station


class River:
    def __init__(self, river_name: str, stations: dict[str, Station]):
        self.river_name = river_name
        self.stations = stations
