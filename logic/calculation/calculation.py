from logic.calculation.calculator import Calculator
from logic.calculation.calculationinput import CalculationInput


class Calculation(object):
    def __init__(self):
        self.input = None
        self._calculator = None

        self.result = {}
        self.normalized_results = {}
        self.weighted_result = {}

    def run(self, *categorizations, epd_datamanager, goal_and_scope):

        self._initialize_calculator()
        original_databases = epd_datamanager.databases

        _set_compliant_databases(epd_datamanager, goal_and_scope)

        self.result.update(
            self._process_categorizations(
                categorizations, epd_datamanager, goal_and_scope.observation_period
            )
        )

        epd_datamanager.databases = original_databases

    def load_input(self, filepath):
        self.input = CalculationInput()
        self.input.load(filepath)

    def normalize(self, method):
        ...

    def weight(self, method):
        ...

    def apply_method(self, method_name, method, *method_arguments):

        self.other_results[method_name] = method(self, *method_arguments)

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


def _set_compliant_databases(epd_datamanager, goal_and_scope):
    if goal_and_scope:
        compliant_databases = dict((sk, db) for sk, db in epd_datamanager.databases.items() \
                                   if db.standard == goal_and_scope.standard)
        if compliant_databases:
            print(f"Using databases compliant to standard defined in goal and scope: {list(compliant_databases.keys())}")
            epd_datamanager.databases = compliant_databases
