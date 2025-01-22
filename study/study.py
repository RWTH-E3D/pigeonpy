from data.epddata.epddatamanager import EpdDataManager
from data.epdattributeloader import EpdAttributeLoader
from study.lcia.lcia import Lcia
from epd.epddataset.en15804A2dataset import En15804A2Dataset


class Study(object):
    def __init__(
            self,
            study_name,
            observation_period,
            environmental_indicators=None,
            life_cycle_stages=None,
            dataset_template=En15804A2Dataset):

        self.study_name = study_name
        self.observation_period = observation_period
        self.dataset_template = dataset_template

        if environmental_indicators or life_cycle_stages:
            self._customize_dataset_template(environmental_indicators, life_cycle_stages)

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

    def _customize_dataset_template(self, indicators, stages):
        attribute_loader = EpdAttributeLoader(indicators, stages, self.dataset_template)
        self.dataset_template.epd_attribute_loader = attribute_loader