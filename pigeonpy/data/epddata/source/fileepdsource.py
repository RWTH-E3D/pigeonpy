"""Defines the abstract base class for local, file-based EPD data sources."""

from pigeonpy.data.epddata.source.epdsource import EpdSource


class FileEpdSource(EpdSource):
    """Abstract class for EPD sources using files as data source."""
    def __init__(self, filepath):
        """Initialize the EPD source using the given filepath.

        Parameters
        ----------
        filepath : str or Path
            The filepath to the database file to be loaded.
        """
        super().__init__()
        self.filepath = filepath
