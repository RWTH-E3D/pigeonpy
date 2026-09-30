from dataclasses import dataclass


@dataclass
class LifeCycleStage:
    """dataclass to hold information for life cycle stages/modules according to EN 15978

    Attributes
    ----------
    abbreviation: str
        Abbreviation of the life cycle stage in lower case
    name : str
        Name of the life cycle stage (module)
    description : str
        Short description of the life cycle stage meaning
    """
    abbreviation: str
    name: str
    description: str
