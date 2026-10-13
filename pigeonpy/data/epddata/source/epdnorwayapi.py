"""Provides the class defining the connection to EPD Norway API."""
from pigeonpy.data.epddata.source.soda4lcaapi import Soda4LcaApi


class EpdNorwayApi(Soda4LcaApi):
    """Class for creating a soda4LCA instance of the EPD Norway API to load EpdDataset objects.

    Class variables
    ---------------
    ROOT : str
        URL for the EPD Norway API resource point

    Attributes
    ----------
    standards : list
        Supported standards by the tool and available in EPD Norway.
    """

    ROOT = "https://epdnorway.lca-data.com/resource"

    def __init__(self):
        """Initialize Soda4LcaApi instance with the EPD Norway API root."""
        super().__init__(self.ROOT)

        self.standards = ["EN15804+A1", "EN15804+A2"]