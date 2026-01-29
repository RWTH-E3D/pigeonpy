from data.epddata.source.fileepdsource import FileEpdSource
import pandas as pd
import numpy as np


class OekobaudatCsv(FileEpdSource):
    """Class that contains methods for fetching datasets in XML format from the oekobaudat API and loading them into
    EpdDataset objects

    Class variables
    ----------
    a1_aliases : list
        Contains the different terminologies used in the Oekobaudat database csv to indicate the standard EN15804+A1
        for a dataset
    a2_aliases : list
        Contains the different terminologies used in the Oekobaudat database csv to indicate the standard EN15804+A2
        for a dataset
    dtype_dict : dict
        Maps the columns of the Oekobaudat csv to dtypes for the file to dataframe processing in pandas

    Attributes
    ----------
    filepath : str
        Path to the Oekobaudat csv file
    standards : list
        Available standards in the Oekobaudat
    dataset_template: EpdDataset
        To determine the used standard for the Oekobaudat csv and to create instances of that class in the EpdDataManager
    data: pd.DataFrame
        Holds the dataframe containing the processed Oekobaudat csv, i.e. all available datasets for the standard
        indicated by the dataset_template

    Parameters
    ----------
    filepath : Path or str
        Path to the oekobaudat csv file
    """

    a1_aliases = ["'DIN EN 15804'", "'EN 15804'", "'DIN EN 15804' / 'ISO 14025'",
                       "'EN 15804' / 'ISO 14025' / 'OEKOBAUDAT Entry Level Compliance'"]
    a2_aliases = ["'DIN EN 15804+A2'", "'EN 15804+A2'", "'DIN EN 15804+A2' / 'ISO 14025'",
                       "'EN 15804+A2' / 'ISO 14025'", "'EN 15804+A2' / 'EN 16485'", "'EN 15804+A2 (EF 3.1)'"]

    dtype_dict = {
        "UUID": str,
        "Name (de)": str,
        "Name (en)": str,
        "Konformität": str,
        "Referenzjahr": "Int64",
        "Bezugseinheit": str,
        "Referenzfluss-Name": str,
        "Modul": str,
        "Szenario": str,
        "PERE": float, "PERM": float, "PERT": float, "PENRE": float, "PENRM": float, "PENRT": float,
        "SM": float,
        "RSF": float, "NRSF": float, "FW": float, "HWD": float, "NHWD": float, "RWD": float,
        "CRU": float,
        "MFR": float, "MER": float, "EEE": float, "EET": float, "GWP": float, "ODP": float,
        "POCP": float,
        "AP": float, "EP": float, "ADPE": float, "ADPF": float,
        "AP (A2)": float, "GWPtotal (A2)": float, "GWPbiogenic (A2)": float, "GWPfossil (A2)": float,
        "GWPluluc (A2)": float, "ETPfw (A2)": float, "PM (A2)": float, "EPmarine (A2)": float,
        "EPfreshwater (A2)": float, "EPterrestrial (A2)": float, "HTPc (A2)": float,
        "HTPnc (A2)": float,
        "IRP (A2)": float, "SOP (A2)": float, "ODP (A2)": float, "POCP (A2)": float,
        "ADPF (A2)": float,
        "ADPE (A2)": float, "WDP (A2)": float
    }

    def __init__(self, filepath):
        super().__init__(filepath)
        self.standards = ["EN15804+A1", "EN15804+A2"]
        self.dataset_template = None
        self.data = None

    def load_epd(self, epd_dataset, epd_id, scenario):
        """Loads the EPD data for a given epd_id from the Oekobaudat dataframe into the provided epd_dataset instance
        by calling associated methods.

        Parameters
        ----------
        epd_dataset : Dataset
            An instance of the dataset class to load EPD data into.
        epd_id : str
            The UUID of the EPD to load.
        scenario : str
            Name of the scenario to be used in the dataset if specified
        """
        lca_dataset_bind = self._filter_dataset(epd_id, epd_dataset)

        if lca_dataset_bind["Modul"].duplicated().any(): # True -> dataset contains scenarios
            lca_dataset_bind = self._handle_scenarios(lca_dataset_bind, scenario, epd_id)

        data_array = self._populate_data_array(epd_dataset, lca_dataset_bind)
        data_array = self._handle_a1_a3_column(epd_dataset, data_array)
        epd_dataset.data = data_array

        self._populate_metadata(epd_dataset, lca_dataset_bind, epd_id, scenario)


    def _filter_dataset(self, epd_id, epd_dataset):
        """Filters the main data for the given epd_id.

        Raises
        ------
        ValueError: If no matching dataset is found.
        """
        dataset_binding = self.data[self.data['UUID'] == epd_id]
        if dataset_binding.empty:
            raise ValueError(
                f"No dataset found for EPD UUID '{epd_id}' and standard '{epd_dataset.standard}' in loaded version of "
                f"Oekobaudat csv '{self.filepath.name}'."
            )
        return dataset_binding

    @staticmethod
    def _handle_scenarios(lca_dataset_bind, scenario, epd_id):
        """

        Parameters
        ----------
        lca_dataset_bind : pd.DataFrame
            Contains the rows of the loaded Oekobaudat csv file that match the epd_id given to the load_epd method. If
            scenarios exist in the dataset, there are multiple rows for the same module present in this lca_dataset_bind
        scenario : str
            Name of the scenario to use or None
        epd_id : str
            UUID used to create the lca_dataset_bind and given to this method for clarity in case an error is raised
        Returns
        -------
        lca_dataset_bind : pd:DataFrame
            The same as above but without duplicate Modul entries. Only the Modul entry for the specified scenario
        """
        duplicate_mask = lca_dataset_bind["Modul"].duplicated(keep=False)
        available_scenarios = (
            lca_dataset_bind.loc[duplicate_mask, ["Modul", "Szenario"]]
            .dropna(subset=["Szenario"])
            .drop_duplicates()
        )

        if pd.notna(scenario) and scenario is not None:

            # test_mode for testing if datasets can be loaded with test_load_dataset_methods.py
            if scenario == "test_mode":
                return lca_dataset_bind

            # Scenarios present and user specified a scenario, but it is not in the available scenarios
            if scenario not in available_scenarios["Szenario"].values:
                raise Exception(
                    f"KeyError during loading of dataset with id '{epd_id}'.\n"
                    f"Given scenario '{scenario}' does not match with available scenarios.\n "
                    f"Available scenarios:\n{available_scenarios}"
                )

            lca_dataset_bind = lca_dataset_bind[
                ~duplicate_mask | (lca_dataset_bind["Szenario"] == scenario)
                ]
        else:
            # Scenarios present, but nothing specified by user
            raise Exception(
                f"Error during loading of dataset. Dataset with id '{epd_id}' contains scenarios. Please specify one.\n"
                f"Available scenarios:\n{available_scenarios}"
            )

        return lca_dataset_bind

    @staticmethod
    def _populate_metadata(epd_dataset, lca_dataset_bind, epd_id, scenario):
        """Populates metadata fields in the EPD dataset."""
        epd_dataset.epd_data_id = epd_id
        epd_dataset.name = lca_dataset_bind['Name (de)'].iloc[0]
        epd_dataset.ref_flow_unit = lca_dataset_bind['Bezugseinheit'].iloc[0]
        epd_dataset.ref_flow_value = lca_dataset_bind['Bezugsgroesse'].iloc[0]
        epd_dataset.scenario = scenario

    @staticmethod
    def _populate_data_array(epd_dataset, lca_dataset_bind):
        """Populates the data array in the EPD dataset using grouped lifecycle stages and indicators."""
        data_array = epd_dataset.data
        grouped = lca_dataset_bind.groupby("Modul")
        indicator_abbreviations = [ind.abbreviation.upper() for ind in epd_dataset.environmental_indicators]

        for stage_index, stage in enumerate(epd_dataset.life_cycle_stages):
            if stage.abbreviation in grouped.groups:
                group = grouped.get_group(stage.abbreviation)
                values = group[indicator_abbreviations].iloc[0].to_numpy()
                data_array[:, stage_index] = values
            else:
                data_array[:, stage_index] = 0.0

        return data_array

    @staticmethod
    def _handle_a1_a3_column(epd_dataset, data_array):
        """Ensures that the A1-A3 column is populated correctly."""
        a1_a3_column_index = [stage.abbreviation for stage in epd_dataset.life_cycle_stages].index("a1_a3")
        if np.count_nonzero(data_array[:, a1_a3_column_index]) == 0:
            data_array[:, a1_a3_column_index] = np.sum(data_array[:, :a1_a3_column_index], axis=1)

        return data_array

    def _load_en15804a1(self):
        use_columns_a1 = ["UUID", "Name (de)", "Name (en)", "Konformität", "Referenzjahr", "Bezugsgroesse",
                          "Bezugseinheit", "Referenzfluss-Name", "Modul", "Szenario",
                          "PERE", "PERM", "PERT", "PENRE", "PENRM", "PENRT", "SM", "RSF", "NRSF", "FW",
                          "HWD", "NHWD", "RWD", "CRU", "MFR", "MER", "EEE", "EET",
                          "GWP", "ODP", "POCP", "AP", "EP", "ADPE", "ADPF"]
        lca_data_bind_pd = pd.read_csv(self.filepath, sep=';', encoding="ISO-8859-1",
                                       usecols=use_columns_a1, converters={'Bezugsgroesse': self.convert_string_to_1},
                                       dtype=self.dtype_dict)
        
        lca_data_bind_pd = lca_data_bind_pd.drop(lca_data_bind_pd[lca_data_bind_pd.Konformität.isin(self.a2_aliases)].index)
        if len(lca_data_bind_pd.loc[lca_data_bind_pd['Konformität'].str.contains('A2')]) != 0:
            print(f"Warning: LCA dataset binding still contains "
                  f"{len(lca_data_bind_pd.loc[lca_data_bind_pd['Konformität'].str.contains('A2')])} datasets"
                  f"conform to standard A2")

        return lca_data_bind_pd

    def _load_en15804a2(self):
        use_columns_a2 = ["UUID", "Name (de)", "Name (en)", "Konformität", "Referenzjahr", "Bezugsgroesse",
                          "Bezugseinheit", "Referenzfluss-Name", "Modul", "Szenario",
                          "PERE", "PERM", "PERT", "PENRE", "PENRM", "PENRT", "SM", "RSF", "NRSF", "FW",
                          # "Additional environmental impact indicators" with high uncertainties (see Ökobaudat Manual)
                          # -> excluded here (If the use is desired, add to json and column names below!!!)
                          # "HTPc (A2)", "HTPnc (A2)", "PM (A2)", "IRP (A2)", "ETPfw (A2)", "SOP (A2)",
                          "HWD", "NHWD", "RWD", "CRU", "MFR", "MER", "EEE", "EET",
                          "AP (A2)", "GWPtotal (A2)", "GWPbiogenic (A2)", "GWPfossil (A2)", "GWPluluc (A2)",
                          "EPmarine (A2)", "EPfreshwater (A2)", "EPterrestrial (A2)", "ODP (A2)", "POCP (A2)",
                          "ADPF (A2)", "ADPE (A2)", "WDP (A2)",
                          ]
        lca_data_bind_pd = pd.read_csv(self.filepath, sep=';', encoding="ISO-8859-1",
                                       usecols=use_columns_a2, converters={'Bezugsgroesse': self.convert_string_to_1},
                                       dtype=self.dtype_dict)
        lca_data_bind_pd = lca_data_bind_pd.drop(lca_data_bind_pd[lca_data_bind_pd.Konformität.isin(self.a1_aliases)].index)

        # Renaming columns to fit the syntax of indicators_en_15804_a2.json
        rename_columns_a2 = {"AP (A2)": "AP", "GWPtotal (A2)": "GWP-TOTAL", "GWPbiogenic (A2)": "GWP-BIOGEN",
                             "GWPfossil (A2)": "GWP-FOSSIL", "GWPluluc (A2)": "GWP-LULUC",
                             "EPmarine (A2)": "EP-MARINE",
                             "EPfreshwater (A2)": "EP-FRESHWATER", "EPterrestrial (A2)": "EP-TERRESTRIAL",
                             "ODP (A2)": "ODP", "POCP (A2)": "POCP", "ADPF (A2)": "ADPF", "ADPE (A2)": "ADPE",
                             "WDP (A2)": "WDP"}
        lca_data_bind_pd.rename(columns=rename_columns_a2, inplace=True)

        return lca_data_bind_pd

    def load(self, dataset_template):
        """Loads the section of the Oekobaudat csv database that contains datasets for the respective standard indicated
         by the dataset template into the data attribute as a pandas Dataframe.

        Parameters
        ----------
        dataset_template : EpdDataset
            Class alias of the dataset class to load EPD data into.
        """
        self.dataset_template = dataset_template
        if self.dataset_template.standard == "EN15804+A1":
            lca_data_bind_pd = self._load_en15804a1()
        elif self.dataset_template.standard == "EN15804+A2":
            lca_data_bind_pd = self._load_en15804a2()
        else:
            raise ValueError(f"{self.dataset_template.standard} is not defined in Ökobaudat")

        self.data = self._clean_and_transform_data(lca_data_bind_pd)

    def contains_dataset(self, epd_id) -> bool:
        """Checks the data attribute containing the pd.DataFrame with the Oekobaudat for existence of a dataset given
        by the epd_id"""
        if epd_id in self.data['UUID'].values:
            return True
        else:
            return False

    @staticmethod
    def _clean_and_transform_data(lca_data_bind_pd):
        """Preprocesses the data by handling missing units, replacing missing indicator values,
        and transforming the 'Modul' column."""
        # missing units exchanged with pcs. (pieces), fits for the current status of the database (09.01.2024)
        lca_data_bind_pd["Bezugseinheit"] = lca_data_bind_pd["Bezugseinheit"].fillna("pcs.")

        # replace missing/ NaN values in indicator columns with zero (0.0)
        for series_name, series in lca_data_bind_pd.items():
            if series.dtype.name == "float64":
                lca_data_bind_pd[series_name] = lca_data_bind_pd[series_name].fillna(0.0)

        # Transform 'Modul' entries with lower case entries and replace a1-a3 with a1_a3:
        lca_data_bind_pd["Modul"] = lca_data_bind_pd["Modul"].str.casefold()
        lca_data_bind_pd.replace({'Modul': 'a1-a3'}, 'a1_a3', inplace=True)
        return lca_data_bind_pd

    @staticmethod
    def convert_string_to_1(value, default_value=1.0):
        """Helper function used while reading the csv file to convert elements in the 'Bezugsgroesse' column of the
        Oekobaudat csv either into float and if not possible the value 1.0"""
        try:
            return float(value)
        except ValueError:
            return default_value