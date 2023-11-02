import uuid

class EpdDataset(object):
    environmental_indicators = None
    life_cycle_stages = None
    def __int__(self):
        self.epd_data_id = str(uuid.uuid1())
        self._name = None
        self.ref_flow_value = None
        self.ref_flow_unit = None

        self._data = None

    def __mul__(self, other):
        pass

    def __add__(self, other):

        if isinstance(other, EpdDataset):
            new = self._data + other._data
            return new
        else:
            print("Addend must be an 'EpdDataset'-object")

    def __sub__(self, other):
        pass

    def __truediv__(self, other):
        pass

    def load(self, filepath, filetype):
        pass

    def save(self, filepath, filetype):
        pass

