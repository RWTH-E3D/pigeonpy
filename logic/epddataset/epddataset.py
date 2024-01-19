import uuid


class EpdDataset(object):
    environmental_indicators = None
    life_cycle_stages = None

    def __init__(self):
        self.epd_data_id = str(uuid.uuid1())
        self._name = None
        self.ref_flow_value = None
        self.ref_flow_unit = None

        self.used_standard = None
        self._data = None

    def __mul__(self, other):
        """Function to multiply the dataset.

        Parameters
        ----------
        other: the object to be multiplied

        Returns
        -------
        result_epd: Instance of self type
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
        """Function to add two EpdDataset-objects

        Parameters
        ----------
        other: EpdDataset
            other EpdDataset to be added

        Returns
        -------
        result_epd: Instance of self type
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
        """Function to subtract other EpdDataset from self

        Parameters
        ----------
        other: EpdDataset
            other EpdDataset to be subtracted

        Returns
        -------
        result_epd: Instance of self type
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
        scalar: scalar which the dataset is divided with

        Returns
        -------
        result_epd: Instance of self type
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

    def load(self, filepath, filetype):
        pass

    def save(self, filepath, filetype):
        pass

