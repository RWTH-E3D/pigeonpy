import numpy as np
import copy
from data.epdattributeloader import EpdAttributeLoader
import data.output.lca_data_output as lca_data_output


class EpdDataset(object):
    """Class that serves as parent class for all implemented dataset classes/ standards. It defines basic attributes and
    contains methods that are used by all dataset subclasses, including dunder methods for the calculation operations
    with datasets, printing the class (__str__) and a method to create custom dataset_templates during runtime.

    Class variables
    ----------
    environmental_indicators : list
        Empty list for environmental indicators
    life_cycle_stages : list
        Empty list for life cycle stages
    standard : str
        The standard associated with a dataset
    epd_attribute_loader : EpdAttributeLoader
        Responsible for loading the environmental indicators and life cycle stages

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
    data : np.ndarray
        matrix to hold the numerical values of a dataset
    history : History
        Contains a list of logs for the history of the dataset (data source, calculations, etc.)

    Parameters
    ----------
    data : np.ndarray
        Can be used to directly assign the data array to the instance
    name : str
        Set the name of the dataset during instantiation
    """
    environmental_indicators = None
    life_cycle_stages = None
    standard = None
    epd_attribute_loader = EpdAttributeLoader()

    def __init__(self, data=None, name=None):
        self.epd_data_id = None
        self.name = name
        self.ref_flow_value = None
        self.ref_flow_unit = None

        self.data = data
        self.history = History()

    def __str__(self):
        """Dunder method for a readable representation of a dataset and its data matrix"""
        row_labels = [indicators.abbreviation for indicators in self.environmental_indicators]
        col_labels = [stages.abbreviation for stages in self.life_cycle_stages]
        data_to_print = np.round(self.data, 4)
        print(f"\nUsed standard: {self.standard}")
        if self.name is not None:
            print(f"Dataset: '{self.name}':")
        else:
            print("Processed dataset:")
        return f'{self.print__data(data_to_print, row_labels=row_labels, col_labels=col_labels)}'

    def __mul__(self, other):
        """Method to multiply the dataset with another dataset or a scalar.

        Parameters
        ----------
        other: EpdDataset or numeric
            The object to multiply with

        Returns
        -------
        result_epd: EpdDataset
            dataset multiplied with other dataset or scalar
        """
        if not isinstance(other, (EpdDataset, np.ndarray, int, float)):
            raise TypeError(f"Multiplication with type '{type(other).__name__}' is not supported.")

        result_epd = type(self)()  # create new instance of the type of self

        try:
            result_epd.data = self.data * (other.data if isinstance(other, EpdDataset) else other)
        except ValueError as e:
            raise ValueError(f"Multiplication failed for dataset '{self.name}'. Possible shape mismatch. {e}")
        except TypeError as e:
            raise TypeError(f"Error when multiplying data array \n'{other.data}' \nof dataset {other.name} with data "
                            f"array \n{self.data} \nof dataset {self.name}. {e}")

        result_epd.history = self.history

        if isinstance(other, EpdDataset):
            result_epd.history.log_operation("Multiplied with other dataset: ")
            result_epd.history.merge_histories(other_dataset=other)
        else:
            result_epd.history.log_operation(f"Multiplied with factor: {other}")

        return result_epd

    def __add__(self, other):
        """Method to add two EpdDataset objects.

        Parameters
        ----------
        other: EpdDataset
            other EpdDataset to be added

        Returns
        -------
        result_epd: EpdDataset
            sum of self and other EpdDataset object
        """
        if not isinstance(other, EpdDataset):
            raise TypeError(f"Addition with type '{type(other).__name__}' is not supported.")

        result_epd = type(self)()  # Create new instance of self type

        try:
            result_epd.data = self.data + other.data
        except ValueError as e:
            raise ValueError(f"Error when adding dataset '{other.name}' to dataset '{self.name}'. "
                             f"Possible shape mismatch. {e}")
        except TypeError as e:
            raise TypeError(f"Error when adding data array \n'{other.data}' \nof dataset {other.name} to data array"
                            f"\n{self.data} \nof dataset {self.name}. {e}")


        result_epd.history = self.history
        result_epd.history.log_operation("Sum calculated with other dataset: ")
        result_epd.history.merge_histories(other_dataset=other)

        return result_epd

    def __sub__(self, other):
        """Method to subtract other EpdDataset from self

        Parameters
        ----------
        other: EpdDataset
            other EpdDataset to be subtracted

        Returns
        -------
        result_epd: EpdDataset
            Difference of self and other EpdDataset object
        """
        if not isinstance(other, EpdDataset):
            raise TypeError(f"Subtraction with type '{type(other).__name__}' is not supported.")

        result_epd = type(self)()  # Create new instance of self type

        try:
            result_epd.data = self.data - other.data
        except ValueError as e:
            raise ValueError(f"Error when subtracting dataset '{other.name}' from dataset '{self.name}'."
                             f"Possible shape mismatch. {e}")
        except TypeError as e:
            raise TypeError(f"Error when subtracting data array \n'{other.data}' \nof dataset {other.name} from data array"
                            f"\n{self.data} \nof dataset {self.name}. {e}")

        result_epd.history = self.history
        result_epd.history.log_operation("Difference calculated with other dataset: ")
        result_epd.history.merge_histories(other_dataset=other)

        return result_epd

    def __truediv__(self, other):
        """Method to divide a dataset by a scalar or another EpdDataset

        Parameters
        ----------
        other : EpdDataset or numerical
            Divisor for calculation

        Returns
        -------
        result_epd: EpdDataset
            Dataset divided by other
        """
        if not isinstance(other, (EpdDataset, np.ndarray, int, float)):
            raise TypeError(f"Division with type '{type(other).__name__}' is not supported.")

        result_epd = type(self)()  # create new instance of the type of self

        np.seterr(divide='raise')
        divisor = other.data if isinstance(other, EpdDataset) else other
        try:
            result_epd.data = np.divide(self.data, divisor, out=np.zeros_like(self.data), where=divisor != 0.0)
        except ValueError as e:
            raise ValueError(f"Division of dataset '{self.name}' with dataset '{other.name}' failed. "
                             f"Possible shape mismatch. {e}")
        except TypeError as e:
            raise TypeError(f"Error when dividing data array \n'{self.data}' \nof dataset {self.name} with data "
                            f"array \n{other.data} \nof dataset {other.name}. {e}")
        np.seterr(divide='ignore')

        result_epd.history = self.history

        if isinstance(other, EpdDataset):
            result_epd.history.log_operation("Divided by other dataset: ")
            result_epd.history.merge_histories(other_dataset=other)
        else:
            result_epd.history.log_operation(f"Divided by factor: {other}")

        return result_epd

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
            data Matrix in string form to be printed by the __str__ dunder method of the class

        """
        max_chars = max([len(str(item)) for item in arr.flatten()])  # char number required to display any item in list
        rw = max([len(str(item)) for item in row_labels])  # width for the indicator column
        readable_data_string = str(
            '%s %s' % (' ' * (rw + 1), ' '.join(self.format__1(max_chars, i) for i in col_labels)))
        for row_label, row in zip(row_labels, arr):
            readable_data_string += "\n"
            readable_data_string += str(
                '%s [%s]' % (self.format__1(rw, row_label), ' '.join(self.format__1(max_chars, i) for i in row)))
        return readable_data_string

    def export(self, path=None, file_format="teco_json", drop_rows=False, add_uuid=False):
        """Exports the datasets data to either 'teco_json' format or 'csv' format. The drop_rows and add_uuid parameters
        are only relevant for the csv export.

        Parameters
        ----------
        path : str or Path
            The path to where the exported file should be located. Defaults to None
        file_format : str
            Indicates the file format for the export. Defaults to 'teco_json'
        drop_rows : bool
            Determines if rows in the data matrix where all values are equal to zero should be neglected for the export
        add_uuid : bool
            Determines if the uuid is added to the csv in the case of a csv export

        """
        if file_format == "teco_json":
            lca_data_output.export_single_dataset_to_json(self, path)
        elif file_format == "csv":
            lca_data_output.export_single_dataset_to_csv(self, path, drop_rows=drop_rows, add_uuid=add_uuid)

    def get(self, abr_indicator, abr_life_cycle_stage):
        """This function returns the value of an indicator for a specific life cycle stage

        Parameters
        ----------
        abr_indicator: str
            the abbreviation of the requested indicator
        abr_life_cycle_stage: str
            the abbreviation of the requested life cycle stage

        Returns
        -------
        value: float
            the value of the requested indicator for the requested life cycle stage
        """
        id_indicator = self._get_index_indicator(abr_indicator)
        id_life_cycle_stage = self._get_index_life_cycle_stage(abr_life_cycle_stage)
        return self.data[id_indicator, id_life_cycle_stage]

    def get_indicator(self, abr_indicator):
        """This functions returns a vector of all values of the requested indicator, i.e. a row of the data matrix

        Parameters
        ----------
        abr_indicator: str
            the abbreviation of the requested indicator

        Returns
        -------
        value vector: np.ndarray
            vector with every value of the requested indicator row
        """
        id_indicator = self._get_index_indicator(abr_indicator)
        return self.data[id_indicator, :]

    def get_sum(self, abr_indicator, excluded_stages=None):
        """This function sums up all life cycle stages of one indicator to one value, except these given in
        'excluded_stages'

        Parameters
        ----------
        abr_indicator: str
            the abbreviation of the requested indicator
        excluded_stages: list
            Contains abbreviations of the life cycle stages that should not be added up

        Returns
        -------
        sum: float
            sum of all life cycle stages ot the requested indicator, except these given in "excluded_stages"
        """
        excluded_value = 0

        if excluded_stages is not None:
            for stage in excluded_stages:
                excluded_value += self.get(abr_indicator, stage)

        return self.get_indicator(abr_indicator).sum() - excluded_value

    def _get_index_life_cycle_stage(self, abr_life_cycle_stage):
        """Returns the index of the life cycle stage given by abbreviation for the data array."""
        for index, life_cycle_stage in enumerate(self.life_cycle_stages):
            if life_cycle_stage.abbreviation == abr_life_cycle_stage:
                return index
        raise KeyError(f"There is no life cycle stage {abr_life_cycle_stage}")

    def _get_index_indicator(self, abr_indicator):
        """Returns the index of the environmental indicator given by abbreviation for the data array."""
        for index, indicator in enumerate(self.environmental_indicators):
            if indicator.abbreviation == abr_indicator:
                return index
        raise KeyError(f"There is no indicator {abr_indicator}")

    @staticmethod
    def format__1(digits, num):
        """Formats each field of the printed data array, so it has the correct width. Digits parameter gives maximum for
        field width and num is the value to be formatted."""
        if digits < len(str(num)):
            print(f"Values < column or row labels. Data matrix of dataset may be empty.")
        return ' ' * (digits - len(str(num))) + str(num)

    @classmethod
    def dimensionless_template(cls, name, resulting_unit):
        """Method to create a template for a dataset class with dimensionless environmental indicators inheriting from
        this class. The created template is used for normalization or weighting methods that result in dimensionless
        data (or data with special unit given by resulting unit) due to their calculation.

        Parameters
        ----------
        name : str
            Specifies the name for the newly created class
        resulting_unit : str
            Declared unit for the environmental indicators

        Returns
        ----------
        dimensionless_dataset_template : type
            Template to create new classes based on this class that contain a custom unit for the environmental
            indicators.

        """

        updated_class_dict = EpdDataset.__dict__.copy()

        updated_class_dict["environmental_indicators"] = copy.deepcopy(cls.environmental_indicators)
        updated_class_dict["life_cycle_stages"] = copy.deepcopy(cls.life_cycle_stages)

        # Todo: Normalizing with a unit like m^2 would lead to the unit being only m^2 while it should be
        #  "indicator unit / m^2"
        for ei in updated_class_dict["environmental_indicators"]:
            ei.abbreviation = f"{ei.abbreviation}"
            ei.name = f"{ei.name} dimensionless"
            ei.unit = resulting_unit
            ei.description = (f"Original description:\n {ei.description}. "
                              f"This Datasets is dimensionless due to the following method: {name}")

        updated_class_dict["standard"] = f"{cls.standard}_{name}"

        dimensionless_dataset_template = type(
            name, (cls,), updated_class_dict
        )
        return dimensionless_dataset_template


class History:
    def __init__(self):
        self.initial_source = None
        self.initial_name = None
        self.entries = []

    def add_data_source(self, epd_id, epd_name, source_key):
        self.initial_source = source_key
        self.initial_name = epd_name
        self.entries.append(f"Dataset '{epd_name}' ({epd_id}) initialized from source '{source_key}'")

    def log_operation(self, entry, replace_last=False):
        if replace_last:
            self.entries[-1] = entry
        else:
            self.entries.append(entry)

    def merge_histories(self, other_dataset):
        self.entries += other_dataset.history.entries
        # return self.entries + other_dataset.history.entries

    def show_history(self):
        for entry in self.entries:
            print(entry + "\n")

    def get_history(self):
        return self.entries


