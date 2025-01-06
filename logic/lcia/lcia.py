import pandas as pd
from logic.lcia.calculator import Calculator
from logic.lcia.calculationinput import CalculationInput


class Lcia(object):
    def __init__(self, dataset_template):
        self.input = None
        self._calculator = None
        self.dataset_template = dataset_template

        self.result = {}
        self.normalized_results = {}
        self.weighted_result = {}

    def run(self, *categorizations, epd_datamanager, observation_period):
        self._initialize_calculator()
        self.result.update(
            self._process_categorizations(
                categorizations, epd_datamanager, observation_period
            )
        )

    def load_input(self, filepath):
        self.input = CalculationInput()
        self.input.load(filepath)

    def normalize(self, method):
        ...

    def weight(self, method_name, weighting_factors, normalization_method=None):
        # Auf alle möglichen Ergebnisse anwenden -> overall_result noch gewichten, wenn epd result mit in self.result
        # gespeichert ist

        weighted_dataset_class_template = self.dataset_template().dimensionless_template("weighted_dataset_class",
                                                                                         self.dataset_template)
        self.weighted_result[method_name] = {}

        if normalization_method and normalization_method in self.normalized_results:
            for categorization in self.normalized_results[normalization_method]:
                self.weighted_result[method_name][categorization] = self.normalized_results[normalization_method][
                    categorization].multiply(weighting_factors)
        elif normalization_method:
            print("Given normalization method not in normalized results. No weighting with given method possible.")
        else:
            for categorization in self.result:
                self.weighted_result[method_name][categorization] = self.result[categorization].apply(
                    lambda dataset: weighted_dataset_class_template(weighting_factors * dataset.data)
                )

    def _initialize_calculator(self):

        self._calculator = self._calculator or Calculator(self.input)

    def _process_categorizations(self, categorizations, epd_datamanager, observation_period):
        results = {}
        for categorization in categorizations:
            results[categorization] = self._run_individual_calculation(
                categorization, epd_datamanager, observation_period
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
