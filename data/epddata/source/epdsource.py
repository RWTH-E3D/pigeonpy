class EpdSource(object):
    """Abstract class containing basic attributes and methods utilized in all subclasses, i.e. implemented EPD sources

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
        """Method to load the EPD dataset given by an epd_id from the respective source."""
        pass

    def load(self, dataset_template):
        """Method to initialize the respective datasource, e.g. load file bindings for database. The dataset template
        is used to determine the standard for the datasource, among other things."""
        pass

    def contains_dataset(self, epd_id) -> bool:
        """Method that checks if the respective source contains a specific dataset given by the epd_id."""
        pass