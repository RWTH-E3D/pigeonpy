from dataclasses import dataclass


@dataclass
class EnvironmentalIndicator:
    abbreviation: str
    name: str
    unit: str
    description: str
