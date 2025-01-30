import pandas as pd
from logic.lcia.calculator import Calculator
from logic.lcia.calculationinput import CalculationInput
from pandas import Series


class Lcia(object):
    def __init__(self, dataset_template):
        self.input = None
        self._calculator = None
        self.dataset_template = dataset_template

        self.dataset_template = dataset_template

        self.result = {}
        self.normalized_results = {}
        self.weighted_results = {}

    def run(self, *categorizations, epd_datamanager, observation_period):
        self._initialize_calculator()
        self.result.update(
            self._process_categorizations(
                categorizations, epd_datamanager, observation_period
            )
        )
        self._calculate_total_result()

    def load_input(self, filepath):
        self.input = CalculationInput()
        self.input.load(filepath)

    def normalize(self, method_name, reference_result, resulting_unit='-'):
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

        for categorization, value in self.result.items():
            if isinstance(value, Series):
                norm_result = value.apply(normalize_dataset)
            elif isinstance(value, self.dataset_template):
                norm_result = normalize_dataset(value)
            else:
                norm_result = None

            self.normalized_results[method_name][categorization] = norm_result

    def weight(self, method_name, weighting_factors, normalization_method=None, resulting_unit='-'):
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

        self._calculator = self._calculator or Calculator(self.input)

    def _process_categorizations(self, categorizations, epd_datamanager, observation_period):
        results = {}
        for categorization in categorizations:
            results[categorization] = self._run_individual_calculation(
                categorization, epd_datamanager, observation_period
            )
        results["Individual EPD"] = self._run_individual_calculation(
            "Individual EPD", epd_datamanager, observation_period
        )
        return results

    def _run_individual_calculation(self, categorization, epd_datamanager, observation_period):

        if isinstance(categorization, tuple):
            return self._calculator.calculate(
                *categorization,
                epd_datamanager=epd_datamanager,
                observation_period=observation_period
            )
        else:
            return self._calculator.calculate(
                categorization,
                epd_datamanager=epd_datamanager,
                observation_period=observation_period
            )

    def _calculate_total_result(self):
        self.result["Total result"] = self.result["Individual EPD"].sum()
        self.result["Total result"].name = "Total result"

    def _calculate_weighting(self, result, method_name, weighting_factors, weighted_dataset_class):
        """Method to eliminate duplication"""
        weight_dataset = lambda dataset: weighted_dataset_class(
            data = (dataset * weighting_factors).data,
            name = dataset.name + "_weighted"
        )

        for categorization, value in result.items():
            if isinstance(value, Series):
                weighted_result = value.apply(weight_dataset)
            elif isinstance(value, self.dataset_template):
                weighted_result = weight_dataset(value)
            else:
                weighted_result = None
            self.weighted_results[method_name][categorization] = weighted_result

    def _create_array_from_dict(self, dict_to_be_converted):
        """Converts a dictionary mapping the normalization or weighting factors to their associated indicator into
        a numpy array with the factors being in the correct index based on the dataset array."""
        temp_instance = self.dataset_template()
        array = temp_instance.data[:, 1][:, None]  # Turn array from shape (x) to shape (x, 1)

        for abbreviation, value in dict_to_be_converted.items():
            index = temp_instance._get_index_indicator(abbreviation)
            array[index] = value

        return array
