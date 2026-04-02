from data.epddata.source.soda4lcacsv import Soda4LcaCsv
import pandas as pd
import numpy as np


class EpdNorwayCsv(Soda4LcaCsv):
    """Class that creates an instance of the soda4LcaCsv class to load soda4LCA CSV database exports and datasets within
    this CSV.

    Parameters
    ----------
    filepath : Path or str
        Path to the EPD Norway CSV export
    """

    def __init__(self, filepath):
        super().__init__(filepath)
        self.standards = ["EN15804+A1", "EN15804+A2"]
