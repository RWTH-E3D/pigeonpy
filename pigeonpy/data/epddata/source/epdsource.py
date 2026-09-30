class EpdSource(object):
    """Abstract class containing basic attributes and methods utilized in all subclasses, i.e. implemented EPD sources.

    Attributes
    ----------
    standards : list
        Contains available standards of the EPD source
    dataset_template : EpdDataset
        Alias for EpdDataset class to specify the standard used for the respective EPD source among other things

    """
    def __init__(self):
        self.standards = None
        self.dataset_template = None

    def load_epd(self, epd_dataset, epd_id, scenario):
        """Method to load the EPD dataset given by an epd_id from the respective source.

        Parameters
        ----------
        epd_dataset : EpdDataset
            Instance to store the loaded EPD data.
        epd_id : str
            Identifier, e.g. UUID, for finding an EPD dataset within a source.
        scenario : str
            Used to select the scenario for an EPD dataset, if scenarios are present.
        """
        pass

    def load(self, dataset_template):
        """Initializes the datasource, e.g. by loading file bindings for the database.

        Parameters
        ----------
        dataset_template : EpdDataset
            The dataset template is used to determine the standard for the datasource.
        """
        pass

    def contains_dataset(self, epd_id) -> bool:
        """Method that checks if the respective source contains a dataset specified by the given epd_id."""
        pass