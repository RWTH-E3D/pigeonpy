class EpdDataManager(object):
    """Class to handle EPD data and their sources.

    The EpdDataManager contains a dictionary to register multiple EPD sources, a method to load the EPD data from a
    source into an EpdDataset object, and it caches already loaded datasets for the case of multiple usages of one
    dataset.

    Attributes
    ----------
    databases : dict
        Contains the registered sources as values with a user defined key
    dataset_template : EpdDataset
        A subclass of EpdDataset itself (not an instance) that serves as a template for creating instances of the given
        class to load the indicator data of an EPD dataset into the data array of the class instance.
    _fetched_datasets : dict
        Caches the data array and name of an already loaded dataset with its uuid as key.

    Parameters
    ----------
    dataset_template : EpdDataset
        Usually gets assigned when instantiating the study class with the dataset_template given to the study class that
        defines the standard for the study.
    """

    def __init__(self, dataset_template):
        self.databases = {}
        self.dataset_template = dataset_template

        self._fetched_datasets = {}

    def register_source(self, source_key, source):
        """Registers a source instance into the databases dictionary with a given key"""
        self.databases[source_key] = source
        self.databases[source_key].load(self.dataset_template)

    def load_epd(self, epd_id, epd_dataset=None, source_key=None):
        """Either loads a dataset from the cached datasets or calls the method of one of the EPD sources in the
        databases dictionary to load the environmental indicator data into an EpdDataset instance. If an EPD is loaded
        for the first time, it is saved in the dataset cache dictionary (_fetched_datasets).

        Parameters
        ----------
        epd_id : str
            UUID of the EPD dataset to be loaded
        epd_dataset : EpdDataset
            Instance of EpdDataset. If None, then an instance is created using the associated method and
            dataset_template attribute.
        source_key : str
            If specified (and found in databases) uses the source indicated by the source_key to load the EPD data from.
            If no source_key is given, it searches the databases for a source that contains a dataset with the given
            epd_id/ uuid.

        Returns
        ----------
        epd_dataset : EpdDataset
            The returned dataset is filled with data and information of the EPD indicated by the UUID.
        """
        epd_dataset = epd_dataset or self._create_dataset_object()

        if epd_id in self._fetched_datasets:
            self._load_from_cache(epd_id, epd_dataset)
            return epd_dataset

        if source_key is None:
            source_key = next(
                (sk for sk, db in self.databases.items() if db.contains_dataset(epd_id)),
                None
            )
            if source_key is None:
                raise Exception(f"No dataset for epd_id '{epd_id}' found in database(s): {self.databases.keys()}")

        if source_key not in self.databases:
            raise ValueError(f"No data source found with source key '{source_key}'")

        self.databases[source_key].load_epd(epd_dataset, epd_id)
        epd_dataset.history.add_data_source(epd_id, epd_dataset.name, source_key)

        self._fetched_datasets[epd_id] = {"name": epd_dataset.name, "data": epd_dataset.data.copy()}

        return epd_dataset

    def _create_dataset_object(self):
        """Returns an instance of the dataset_template"""
        return self.dataset_template()

    def _load_from_cache(self, epd_id, epd_dataset):
        """Assigns name and data of an already loaded dataset from the dictionary that caches already loaded datasets
        to another instance."""
        epd_dataset.name = self._fetched_datasets[epd_id].get("name")
        epd_dataset.data = self._fetched_datasets[epd_id].get("data").copy()
