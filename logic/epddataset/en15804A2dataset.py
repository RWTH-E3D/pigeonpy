from logic.epddataset.epddataset import EpdDataset
from data.epddata.epddatamanager import EpdDataManager
import numpy as np


class En15804A2Dataset(EpdDataset):
    """Class that contains information for a Dataset according to standard EN 15804+A2 and inherits from EpdDataset
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
    environmental_indicators = EpdDataset.epd_attribute_loader.indicators_a2
    life_cycle_stages = EpdDataset.epd_attribute_loader.life_cycle_stages
    standard = "EN15804+A2"

    def __init__(self):

        super().__init__()
        self.data = np.full((len(self.environmental_indicators),len(self.life_cycle_stages)), 0.0)

    def load_lca_dataset(self, epd_id, epd_data_manager, source_key = None):
        """Method that calls the functions to load a dataset from the file binding into the instance dependent
        on the passed file format inside the DataClass instance

        Parameters
        ----------
        epd_id : str
            String with LCA id for the dataset to be loaded
        epd_data_manager : EpdDataManager
            Instance of EpdDataManager containing the different epd sources
        source_key : str
            If given, the EpdDataManager loads the epd from the source, specified by the source_key
        """
        epd_data_manager.load_epd(epd_id, epd_dataset=self, source_key=source_key)

    def dimensionless_template(name, dataset_template):
        """Method to create a template for a dataset class with dimensionless environmental indicators inheriting from
        this class. The created template is used for normalization or weighting methods that result in dimensionless
        data due to their calculation

        Parameters
        ----------
        name : str
            Specifies the name for the newly created class
        dataset_template : En15804A2Dataset
            Serves as template and parent for the newly created class

        Returns
        ----------
        dimensionless_dataset_template : type
            Template to create new classes based on En15804A2Datasets that don't have a unit for the environmental
            indicators and take a data_array as argument in its constructor

        """

        updated_class_dict = (dict(dataset_template.__dict__))

        def __init__(self, data_array=None):
            super().__init__()
            self.data = data_array
            self.standard = "EN15804+A2" + f"_{name}"

        updated_class_dict.update({
            'environmental_indicators': dataset_template.epd_attribute_loader.indicators_a2_dimensionless,
            '__init__': __init__
            }
        )
        dimensionless_dataset_template = type(
            name, (dataset_template,), updated_class_dict
        )
        return dimensionless_dataset_template
