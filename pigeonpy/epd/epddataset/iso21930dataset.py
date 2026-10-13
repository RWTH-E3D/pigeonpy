"""Provides a subclass for holding EPD datasets conform with the standard ISO 21930."""

from pigeonpy.epd.epddataset.epddataset import EpdDataset
from pigeonpy.data.epddata.epddatamanager import EpdDataManager
import numpy as np


class Iso21930Dataset(EpdDataset):
    """Class that contains information for a Dataset according to international standard ISO 21930.

    See EpdDataset class for inherited attributes and methods.

    The class always contains the environmental_indicators and life_cycle_stages lists associated to the ISO 21930
    standard. The lists contain instances of the EnvironmentalIndicator and LifeCycleStage classes, which in turn
    contain the indicators and stages specified in the associated JSON files in input/inputdata/. When creating a study
    instance, the desired indicators and stages can be narrowed down by passing lists of the desired indicators and/or
    stages.

    Class variables
    ---------------
    environmental_indicators : list
        A list containing the environmental indicators as instances of the EnvironmentalIndicator class taken from the
        EpdAttributeLoader
    life_cycle_stages : list
        A list containing the life cycle stages as instances of the LifeCycleStage class taken from the
        EpdAttributeLoader
    standard : str
        Sets the standard of this class to ISO 21930

    Attributes
    ----------
    data : np.ndarray
        Numpy array containing the values for the environmental indicators in the order defined by the JSON files
        for the life cycle stages and environmental indicators, 'life_cycle_stages_en_15978.json' and
        'indicators_iso_21930.json' respectively.

    """
    environmental_indicators = EpdDataset.epd_attribute_loader.indicators_iso_21930
    life_cycle_stages = EpdDataset.epd_attribute_loader.life_cycle_stages
    standard = "ISO21930"

    def __init__(self):
        """Initializes the data attribute by considering the amount of indicators and stages present in the respective
        class variables for the case of using a fraction of the original indicators and stages.

        The data attribute may also be passed as argument to the constructor.
        """
        super().__init__()
        self.data = np.full((len(self.environmental_indicators),len(self.life_cycle_stages)), 0.0)


    def load_lca_dataset(self, epd_id, epd_data_manager, scenario = None, source_key = None):
        """Calls method from EpdDataManager to load a dataset from a source into the instance.

        Parameters
        ----------
        epd_id : str
            String with LCA id for the dataset to be loaded
        epd_data_manager : EpdDataManager
            Instance of EpdDataManager containing the different epd sources
        scenario : str
            Name of the scenario to be used in the dataset if specified
        source_key : str
            If given, the EpdDataManager loads the epd from the source, specified by the source_key
        """
        epd_data_manager.load_epd(epd_id, scenario=scenario, epd_dataset=self, source_key=source_key)


