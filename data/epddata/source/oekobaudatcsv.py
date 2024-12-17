from data.epddata.source.fileepdsource import FileEpdSource
import pandas as pd
import numpy as np


class OekobaudatCsv(FileEpdSource):
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

    def __init__(self, name, filepath):
        super().__init__(name, filepath)
        self.standards = ["EN15804+A1", "EN15804+A2"]
        self.dataset_template = None
        self.data = None

    @staticmethod
    def convert_string_to_1(value, default_value=1.0):
        """Helper function to convert values in pd Dataframe"""
        try:
            return float(value)
        except ValueError:
            return default_value

    def load_epd(self, epd_dataset, epd_id):
        try:
            lca_dataset_mask = self.data['UUID'].values == epd_id
            lca_dataset_bind = self.data[lca_dataset_mask]

            epd_dataset.epd_data_id = epd_id
            epd_dataset._name = lca_dataset_bind['Name (de)'].iloc[0]
            epd_dataset.ref_flow_unit = lca_dataset_bind['Bezugseinheit'].iloc[0]
            epd_dataset.ref_flow_value = lca_dataset_bind['Bezugsgroesse'].iloc[0]
        except IndexError:
            raise Exception(f"No dataset for combination of given lca id '{epd_id}' and standard '{epd_dataset.standard}' "
                            f"was found.")

        data_array = epd_dataset.data
        grouped = lca_dataset_bind.groupby("Modul")

        test_list = [indicator.abbreviation.upper() for indicator in epd_dataset.environmental_indicators]

        for i, stage in enumerate(epd_dataset.life_cycle_stages):
            group = grouped.get_group(stage.abbreviation) if stage.abbreviation in grouped.groups else None
            if group is not None:
                values = group[test_list].iloc[0].values
                data_array[:, i] = values
            else:
                data_array[:, i] = 0.0

        a1_a3_column_index = [stage.abbreviation for stage in epd_dataset.life_cycle_stages].index("a1_a3")
        if np.count_nonzero(data_array[:, a1_a3_column_index]) == 0:
            data_array[:, a1_a3_column_index] = np.sum(data_array[:, :a1_a3_column_index], axis=1)

        epd_dataset._data = data_array


    def _load_en15804a1(self):
        use_columns_a1 = ["UUID", "Name (de)", "Name (en)", "Konformität", "Referenzjahr", "Bezugsgroesse",
                          "Bezugseinheit", "Referenzfluss-Name", "Modul",
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
        self.dataset_template = dataset_template()
        if self.dataset_template.standard == "EN15804+A1":
            lca_data_bind_pd = self._load_en15804a1()

        elif self.dataset_template.standard == "EN15804+A2":
            lca_data_bind_pd = self._load_en15804a2()

        else:
            raise ValueError(f"{self.dataset_template.standard} is not defined in Ökobaudat")

        # missing units exchanged with pcs. (pieces), fits for the current status of the database (09.01.2024)
        lca_data_bind_pd["Bezugseinheit"] = lca_data_bind_pd["Bezugseinheit"].fillna("pcs.")
        # replace missing/ NaN values in indicator columns with zero (0.0)
        for series_name, series in lca_data_bind_pd.items():
            if series.dtype.name == "float64":
                lca_data_bind_pd[series_name] = lca_data_bind_pd[series_name].fillna(0.0)
        # Transform 'Modul' entries with lower case entries and replace a1-a3 with a1_a3:
        lca_data_bind_pd["Modul"] = lca_data_bind_pd["Modul"].str.casefold()
        lca_data_bind_pd["Modul"].replace('a1-a3', 'a1_a3', inplace=True)

        self.data = lca_data_bind_pd

    def contains_dataset(self, epd_id) -> bool:
        if epd_id in self.data['UUID'].values:
            return True
        else:
            return False