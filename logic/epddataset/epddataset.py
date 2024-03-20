import numpy as np
from data.dataclass import DataClass
from logic.environmentalindicator.environmentalindicator import EnvironmentalIndicator
from logic.lifecyclestage.lifecyclestage import LifeCycleStage
import data.output.lca_data_output as lca_data_output

class EpdDataset(object):
    """Abstract class for basic attributes and Epd dataset metadata

    Contains dunder methods for basic calculations of datasets and representing the data

    Class variables
    ----------
    environmental_indicators : list
        Empty list for environmental indicators
    life_cycle_stages : list
        Empty list for life cycle stages

    Attributes
    ----------
    epd_data_id : -
        lca id for the contained dataset
    _name : -
        Name of the contained dataset
    ref_flow_value : -
        Value of the reference flow
    ref_flow_unit : -
        Unit of the reference flow
    used_standard : -
        Information about the used standard
    _data : -
        matrix to hold the numerical values of a dataset

    """
    environmental_indicators = None
    life_cycle_stages = None

    def __init__(self):
        self.epd_data_id = None
        self._name = None
        self.ref_flow_value = None
        self.ref_flow_unit = None

        self.used_standard = None
        self._data = None

    def __str__(self):
        """Dunder method for a readable representation of a dataset and its data matrix"""

        row_labels = [indicators.abbreviation for indicators in self.environmental_indicators]
        col_labels = [stages.abbreviation for stages in self.life_cycle_stages]
        data_to_print = np.round(self._data, 4)
        print(f"\nUsed standard: {self.used_standard}")
        if self._name is not None:
            print(f"Dataset for '{self._name}':")
        else:
            print("Processed dataset")
        return f'{self.print__data(data_to_print, row_labels=row_labels, col_labels=col_labels)}'

    def __mul__(self, other):
        """Method to multiply the dataset with another dataset or a scalar.

        Parameters
        ----------
        other: the object to be multiplied

        Returns
        -------
        result_epd: EpdDataset (instance of self type)
            dataset multiplied with other dataset or scalar
        """
        try:
            if isinstance(other, EpdDataset):
                new_data = self._data * other._data
            else:
                new_data = self._data * other

            result_epd = type(self)()
            result_epd._data = new_data
            return result_epd

        except TypeError as Error:
            raise TypeError(f"Error when multiplying something to dataset {self._name}. {Error}")
        except ValueError as Error:
            raise ValueError(f"Error when multiplying something to dataset {self._name}. {Error}")

    def __add__(self, other):
        """Method to add two EpdDataset-objects

        Parameters
        ----------
        other: EpdDataset
            other EpdDataset to be added

        Returns
        -------
        result_epd: EpdDataset (instance of self type)
            sum of self and other EpdDataset-object
        """
        try:
            # __add__ Methode nur für das Addieren zweier data Matrizen von EpdDataset Objekten und nichts anderes?
            # --> Durch if statement wird verhindert, dass Error ausgelöst wird
            # if isinstance(other, EpdDataset):
            new_data = self._data + other._data
            result_epd = type(self)()
            result_epd._data = new_data
            return result_epd

        except AttributeError as Error:
            raise AttributeError(f"Error when adding something to the dataset {self._name}. {Error}")
        except ValueError as Error:
            raise ValueError(f"Error when adding something to the dataset {self._name}. {Error}")

    def __sub__(self, other):
        """Method to subtract other EpdDataset from self

        Parameters
        ----------
        other: EpdDataset
            other EpdDataset to be subtracted

        Returns
        -------
        result_epd: EpdDataset (instance of self type)
            Difference of self and other EpdDataset-object
        """
        try:
            # siehe __add__ Methode
            # if isinstance(other, EpdDataset):
            new_data = self._data - other._data
            result_epd = type(self)()
            result_epd._data = new_data
            return result_epd

        except AttributeError as Error:
            raise AttributeError(f"Error when subtracting something from the dataset {self._name}. {Error}")
        except ValueError as Error:
            raise ValueError(f"Error when subtracting something from the dataset {self._name}. {Error}")

    def __truediv__(self, other):
        """ Function to divide a dataset by a scalar

        Parameters
        ----------
        other : Scalar the dataset is divided with

        Returns
        -------
        result_epd: EpdDataset (instance of self type)
            dataset divided by scalar
        """
        np.seterr(divide = 'raise')
        try:
            new_data = self._data / other
            result_epd = type(self)()
            result_epd._data = new_data
            np.seterr(divide='ignore')
            return result_epd

        except FloatingPointError as Error:
            raise FloatingPointError(f"Error when dividing the dataset {self._name} with something. {Error}")
        except TypeError as Error:
            raise TypeError(f"Error when dividing the dataset {self._name} with something. {Error}")
        except ValueError as Error:
            raise ValueError(f"Error when dividing the dataset {self._name} with something. {Error}")



    def set_indicators_and_stages(self):
        """Class method to set the class variables for environmental indicators and life cycle stages the first time
        the class is loaded"""

        tmp_dataclass = DataClass(used_standard=self.used_standard)

        for indicator in tmp_dataclass.indicators_bind:
            new_indicator = EnvironmentalIndicator(abbreviation=indicator["abbreviation"], name=indicator["name"],
                                                   unit=indicator["unit"], description=indicator["description"])
            self.environmental_indicators.append(new_indicator)

        for stage in tmp_dataclass.life_cycle_stages_bind:
            new_stage = LifeCycleStage(abbreviation=stage["abbreviation"], name=stage["name"],
                                       description=stage["description"])
            self.life_cycle_stages.append(new_stage)

        del tmp_dataclass

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

    def export(self, path=None ,file_format="csv", drop_rows=False, add_uuid=False):
        if file_format == "teco_json":
            lca_data_output.export_single_dataset_to_json(self, path)
        else:
            lca_data_output.export_single_dataset_to_csv(self, path, drop_rows=drop_rows, add_uuid=add_uuid)

    def get(self, abr_indicator, abr_life_cycle_stage):
        id_indicator = self._get_index_indicator(abr_indicator)
        id_life_cycle_stage = self._get_index_life_cycle_stage(abr_life_cycle_stage)
        return self._data[id_indicator,id_life_cycle_stage]

    def get_indicator(self, abr_indicator):
        id_indicator = self._get_index_indicator(abr_indicator)
        return self._data[id_indicator, :]

    def get_sum(self, abr_indicator, excluded_stages = None):

        excluded_value = 0

        if excluded_stages is not None:
            for stage in excluded_stages:
                excluded_value += self.get(abr_indicator, stage)

        return self.get_indicator(abr_indicator).sum() - excluded_value

    def _get_index_life_cycle_stage(self, abr_life_cycle_stage):
        for index, life_cycle_stage in enumerate(self.life_cycle_stages):
            if life_cycle_stage.abbreviation == abr_life_cycle_stage:
                return index
        raise KeyError(f"There is no life cycle stage {abr_life_cycle_stage}")




    def _get_index_indicator(self, abr_indicator):
        for index, indicator in enumerate(self.environmental_indicators):
            if indicator.abbreviation == abr_indicator:
                return index
        raise KeyError(f"There is no indicator {abr_indicator}")

    @staticmethod
    def format__1(digits, num):
        if digits < len(str(num)):
            # raise Exception("digits<len(str(num))")
            print(f"Values < column or row labels. Data matrix of dataset may be empty.")
        return ' ' * (digits - len(str(num))) + str(num)