from dataclasses import dataclass, field


@dataclass
class GoalAndScope:
    """dataclass to hold information for life cycle stages according to EN 15978"""
    standard: str
    considered_stages: list = field(default_factory=list)
    considered_indicators: list = field(default_factory=list)
    description: str = ""
