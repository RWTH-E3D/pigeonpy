import pandas as pd
import numpy as np


class CalculationInput(object):
    """Class that parses the input csv file and prepares the input for the calculator utilizing database structures from
    the pandas library

    Attributes
    ----------
    calculation_df : pd.Dataframe
        Contains the calculation dataframe -> input csv + Calculation id - defined partitions
    category_df : pd.Dataframe
        For every partition, contains the category value for the calculation df entries
    partition_df : pd.Dataframe
        Contains the defined partitions from the input csv
    _calculation_header : list
        Header for the calculation_df
    _category_header : list
        Header for the category_df
    _partition_header : list
        Header for the partition_df
    """
    def __init__(self):
        self._calculation_header = ["Calculation_id", "Amount", "UUID", "EPD name", "Comment", "Service life"]
        self._category_header = ["Calculation_id", "Category_name", "Partition_id"]
        self._partition_header = ["Partition_id", "Partition_name"]

        self.calculation_df = None
        self.category_df = None
        self.partition_df = None

    def load(self, filepath, individual_column_names=False):
        """Method to set the class attributes (dataframes with calculation info, partitions, categories)
        based on the input csv

        Parameters
        ----------
        filepath : str
            Path to the input csv file
        individual_column_names : bool
            If False, matches columns by names defined in calculation header; otherwise, uses predefined positions.
        """

        import_df = self._load_and_preprocess_csv(filepath)

        if individual_column_names:
            self._populate_dataframes_positional(import_df)
        else:
            self._populate_dataframes_dynamically(import_df)

    def _load_and_preprocess_csv(self, filepath):
        """Method to load the input csv into a pandas dataframe, clean UUID column from whitespaces, create an index
        column and a column for the calculation of all individual datasets as a separate partition"""
        df = (pd.read_csv(filepath, sep=',', encoding='ANSI'))
        df['UUID'] = df['UUID'].str.strip()
        df.insert(0, self._calculation_header[0], df.index)
        df.insert(len(df.columns), "Individual EPD", df["EPD name"])
        return df

    def _populate_dataframes_dynamically(self, import_df):
        """Populate the dataframes for calculation, category and partition dynamically based on the defined
        headers"""
        try:
            calculations = import_df[self._calculation_header].copy()
        except KeyError as error:
            raise KeyError(f"Column names from input csv do not match the specifications for obligatory column names."
                           f"Columns must include: '{self._calculation_header[1:]}'. {error}")
        categories = []
        partitions = []
        for partition_idx, partition_name in enumerate(import_df.columns[len(self._calculation_header):]):
            partitions.append([partition_idx, partition_name])
            category_dict = {
                self._category_header[0]: calculations[self._calculation_header[0]].values.tolist(),
                self._category_header[1]: import_df[partition_name].values.tolist(),
                self._category_header[2]: partition_idx
            }
            categories.append(category_dict)

        self.calculation_df = calculations
        self.partition_df = pd.DataFrame(partitions, columns=self._partition_header)
        self.category_df = pd.concat([pd.DataFrame(entry) for entry in categories])

    def _populate_dataframes_positional(self, import_df):
        """For the case that column names in the input csv differ from those defined in the headers, this method
        populates the calculation, partition and category dataframe based on the positions, not the column names
        so the first 6 columns can be named differently but must respect the correct column order."""
        partitions = [[idx, col] for idx, col in enumerate(import_df.columns[5:])]
        categories = []
        calculations = []

        for idx, row in import_df.iloc[:, :5].iterrows():
            calculations.append([idx] + row.tolist())

        for col_idx, col_name in partitions:
            col_values = import_df.iloc[:, col_idx + 5]
            for idx, val in enumerate(col_values):
                categories.append([idx, val, col_idx])

        self.calculation_df = pd.DataFrame(calculations, columns=self._calculation_header)
        self.category_df = pd.DataFrame(categories, columns=self._category_header)
        self.partition_df = pd.DataFrame(partitions, columns=self._partition_header)

    def calculate_component_replacements(self, observation_period):
        """Calculates the amount of replacements for every entry of the input dataframe based on the observation period
        specified in the Goal and Scope of the study"""
        self.calculation_df["Replacements"] = np.ceil(observation_period / self.calculation_df["Service life"]) - 1

    def select_by_partition(self, *partitions):
        """Method to create a dataframe for the calculation which additionally contains the category or category
        combination according to which the datasets will be calculated.

        Parameters
        ----------
        *partitions: str
            The category names as strings according to which the calculation will be made

        Returns
        -------
        calc_df: pd.DataFrame
            Contains information for the calculation; UUIDs, amounts, category/ categories
        """
        if len(partitions) == 1:
            return self._filter_by_single_partition(partitions[0])
        return self._filter_by_multiple_partitions(partitions)

    def _filter_by_single_partition(self, partition):
        """Creates/ Returns a dataframe for the calculator by joining the initial calculation dataframe (created by
        loading the input) with the category values of the  according to which the datasets will be
        calculated"""
        chosen_partition = self.partition_df.query(
            "Partition_name == @partition"
        )
        associated_category_values = pd.merge(
            self.category_df, chosen_partition, on="Partition_id", how='inner'
        )
        return pd.merge(
            self.calculation_df, associated_category_values, on="Calculation_id", how='inner'
        )

    def _filter_by_multiple_partitions(self, partitions):
        """Creates/ Returns a dataframe for the calculator by joining the initial calculation dataframe (created by
        loading the input) with the category values of the partition combination according to which the datasets
        will be calculated."""

        category_values_df = self.category_df.merge(
            self.partition_df, on='Partition_id'
        )
        combined_categories_pivot_df = (
            category_values_df.pivot(
            index='Calculation_id', columns='Partition_name', values='Category_name'
            )
            .reset_index()
            .fillna('')
        )
        combined_categories_pivot_df['Category_name'] = combined_categories_pivot_df[list(partitions)].apply(tuple, axis=1)
        calc_df = self.calculation_df.merge(
            combined_categories_pivot_df, on='Calculation_id', how='left'
        )
        calc_df.insert(2, "Partition_name", ' '.join(partitions))
        return calc_df
