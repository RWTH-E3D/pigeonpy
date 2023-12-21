import collections
import os
import json


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

        if self.used_standard == "A1":
            self.path_indicators = get_full_path(os.path.join(
                    "data", "input", "inputdata", "indicators_en_15804_a1.json"
                ))
            if self.file_format == "teco_json":
                self.path_lca_data = get_full_path(os.path.join(
                    "data", "input", "inputdata", "LcaDataTeco.json"
                ))
            elif self.file_format == "csv":
                pass
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


def get_full_path(relative_path):

    directory = os.path.dirname(__file__)
    src = "dynamic_lca_draft"
    last_index = directory.rfind(src)
    project_path = os.path.join(directory[:last_index], src)
    full_path = os.path.join(project_path, relative_path)

    return full_path
