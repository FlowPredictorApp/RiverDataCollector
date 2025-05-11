from river_data_collector.river_downloader.models.station import Station


class River:
    def __init__(self, name: str, stations: dict[str, Station]):
        self.name = name
        self.stations = stations
