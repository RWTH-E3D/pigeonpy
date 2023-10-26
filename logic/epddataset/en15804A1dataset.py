from epddataset import EPDDataset
import numpy as np

class En15804A1Dataset(EpdDataset):
    environmental_indicators = []
    life_cycle_stages = None
    def __init__(self, environmental_indicator = None, life_cycle_stages = None):

        self._environmental_indicators = []
        self._life_cycle_stages = []
        self._data = np.empty(24,18)