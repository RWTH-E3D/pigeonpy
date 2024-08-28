from data.dataclass import DataClass
from logic.calculator import Calculator
from logic.epddataset.epddataset import EpdDataset
from logic.goalandscope import GoalAndScope
import pandas as pd


class Study(object):
    def __init__(self,
                 study_name,
                 input_csv_path,
                 lca_data_input_format,
                 used_standard=None,
                 categorizations=None):

        self.study_name = study_name
        self.categorizations = categorizations

        self.goal_and_scope = GoalAndScope()

        self.used_standard = used_standard
        self.lca_data_input_format = lca_data_input_format
        self.__input_csv_path = input_csv_path
        self.data_class = self.initiate_dataclass()
        self.__calculator_object = self.__create_calculator_object()

        self._used_stages = self.data_class.life_cycle_stages_bind
        self._used_indicators = self.data_class.indicators_bind

        self.grouped_results = {}
        self.epd_results = pd.Series
        self.overall_results = EpdDataset()

    def set_goal_and_scope(self, standard, considered_stages=[], considered_indicators=[], description=""):
        """Function to set goal and scope of the study

        Parameters
        ----------
        standard : str
            EPD standard used in the study for calculation
        considered_stages : list
            List of all life cycle stages considered in the study. Default is [] which is equal to evry stage from the used EPD
            standard
        considered_indicators : list
            List of all
        description

        Returns
        -------

        """

        self.goal_and_scope = GoalAndScope(standard, considered_stages, considered_indicators, description)


    def initiate_dataclass(self):
        new_dataclass = DataClass(used_standard=self.used_standard, file_format=self.lca_data_input_format)
        return new_dataclass

    def __create_calculator_object(self):
        new_calculator = Calculator(used_standard=self.used_standard, lca_data_input_format=self.lca_data_input_format)
        new_calculator.import_calculation(self.__input_csv_path)
        return new_calculator

    def add_categorizations(self, *categorizations):
        """Method to add a categorization to an existing calculation.

        Parameters
        ----------
        categorizations : str or tuple of strings
            Can be a single string, a tuple of two strings or a combination of the two which are added
            to the calculations dictionary entry specified by the calculation_name

        """

        existing_categorizations = list(self.categorizations)
        new_categorizations = existing_categorizations + list(categorizations)
        self.categorizations = tuple(new_categorizations)

    def remove_categorizations(self, *categorizations):
        """Method to remove a categorization from an existing calculation

        Parameters
        ----------
        categorizations : str or tuple of strings
            The categorizations which should be removed

        """

        existing_categorizations = list(self.categorizations)
        for categorization in categorizations:
            existing_categorizations.remove(categorization)
        self.categorizations = tuple(existing_categorizations)

    def calculate_study(self):
        for categorization in self.categorizations:
            if type(categorization) == tuple:
                epd_quantities = self.__calculator_object.calculate_epd_quantities(*categorization,
                                                                                   dataclass=self.data_class)
            else:
                epd_quantities = self.__calculator_object.calculate_epd_quantities(categorization,
                                                                                   dataclass=self.data_class)
            self.grouped_results[str(categorization)] = self.__calculator_object.calculate_categorizations(
                epd_quantities)

            # if self._used_indicators != self.dataclass.indicators_bind or self._used_stages != self.dataclass.life_cycle_stages_bind:
            #     new_result = self.exclude_stages_and_indicators()

        epd_results = self.__calculator_object.calculate_epd_quantities("epd categorization",
                                                                        dataclass=self.data_class)
        self.epd_results = self.__calculator_object.calculate_categorizations(epd_results)
        self.overall_results = self.epd_results.sum()

    def exclude_stages(self, *stages_to_exclude):
        to_exclude = set()
        for stage in stages_to_exclude:
            if isinstance(stage, str):
                to_exclude.add(stage)
            elif isinstance(stage, list):
                to_exclude.update(stage)
            else:
                raise ValueError("Stages must be either given as lowercase strings or a list of strings")

        self._used_stages = [stage for stage in self._used_stages if stage["abbreviation"] not in to_exclude]

    def exclude_indicators(self, *indicators_to_exclude):
        to_exclude = set()
        for indicator in indicators_to_exclude:
            if isinstance(indicator, str):
                to_exclude.add(indicator)
            elif isinstance(indicator, list):
                to_exclude.update(indicator)
            else:
                raise ValueError("Indicators must be either given as lowercase strings or a list of strings")

        self._used_indicators = [indicator for indicator in self._used_indicators if
                                 indicator["abbreviation"] not in to_exclude]

    """
    def exclude_stages_and_indicators(self):
        # create new datasets with instances of OtherDataset and the information of the
        # datasets from the calculated dataframe for all datasets inside
        for index, dataset in self.grouped_results.items():
            new_dataset = OtherDataset(used_standard=dataset.used_standard,
                                       used_stages=self.used_stages,
                                       used_indicators=self.used_indicators)
            new_dataset.load_data_from_dataset(dataset)
            self.grouped_results[index] = new_dataset

        # Alternative:
        # use the existing datasets and exclude the stages not needed by using the _get_index methods from
        # EpdDataset class --> for later visualizations or exports probably more performative than creating new instances
    """

    def compare(self, other_result_to_compare_with):
        pass

    def normalize(self, data_for_normalization):
        pass

    def weight_results(self):
        pass
