from data.epddata.source.epdsource import EpdSource


class FileEpdSource(EpdSource):
    """Abstract class for EPD sources using files as data source."""
    def __init__(self, filepath):
        """Initialize the EPD source using the given filepath."""
        super().__init__()
        self.filepath = filepath
