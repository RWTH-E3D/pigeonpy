from pathlib import Path
from data.dataclass import DataClass
import data.output.lca_data_output as lca_data_output
from data.output.study import Study


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

    _name : str
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

    def __init__(self, used_standard = "A2", lca_data_input_format="csv"):
        self._name = "Project"
        self.studies = {}


    def add_study(self, *categorizations, study_name, input_csv_path, used_standard, lca_input_format):
        """Adds a study to the studies dictionary.

        This method needs a name for identification, a path to an input csv file and the standard as well
        as the input format for the lca data to create an instance of the Study class.

        Parameters
        ----------
        study_name : str
            A name to identify the calculation
        input_csv_path : str
            A path to the input csv file containing information about the required datasets and
            categorizations
        used_standard : str
            The standard used for the study
        lca_input_format : str
            The file format that is used for the study
        categorizations : str or tuple of strings (optional)
            The categorizations according to which the calculation should be carried out. It is possible to
            pass the categorizations in this method as a single string or a tuple of strings but it is also
            possible to pass nothing and add the categorizations later with the related method.

        """

        new_study = Study(study_name=study_name,
                          input_csv_path=input_csv_path,
                          used_standard=used_standard,
                          lca_data_input_format=lca_input_format,
                          categorizations=categorizations)
        self.studies[study_name] = {"input csv path": input_csv_path, "used standard": used_standard,
                                    "lca data input format": lca_input_format, "Study object": new_study}

        return new_study

    def remove_study(self, study_name):
        """Removes a study entry with the given name from the studies dictionary.

        Parameters:
        ----------
        name : str
            The name for which the study should be removed.

        """

        try:
            del self.studies[study_name]
        except KeyError as Error:
            print(f"Study for removal not found. {Error}")

    def get_study(self, study_name):
        study = self.studies.get(study_name)
        if not study:
            raise ValueError(f"No study found with name {study_name}")
        return study

    def calculate_all_studies(self):
        """Method to calculate every entry from the studies dictionary and save its results in the
        Study instance.

        Calls the calculate method from the Calculator class for every categorization contained in the
        categorizations part of the study dictionary entry and saves the results in the results
        dictionary under the name of the calculation and the categorization.

        """
        for study_name, study_object in self.studies.items():
            study_object['Study object'].calculate_study()


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
