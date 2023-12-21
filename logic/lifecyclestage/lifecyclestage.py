from dataclasses import dataclass


@dataclass
class LifeCycleStage:
    abbreviation: str
    name: str
    description: str
