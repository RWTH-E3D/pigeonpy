class EpdDataManager(object):

    def __init__(self):
        self.databases = {}
        self._selected_source = None

    def register_source(self, source_key, source):
        self.databases[source_key] = source
        self.databases[source_key].load()
        self._selected_source = source

    def set_source(self, source_key):
        if source_key in self.databases:
            self._selected_source = self.databases[source_key]
        else:
            raise ValueError(f"No source with source key {source_key} found!")

    def load_epd(self, epd_id, epd_dataset=None, source_key = None, standard = None):
        if epd_dataset is None:
            epd_dataset = self._create_dataset_object(source_key = source_key)
        if source_key in self.databases:
            self.databases[source_key].load_epd(epd_dataset, epd_id)
            return epd_dataset
        if source_key is None:
            for sk in self.databases:
                try:
                    self.databases[sk].load_epd(epd_dataset, epd_id)
                except:
                    raise ValueError(f"No EPD with ID {epd_id} found!")

                return epd_dataset
        else:
            raise ValueError(f"No data source found with source key '{source_key}'")

    def _create_dataset_object(self, source_key=None):
        if source_key:
            return type(self.databases[source_key].template_dataset)()
        else:
            return type(self._selected_source.template_dataset)()
