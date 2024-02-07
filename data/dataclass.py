import collections
import os
import json
import pandas as pd


class DataClass(object):
    """Class for file and data bindings.

    Loads files with information about indicators, life cycle stages and lca data (json, CSV)
    and binds the data in its attributes

    Parameters
    ----------
    used_standard : str
        Indicates which standard (EN 15804+A1/ EN 15804+A2) should be used for the data ('A1', 'A2',
        default: 'A1').
    file_format : str
        File format for the lca database to be used either from teco in json format or from the Oekobaudat
        in CSV ('teco_json', 'CSV', default: 'teco_json').

    Attributes
    ----------
    used_standard : str
        Indicates which standard (EN 15804+A1/ EN 15804+A2) should be used for the data ('A1', 'A2',
        default: 'A1')
    file_format : str
        File format for the lca database to be used either from teco in json format or from the Oekobaudat
        in CSV ('teco_json', 'CSV', default: 'teco_json').
    life_cycle_stages_bind : list
        A list containing the life cycle stages according to EN 15978
    indicators_bind : list
        A list containing the environmental indicators dependent on the used_standard
    lca_data_bind : collections.OrderedDictionary (for teco_json) or pd DataFrame (for CSV)
        Binding containing the lca datasets dependent on the file_format
    path_life_cycle_stages : str
        Full path to life_cycle_stages_en_15978.json
        Default: dynamic_lca_draft/data/input/inputdata/life_cycle_stages_en_15978.json
    path_indicators: str
        Full path to indicators_en_15804_a1.json or indicators_en_15804_a2.json dependent on the
        used_standard (default: 'A1')
    path_lca_data : str
        Full path to LcaDataTeco.json or OBD_2023_I_2024-01-09T12_49_34.csv dependet on the
        file_format (default: 'teco_json')

    """
    def __init__(self, used_standard="A1", file_format="teco_json"):
        self.used_standard = used_standard
        self.file_format = file_format

        self.life_cycle_stages_bind = None
        self.indicators_bind = None
        self.lca_data_bind = None
        # self.teco_json_lca_data_bind = None
        # self.csv_lca_data_bind = None
        # self.xml_lca_data_bind = None

        self.path_life_cycle_stages = get_full_path(os.path.join(
            "data", "input", "inputdata", "life_cycle_stages_en_15978.json"
        ))

        if self.used_standard == "A1":
            self.path_indicators = get_full_path(os.path.join(
                "data", "input", "inputdata", "indicators_en_15804_a1.json"
            ))
        elif self.used_standard == "A2":
            self.path_indicators = get_full_path(os.path.join(
                "data", "input", "inputdata", "indicators_en_15804_a2.json"
            ))
            # teco_json enthält nur Datensätze für A1 -> csv einziges Dateiformat für A2
            self.file_format = "csv"

        if self.file_format == "teco_json":
            self.path_lca_data = get_full_path(os.path.join(
                "data", "input", "inputdata", "LcaDataTeco.json"
            ))
        elif self.file_format == "csv":
            # database download: 09.01.2024
            self.path_lca_data = get_full_path(os.path.join(
                "data", "input", "inputdata", "OBD_2023_I_2024-01-09T12_49_34.csv"
            ))
        elif self.file_format == "xml":
            pass

        self.load_life_cycle_stages()
        self.load_indicators()
        self.load_lca_data_binding()

    def load_lca_data_binding(self):
        """Loads the lca datasets from the file into the lca_data_bind parameter or for CSV data calls the
        load_and_preprocess_csv_binding method"""
        if self.path_lca_data.endswith("json") and os.path.isfile(self.path_lca_data):
            try:
                with open(self.path_lca_data, "r+") as f:
                    self.lca_data_bind = json.load(
                        f, object_pairs_hook=collections.OrderedDict
                    )
            except json.decoder.JSONDecodeError:
                print("The json LCA-data file seems to be broken.")
        elif self.path_lca_data.endswith("csv") and os.path.isfile(self.path_lca_data):
            self.load_and_preprocess_csv_binding()

    def load_life_cycle_stages(self):
        """Loads the life cycle stages defined in the json file as a list into the life cycle stages binding"""
        if self.path_life_cycle_stages.endswith("json") and os.path.isfile(self.path_life_cycle_stages):
            try:
                with open(self.path_life_cycle_stages, "r+") as f:
                    self.life_cycle_stages_bind = json.load(
                        f, object_pairs_hook=collections.OrderedDict
                    )
                    self.life_cycle_stages_bind = list(self.life_cycle_stages_bind["LifeCycleStages"])
            except json.decoder.JSONDecodeError:
                print("The json file for the life cycle stages seems to be broken.")

    def load_indicators(self):
        """Loads the indicators defined in the json files for the two possible standards (A1, A2) as a list into
        the life cycle stages binding"""
        if self.path_indicators.endswith("json") and os.path.isfile(self.path_indicators):
            try:
                with open(self.path_indicators, "r+") as f:
                    self.indicators_bind = json.load(
                        f, object_pairs_hook=collections.OrderedDict
                    )
                    if self.used_standard == "A1":
                        self.indicators_bind = list(self.indicators_bind["indicators_en_15804_a1"])
                    elif self.used_standard == "A2":
                        self.indicators_bind = list(self.indicators_bind["indicators_en_15804_a2"])
            except json.decoder.JSONDecodeError:
                print("The json file for the environmental indicators seems to be broken.")

    def load_and_preprocess_csv_binding(self):
        """Method to load data from the Oekobaudat CSV into a pandas DataFrame and preprocess it. Sorting out not
        needed columns and datasets dependent on the used_standard (CSV contains unsorted datasets for multiple
        standards) as well as aligning the syntax of the datasets for later use resulting in a lca_data_binding with a
        pd DataFrame to load single datasets from"""

        dtype_dict = {"UUID": str,
                      "Name (de)": str,
                      "Name (en)": str,
                      "Konformität": str,
                      "Referenzjahr": int,
                      # "Bezugsgroesse": float, # Error, da Strings in Spalte enthalten sind -> converter s.u.
                      "Bezugseinheit": str,
                      "Referenzfluss-Name": str,
                      "Modul": str,
                      "PERE": float, "PERM": float, "PERT": float, "PENRE": float, "PENRM": float, "PENRT": float,
                      "SM": float,
                      "RSF": float, "NRSF": float, "FW": float, "HWD": float, "NHWD": float, "RWD": float, "CRU": float,
                      "MFR": float, "MER": float, "EEE": float, "EET": float, "GWP": float, "ODP": float, "POCP": float,
                      "AP": float, "EP": float, "ADPE": float, "ADPF": float,
                      "AP (A2)": float, "GWPtotal (A2)": float, "GWPbiogenic (A2)": float, "GWPfossil (A2)": float,
                      "GWPluluc (A2)": float, "ETPfw (A2)": float, "PM (A2)": float, "EPmarine (A2)": float,
                      "EPfreshwater (A2)": float, "EPterrestrial (A2)": float, "HTPc (A2)": float, "HTPnc (A2)": float,
                      "IRP (A2)": float, "SOP (A2)": float, "ODP (A2)": float, "POCP (A2)": float, "ADPF (A2)": float,
                      "ADPE (A2)": float, "WDP (A2)": float}

        if self.used_standard == "A1":
            use_columns_a1 = ["UUID", "Name (de)", "Name (en)", "Konformität", "Referenzjahr", "Bezugsgroesse",
                              "Bezugseinheit", "Referenzfluss-Name", "Modul",
                              "PERE", "PERM", "PERT", "PENRE", "PENRM", "PENRT", "SM", "RSF", "NRSF", "FW",
                              "HWD", "NHWD", "RWD", "CRU", "MFR", "MER", "EEE", "EET",
                              "GWP", "ODP", "POCP", "AP", "EP", "ADPE", "ADPF"]
            lca_data_bind_pd = pd.read_csv(self.path_lca_data, sep=';', encoding="ISO-8859-1",
                                           usecols=use_columns_a1, converters={'Bezugsgroesse': convert_string_to_1},
                                           dtype=dtype_dict)
            # delete all rows containing Datasets for Standard +A2
            lca_data_bind_pd = lca_data_bind_pd.drop(
                lca_data_bind_pd[
                    (lca_data_bind_pd.Konformität == "'DIN EN 15804+A2'")
                    | (lca_data_bind_pd.Konformität == "'EN 15804+A2'")
                    | (lca_data_bind_pd.Konformität == "'DIN EN 15804+A2' / 'ISO 14025'")
                    | (lca_data_bind_pd.Konformität == "'EN 15804+A2' / 'ISO 14025'")
                    | (lca_data_bind_pd.Konformität == "'EN 15804+A2' / 'EN 16485'")
                    ].index)
            if len(lca_data_bind_pd.loc[lca_data_bind_pd['Konformität'].str.contains('A2')]) != 0:
                print(f"Warning: LCA dataset binding still contains "
                      f"{len(lca_data_bind_pd.loc[lca_data_bind_pd['Konformität'].str.contains('A2')])} datasets"
                      f"conform to standard A2")

        elif self.used_standard == "A2":
            use_columns_a2 = ["UUID", "Name (de)", "Name (en)", "Konformität", "Referenzjahr", "Bezugsgroesse",
                              "Bezugseinheit", "Referenzfluss-Name", "Modul",
                              "PERE", "PERM", "PERT", "PENRE", "PENRM", "PENRT", "SM", "RSF", "NRSF", "FW",
                              # "Additional environmental impact indicators" with high uncertainties (Ökobaudat Manual)
                              # -> excluded here (If the use is desired, add to json and column names below!!!)
                              # "HTPc (A2)", "HTPnc (A2)", "PM (A2)", "IRP (A2)", "ETPfw (A2)", "SOP (A2)",
                              "HWD", "NHWD", "RWD", "CRU", "MFR", "MER", "EEE", "EET",
                              "AP (A2)", "GWPtotal (A2)", "GWPbiogenic (A2)", "GWPfossil (A2)", "GWPluluc (A2)",
                              "EPmarine (A2)", "EPfreshwater (A2)", "EPterrestrial (A2)", "ODP (A2)", "POCP (A2)",
                              "ADPF (A2)", "ADPE (A2)", "WDP (A2)",
                               ]
            lca_data_bind_pd = pd.read_csv(self.path_lca_data, sep=';', encoding="ISO-8859-1",
                                           usecols=use_columns_a2, converters={'Bezugsgroesse': convert_string_to_1},
                                           dtype=dtype_dict)
            lca_data_bind_pd = lca_data_bind_pd.drop(
                lca_data_bind_pd[
                    (lca_data_bind_pd.Konformität == "'DIN EN 15804'")
                    | (lca_data_bind_pd.Konformität == "'EN 15804'")
                    | (lca_data_bind_pd.Konformität == "'DIN EN 15804' / 'ISO 14025'")
                    | (lca_data_bind_pd.Konformität == "'EN 15804' / 'ISO 14025'")
                    | (lca_data_bind_pd.Konformität == "'EN 15804' / 'ISO 14025' / 'OEKOBAUDAT Entry Level Compliance'")
                    ].index)
            # Renaming columns to fit the syntax of indicators_en_15804_a2.json
            rename_columns_a2 = {"AP (A2)": "AP", "GWPtotal (A2)": "GWP-TOTAL", "GWPbiogenic (A2)": "GWP-BIOGEN",
                              "GWPfossil (A2)": "GWP-FOSSIL", "GWPluluc (A2)": "GWP-LULUC", "EPmarine (A2)": "EP-MARINE",
                              "EPfreshwater (A2)": "EP-FRESHWATER", "EPterrestrial (A2)": "EP-TERRESTRIAL",
                              "ODP (A2)": "ODP", "POCP (A2)": "POCP", "ADPF (A2)": "ADPF", "ADPE (A2)": "ADPE",
                              "WDP (A2)": "WDP"}
            lca_data_bind_pd.rename(columns=rename_columns_a2, inplace=True)

        # missing units exchanged with pcs. (pieces), fits for the current status of the database (09.01.2024)
        lca_data_bind_pd["Bezugseinheit"] = lca_data_bind_pd["Bezugseinheit"].fillna("pcs.")
        # replace missing/ NaN values in indicator columns with zero (0.0)
        for series_name, series in lca_data_bind_pd.items():
            if series.dtype.name == "float64":
                lca_data_bind_pd[series_name] = lca_data_bind_pd[series_name].fillna(0.0)
        # Transform 'Modul' entries with lower case entries and replace a1-a3 with a1_a3:
        lca_data_bind_pd["Modul"] = lca_data_bind_pd["Modul"].str.casefold()
        lca_data_bind_pd["Modul"].replace('a1-a3', 'a1_a3', inplace=True)

        self.lca_data_bind = lca_data_bind_pd


def convert_string_to_1(value, default_value=1.0):
    """Helper function to convert values in pd Dataframe"""
    try:
        return float(value)
    except ValueError:
        return default_value


def get_full_path(relative_path):
    """Helper function to build full paths to files

    Parameters
    ----------
    relative_path : str
        relative path to file with filename starting with first folder hierarchy inside dynamic_lca_draft

    Returns
    ----------
    full_path : str
        full path to file
    """
    directory = os.path.dirname(__file__)
    src = "dynamic_lca_draft"
    last_index = directory.rfind(src)
    project_path = os.path.join(directory[:last_index], src)
    full_path = os.path.join(project_path, relative_path)

    return full_path
