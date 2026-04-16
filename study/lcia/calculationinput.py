import csv
import pandas as pd


class CsvValidationError(Exception):
    """Custom exception for input CSV issues."""
    pass

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
    _mandatory_columns : list
        Columns that are mandatory in the input csv. Marked with the hash sign '#', they represent pre-defined columns
        that are not part of partitions.
    _subset_header : list
        Header for the subset_df
    _partition_header : list
        Header for the partition_df
    """
    def __init__(self):
        self._calculation_header = ["calculation_id", "amount", "epd_id", "epd_name", "scenario", "replacement_cycle", "comment"]
        self._mandatory_columns = ["#amount", "#epd_id", "#epd_name", "#scenario"]

        self._input_csv_dtypes = {
                "#amount": "float64",
                "#replacement_cycle": "Int64" # Capital 'I' to allow NaN values
        }

        self._subset_header = ["calculation_id", "subset_name", "partition_id"]
        self._partition_header = ["partition_id", "partition_name"]

        self.calculation_df = None
        self.subset_df = None
        self.partition_df = None

        self.validation_error = CsvValidationError()

    def load(self, filepath, sep = ","):
        """Method to set the class attributes (dataframes with calculation info, partitions, categories)
        based on the input csv

        Parameters
        ----------
        filepath : str
            Path to the input csv file
        sep : str
            Separator used in the input csv file
        """
        import_df = self._validate_load_and_preprocess_csv(filepath, sep = sep)

        self._initialize_calculation_dataframes(import_df)

    def _validate_load_and_preprocess_csv(self, filepath, sep = ","):
        """Validates the input CSV file in terms of: Correct column numbers in each row (too few/many), empty lines,
        correct dtypes, required columns, and required values in mandatory columns.
        Removes the '#' sign in front of mandatory columns for the resulting dataframe.

        Parameters
        ----------
        filepath : str
            Path to the input CSV file
        sep : str
            Separator used in CSV file

        Raises
        ------
        CsvValidationError : Exception
            See class definition above. Includes the original Error type in the error message.
        """
        self._validate_column_counts(filepath, sep)

        try:
            df = pd.read_csv(
                filepath,
                sep=sep,
                na_values=["", '"', "'", "NA", "NaN", None],
                on_bad_lines="error",
                skip_blank_lines=True, # Skips only if line is fully empty
                dtype="string", # All columns with dtype "string" first, because type casting throws more detailed error
                keep_default_na=False
            )
        except pd.errors.ParserError as e:
            raise CsvValidationError(
                f"Parsing of input csv file failed: {e}"
            ) from e

        df = df.dropna(how="all") # drop entirely empty rows, in case they slipped through the read_csv process
        df = df.astype(self._input_csv_dtypes) # Cast #amount and #replacement_cycle columns to correct types

        try:
            df[self._mandatory_columns]
        except KeyError as e:
            raise CsvValidationError(
                f"Column names from input csv do not match the specifications for obligatory column "
                f"names. Columns must include:\n '{self._mandatory_columns}' \n{e}"
            ) from e

        # columns with values required in each element; scenario is allowed to have empty elements
        na_mask = df[["#amount", "#epd_id", "#epd_name"]].isna().any(axis=1)
        if na_mask.any():
            bad_rows = df.loc[na_mask]
            pd.set_option('display.expand_frame_repr', False)
            raise CsvValidationError(
                f"\n{na_mask.sum()} rows have missing values in required columns "
                f"{'#amount', '#epd_id', '#epd_name'}.\n"
                f"Problematic rows:\n {bad_rows}"
            )

        df.columns = [column.replace("#", "") for column in df.columns]

        df["epd_id"] = df["epd_id"].str.strip()
        df.insert(0, self._calculation_header[0], df.index)
        df.insert(len(df.columns), "unique_epd", df["epd_name"])
        return df

    @staticmethod
    def _validate_column_counts(filepath, sep):
        """Checks input csv file for correct column counts in each row based on the amount of columns in the header.
        Pandas read_csv method only checks for rows with too many columns and has a bug if the error is present in the
        first line after the header (https://github.com/pandas-dev/pandas/issues/47490).

        Parameters
        ----------
        filepath : str
            Path to input CSV file
        sep
            Separator used in input CSV file
        """
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.reader(f, delimiter=sep)

            try:
                header = next(reader)
            except StopIteration:
                raise CsvValidationError("Input CSV file is empty")

            number_of_columns = len(header)

            for line_no, row in enumerate(reader, start=2):
                if not row or all(cell.strip() == "" for cell in row):
                    continue

                if len(row) != number_of_columns:
                    raise CsvValidationError(
                        f"Column-count mismatch in line {line_no}: "
                        f"expected {number_of_columns} columns (from header), got {len(row)}.\n"
                        f"Please check separators/quoting in that line."
                    )

    def _initialize_calculation_dataframes(self, import_df):
        """Initialize internal calculation, partition, and subset dataframes from a preprocessed import dataframe.

        Parameters
        ----------
        import_df : pd.DataFrame
            The loaded and preprocessed csv as dataframe
        """
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
            Contains information for the calculation; epd_id, amounts, subset/ categories
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
