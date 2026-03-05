import pandas as pd


class CalculationInput(object):
    """Class that parses the input csv file and prepares the input for the calculator utilizing database structures from
    the pandas library

    Attributes
    ----------
    calculation_df : pd.Dataframe
        Contains the calculation dataframe -> input csv + Calculation id - defined partitions
    subset_df : pd.Dataframe
        For every partition, contains the subset value for the calculation df entries
    partition_df : pd.Dataframe
        Contains the defined partitions from the input csv
    _calculation_header : list
        Header for the calculation_df
    _subset_header : list
        Header for the subset_df
    _partition_header : list
        Header for the partition_df
    """
    def __init__(self):
        self._calculation_header = ["calculation_id", "#amount", "#uuid", "#epd_name", "#scenario", "#replacement_cycle", "#comment"]
        self._mandatory_columns = ["#amount", "#uuid", "#epd_name", "#scenario"]

        self._subset_header = ["calculation_id", "subset_name", "partition_id"]
        self._partition_header = ["partition_id", "partition_name"]

        self.calculation_df = None
        self.subset_df = None
        self.partition_df = None

    def load(self, filepath, sep = ","):
        """Method to set the class attributes (dataframes with calculation info, partitions, categories)
        based on the input csv

        Parameters
        ----------
        filepath : str
            Path to the input csv file
        """
        import_df = self._load_and_preprocess_csv(filepath, sep = sep)

        self._initialize_calculation_dataframes(import_df)

    def _load_and_preprocess_csv(self, filepath, sep = ","):
        """Method to load the input csv into a pandas dataframe, clean UUID column from whitespaces, create an index
        column and a column for the calculation of all individual datasets as a separate partition

        Parameters
        ----------
        filepath : str
            Path to the input csv file
        """
        df = (pd.read_csv(filepath, sep=sep, encoding='ANSI'))

        try:
            df[self._mandatory_columns]
        except KeyError as error:
            raise KeyError(f"Column names from input csv do not match the specifications for obligatory column names."
                           f"Columns must include: '{self._mandatory_columns}'. {error}")

        df["uuid"] = df["uuid"].str.strip()
        df.insert(0, self._calculation_header[0], df.index)
        df.insert(len(df.columns), "unique_epd", df["epd_name"])
        return df

    def _initialize_calculation_dataframes(self, import_df):
        """Initialize internal calculation, partition, and subset dataframes from a preprocessed import dataframe.

        Parameters
        ----------
        import_df : pd.DataFrame
            The loaded and preprocessed csv as dataframe
        """
        #todo: check for datatypes of subsets. In the moment a subset of the name "00" will be transformed into an integer
        # all subsets should be strings to ensure consistency

        cols_to_copy = [c for c in self._calculation_header if c in import_df]
        calculations = import_df[cols_to_copy].copy()

        categories = []
        partitions = []

        for partition_idx, partition_name in enumerate(import_df.drop(columns=self._calculation_header).columns):
            partitions.append([partition_idx, partition_name])
            subset_dict = {
                self._subset_header[0]: calculations[self._calculation_header[0]].values.tolist(),
                self._subset_header[1]: import_df[partition_name].values.tolist(),
                self._subset_header[2]: partition_idx
            }
            categories.append(subset_dict)

        self.calculation_df = calculations
        self.partition_df = pd.DataFrame(partitions, columns=self._partition_header)
        self.subset_df = pd.concat([pd.DataFrame(entry) for entry in categories])

    def get_calculation_df_for_partitions(self, *partitions):
        """Return a calculation-ready dataframe filtered by one or more partitions.

        Parameters
        ----------
        *partitions : str
            The subset names as strings according to which the calculation will be made

        Returns
        -------
        calc_df : pd.DataFrame
            Contains information for the calculation; UUIDs, amounts, subset/ categories
        """
        if len(partitions) == 1:
            return self._filter_by_single_partition(partitions[0])
        return self._filter_by_multiple_partitions(partitions)

    def _filter_by_single_partition(self, partition):
        """Creates/ Returns a dataframe for the calculator by joining the initial calculation dataframe (created by
        loading the input) with the subset values of the partition according to which the datasets will be
        calculated

        Parameters
        ----------
        partition : str
            Name of the partition

        Returns
        -------
        calc_df : pd.DataFrame
            Initial calculation dataframe filtered by partition. Contains only rows relevant for the given partition.
        """
        chosen_partition = self.partition_df.query(
            "partition_name == @partition"
        )
        associated_subset_values = pd.merge(
            self.subset_df, chosen_partition, on="partition_id", how='inner'
        )
        return pd.merge(
            self.calculation_df, associated_subset_values, on="calculation_id", how='inner'
        )

    def _filter_by_multiple_partitions(self, partitions):
        """Creates/ Returns a dataframe for the calculator by joining the initial calculation dataframe (created by
        loading the input) with the subset values of the partition combination according to which the datasets
        will be calculated.

        Parameters
        ----------
        partitions : tuple
            Contains the strings of the partitions for the partition combination

        Returns
        -------
        calc_df : pd.DataFrame
            Initial calculation dataframe filtered by partitions. Contains only rows relevant for the partitions.
        """
        subset_values_df = self.subset_df.merge(
            self.partition_df, on='partition_id'
        )
        combined_categories_pivot_df = (
            subset_values_df.pivot(
            index='calculation_id', columns='partition_name', values='subset_name'
            )
            .reset_index()
        )
        combined_categories_pivot_df = combined_categories_pivot_df.where(pd.notna(combined_categories_pivot_df), '')

        combined_categories_pivot_df['subset_name'] = combined_categories_pivot_df[list(partitions)].apply(tuple, axis=1)
        calc_df = self.calculation_df.merge(
            combined_categories_pivot_df, on='calculation_id', how='left'
        )
        calc_df.insert(2, "partition_name", ' '.join(partitions))
        return calc_df
