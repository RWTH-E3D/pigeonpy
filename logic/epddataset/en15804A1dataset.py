from logic.epddataset.epddataset import EpdDataset
from data.dataclass import DataClass
import data.input.lca_dataset_input as lca_dataset_input
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
    _name : str
        Name of the contained dataset
    ref_flow_value : float
        Value of the reference flow
    ref_flow_unit : str
        Unit of the reference flow
    used_standard : str
        Information about the used standard
    _data : ndarray
        Numpy array containing the values for the environmental indicators in the order given by the json files
        for the life cycle stages and indicators

    """
    environmental_indicators = []
    life_cycle_stages = []
    stages_and_indicators_loaded = False

    def __init__(self):

        super().__init__()
        self._data = np.full((25, 18), 0.0)
        self.used_standard = "A1"
        if not En15804A1Dataset.stages_and_indicators_loaded:
            EpdDataset.set_indicators_and_stages(self)
            En15804A1Dataset.stages_and_indicators_loaded = True


    def load_lca_dataset(self, given_lca_id, data_class=None):
        """Method that calls the functions to load a dataset from the file binding into the instance dependent
        on the passed file format inside the DataClass instance

        Parameters
        ----------
        given_lca_id : str
            String with LCA id for the dataset to be loaded
        data_class : DataClass
            Instance of DataClass with file and data bindings

        """
        if data_class is None:
            data_class = DataClass(used_standard="A1", file_format="teco_json")

        if data_class.file_format == "teco_json":
            lca_dataset_input.load_lca_dataset_json(self, given_lca_id, data_class)
        elif data_class.file_format == "csv":
            lca_dataset_input.load_lca_dataset_csv(self, given_lca_id, data_class)
        else:
            print(f"Given input file format '{data_class.file_format}' for given id '{given_lca_id}' not available."
                  f"\nAvailable input formats: 'teco_json', 'csv'")

