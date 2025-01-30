class EpdDataManager(object):

    def __init__(self, dataset_template):
        self.databases = {}
        self.dataset_template = dataset_template

        self._fetched_datasets = {}

    def register_source(self, source_key, source):
        self.databases[source_key] = source
        self.databases[source_key].load(self.dataset_template)

    def load_epd(self, epd_id, epd_dataset=None, source_key=None):
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
        return self.dataset_template()

    def _load_from_cache(self, epd_id, epd_dataset):
        epd_dataset.name = self._fetched_datasets[epd_id].get("name")
        epd_dataset.data = self._fetched_datasets[epd_id].get("data").copy()
