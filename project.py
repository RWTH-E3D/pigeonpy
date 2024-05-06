from pathlib import Path
import data.output.lca_data_output as lca_data_output
from logic.calculator.calculator import Calculator


class Project(object):

    def __init__(self):
        self._name = "Project"

        self.calculations = {}
        self.results = {}


    def add_calculation(self, name, path, *categorizations):
        new_calculator = Calculator()
        new_calculator.import_calculation(path)
        self.calculations[name] = {"calculator": new_calculator, "categorizations": categorizations}

    def add_categorization(self, calculation_name, *categorizations):
        existing_categorizations = list(self.calculations[calculation_name]["categorizations"])
        new_categorizations = existing_categorizations + list(categorizations)
        self.calculations[calculation_name].update({"categorizations": tuple(new_categorizations)})

    def remove_categorization(self, calculation_name, *categorizations):
        existing_categorizations = list(self.calculations[calculation_name]["categorizations"])
        for categorization in categorizations:
            existing_categorizations.remove(categorization)
        self.calculations[calculation_name].update({"categorizations": tuple(existing_categorizations)})

    def calculate_all(self):

        for name, obj in self.calculations.items():
            self.results[name] = {}
            tmp_calculator = obj["calculator"]
            for categorization in obj["categorizations"]:

                if type(categorization) == tuple:
                    tmp_result = tmp_calculator.calculate(categorization[0],
                                                          categorization[1])
                else:
                    tmp_result = tmp_calculator.calculate(categorization)
                self.results[name].update({str(categorization): tmp_result})

    def export_results(self, directory_path=None, all_results=False, one_file=False, calculation_name=None, categorization_name=None, dataset_name=None):

        export_dir_path = Path()
        if directory_path is None:
            path_to_output_folder = Path(__file__).parent / "data" / "output"
            Path.mkdir(path_to_output_folder / self._name, exist_ok=True)
            export_dir_path = path_to_output_folder / self._name
        elif Path(directory_path).is_dir() and Path(directory_path).exists:
            export_dir_path = directory_path
        else:
            print("Specify a valid directory path or none.")

        if all_results and not one_file:
            for name, calculation in self.results.items():
                for categorization in calculation:
                    name_for_file = name + " " + str(categorization) + ".csv"
                    file_path = export_dir_path / name_for_file

                    lca_data_output.export_calculated_dataframe(df=self.results[name][categorization],
                                                                path =file_path,
                                                                drop_rows=True)
        elif all_results and one_file:
            pass

        # Export methods to be revised in the future



input_csv_path = "C:\\Users\\J.K. Rollerblade\\PycharmProjects\\dynamic_lca_draft\\data\\input\\inputdata\\input_data_dynamic_csv_V2.CSV"

test = Project()
test._name = "Test_project"

test.add_calculation("2 Single Categorizations", input_csv_path, "Category1", "Year Disposal")

test.add_calculation("Tuple Categorization", input_csv_path)
test.add_categorization("Tuple Categorization", "test123", ("Category1","Year Installation for components or occurence for consumption"), "test456")
test.remove_categorization("Tuple Categorization", "test456", "test123")

test.calculate_all()
test.export_results(all_results=True)

temp = test.results['2 Single Categorizations']['Category1']["Foundation"]
print(temp)

