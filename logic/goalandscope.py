from dataclasses import dataclass


@dataclass
class GoalAndScope:
    """dataclass to hold information for life cycle stages according to EN 15978"""
    standard: str
    considered_stages: list = []
    considered_indicators: list = []
    description: str = ""
