import copy

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

    """
    def __init__(
            self,
            study_name,
            observation_period,
            environmental_indicators=None,
            life_cycle_stages=None,
            dataset_template=En15804A2Dataset):
        """Initializes a study instance.

        Each study requires a name and observation period. The environmental indicators and life cycle stages can be
        customized individually by passing lists of the desired indicators and life cycle stages to include in the study.

        Parameters
        ----------
        study_name : str
            Can be chosen arbitrarily.
        observation_period : int
            Period in years used as time frame for the calculation of component replacements
        dataset_template : type(EpdDataset)
            Subclass object of EpdDataset (not an instance of the class, i.e. no parentheses). Defaults to
            En15804A2Dataset which then serves as the standard for the study.
        environmental_indicators : list
            A list of abbreviations for the environmental indicators which, if specified, define the indicators used in the
            study. Defaults to None
        life_cycle_stages : list
            A list of abbreviations for the life cycle stages which, if specified, define the life cycle stages used in the
            study. Defaults to None

        """

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
        """Starts the calculation process based on the partitions given as the argument.

        Parameters
        ----------
        partitions : tuple
            Contains the partitions according to which the calculation is made. Can be a single string, tuple or a
            combination of strings and tuples.
        """
        self.lcia.run(
            *partitions,
            epd_datamanager=self.epd_datamanager,
            observation_period=self.observation_period
        )

    def load_calculation_input(self, filepath, sep=","):
        """Loads the input CSV file based on the filepath.

        Parameters
        ----------
        filepath : str or Path
            Path to the input CSV file.
        sep : str
            Separator used in the input CSV file.
        """
        self.lcia.load_input(filepath, sep=sep)

    def _customize_dataset_template(self, indicators, stages):
        """If environmental_indicators or life_cycle_stages are given during initialization of the study this method
        creates a new subclass of the dataset_template containing only the desired indicators and life cycle stages,
        leaving the original template class unchanged.

        Parameters
        ----------
        indicators : list
            Abbreviations for the desired indicators to use in the study.
        stages : list
            Abbreviations for the desired life cycle stages to use in the study.
        """
        # Create a new subclass to avoid mutating the original template class
        custom_class = type(
            f"{self.dataset_template.__name__}_{self.study_name}",
            (self.dataset_template,),
            {
                "environmental_indicators": copy.deepcopy(self.dataset_template.environmental_indicators),
                "life_cycle_stages": copy.deepcopy(self.dataset_template.life_cycle_stages),
                "standard": self.dataset_template.standard,
            }
        )

        # Let EpdAttributeLoader filter the attributes on the NEW class
        attribute_loader = EpdAttributeLoader(indicators, stages, custom_class)
        custom_class.epd_attribute_loader = attribute_loader

        # Update to use the new custom class
        self.dataset_template = custom_class