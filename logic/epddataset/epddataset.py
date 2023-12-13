import uuid

class EpdDataset(object):
    environmental_indicators = None
    life_cycle_stages = None
    def __init__(self):
        self.epd_data_id = str(uuid.uuid1())
        self._name = None
        self.ref_flow_value = None
        self.ref_flow_unit = None

        self._data = None

    def __mul__(self, other):
        """Function to multiply the dataset.

        Parameters
        ----------
        other: the object to be multiplied

        Returns
        -------
        result dataset

        """
        try:
            if isinstance(other, EpdDataset):
                new_data = self._data * other._data
            else:
                new_data = self._data * other

            result_epd = EpdDataset()
            result_epd._data = new_data

        except TypeError as Error:
            raise TypeError(f"Error when multiplying something to dataset {self._name}. {Error}")
        except ValueError as Error:
            raise ValueError(f"Error when multiplying something to dataset {self._name}. {Error}")

        return result_epd




    def __add__(self, other):
        """Function to add two EpdDataset-objects

        Parameters
        ----------
        other: EpdDataset
            other EpdDataset to be added
        Returns
        -------
        result_epd: EpdDataset
            sum of self and other EpdDataset-object
        """
        try:
            if isinstance(other, EpdDataset):
                new_data = self._data + other._data

                result_epd = EpdDataset()
                result_epd._data = new_data

        except TypeError as Error:
            raise TypeError(f"Error when adding something to the dataset {self._name}. {Error}")
        except ValueError as Error:
            raise ValueError(f"Error when adding something to the dataset {self._name}. {Error}")

        return result_epd

    def __sub__(self, other):
        """Function to subtract other EpdDataset from self

        Parameters
        ----------
        other: EpdDataset
            other EpdDataset to be subtracted
        Returns
        -------
        result_epd: EpdDataset
            Difference of self and other EpdDataset-object
        """
        try:
            
            if isinstance(other, EpdDataset):
                new_data = self._data - other._data

            result_epd = EpdDataset()
            result_epd._data = new_data

        except TypeError as Error:
            raise TypeError(f"Error when subtracting something from the dataset {self._name}. {Error}")
        except ValueError as Error:
            raise ValueError(f"Error when subtracting something from the dataset {self._name}. {Error}")

        return result_epd

    def __truediv__(self, other):
        pass

    def load(self, filepath, filetype):
        pass

    def save(self, filepath, filetype):
        pass

