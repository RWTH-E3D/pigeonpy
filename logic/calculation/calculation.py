from logic.calculation.calculator import Calculator
from logic.calculation.calculationinput import CalculationInput
class Calculation(object):
    def __init__(self):
        self.input = None
        self._calculator = None
        self.result = None
        self.other_results = {}

    def run(self, *categorizations, epd_datamanager, goal_and_scope):
        self._calculator = self._calculator or Calculator(self.input)
        original_databases = epd_datamanager.databases
        if goal_and_scope:
            compliant_databases = dict((sk, db) for sk, db in epd_datamanager.databases.items() \
                                       if db.standard == goal_and_scope.standard)
            if compliant_databases:
                print(f"Using databases compliant to standard defined in goal and scope: {list(compliant_databases.keys())}")
                epd_datamanager.databases = compliant_databases

        self.result = self._calculator.calculate(*categorizations, epd_datamanager=epd_datamanager)
        epd_datamanager.databases = original_databases

    def load_input(self, filepath):
        self.input = CalculationInput()
        self.input.load(filepath)
    def apply_method(self, method_name, method, *method_arguments):

        self.other_results[method_name] = method(self, *method_arguments)

