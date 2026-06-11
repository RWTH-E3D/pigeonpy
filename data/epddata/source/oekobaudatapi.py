from data.epddata.source.soda4lcaapi import Soda4LcaApi


class OekobaudatApi(Soda4LcaApi):
    """Class for creating a soda4LCA instance of the Ökobaudat API to load EpdDataset objects.

    Class variables
    ----------
    ROOT : str
        URL for the Oekobaudat API resource point

    Attributes
    ----------
    standards : list
        Supported standards by the tool and available in the Ökobaudat.
    """

    ROOT = "https://oekobaudat.de/OEKOBAU.DAT/resource"

    def __init__(self):
        """Initialize Soda4LcaApi instance with the Ökobaudat API root."""
        super().__init__(self.ROOT)

        self.standards = ["EN15804+A1", "EN15804+A2"]
