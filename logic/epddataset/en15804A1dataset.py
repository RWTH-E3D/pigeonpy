from epddataset import EPDDataset
class En15804A1Dataset(EpdDataset):
    environmental_indicators = []
    life_cycle_stages = None
    def __init__(self):

        self._environmental_indicators = []
        self._life_cycle_stages = []
        self._data = None