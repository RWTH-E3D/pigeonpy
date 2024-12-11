class EpdSource(object):

    def __init__(self, name):
        self.name = name
        self.standards = None
        self.standard = None
        self.template_dataset = None

    def load_epd(self, epd_dataset, epd_id):
        pass


    def load(self):
        pass

    def contains_dataset(self, epd_id) -> bool:
        pass