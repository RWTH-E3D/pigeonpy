class EpdDataManager(object):

    def __init__(self, dataset_template):
        self.databases = {}
        self.dataset_template = dataset_template

    def register_source(self, source_key, source):
        self.databases[source_key] = source
        self.databases[source_key].load(self.dataset_template)

    def load_epd(self, epd_id, epd_dataset=None, source_key=None):
        if source_key is None:
            for sk, database in self.databases.items():
                if database.contains_dataset(epd_id):
                    source_key = sk
                    break
            else:
                raise Exception(f"No dataset for epd_id '{epd_id}' found in database(s): {self.databases.keys()}")

        if epd_dataset is None:
            epd_dataset = self._create_dataset_object()

        if source_key in self.databases:
            self.databases[source_key].load_epd(epd_dataset, epd_id)
            epd_dataset.history.add_data_source(epd_id, epd_dataset.name, source_key)
            return epd_dataset
        else:
            raise ValueError(f"No data source found with source key '{source_key}'")

    def _create_dataset_object(self):
        return self.dataset_template()
