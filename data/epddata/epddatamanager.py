class EpdDataManager(object):

    def __init__(self):
        self.databases = {}

    def register_source(self, source_key, source):
        self.databases[source_key] = source
        self.databases[source_key].load()

    def load_epd(self, epd_dataset, epd_id, source_key = None, standard = None):
        if source_key in self.databases:
            return self.databases[source_key].load_epd(epd_dataset, epd_id)
        if source_key is None:
            for sk in self.databases:
                try:
                    ds = self.databases[sk].load_epd(epd_dataset, epd_id)
                except:
                    raise ValueError(f"No EPD with ID {epd_id} found!")

                return ds
        else:
            raise ValueError(f"No data source found with source key '{source_key}'")

