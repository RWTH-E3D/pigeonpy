from epd.epddataset.epddataset import EpdDataset
from data.epddata.epddatamanager import EpdDataManager
import numpy as np


class En15804A2Dataset(EpdDataset):
    """Class that contains information for a Dataset according to standard EN 15804+A2 and inherits from EpdDataset
    class.

    The class always contains the environmental_indicators and life_cycle_stages lists associated to the EN15804+A2
    standard. The lists contain instances of the EnvironmentalIndicator and LifeCycleStage classes, which in turn
    contain the indicators and stages specified in the associated JSON files in input/inputdata/. When creating a study
    instance, the desired indicators and stages can be narrowed down by passing lists of the desired indicators and/or
    stages.

    Class variables
    ----------
    environmental_indicators : list
        A list containing the environmental indicators as instances of the EnvironmentalIndicator class taken from the
        EpdAttributeLoader
    life_cycle_stages : list
        A list containing the life cycle stages as instances of the LifeCycleStage class taken from the
        EpdAttributeLoader
    standard : str
        Specifies the standard of this class -> EN15804+A2

    Attributes
    ----------
    epd_id : str
        epd_id of the contained dataset
    name : str
        Name of the dataset
    ref_flow_value : float
        Value of the reference flow
    ref_flow_unit : str
        Unit of the reference flow
    data : ndarray
        Numpy array containing the values for the environmental indicators in the order defined by the json files
        for the life cycle stages and environmental indicators

    """
    environmental_indicators = EpdDataset.epd_attribute_loader.indicators_a2
    life_cycle_stages = EpdDataset.epd_attribute_loader.life_cycle_stages
    standard = "EN15804+A2"

    def __init__(self):
        """Initializes the data attribute by considering the amount of indicators and stages present in the respective
        class variables for the case of using a fraction of the original indicators and stages."""
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


