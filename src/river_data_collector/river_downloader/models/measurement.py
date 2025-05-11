import datetime
from enum import Enum
from typing import List

class MeasurementType:
    Hydrological = "Hydrological"
    Meteorological = "Meteorological"

class MeasurementMetadata:
    def __init__(self, name: str, unit: str, type: MeasurementType):
        self.name = name
        self.unit = unit
        self.type = type
        
class RiverMeasurementsNames(Enum):
    TIMESTAMP = "TIMESTAMP"
    WATER_LEVEL = "WATER_LEVEL"
    WATER_TEMPERATURE = "WATER_TEMPERATURE"
    FLOW = "FLOW"

RiverMesaurements = {
    RiverMeasurementsNames.FLOW.value : MeasurementMetadata(RiverMeasurementsNames.FLOW.value, "m3/s", MeasurementType.Hydrological),
    RiverMeasurementsNames.WATER_LEVEL.value : MeasurementMetadata(RiverMeasurementsNames.WATER_LEVEL.value, "cm", MeasurementType.Hydrological),
    RiverMeasurementsNames.WATER_TEMPERATURE.value : MeasurementMetadata(RiverMeasurementsNames.WATER_TEMPERATURE.value, "°C", MeasurementType.Hydrological),
}

class BasicMeasurement:
    def __init__(self, value: str, timestamp: datetime):
        self.value = value
        self.timestamp = timestamp

class MeasurementsCollection:
    def __init__(self, metadata: MeasurementMetadata, measurements: List[BasicMeasurement]):
        self.metadata = metadata
        self.measurements = measurements