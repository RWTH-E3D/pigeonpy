from data.epddata.source.epdsource import EpdSource


class ApiEpdSource(EpdSource):
    """Abstract class for EPD API sources."""
    def __init__(self):
        super().__init__()
