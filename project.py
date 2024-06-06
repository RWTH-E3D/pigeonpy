from pathlib import Path
import data.output.lca_data_output as lca_data_output
from logic.calculator.calculator import Calculator


class Project(object):
    """This is the top class for creating projects to carry out LCA calculations

    The class can be used for script based interaction with the program. It contains methods for adding
    and removing calculations, adding and removing categorizations for specific calculations, calculating
    the existing calculations saved in a dictionary as class attribute and for exporting calculated results.
    A calculation represents an instance of the Calculator class together with an input csv that contains
    information for the calculation and the various categorizations for which calculations are to be
    performed.

    Attributes
    ----------

    name : str
        Name of the project with the default name "Project"
    used_standard : str
        The standard (A1 or A2) used in the project
    lca_data_input_format : str
        The data type for the input format (csv, teco_json)
    calculations : dict
        A dictionary containing the different calculations with name, path for the input csv and
        categorizations for calculation
    results : dict
        A dictionary containing the calculated results. Results created by the "calculate_all" method are
        saved into the result dictionary under the same name with which they are registered in the
        calculations dictionary.

    """

    def __init__(self):
        self._name = "Project"
        self.used_standard = "A2"
        self.lca_data_input_format = "csv"

        self.calculations = {}
        self.results = {}


    def add_calculation(self, name, path, *categorizations):
        """Adds a calculation to the calculations dictionary.

        This method needs a name for identification and a path to an input csv file to create an
        instance of the Calculator class to save everything together as one entry in the dictionary.

        Parameters
        ----------
        name : str
            A name to identify the calculation
        path : str
            A path to the input csv file containing information about the required datasets and
            categorizations
        categorizations : str or tuple of strings (optional)
            The categorizations according to which the calculation should be carried out. It is possible to
            pass the categorizations in this method as a single string or a tuple of strings but it is also
            possible to pass nothing and add the categorizations later with the related method.

        """

        new_calculator = Calculator(used_standard=self.used_standard, lca_data_input_format=self.lca_data_input_format)
        new_calculator.import_calculation(path)
        self.calculations[name] = {"calculator": new_calculator, "categorizations": categorizations}

    def remove_calculation(self, name):
        """Removes a calculation entry with the given name from the calculations dictionary.

        Parameters:
        ----------
        name : str
            The name for which the calculation should be removed.

        """

        try:
            del self.calculations[name]
        except KeyError as Error:
            print(f"Calculation for removal not found. {Error}")

    def add_categorization(self, calculation_name, *categorizations):
        """Method to add a categorization to an existing calculation.

        Parameters
        ----------
        calculation_name : str
            Name of the calculation the categorization should be added to
        categorizations : str or tuple of strings
            Can be a single string, a tuple of two strings or a combination of the two which are added
            to the calculations dictionary entry specified by the calculation_name

        """

        existing_categorizations = list(self.calculations[calculation_name]["categorizations"])
        new_categorizations = existing_categorizations + list(categorizations)
        self.calculations[calculation_name].update({"categorizations": tuple(new_categorizations)})

    def remove_categorization(self, calculation_name, *categorizations):
        """Method to remove a categorization from an existing calculation

        Parameters
        ----------
        calculation_name : str
            Name of the calculation the categorization should be removed from
        categorizations : str or tuple of strings
            The categorizations which should be removed

        """

        existing_categorizations = list(self.calculations[calculation_name]["categorizations"])
        for categorization in categorizations:
            existing_categorizations.remove(categorization)
        self.calculations[calculation_name].update({"categorizations": tuple(existing_categorizations)})

    def calculate_all(self):
        """Method to calculate every entry from the calculations dictionary and save its results in the
        result dictionary.

        Calls the calculate method from the Calculator class for every categorization contained in the
        categorizations part of the calculation dictionary entry and saves the results in the results
        dictionary under the name of the calculation and the categorization.

        """

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

    def export_results(self, directory_path=None,
                       all_results=True,
                       one_file=False,
                       calculation_name=None,
                       categorization_name=None,
                       dataset_name=None):
        """Method to export calculated datasets to csv by calling the associated function in the lca_data_output
        module. (Export methods to be revised in the future)

        Parameters
        ----------
        directory_path : str
            Path to the directory where the results should be exported to
        all_results : boolean
            If True all calculated results are exported. If False the calculation_name and/or categorization
            name and/or dataset_name need to be specified (False case not yet implemented)
        one_file : boolean
            If True all results are exported to one csv file. If False a csv file created for every categorization.
        calculation_name : str (Not yet implemented)
            The calculation which should be exported specified by name
        categorization_name : str (Not yet implemented)
            The categorization which should be exported specified by name (or tuple of names)
        dataset_name : str (Not yet implemented)
            A single dataset which should be exported specified by a category or a tuple of two categories

        """

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


