from logic.calculation.calculator import Calculator
from logic.calculation.calculationinput import CalculationInput
class Calculation(object):
    def __init__(self):
        self.input = None
        self._calculator = None
        self.result = None
        self.other_results = {}

    def run(self, *categorizations, epd_datamanager):
        if self._calculator is None:
            self._calculator = Calculator(self.input)
        self.result = self._calculator.calculate(*categorizations, epd_datamanager=epd_datamanager)

    def load_input(self, filepath):
        self.input = CalculationInput()
        self.input.load(filepath)
    def apply_method(self, method_name, method, *method_arguments):

        self.other_results[method_name] = method(self, *method_arguments)

