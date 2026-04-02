from data.epddata.source.soda4lcaapi import Soda4LcaApi


class OekobaudatApi(Soda4LcaApi):
    """Class that creates a soda4LCA instance for the Oekobaudat API to load EpdDataset objects

    Class variables
    ----------
    ROOT : str
        URL for the Oekobaudat API resource point
    """

    ROOT = "https://oekobaudat.de/OEKOBAU.DAT/resource"

    def __init__(self):
        super().__init__(self.ROOT)

        self.standards = ["EN15804+A1", "EN15804+A2"]
