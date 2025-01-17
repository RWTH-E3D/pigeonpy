from dataclasses import dataclass


@dataclass
class LifeCycleStage:
    """dataclass to hold information for life cycle stages according to EN 15978"""
    abbreviation: str
    name: str
    description: str
