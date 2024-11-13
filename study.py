from logic.calculation.calculation import Calculation
from logic.calculation.calculator import Calculator
from logic.calculation.calculationinput import CalculationInput
from logic.epddataset.epddataset import EpdDataset
from logic.goalandscope import GoalAndScope
from data.epddata.epddatamanager import EpdDataManager
import pandas as pd


class Study(object):
    def __init__(self, study_name):

        self.study_name = study_name
        self.goal_and_scope = None
        self.calculation = Calculation()
        self.epd_datamanager = EpdDataManager()

    def run_calculation(self, *categorizations):
        self.calculation.run(*categorizations, epd_datamanager=self.epd_datamanager,
                             goal_and_scope=self.goal_and_scope)


    def load_calculation_input(self, filepath):
        self.calculation.load_input(filepath)
    def apply_method(self, method_name, method, *method_arguments):

        self.calculation.apply_method(method_name, method, *method_arguments)
