from data.epddata.source.soda4lcacsv import Soda4LcaCsv
import pandas as pd
import numpy as np


class EpdNorwayCsv(Soda4LcaCsv):
    """Class for creating an instance of the Soda4LcaCsv class to load CSV Export from EPD Norway and datasets within
    this CSV.

    Attributes
    ----------
    standards : list
        Supported standards by the tool and available in EPD Norway.
    """

    def __init__(self, filepath):
        """Initialize a Soda4LcaCsv instance with the filepath to the EPD Norway CSV export file.

        Parameters
        ----------
        filepath : Path or str
            Path to the EPD Norway CSV export
        """
        super().__init__(filepath)
        self.standards = ["EN15804+A1", "EN15804+A2"]
