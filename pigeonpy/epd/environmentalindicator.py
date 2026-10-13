"""Defines the EnvironmentalIndicator dataclass."""

from dataclasses import dataclass


@dataclass
class EnvironmentalIndicator:
    """dataclass to hold information for Environmental indicators according to EN 15804+A1 or EN 15804+A2."""
    abbreviation: str
    name: str
    unit: str
    description: str
