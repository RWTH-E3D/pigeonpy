from logic.epddataset.epddataset import EpdDataset
from data.epddata.epddatamanager import EpdDataManager
import numpy as np


class En15804A1Dataset(EpdDataset):
    """Class that contains information for a Dataset according to standard EN 15804+A1 and inherits from EpdDataset
    class

    Class variables
    ----------
    environmental_indicators : list
        A list containing the environmental indicators as instances of the EnvironmentalIndicator class
    life_cycle_stages : list
        A list containing the life cycle stages as instances of the LifeCycleStage class
    stages_and_indicators_loaded : boolean
        States whether the indicators and stages are already loaded, changes the first time the class is loaded to True

    Attributes
    ----------
    epd_data_id : str
        lca id for the contained dataset
    name : str
        Name of the contained dataset
    ref_flow_value : float
        Value of the reference flow
    ref_flow_unit : str
        Unit of the reference flow
    standard : str
        Information about the used standard
    data : ndarray
        Numpy array containing the values for the environmental indicators in the order given by the json files
        for the life cycle stages and indicators

    """
    environmental_indicators = EpdDataset.epd_attribute_loader.indicators_a1
    life_cycle_stages = EpdDataset.epd_attribute_loader.life_cycle_stages

    def __init__(self):

        super().__init__()
        self.data = np.full((25, 18), 0.0)
        self.standard = "EN15804+A1"

    def load_lca_dataset(self, epd_id, epd_data_manager, source_key = None):
        """Method that calls the functions to load a dataset from the file binding into the instance dependent
        on the passed file format inside the DataClass instance

        Parameters
        ----------
        epd_id : str
            String with LCA id for the dataset to be loaded
        data_class : DataClass
            Instance of DataClass with file and data bindings

        """
        epd_data_manager.load_epd(epd_id, epd_dataset=self, source_key=source_key)
