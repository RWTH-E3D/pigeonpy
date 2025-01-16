from logic.lcia.lcia import Lcia
from data.epddata.epddatamanager import EpdDataManager
from logic.epddataset.en15804A2dataset import En15804A2Dataset


class Study(object):
    def __init__(self, study_name, observation_period, dataset_template=En15804A2Dataset):

        self.study_name = study_name
        self.observation_period = observation_period
        self.dataset_template = dataset_template
        self.lcia = Lcia(dataset_template)
        self.epd_datamanager = EpdDataManager(dataset_template)

    def run_calculation(self, *categorizations):
        self.lcia.run(
            *categorizations,
            epd_datamanager=self.epd_datamanager,
            observation_period=self.observation_period
        )

    def load_calculation_input(self, filepath):
        self.lcia.load_input(filepath)
