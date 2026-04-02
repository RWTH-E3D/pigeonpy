from data.epddata.source.soda4lcaapi import Soda4LcaApi


class EpdNorwayApi(Soda4LcaApi):
    """Class that creates a soda4LCA instance for the EPD Norway API to load EpdDataset objects

    Class variables
    ----------
    ROOT : str
        URL for the EPD Norway API resource point
    """

    ROOT = "https://epdnorway.lca-data.com/resource"

    def __init__(self):
        super().__init__(self.ROOT)

        self.standards = ["EN15804+A1", "EN15804+A2"]