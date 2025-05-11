import datetime
from typing import List


class MeasurementType:
    Hydrological = "Hydrological"
    Meteorological = "Meteorological"

class MeasurementMetadata:
    def __init__(self, name: str, unit: str, type: MeasurementType):
        self.name = name
        self.unit = unit
        self.type = type

class RiverMesaurements:
    Flow = MeasurementMetadata("Flow", "m3/s", MeasurementType.Hydrological),
    WaterLevel = MeasurementMetadata("Water Level", "cm", MeasurementType.Hydrological),

class BasicMeasurement:
    def __init__(self, value: str, timestamp: datetime):
        self.value = value
        self.timestamp = timestamp

class MeasurementsCollection:
    def __init__(self, metadata: MeasurementMetadata, measurements: List[BasicMeasurement]):
        self.metadata = metadata
        self.measurements = measurements