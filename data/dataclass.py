import collections
import os
import json
import pandas as pd


class DataClass(object):
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
        # database download: 09.01.2024
        self.path_lca_data_csv = get_full_path(os.path.join(
                    "data", "input", "inputdata", "OBD_2023_I_2024-01-09T12_49_34.csv"
                ))

        if self.used_standard == "A1":
            self.path_indicators = get_full_path(os.path.join(
                    "data", "input", "inputdata", "indicators_en_15804_a1.json"
                ))
            if self.file_format == "teco_json":
                self.path_lca_data = get_full_path(os.path.join(
                    "data", "input", "inputdata", "LcaDataTeco.json"
                ))
            elif self.file_format == "csv":
                self.path_lca_data = self.path_lca_data_csv
            elif self.file_format == "xml":
                pass
        elif self.used_standard == "A2":
            pass

        self.load_lca_data_binding()
        self.load_life_cycle_stages()
        self.load_indicators()

    def load_lca_data_binding(self):
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
        if self.path_life_cycle_stages.endswith("json") and os.path.isfile(self.path_life_cycle_stages):
            try:
                with open(self.path_life_cycle_stages, "r+") as f:
                    self.life_cycle_stages_bind = json.load(
                        f, object_pairs_hook=collections.OrderedDict
                    )
            except json.decoder.JSONDecodeError:
                print("The json file for the life cycle stages seems to be broken.")

    def load_indicators(self):
        if self.path_indicators.endswith("json") and os.path.isfile(self.path_indicators):
            try:
                with open(self.path_indicators, "r+") as f:
                    self.indicators_bind = json.load(
                        f, object_pairs_hook=collections.OrderedDict
                    )
            except json.decoder.JSONDecodeError:
                print("The json file for the environmental indicators seems to be broken.")

    def load_and_preprocess_csv_binding(self):
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
                      "AP": float, "EP": float, "ADPE": float, "ADPF": float}

        if self.used_standard == "A1":
            use_columns_a1 = ["UUID", "Name (de)", "Name (en)", "Konformität", "Referenzjahr", "Bezugsgroesse",
                              "Bezugseinheit", "Referenzfluss-Name", "Modul",
                              "PERE", "PERM", "PERT", "PENRE", "PENRM", "PENRT", "SM", "RSF", "NRSF", "FW",
                              "HWD", "NHWD", "RWD", "CRU", "MFR", "MER", "EEE", "EET",
                              "GWP", "ODP", "POCP", "AP", "EP", "ADPE", "ADPF"]
            lca_data_bind_pd = pd.read_csv("OBD_2023_I_2024-01-09T12_49_34.csv", sep=';', encoding="ISO-8859-1",
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
                              "HWD", "NHWD", "RWD", "CRU", "MFR", "MER", "EEE", "EET",
                              "AP(A2)", "GWPtotal(A2)", "GWPbiogenic(A2)", "GWPfossil(A2)", "GWPluluc(A2)", "ETPfw(A2)",
                              "PM(A2)", "EPmarine(A2)", "EPfreshwater(A2)", "EPterrestrial(A2)", "HTPc(A2)",
                              "HTPnc(A2)", "IRP(A2)", "SOP(A2)", "ODP(A2)", "POCP(A2)", "ADPF(A2)", "ADPE(A2)",
                              "WDP(A2)"]
            lca_data_bind_pd = pd.read_csv("OBD_2023_I_2024-01-09T12_49_34.csv", sep=';', encoding="ISO-8859-1",
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

        lca_data_bind_pd = lca_data_bind_pd.reset_index()
        # missing units exchanged with pcs. (pieces), fits for the current status of the database (09.01.2024)
        lca_data_bind_pd["Bezugseinheit"] = lca_data_bind_pd["Bezugseinheit"].fillna("pcs.")

        self.lca_data_bind = lca_data_bind_pd


def convert_string_to_1(value, default_value=1.0):
    try:
        return float(value)
    except ValueError:
        return default_value


def get_full_path(relative_path):

    directory = os.path.dirname(__file__)
    src = "dynamic_lca_draft"
    last_index = directory.rfind(src)
    project_path = os.path.join(directory[:last_index], src)
    full_path = os.path.join(project_path, relative_path)

    return full_path
