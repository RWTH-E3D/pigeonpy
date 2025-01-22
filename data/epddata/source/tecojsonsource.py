from data.epddata.source.fileepdsource import FileEpdSource
from pathlib import Path
import json

class TecoJson(FileEpdSource):

    def __init__(self, name, filepath=None):
        if not filepath:
            filepath = Path.cwd()  / "data" / "input" / "inputdata" / "LcaDataTeco.json"
        super().__init__(name, filepath)
        self.standards = ["EN15804+A1"]
        self.data = None
        self.dataset_template = None

    def load(self, dataset_template):
        self.dataset_template = dataset_template()
        with open(self.filepath, "r+") as f:
            self.data = json.load(f)

    def load_epd(self, epd_dataset, epd_id):
        try:
            lca_dataset_bind = self.data[epd_id]
        except KeyError:
            raise KeyError(f"No dataset for given epd id '{epd_id}' was found.")

        epd_dataset.epd_data_id = epd_id
        epd_dataset.name = lca_dataset_bind["name"]
        epd_dataset.ref_flow_unit = lca_dataset_bind["ref_flow"]["unit"]
        epd_dataset.ref_flow_value = lca_dataset_bind["ref_flow"]["value"]

        for indicator_index, indicator in enumerate(epd_dataset.environmental_indicators):
            if indicator.abbreviation in lca_dataset_bind.keys():
                for stage_index, stage in enumerate(epd_dataset.life_cycle_stages):
                    if stage.abbreviation in lca_dataset_bind[indicator.abbreviation]:
                        epd_dataset.data[indicator_index][stage_index] = float(
                            (lca_dataset_bind[indicator.abbreviation][stage.abbreviation]))
                    elif (stage.abbreviation == "a1_a3") and (
                            "a1_a3" not in lca_dataset_bind[indicator.abbreviation]):
                        # Alle vorhandenen Werte werden aufaddiert
                        # Warnung: Bei Verrechnung mit anderen Datensätzen wird die stage a1_a3 im Ergebnis Datensatz
                        # nicht mehr die Summe aus a1,a2,a3 ergeben
                        try:
                            epd_dataset.data[indicator_index][stage_index] = float(
                                lca_dataset_bind[indicator.abbreviation]["a1"]
                                + lca_dataset_bind[indicator.abbreviation]["a2"]
                                + lca_dataset_bind[indicator.abbreviation]["a3"]
                            )
                        except KeyError:
                            # print(f"Stage a1_a3 of dataset '{(lca_dataset_bind['name'])}' with id: '{given_lca_id}' for "
                            #       f"indicator '{indicator.abbreviation}' is calculated without stage {Error},"
                            #       f"because it is not contained in the dataset.")
                            epd_dataset.data[indicator_index][stage_index] = float(
                                lca_dataset_bind[indicator.abbreviation].get("a1", 0.0)
                                + lca_dataset_bind[indicator.abbreviation].get("a2", 0.0)
                                + lca_dataset_bind[indicator.abbreviation].get("a3", 0.0)
                            )

    def contains_dataset(self, epd_id):
        if epd_id in self.data:
            return True
        else:
            return False
