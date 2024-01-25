

class EpdDataset(object):
    """Abstract class for basic attributes and Epd dataset metadata as well as basic calculation dunder
    methods for easy calculations of datasets

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
            if isinstance(other, EpdDataset):
                new_data = self._data + other._data
                result_epd = type(self)()
                result_epd._data = new_data
                return result_epd

        except TypeError as Error:
            raise TypeError(f"Error when adding something to the dataset {self._name}. {Error}")
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
            if isinstance(other, EpdDataset):
                new_data = self._data - other._data
                result_epd = type(self)()
                result_epd._data = new_data
                return result_epd

        except TypeError as Error:
            raise TypeError(f"Error when subtracting something from the dataset {self._name}. {Error}")
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
        try:
            new_data = self._data / other
            result_epd = type(self)()
            result_epd._data = new_data
            return result_epd

        except TypeError as Error:
            raise TypeError(f"Error when dividing the dataset {self._name} with something. {Error}")
        except ValueError as Error:
            raise ValueError(f"Error when dividing the dataset {self._name} with something. {Error}")

