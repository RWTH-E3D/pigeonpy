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

    def normalize(self, method_name, reference_result):
        if isinstance(reference_result, dict):
            reference_result = self._create_array_from_dict(reference_result)

        normalized_dataset_class = self.dataset_template.dimensionless_template(f"NormalizedDataset{method_name}")

        self.normalized_results[method_name] = {}

        normalize_dataset = lambda dataset: normalized_dataset_class((dataset / reference_result).data)

        for categorization, value in self.result.items():
            if isinstance(value, Series):
                norm_result = value.apply(normalize_dataset)
            elif isinstance(value, self.dataset_template):
                norm_result = normalize_dataset(value)

            self.normalized_results[method_name][categorization] = norm_result

    def weight(self, method_name, weighting_factors, normalization_method=None):
        if isinstance(weighting_factors, dict):
            weighting_factors = self._create_array_from_dict(weighting_factors)

        weighted_dataset_class_template = self.dataset_template.dimensionless_template("weighted_dataset_class",
                                                                                         self.dataset_template)
        self.weighted_results[method_name] = {}

        if normalization_method and normalization_method in self.normalized_results:
            for categorization in self.normalized_results[normalization_method]:
                self._calculate_weighting(self.normalized_results[normalization_method], categorization, method_name, weighting_factors,
                                          weighted_dataset_class_template)
        elif normalization_method:
            print(f"Given normalization method not in normalized results. "
                  f"No weighting with given method {normalization_method} possible.")
        else:
            for categorization in self.result:
                self._calculate_weighting(self.result, categorization, method_name, weighting_factors,
                                          weighted_dataset_class_template)

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

    def _calculate_weighting(self, result, categorization, method_name, weighting_factors, dataset_class_template):
        if type(result[categorization]) == self.dataset_template:
            #todo: update in the same way as in calculate normalization?
            self.weighted_results[method_name][categorization] = result[categorization] * weighting_factors
        else:
            self.weighted_results[method_name][categorization] = result[categorization].apply(
                lambda dataset: dataset_class_template((dataset * weighting_factors).data)
            )

    def _create_array_from_dict(self, dict_to_be_converted):
        temp_instance = self.dataset_template()
        array = temp_instance.data[:, 1]
        array = array[:, None]  # turn array from shape (x) to shape (x, 1)
        for attribute_abbreviation in dict_to_be_converted:
            index = temp_instance._get_index_indicator(attribute_abbreviation)
            array[index] = dict_to_be_converted[attribute_abbreviation]
        del temp_instance
        return array