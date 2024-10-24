class EpdDataManager(object):

    def __init__(self):
        self.databases = {}

    def register_source(self, source_key, source):
        differing_standards = dict((sk, database) for sk, database in self.databases.items() if database.standard
                                   != source.standard)
        if differing_standards:
            print(f"Warning: The standard of your source ({source_key}, {source.standard}) differs "
                  f"from the already existing source(s): ({list(differing_standards.keys())}).\n")
        self.databases[source_key] = source
        self.databases[source_key].load()

    def load_epd(self, epd_id, epd_dataset=None, source_key = None, standard = None):
        if source_key is None:
            for sk, database in self.databases.items():
                if database.contains_dataset(epd_id):
                    source_key = sk
                    break
            else:
                raise Exception(f"No dataset for epd_id '{epd_id}' found in database(s): {self.databases.keys()}")

        if epd_dataset is None:
            epd_dataset = self._create_dataset_object(source_key)

        if source_key in self.databases:
            self.databases[source_key].load_epd(epd_dataset, epd_id)
            epd_dataset.history.add_data_source(epd_id, source_key)
            return epd_dataset
        else:
            raise ValueError(f"No data source found with source key '{source_key}'")

    def _create_dataset_object(self, source_key):
        source = self.databases[source_key]
        return type(source.template_dataset)()
