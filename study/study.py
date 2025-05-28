from data.epddata.epddatamanager import EpdDataManager
from data.epdattributeloader import EpdAttributeLoader
from study.lcia.lcia import Lcia
from epd.epddataset.epddataset import EpdDataset
from epd.epddataset.en15804A2dataset import En15804A2Dataset


class Study(object):
    """Class for managing the LCIA calculations.

    Used as interface for loading the CSV input file, registering EPD sources via the epd_datamanager, conducting the
    LCIA based normalization and weighting as well as defining the parameters for the study like the observation period
    or the selection of environmental indicators and life cycle stages that are to be considered.

    Attributes
    ----------
    study_name : str
        Given name for the study.
    observation period : int
        The observation period for the study used for calculating component replacements based on their service life if
        given.
    dataset_template : EpdDataset
        Subclass of EpdDataset (not an instance) that serves as a template for creating instances and extract standard
        based metadata, e.g. the indicators and life cycle stages for EN15804+A2.
    lcia : Lcia
        Instance of Lcia class that contains the results of the calculations.
    epd_datamanager : EpdDataManager
        Instance of EpdDataManager that stores the registered EPD sources and already loaded/ cached datasets.

    Parameters
    ----------
    study_name : str
        Can be chosen arbitrarily.
    observation_period : int
        Period in years used as time frame for the calculation of component replacements
    environmental_indicators : list
        A list of abbreviations for the environmental indicators which, if specified, define the indicators used in the
        study. Defaults to None
    life_cycle_stages : list
        A list of abbreviations for the life cycle stages which, if specified, define the life cycle stages used in the
        study. Defaults to None
    dataset_template : type[EpdDataset()]
        Subclass of EpdDataset (not an instance/ no parentheses). Defaults to En15804A2Dataset which then serves as the standard for the
        study.
    """
    def __init__(
            self,
            study_name,
            observation_period,
            environmental_indicators=None,
            life_cycle_stages=None,
            dataset_template=En15804A2Dataset):

        self.study_name = study_name
        self.observation_period = observation_period

        if isinstance(dataset_template, EpdDataset):
            raise Exception("dataset_template must be the class itself, not an instance, i.e. type(EpdDataset()).")
        self.dataset_template = dataset_template

        if environmental_indicators or life_cycle_stages:
            self._customize_dataset_template(environmental_indicators, life_cycle_stages)

        self.lcia = Lcia(self.dataset_template)
        self.epd_datamanager = EpdDataManager(self.dataset_template)

    def run_calculation(self, *partitions):
        """Starts the calculation process based on the partitions given as the argument."""
        self.lcia.run(
            *partitions,
            epd_datamanager=self.epd_datamanager,
            observation_period=self.observation_period
        )

    def load_calculation_input(self, filepath):
        """Loads the input CSV file based on the filepath"""
        self.lcia.load_input(filepath)

    def _customize_dataset_template(self, indicators, stages):
        """If environmental_indicators or life_cycle_stages are given during initialization of the study this method
        alters the dataset_template so it only contains the desired indicators and life cycle stages."""
        attribute_loader = EpdAttributeLoader(indicators, stages, self.dataset_template)
        self.dataset_template.epd_attribute_loader = attribute_loader