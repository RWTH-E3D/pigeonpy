"""Defines the EnvironmentalIndicator dataclass."""

from dataclasses import dataclass


@dataclass
class EnvironmentalIndicator:
    """dataclass to hold information for Environmental indicators according to EN 15804+A1 or EN 15804+A2.

    Attributes
    ----------
    abbreviation: str
        Abbreviation of the environmental indicator in lower case
    name : str
        Full name of the environmental indicator
    unit : str
        The indicators unit
    description : str
        Short description of the indicator meaning
    """
    abbreviation: str
    name: str
    unit: str
    description: str
