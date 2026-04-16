class EpdDataManager(object):
    """Class to handle EPD data and their sources.

    The EpdDataManager contains a dictionary to register multiple EPD sources, a method to load the EPD data from a
    source into an EpdDataset object, and it caches already loaded datasets for the case of multiple usages of one
    dataset.

    Attributes
    ----------
    sources : dict
        Contains the registered sources as values with a user defined key
    dataset_template : EpdDataset
        A subclass of EpdDataset itself (not an instance) that serves as a template for creating instances of the given
        class to load the indicator data of an EPD dataset into the data array of the class instance.
    _fetched_datasets : dict
        Caches the data array and name of an already loaded dataset with its epd_id as key.

    """

    def __init__(self, dataset_template):
        """Initializes the EpdDataManager with an EpdDataset template.

        Parameters
        ----------
        dataset_template : EpdDataset
            Usually assigned automatically when instantiating a study class instance with a dataset_template to defines
            the standard for the study.
        """
        self.sources = {}
        self.dataset_template = dataset_template

        self._fetched_datasets = {}

    def register_source(self, source_key, source):
        """Registers a source instance into the sources dictionary with a given key and calls its load() method."""
        self.sources[source_key] = source
        self.sources[source_key].load(self.dataset_template)

    def load_epd(self, epd_id, scenario=None, epd_dataset=None, source_key=None):
        """Either loads a dataset from the cached datasets or calls the method of one of the EPD sources in the
        sources dictionary to load the environmental indicator data into an EpdDataset instance. If an EPD is loaded
        for the first time, it is saved in the dataset cache dictionary (_fetched_datasets).

        Parameters
        ----------
        epd_id : str
            epd_id of the EPD dataset to be loaded
        scenario : str
            Scenario name to identify the scenario that should be loaded into the dataset object; can be None or nan
        epd_dataset : EpdDataset
            Instance of EpdDataset. If None, then an instance is created using the associated method and
            dataset_template attribute.
        source_key : str
            If specified (and found in sources) uses the source indicated by the source_key to load the EPD data from.
            If no source_key is given, it searches the sources for a source that contains a dataset with the given
            epd_id.

        Returns
        ----------
        epd_dataset : EpdDataset
            The returned dataset is filled with data and information of the EPD indicated by the epd_id.

        Raises
        ------
        ValueError :
            When a source_key is given, which is not present in the sources dictionary.
        Exception :
            A dataset for the given epd_id could not be found/loaded from a source present in the sources dictionary.
        """
        epd_dataset = epd_dataset or self._create_dataset_object()

        if (epd_id, scenario) in self._fetched_datasets:
            self._load_from_cache(epd_id, epd_dataset, scenario)
            return epd_dataset

        if source_key and source_key not in self.sources:
            raise ValueError(f"No data source found with source key '{source_key}'")

        if source_key is None:
            for sk, db in self.sources.items():
                try:
                    if db.contains_dataset(epd_id):
                        source_key = sk
                        self.sources[source_key].load_epd(epd_dataset, epd_id, scenario)
                        break
                    else:
                        continue
                except NotImplementedError:
                    # API sources like the soda4LCA API nodes do not allow the search for a dataset by UUID/epd_id, so
                    # it tries to load the dataset directly, raising an error, if it is not present in the API source
                    source_key = sk
                    self.sources[source_key].load_epd(epd_dataset, epd_id, scenario)
                    break

            if source_key is None:
                raise Exception(f"No dataset for epd_id '{epd_id}' found in database(s): {self.sources.keys()}")

        epd_dataset.history.add_data_source(epd_id, epd_dataset.name, source_key)

        self._cache_dataset_content(epd_id, epd_dataset, scenario)

        return epd_dataset

    def _create_dataset_object(self):
        """Returns an instance of the dataset_template."""
        return self.dataset_template()

    def _cache_dataset_content(self, epd_id, epd_dataset, scenario):
        """Saves the content from the epd_dataset to the _fetched_datasets dictionary with the epd_id as key."""
        self._fetched_datasets[(epd_id, scenario)] = {
            "name": epd_dataset.name,
            "scenario": epd_dataset.scenario,
            "data": epd_dataset.data.copy(),
            "initial_source": epd_dataset.history.initial_source
        }

    def _load_from_cache(self, epd_id, epd_dataset, scenario):
        """Assigns name and data of an already loaded dataset from the dictionary that caches already loaded datasets
        to another instance."""
        epd_dataset.name = self._fetched_datasets[(epd_id, scenario)].get("name")
        epd_dataset.scenario = self._fetched_datasets[(epd_id, scenario)].get("scenario")
        epd_dataset.data = self._fetched_datasets[(epd_id, scenario)].get("data").copy()
        epd_dataset.history.add_data_source(
            epd_id,
            epd_dataset.name,
            self._fetched_datasets[(epd_id, scenario)].get("initial_source")
        )
