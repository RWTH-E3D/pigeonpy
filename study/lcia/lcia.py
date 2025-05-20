from study.lcia.calculator import Calculator
from study.lcia.calculationinput import CalculationInput
from pandas import Series


class Lcia(object):
    """Every study holds one Lcia object. This class contains the results of the calculations carried out. It also
    manages the calculation input, the calculation itself as well as the normalization and weighting of the results.

    Attributes
    ----------
    input : CalculationInput
        Instance that contains the content of one input csv file together with the dataframes needed for the calculation
        that are created during the loading process of an input file.
    _calculator : Calculator
        Performs the calculations based on the CalculationInput and writes the results to the result attribute.
    dataset_template : EpdDataset
        Subclass of EpdDataset (not an instance) that serves as a template for creating instances and extract standard
        based metadata.
    result : dict
        Dictionary containing a Series for every given partition and the Total results. Partition names or "Total result"
        are the .keys
    normalized_results : dict
        Contains the normalized results in the same form as the result attribute
    weighted_results : dict
        Contains the weighted results in the same form as the result attribute

    Parameters
    ----------
    dataset_template : EpdDataset
        Gets assigned directly when creating a study with the belonging dataset_template.
    """
    def __init__(self, dataset_template):
        self.input = None
        self._calculator = None
        self.dataset_template = dataset_template

        self.result = {}
        self.normalized_results = {}
        self.weighted_results = {}

    def run(self, *partitions, epd_datamanager, observation_period):
        """Starts the calculation process by initializing the calculator, calculating the partition-based results, the
        "Total result" and the "Individual EPD" result (each EPD multiplied with the given amount in the input csv file)
         of the study.

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
        """
        self._initialize_calculator()
        self.result.update(
            self._process_partitions(
                partitions, epd_datamanager, observation_period
            )
        )
        self._calculate_total_result()

    def load_input(self, filepath):
        """Instantiates CalculationInput class and calls the load function for preprocessing the input CSV file given
        with the filepath."""
        self.input = CalculationInput()
        self.input.load(filepath)

    def normalize(self, method_name, reference_result, resulting_unit='-'):
        """Performs a normalization calculation of the indicator impacts in relation to the reference information given
        with the reference_result argument. The results of the normalization are saved to the normalized_results dict in
        the instance attribute. For every existing partition in the result attribute, a normalization is performed.

        The method creates a class template for normalized datasets using the dimensionless_template method of the
        EpdDataset class to provide the correct basis for normalization.

        Parameters
        ----------
        method_name : str
            Used to identify the results later, also for the case of applying different normalization methods in the
            same study or having weighting methods that are based on specific normalization methods.
        reference_result : np.ndarray or dict
            If the reference result is a numpy array, it is used directly as divisor for the normalization, note here
            that the correct order of the normalization factors is equivalent to the order of the impact categories as
            defined in the corresponding indicators json file and omitted indicators in the study must also be
            considered.
            When using a dictionary for reference values, the order and omission of indicators does not matter. The key
            indicates the indicator abbreviation (according to the abbreviation in the json file) and the value is the
            reference factor.
        resulting_unit : str
            The unit for the environmental indicators after calculation. Default is '-'/ percentage.
        """
        if isinstance(reference_result, dict):
            reference_result = self._create_array_from_dict(reference_result)

        normalized_dataset_class = self.dataset_template.dimensionless_template(
            f"NormalizedDataset_{method_name}", resulting_unit
        )

        self.normalized_results[method_name] = {}

        normalize_dataset = lambda dataset: normalized_dataset_class(
            data = (dataset / reference_result).data,
            name = dataset.name + "_normalized"
        )

        for partition, value in self.result.items():
            if isinstance(value, Series):
                norm_result = value.apply(normalize_dataset)
            elif isinstance(value, self.dataset_template):
                norm_result = normalize_dataset(value)
            else:
                norm_result = None

            self.normalized_results[method_name][partition] = norm_result

    def weight(self, method_name, weighting_factors, normalization_method=None, resulting_unit='-'):
        """Performs a weighting calculation of the indicator impacts based on the given weighting_factors argument.
        The result of the weighting is saved to the weighted_results dict in the instance attribute. If the weighting
        should be based on a previously applied normalization, the method_name given in the normalization must be given
        as the normalization_method argument here. If no method_name is specified, the weighting is applied to the
        result attribute.

        The method creates a class template for weighted datasets using the dimensionless_template method of the
        EpdDataset class to provide the correct basis for weighting.

        Parameters
        ----------
        method_name : str
            Used to identify the results later and for the case of applying different weighting methods/ factors in the
            same study.
        weighting_factors : np.ndarray or dict
            For the case of a numpy array, the factors are applied directly to the indicator values, note here
            that the correct order of the normalization factors is equivalent to the order of the impact categories as
            defined in the corresponding indicators json file and omitted indicators in the study must also be
            considered.
            When using a dictionary for weighting factors, the order and omission of indicators does not matter. The key
            indicates the indicator abbreviation (according to the abbreviation in the json file) and the value is the
            weighting factor.
        normalization_method : str
            If specified, the given weighting_factors are applied to the normalization method given by its name (if
            exists). Default is None, resulting in the weighting of the existing partitions in the result attribute.
        resulting_unit : str
            The unit for the environmental indicators after calculation. Default is '-'/ percentage.
        """
        if isinstance(weighting_factors, dict):
            weighting_factors = self._create_array_from_dict(weighting_factors)

        weighted_dataset_class = self.dataset_template.dimensionless_template(
            f"WeightedDataset_{method_name}", resulting_unit
        )

        self.weighted_results[method_name] = {}

        if normalization_method and normalization_method in self.normalized_results:
            self._calculate_weighting(
                self.normalized_results[normalization_method],
                method_name, weighting_factors, weighted_dataset_class
            )
        elif normalization_method:
            print(f"Method '{normalization_method}' not in normalized results. No weighting possible.")
        else:
            self._calculate_weighting(
                self.result,
                method_name, weighting_factors, weighted_dataset_class
            )

    def _initialize_calculator(self):
        """If no Calculator instance is present, it creates one based on the CalculationInput instance present in the
        input attribute."""
        self._calculator = self._calculator or Calculator(self.input)

    def _process_partitions(self, partitions, epd_datamanager, observation_period):
        """Iterates through the partitions and creates the result for the "Individual EPD" calculation that contains
        an entry for every individual EPD present in the input.

        Parameters
        ----------
        see 'run' method for explanations

        Returns
        -------
        results : dict
            Contains the calculation results for the given partitions.
        """
        results = {}
        for partition in partitions:
            results[partition] = self._run_individual_calculation(
                partition, epd_datamanager, observation_period
            )
        results["Individual EPD"] = self._run_individual_calculation(
            "Individual EPD", epd_datamanager, observation_period
        )
        return results

    def _run_individual_calculation(self, partition, epd_datamanager, observation_period):
        """Calls the calculate method of the Calculator class for a single partition, differentiating between the cases
        of single string partition or tuple partition and returns the calculated pd.Series object."""
        if isinstance(partition, tuple):
            return self._calculator.calculate(
                *partition,
                epd_datamanager=epd_datamanager,
                observation_period=observation_period
            )
        else:
            return self._calculator.calculate(
                partition,
                epd_datamanager=epd_datamanager,
                observation_period=observation_period
            )

    def _calculate_total_result(self):
        """Calculates the total result of the study as one single EpdDataset by summing over the Individual Epd result."""
        self.result["Total result"] = self.result["Individual EPD"].sum()
        self.result["Total result"].name = "Total result"

    def _calculate_weighting(self, result, method_name, weighting_factors, weighted_dataset_class):
        """Method to eliminate duplication. Calculates the weighting for the given result which is either the result
         attribute or a previously calculated normalization result."""
        weight_dataset = lambda dataset: weighted_dataset_class(
            data = (dataset * weighting_factors).data,
            name = dataset.name + "_weighted"
        )

        for partition, value in result.items():
            if isinstance(value, Series):
                weighted_result = value.apply(weight_dataset)
            elif isinstance(value, self.dataset_template):
                weighted_result = weight_dataset(value)
            else:
                weighted_result = None
            self.weighted_results[method_name][partition] = weighted_result

    def _create_array_from_dict(self, dict_to_be_converted):
        """Converts a dictionary mapping the normalization or weighting factors to their associated indicator into
        a numpy array with the factors being in the correct index based on the dataset array."""
        temp_instance = self.dataset_template()
        array = temp_instance.data[:, 1][:, None]  # Turn array from shape (x) to shape (x, 1)

        for abbreviation, value in dict_to_be_converted.items():
            index = temp_instance._get_index_indicator(abbreviation)
            array[index] = value

        return array
