from dataclasses import dataclass
from typing import Optional

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
    epd_id : str
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

    def __init__(self, data=None, name=None, history=None):
        self.epd_id = None
        self.name = name
        self.ref_flow_value = None
        self.ref_flow_unit = None
        self.scenario = None

        self.data = data
        self.history = history or History()

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
        return f'{self.create_printable_string_from_data_array(data_to_print, row_labels=row_labels, col_labels=col_labels)}'

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
            raise TypeError(f"Error when multiplying data array \n'{self.data}' \nof dataset {self.name} with multiplier"
                            f"\nname: {other.name if isinstance(other, EpdDataset) else 'scalar'} "
                            f"\n{other.data if isinstance(other, EpdDataset) else other} \n{e}")

        result_epd.history = self.history.create_clone()

        if isinstance(other, EpdDataset):
            result_epd.history.log_mul_other(other)
        else:
            result_epd.history.log_mul_factor(other)

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


        result_epd.history = self.history.create_clone()

        result_epd.history.log_add(other)

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

        result_epd.history = self.history.create_clone()

        result_epd.history.log_sub(other)

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
            raise ValueError(f"Division of dataset '{self.name}' with Divisor '{other}' failed. "
                             f"Possible shape mismatch. {e}")
        except TypeError as e:
            raise TypeError(f"Error when dividing data array \n'{self.data}' \nof dataset {self.name} with Divisor "
                            f"\nname: {other.name if isinstance(other, EpdDataset) else 'scalar'} "
                            f"\n{other.data if isinstance(other, EpdDataset) else other} \n{e}")
        np.seterr(divide='ignore')

        result_epd.history = self.history.create_clone()

        if isinstance(other, EpdDataset):
            result_epd.history.log_truediv_other(other)
        else:
            result_epd.history.log_truediv_divisor(other)

        return result_epd

    def create_printable_string_from_data_array(self, arr, row_labels=None, col_labels=None):
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
        fmt = self._format_data_array_element_for_printing

        max_chars = max(len(str(item)) for item in arr.flatten()) # char number required to display any item in list
        rw = max(len(str(item)) for item in row_labels) # width for the indicator column

        lines = []

        header = (
                " " * (rw + 1)
                + " ".join(fmt(max_chars, label) for label in col_labels)
        )
        lines.append(header)

        for row_label, row in zip(row_labels, arr):
            row_label_str = fmt(rw, row_label)
            row_values_str = " ".join(fmt(max_chars, val) for val in row)
            lines.append(f"{row_label_str} [{row_values_str}]")

        return "\n".join(lines)

    def show_history(self, summary=True):
        """Shortcut for displaying the history/logs of the epd dataset by calling the associated method in History
        class.

        Parameters
        ----------
        summary : bool
            Determines the level of detail. If True, the entries in History are summarized and if not, every entry is
            printed
        """
        print(f"History for dataset '{self.name}': ")
        self.history.show_history(summary=summary)

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

    def get_sum(self, abr_indicator=None, excluded_stages=None):
        """This method sums up the indicator values over the life cycle stages. If the abr_indicator argument is
        specified, only the sum for this indicator is returned and if nothing is specified, a vector containing the sums
        for every indicator available is returned. With the excluded_stages argument, one can define a list with
        life cycle stages that should not be included in the calculation of the sum(s).

        Parameters
        ----------
        abr_indicator: str
            The abbreviation of the requested indicator. If None, all indicators are summed up.
        excluded_stages: list
            Contains abbreviations of the life cycle stages that should not be summed up

        Returns
        -------
        sum: float or np.ndarray
            sum of all life cycle stages ot the requested indicator, except these given in "excluded_stages"
        """
        if excluded_stages is not None:
            column_indexes_to_exclude = [self._get_index_life_cycle_stage(stage_abr) for stage_abr in excluded_stages]
            data_copy = np.delete(self.data, column_indexes_to_exclude, axis=1)
        else:
            data_copy = np.copy(self.data)

        if abr_indicator is not None:
            return data_copy[self._get_index_indicator(abr_indicator), :].sum()
        else:
            return data_copy.sum(axis=1)

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

    def sum_to_stage(self, stage):
        indicator_sums = self.data.sum(axis = 1)
        self.data = np.zeros_like(self.data)
        stage_id = self._get_index_life_cycle_stage(stage)
        self.data[:, stage_id] = indicator_sums
        #todo: Find out whether it makes more sense to overwrite self.data or return a new data record and adjust it if necessary.

    @staticmethod
    def _format_data_array_element_for_printing(width, value):
        """Formats each field of the printed data array, so it has the correct width. Digits parameter gives maximum for
        field width and num is the value to be formatted."""
        value_str = str(value)
        value_len = len(value_str)

        if value_len > width:
            print(f"Values < column or row labels. Data matrix of dataset may be empty.")

        return ' ' * (width - value_len) + value_str

    @classmethod
    def create_dimensionless_template(cls, name, resulting_unit):
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

        # Note: Specifying a unit like m^2 would lead to the unit being only m^2 when it should be"indicator unit / m^2"
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
    """Class for logging operations and calculations performed on EpdDataset objects. Every operation or calculation
    step creates a text element that is appended to the 'entries' attribute. An instance gets initialized every time a
    EpdDataset object is created.

    Attributes
    ----------
    initial_source : str
        Contains the name of the source that was used to load EPD data into the EpdDataset object.
    initial_name : str
        The name of the EPD whose data was loaded into the EpdDataset object.
    initial_epd_id : str
        ID, e.g. UUID, of EPD whose data was loaded into the EpdDataset object.
    contained_epd_ids : set
        ID's of all EPDs that were aggregated in the dataset
    epd_infos : dict
        The name and source of all contained EPDs, identified with IDs as dictionary keys
    entries : list
        Contains string objects for every operation/ calculation step.
    """
    def __init__(self):
        self.initial_source = None
        self.initial_name = None
        self.initial_epd_id = None

        self.contained_epd_ids = set()
        self.epd_infos = {}
        self.entries = []

    @dataclass(frozen=True)
    class Entry:
        """Single history entry.

        kind:
            "init"              – dataset initialized from source
            "mul_scalar"        – multiplied by factor (scalar or array)
            "mul_other"         – multiplied by other dataset
            "sum"               – sum with other dataset
            "diff"              - difference with other dataset
            "truediv_divisor"   - division with divisor (scalar or array)
            "truediv_other"     - division with other dataset
            "replacements"      – replacement calculation
            "normalize"         – normalization
            "weighting"         – weighting
            "other"             – generic
        message:
            String object that describes the operation associated with the entry 
        factor:
            Stores the numeric factor for scalar operations (e.g. multiply, divide)
        epd_id:
            The id of the EPD, the operation was performed on or None, if the operation involved more than 1 dataset
        """
        kind: str
        message: str
        operand: Optional[float] = None
        epd_id: Optional[str] = None

        def __str__(self):
            return f"Operation: {self.kind}; Message: {self.message}"
        

    def create_clone(self):
        """Used to clone the History object (self) to prevent using a deepcopy which slows down the process when
        handling histories with many entries

        Returns
        -------
        cloned_history : History
            Basically a clone of the present History object with the same attributes as self
        """
        clone = History()

        clone.initial_source = self.initial_source
        clone.initial_name = self.initial_name
        clone.initial_epd_id = self.initial_epd_id

        clone.contained_epd_ids = set(self.contained_epd_ids)
        clone.epd_infos = dict(self.epd_infos)
        clone.entries = list(self.entries)

        return clone

    def add_data_source(self, epd_id, epd_name, source_key):
        """Creates the first entry and sets the objects attributes.

        Parameters
        ----------
        epd_id : str
            The UUID of the EPD
        epd_name : str
            The name of the EPD
        source_key :
            The user defined name/ key of the EpdSource object given when registering the source, not the one given when
            creating the source.
        """
        self.initial_source = source_key
        self.initial_name = epd_name
        self.initial_epd_id = epd_id

        self.contained_epd_ids = {epd_id}
        self.epd_infos[epd_id] = {"name": epd_name, "source": source_key}

        msg = f"Dataset '{epd_name}' ({epd_id}) initialized from source '{source_key}'"
        self.entries.append(History.Entry(kind="init", message=msg, epd_id=epd_id))

    def log_operation(self, entry, replace_last=False):
        """Adds a given entry to the entries list with the option to replace the last entry with the given entry.
        If the entry is not yet an Entry object, this will be created first, before appending it either as the last
        element of entries or replacing the current last entry, when replace_last is set to True."""
        if not isinstance(entry, History.Entry):
            entry = History.Entry(kind="other", message=entry, epd_id=self._single_epd_id())

        if replace_last and self.entries:
            self.entries[-1] = entry
        else:
            self.entries.append(entry)

    def log_mul_factor(self, factor):
        """Logs a multiplication with a factor."""
        msg = f"Multiplied with factor(s):\n {factor}"
        self.entries.append(History.Entry(kind="mul_scalar", message=msg, operand=factor, epd_id=self._single_epd_id()))

    def log_mul_other(self, other_dataset):
        """Logs a multiplication with another dataset."""
        msg = f"Multiplied with other dataset: {other_dataset.history.initial_name}"
        self.entries.append(History.Entry(kind="mul_other", message=msg, operand=other_dataset.data, epd_id=None))
        self.merge_histories(other_dataset=other_dataset)

    def log_add(self, other_dataset):
        """Logs the calculation of a sum with another dataset."""
        msg = f"Sum calculated with other dataset: {other_dataset.history.initial_name}"
        self.entries.append(History.Entry(kind="sum", message=msg, epd_id=None))
        self.merge_histories(other_dataset=other_dataset)

    def log_sub(self, other_dataset):
        """Logs the calculation of a difference with another dataset."""
        msg = f"Difference calculated with other dataset: {other_dataset.history.initial_name}"
        self.entries.append(History.Entry(kind="diff", message=msg, epd_id=None))
        self.merge_histories(other_dataset=other_dataset)

    def log_truediv_divisor(self, divisor):
        """Logs a division by a factor."""
        msg = f"Divided by scalar(s):\n {divisor}"
        self.entries.append(History.Entry(kind="truediv_divisor", message=msg, operand=divisor, epd_id=self._single_epd_id()))

    def log_truediv_other(self, other_dataset):
        """Logs a division by another dataset."""
        msg = f"Divided by other dataset: {other_dataset.history.initial_name}"
        self.entries.append(History.Entry(kind="truediv_other", message=msg, operand=other_dataset.data, epd_id=None))
        self.merge_histories(other_dataset=other_dataset)

    def log_replacements(self, replacements):
        """Logs the calculation of a replacement with kind: replacements, and replaces it with the last existing log,
        which was automatically generated by the replacement calculation of kind: mul_scalar."""
        msg = f"Calculated component replacements: {self.initial_name} += {replacements} * {self.initial_name}"
        # Replace last existing entry in self.entries, since the replacement calculation already called log_add()
        self.entries[-1] = History.Entry(kind="replacements", message=msg, operand=replacements, epd_id=self._single_epd_id())

    def log_normalize(self, method_name, reference_result):
        """Logs a normalization calculation with a reference result."""
        msg = f"Normalized with normalization method '{method_name}' and reference values\n{reference_result}"
        self.entries.append(History.Entry(kind="normalize", message=msg, operand=reference_result, epd_id=None))

    def log_weighting(self, method_name, weighting_factors):
        """Logs a weighting calculation with weighting factors."""
        msg = f"Weighted with weighting method '{method_name}' and weighting factors\n{weighting_factors}"
        self.entries.append(History.Entry(kind="weighting", message=msg, operand=weighting_factors, epd_id=None))

    def merge_histories(self, other_dataset):
        """Merges the Histories of two individual EpdDataset objects together, when an operation involves two datasets."""
        other_hist = other_dataset.history

        # add contained epd_ids to the contained epd_ids of self if not yet present
        self.contained_epd_ids |= other_hist.contained_epd_ids
        # merge metadata
        for epd_id, info in other_hist.epd_infos.items():
            if epd_id not in self.epd_infos:
                self.epd_infos[epd_id] = info
        # append entries which already contain epd_id's
        self.entries += other_hist.entries

    def get_history(self):
        """Returns the entries attribute of the object"""
        return self.entries

    def show_history(self, summary=True):
        """Displays the history/logs of the epd dataset by calling the associated method in History class.

        Parameters
        ----------
        summary : bool
            Determines the level of detail. If True, the History entries are summarized and if not, every entry is
            printed out separately.
        """
        if not summary:
            print("Printing history entries:\n")
            for entry in self.entries:
                print(entry)
                print()
        else:
            print("Printing summarized history:\n")
            self._summarize_history()

    def _summarize_history(self):
        """Creates the summary based on the Entry objects in the entries attribute. It summarizes them based on
        operations involving single datasets (per_epd) and global operations (global_entries) either involving two
        datasets or other operations like normalization and/or weighting.The summarized information is printed out in
        the same structured way."""
        from collections import Counter, defaultdict

        # group entries per epd_id; epd_id=None are global operations
        per_epd = defaultdict(list)
        global_entries = []
        for e in self.entries:
            if e.epd_id is None:
                global_entries.append(e)
            else:
                per_epd[e.epd_id].append(e)

        # per-EPD summaries
        for epd_id, entries in per_epd.items():
            info = self.epd_infos.get(epd_id, {})
            name = info.get("name", "unknown")
            source = info.get("source", "unknown")

            print(f"Dataset '{name}' ({epd_id}) initialized from source '{source}'")

            # scalar multiplications: show distinct factors and counts
            scalar_factors = [e.operand for e in entries if e.kind == "mul_scalar" and e.operand is not None]
            factor_counts = Counter(scalar_factors)

            if factor_counts:
                print("  Scalar multiplications:")
                for factor, count in factor_counts.items():
                    if count == 1:
                        print(f"    - multiplied by {factor}")
                    else:
                        print(f"    - multiplied by {factor} (repeated {count} times)")

            # replacements (just count and print messages grouped)
            replace_msgs = [e.message for e in entries if e.kind == "replacements"]
            replace_counts = Counter(replace_msgs)
            if replace_counts:
                print("  Replacement operations:")
                for msg, count in replace_counts.items():
                    if count == 1:
                        print(f"    - {msg}")
                    else:
                        print(f"    - {msg} (repeated {count} times)")
            # blank line between datasets
            print()

        # global operations (normalized, weighted, adds, etc.)
        if global_entries:
            print("Global operations (applied to the aggregated dataset):")
            norm_msgs = [e.message for e in global_entries if e.kind == "normalize"]
            weight_msgs = [e.message for e in global_entries if e.kind == "weighting"]
            add_msgs = [e.message for e in global_entries if e.kind == "sum"]
            other_msgs = [e.message for e in global_entries if e.kind not in {"normalize", "weighting", "sum"}]

            for msgs, title in [
                (norm_msgs, "  Normalization:"),
                (weight_msgs, "  Weighting:"),
                (add_msgs, "  Summations:"),
                (other_msgs, "  Other:"),
            ]:
                if msgs:
                    print(title)
                    counts = Counter(msgs)
                    for msg, count in counts.items():
                        if count == 1:
                            print(f"    - {msg}")
                        else:
                            print(f"    - {msg} (repeated {count} times)")
                    print()

    def _single_epd_id(self):
        """If this dataset currently represents exactly one EPD, return its ID, otherwise returns None"""
        if len(self.contained_epd_ids) == 1:
            return next(iter(self.contained_epd_ids))
        return None