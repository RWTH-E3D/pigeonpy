from logic.epddataset.epddataset import EpdDataset
from data.dataclass import DataClass
from logic.environmentalindicator.environmentalindicator import EnvironmentalIndicator
from logic.lifecyclestage.lifecyclestage import LifeCycleStage
import data.input.lca_dataset_input as lca_dataset_input
import numpy as np


class En15804A1Dataset(EpdDataset):
    """Class that contains information for a Dataset according to standard EN 15804+A1 and inherits from EpdDataset
    class.

    Contains methods to load and represent datasets

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

    @classmethod
    def set_indicators_and_stages(cls):
        """Class method to set the class variables for environmental indicators and life cycle stages the first time
        the class is loaded"""
        tmp_dataclass = DataClass()

        for indicator in tmp_dataclass.indicators_bind:
            new_indicator = EnvironmentalIndicator(abbreviation=indicator["abbreviation"], name=indicator["name"],
                                                   unit=indicator["unit"], description=indicator["description"])
            cls.environmental_indicators.append(new_indicator)

        for stage in tmp_dataclass.life_cycle_stages_bind:
            new_stage = LifeCycleStage(abbreviation=stage["abbreviation"], name=stage["name"],
                                       description=stage["description"])
            cls.life_cycle_stages.append(new_stage)

        cls.stages_and_indicators_loaded = True
        del tmp_dataclass

    def __init__(self):

        super().__init__()
        self._data = np.full((25, 18), 0.0)
        self.used_standard = "En15804+A1"
        if not self.stages_and_indicators_loaded:
            En15804A1Dataset.set_indicators_and_stages()

    def __str__(self):
        """Dunder method for a readable representation of a dataset and its _data matrix"""

        row_labels = [indicators.abbreviation for indicators in self.environmental_indicators]
        col_labels = [stages.abbreviation for stages in self.life_cycle_stages]
        data_to_print = np.round(self._data, 4)
        print(f"\nUsed standard: {self.used_standard}")
        if self._name is not None:
            print(f"Dataset for '{self._name}':")
        else:
            print("Processed dataset")
        return f'{self.print__data(data_to_print, row_labels=row_labels, col_labels=col_labels)}'

    def load_lca_dataset(self, given_lca_id, data_class):
        """Method that calls the functions to load a dataset from the file binding into the instance dependent
        on the passed file format inside the DataClass instance

        Parameters
        ----------
        given_lca_id : str
            String with LCA id for the dataset to be loaded
        data_class : DataClass
            Instance of DataClass with file and data bindings

        """
        if data_class.file_format == "teco_json":
            lca_dataset_input.load_lca_dataset_json(self, given_lca_id, data_class)
        elif data_class.file_format == "csv":
            lca_dataset_input.load_lca_dataset_csv(self, given_lca_id, data_class)
        else:
            print(f"Given input file format '{data_class.file_format}' for given id '{given_lca_id}' not available."
                  f"\nAvailable input formats: 'teco_json', 'csv'")

    # Test: methods to print the class in a representative way (could be moved to another module)
    def print__data(self, arr, row_labels=None, col_labels=None):
        """Method that prints the _data array together with the life cycle stages from the class variable
         as columns and the environmental indicators as rows in a readable way

        Parameters
        ----------
        arr : ndarray
            Passed numpy array to be printed inside the matrix
        row_labels : list
            A list of the abbreviations for the environmental indicators
        col_labels : list
            A list of the abbreviations for the life cycle stages

        Returns
        ----------
        readable_data_string : str
            _data Matrix in string form to be printed by the __str__ dunder method of the class

        """

        max_chars = max([len(str(item)) for item in arr.flatten()])  # char number required to display any item in list
        rw = max([len(str(item)) for item in row_labels])
        readable_data_string = str('%s %s' % (' ' * (rw + 1), ' '.join(self.format__1(max_chars, i) for i in col_labels)))
        for row_label, row in zip(row_labels, arr):
            readable_data_string += "\n"
            readable_data_string += str('%s [%s]' % (self.format__1(rw, row_label), ' '.join(self.format__1(max_chars, i) for i in row)))
        return readable_data_string

    @staticmethod
    def format__1(digits, num):
        if digits < len(str(num)):
            raise Exception("digits<len(str(num))")
        return ' ' * (digits - len(str(num))) + str(num)
