import copy
from pandas import Series
from study.calculationinput import CalculationInput
from study.calculator import calculate
from data.epddata.epddatamanager import EpdDataManager
from data.epdattributeloader import EpdAttributeLoader
from data.output.lca_data_output import export_study_result
from epd.epddataset.epddataset import EpdDataset
from epd.epddataset.en15804A2dataset import En15804A2Dataset


class Study(object):
    """Class for managing the LCIA calculations and an interface to interact with the tools main functionalities.

    Contains methods for loading the CSV input file, registering EPD sources via the epd_datamanager, run calculations,
    conducting the LCIA based normalization and weighting as well as defining the parameters for the study. These include
    observation period, the selection of environmental indicators and life cycle stages that are to be considered, or a
    life cycle stage that should be used to store replacements, if calculated.

    Attributes
    ----------
    study_name : str
        Given name for the study.
    observation period : int
        The observation period for the study used for calculating component replacements based on their service life if
        given.
    dataset_template : EpdDataset
        Subclass of EpdDataset (not an instance) that serves as a template for creating instances and extract standard
        based metadata, e.g. the indicators and life cycle stages for EN15804+A2.
    epd_datamanager : EpdDataManager
        Instance of EpdDataManager that stores the registered EPD sources and already loaded/ cached datasets.

    """
    def __init__(
            self,
            study_name,
            observation_period,
            environmental_indicators=None,
            life_cycle_stages=None,
            replacement_stage=None,
            dataset_template=En15804A2Dataset):
        """Initializes a study instance.

        Each study requires a name and observation period. The environmental indicators and life cycle stages can be
        customized individually by passing lists of the desired indicators and life cycle stages to include in the study.

        Parameters
        ----------
        study_name : str
            Can be chosen arbitrarily.
        observation_period : int
            Period in years used as time frame for the calculation of component replacements
        dataset_template : type(EpdDataset)
            Subclass object of EpdDataset (not an instance of the class, i.e. no parentheses). Defaults to
            En15804A2Dataset which then serves as the standard for the study.
        environmental_indicators : list
            A list of abbreviations for the environmental indicators which, if specified, define the indicators used in
            the study. Defaults to None
        life_cycle_stages : list
            A list of abbreviations for the life cycle stages which, if specified, define the life cycle stages used in
            the study. Defaults to None
        replacement_stage : str
            Abbreviation for the life cycle stage that is used to store replacement indicator values. E.g. stage 'b4'
            when using standard EN15804. If not specified, i.e. None, replacements are calculated by multiplying the
            whole dataset with the amount of replacements.
        """

        self.study_name = study_name
        self.observation_period = observation_period
        self.replacement_stage = replacement_stage

        if isinstance(dataset_template, EpdDataset):
            raise Exception("dataset_template must be the class itself, not an instance, i.e. type(EpdDataset()).")
        self.dataset_template = dataset_template

        if environmental_indicators or life_cycle_stages:
            self.dataset_template = self.dataset_template.get_customized_dataset_class(environmental_indicators,
                                                                                       life_cycle_stages,
                                                                                       class_name = f"{self.dataset_template.__name__}_{self.study_name}")

        self.epd_datamanager = EpdDataManager(self.dataset_template)
        self.calculation_input = CalculationInput()

        self.result = {}

    def run_calculation(self, *partitions):
        """Starts the calculation process based on the partitions given as the argument.

        Parameters
        ----------
        partitions : tuple
            Contains the partitions according to which the calculation is made. Can be a single string, tuple or a
            combination of strings and tuples.
        """

        self.result.update(
            {"indicator_values": self._process_partitions(
                partitions,
                self.epd_datamanager,
                self.observation_period,
                self.replacement_stage
            )}
        )
        self._calculate_total_result()


    def load_calculation_input(self, filepath, sep=","):
        """Loads an input CSV file (filepath) with the CalculationInput instance in the calculation_input attribute.

        Parameters
        ----------
        filepath : str or Path
            Path to the input CSV file.
        sep : str
            Separator used in the input CSV file.
        """
        self.calculation_input.load(filepath, sep=sep)


    def normalize(self, method_name, reference_result, resulting_unit='-'):
        """Performs a normalization calculation of the indicator impacts in relation to the reference information given
        with the reference_result argument. The results of the normalization are saved to the normalized_results dict in
        the instance attribute. For every existing partition in the result attribute, a normalization is performed.

        The method creates a class template for normalized datasets using the create_dimensionless_template method of the
        EpdDataset class to provide the correct basis for normalization.

        Parameters
        ----------
        method_name : str
            Used to identify the results later, also for the case of applying different normalization methods in the
            same study or having weighting methods that are based on specific normalization methods.
        reference_result : np.ndarray or dict
            If the reference result is a numpy array, it is used directly as divisor for the normalization, note here
            that the correct order of the normalization factors is equivalent to the order of the impact categories as
            defined in the corresponding indicators JSON file and omitted indicators in the study must also be
            considered.
            When using a dictionary for reference values, the order and omission of indicators does not matter. The key
            indicates the indicator abbreviation (according to the abbreviation in the JSON file) and the value is the
            reference factor.
        resulting_unit : str
            The unit for the environmental indicators after calculation. Default is '-'/ percentage.
        """
        if isinstance(reference_result, dict):
            reference_result = self._create_array_from_dict(reference_result)

        normalized_dataset_class = self.dataset_template.create_dimensionless_template(
            f"NormalizedDataset_{method_name}", resulting_unit
        )

        self.result[method_name] = {}

        normalize_dataset = lambda dataset: normalized_dataset_class(
            data = (dataset / reference_result).data,
            name = dataset.name + "_normalized",
            history = dataset.history.create_clone()
        )

        reference_result_log = ""
        for idx, indicator in enumerate(normalized_dataset_class.environmental_indicators):
            reference_result_log += f"      {indicator.abbreviation}: {reference_result[idx, 0]}\n"
        def log_normalization(dataset):
            dataset.history.log_normalize(method_name, reference_result_log)
            return dataset

        for partition, value in self.result["indicator_values"].items():
            if isinstance(value, Series):
                norm_result = value.apply(normalize_dataset)
                norm_result = norm_result.apply(log_normalization)
            elif isinstance(value, self.dataset_template):
                norm_result = normalize_dataset(value)
                norm_result = log_normalization(norm_result)
            else:
                norm_result = None

            self.result[method_name][partition] = norm_result

    def weight(self, method_name, weighting_factors, normalization_method=None, resulting_unit='-'):
        """Performs a weighting calculation of the indicator impacts based on the given weighting_factors argument.

        The result of the weighting is saved to the weighted_results dict in the instance attribute. If the weighting
        should be based on a previously applied normalization, the method_name given in the normalization must be given
        as the normalization_method argument here. If no method_name is specified, the weighting is applied to the
        result attribute.

        A class template is created for weighted datasets using the create_dimensionless_template method of the
        EpdDataset class to provide the correct basis for weighting.

        Parameters
        ----------
        method_name : str
            Used to identify the results later and for the case of applying different weighting methods/ factors in the
            same study.
        weighting_factors : np.ndarray or dict
            For the case of a numpy array, the factors are applied directly to the indicator values, note here
            that the correct order of the normalization factors is equivalent to the order of the impact categories as
            defined in the corresponding indicators JSON file and omitted indicators in the study must also be
            considered.
            When using a dictionary for weighting factors, the order and omission of indicators does not matter. The key
            indicates the indicator abbreviation (according to the abbreviation in the JSON file) and the value is the
            weighting factor.
        normalization_method : str
            If specified, the given weighting_factors are applied to the normalization method given by its name (if
            exists). Default is None, resulting in the weighting of the existing partitions in the result attribute.
        resulting_unit : str
            The unit for the environmental indicators after calculation. Default is '-'/ percentage.
        """
        if isinstance(weighting_factors, dict):
            weighting_factors = self._create_array_from_dict(weighting_factors)

        weighted_dataset_class = self.dataset_template.create_dimensionless_template(
            f"WeightedDataset_{method_name}", resulting_unit
        )

        self.result[method_name] = {}

        if normalization_method and normalization_method in self.result:
            self._calculate_weighting(
                self.result[normalization_method],
                method_name, weighting_factors, weighted_dataset_class
            )
        elif normalization_method:
            print(f"Method '{normalization_method}' not in normalized results. No weighting possible.")
        else:
            self._calculate_weighting(
                self.result["indicator_results"],
                method_name, weighting_factors, weighted_dataset_class
            )


    def export(self, output_dir=None, file_format="csv", drop_rows=False, add_uuid=False, merge=True):
        """Calls the export function for the output of results.

        Allows for the output of all results into one file (merge=True) or the output of each
        result type (indicator_values, normalized, weighted) and calculated partition separately (merge=False).

        Parameters
        ----------
        output_dir : Path or str
            Directory path for export
        file_format : str
            Export format, 'csv' or 'teco_json' (JSON) available
        drop_rows : bool
            Removes rows (row = life cycle stage), where all indicator values are zero.
        add_uuid : bool
            Creates and adds a UUID to each exported dataset
        merge : bool
            If True, all dictionaries in self.result are combined and exported into one file

        """
        export_study_result(
            self.study_name,
            self.result,
            output_dir=output_dir,
            file_format=file_format,
            drop_rows=drop_rows,
            add_uuid=add_uuid,
            merge=merge
        )


    def _process_partitions(self, partitions, epd_datamanager, observation_period, replacement_stage):
        """Iterates through the partitions and creates the result for the "unique_epd" calculation that contains
        an entry for every unique EPD present in the input.

        All parameters passed by the run() method.

        Parameters
        ----------
        partitions : tuple
            Contains the partitions according to which the calculation is made. Can be a single string, tuple or a
            combination of strings and tuples.
        epd_datamanager : EpdDataManager
            Instance of the EpdDataManager class that contains the registered data sources and cached datasets from
            which the datasets are loaded during calculation.
        observation_period : int
            Observation period defined for the conducted study to use as the basis for the calculation of component
            replacements.
        replacement_stage : str
            asd

        Returns
        -------
        results : dict
            Contains the calculation results for the given partitions.
        """
        results = {}
        for partition in partitions:
            results[partition] = self._calculate_partition(
                partition, epd_datamanager, observation_period, replacement_stage=replacement_stage
            )
        results["unique_epd"] = self._calculate_partition(
            "unique_epd", epd_datamanager, observation_period, replacement_stage=replacement_stage
        )
        return results

    def _calculate_partition(self, partition, epd_datamanager, observation_period, replacement_stage):
        """Calls the calculate method of the Calculator class for a single partition, differentiating between the cases
        of single string partition or tuple partition and returns the calculated pd.Series object.

        Parameters
        ----------
        partition : str or tuple
            The partition to be calculated
        epd_datamanager : EpdDatamanager
            Passed through to the calculate method for loading the datasets during calculation
        observation_period : int
            Used to calculate the replacements in the calculate method
        replacement_stage : str
            asd

        Returns
        -------
        results : dict
            Contains the calculation results for the given partitions.
        """
        if isinstance(partition, tuple):
            return calculate(
                *partition,
                calculation_input=self.calculation_input,
                epd_datamanager=epd_datamanager,
                observation_period=observation_period,
                replacement_stage=replacement_stage
            )
        else:
            return calculate(
                partition,
                calculation_input=self.calculation_input,
                epd_datamanager=epd_datamanager,
                observation_period=observation_period,
                replacement_stage=replacement_stage
            )

    def _calculate_total_result(self):
        """Calculates the total_result of the study as one single EpdDataset by summing over the unique_epd result."""
        self.result["indicator_values"]["total_result"] = self.result["indicator_values"]["unique_epd"].sum()
        self.result["indicator_values"]["total_result"].name = "total_result"

    def _calculate_weighting(self, result, method_name, weighting_factors, weighted_dataset_class):
        """Apply weighting factors to calculation or normalization results.

        Handles both pandas Series and dataset instances and stores the weighted results under the given method name
        in 'self.result'.
        This method exists to avoid duplication between weighting of indicator results and normalized results.

        Parameters
        ----------
        result : dict or EpdDataset
            Entry from the result attribute of the Study instance
        method_name : str
            Name of the weighting method for identification
        weighting_factors : np.ndarray
            Multiplication factors containing the weights
        weighted_dataset_class : type(EpdDataset)
            Template for creating weighted datasets
        """
        weight_dataset = lambda dataset: weighted_dataset_class(
            data = (dataset * weighting_factors).data,
            name = dataset.name + "_weighted",
            history = dataset.history.create_clone()
        )

        weighting_factors_log = ""
        for idx, indicator in enumerate(weighted_dataset_class.environmental_indicators):
            weighting_factors_log += f"      {indicator.abbreviation}: {weighting_factors[idx, 0]*100} %\n"
        def log_weighting(dataset):
            dataset.history.log_weighting(method_name, weighting_factors_log)
            return dataset

        for partition, value in result.items():
            if isinstance(value, Series):
                weighted_result = value.apply(weight_dataset)
                weighted_result = weighted_result.apply(log_weighting)
            elif isinstance(value, self.dataset_template):
                weighted_result = weight_dataset(value)
                weighted_result = log_weighting(weighted_result)
            else:
                weighted_result = None

            self.result[method_name][partition] = weighted_result

    def _create_array_from_dict(self, dict_to_be_converted):
        """Converts a dictionary, which maps the normalization or weighting factors to their associated indicator into
        a numpy array with the factors being in the correct index based on the dataset array."""
        temp_instance = self.dataset_template()
        array = temp_instance.data[:, 1][:, None]  # Turn array from shape (x) to shape (x, 1)

        for abbreviation, value in dict_to_be_converted.items():
            index = temp_instance._get_index_indicator(abbreviation)
            array[index] = value

        return array
