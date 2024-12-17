from logic.lcia.calculator import Calculator
from logic.lcia.calculationinput import CalculationInput


class Lcia(object):
    def __init__(self):
        self.input = None
        self._calculator = None

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

    def weight(self, method_name, weighting_factors):
        ...

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
