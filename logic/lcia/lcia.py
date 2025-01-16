import pandas as pd
from logic.lcia.calculator import Calculator
from logic.lcia.calculationinput import CalculationInput


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

        normalized_dataset_class = self.dataset_template().dimensionless_template("normalized_dataset_class", self.dataset_template)
        self.normalized_results[method_name] = {}

        for categorization in self.result:
            self._calculate_normalization(self.result, categorization, method_name, reference_result,
                                      normalized_dataset_class)

        for categorization in self.result:
            self.normalized_results["method_name"][categorization] = self.result[categorization] / reference_result

            self.normalized_results["method_name"][categorization] = normalized_dataset_class()

    def _calculate_normalization(self, result, categorization, method_name, reference_result, dataset_class_template):
        if type(result[categorization]) == type(self.dataset_template()):
            self.normalized_results[method_name][categorization] = self.result[categorization] / reference_result
        else:
            self.normalized_results[method_name][categorization] = result[categorization].apply(
                lambda dataset: dataset_class_template(dataset.data / reference_result)


    def weight(self, method_name, weighting_factors, normalization_method=None):

        weighted_dataset_class_template = self.dataset_template().dimensionless_template("weighted_dataset_class",
                                                                                         self.dataset_template)
        self.weighted_results[method_name] = {}

        if normalization_method and normalization_method in self.normalized_results:
            for categorization in self.normalized_results[normalization_method]:
                self._calculate_weighting(self.normalized_results, categorization, method_name, weighting_factors,
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
        if type(result[categorization]) == type(self.dataset_template()):
            self.weighted_results[method_name][categorization] = result[categorization] * weighting_factors
        else:
            self.weighted_results[method_name][categorization] = result[categorization].apply(
                lambda dataset: dataset_class_template(weighting_factors * dataset.data)
            )
