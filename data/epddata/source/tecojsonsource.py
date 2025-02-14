from data.epddata.source.fileepdsource import FileEpdSource
from pathlib import Path
import json

class TecoJson(FileEpdSource):
    """A class to handle EPD (Environmental Product Declaration) data stored in a JSON file according to the software
    tool Teco (Teaser+eco).

    Attributes
    ----------
    name : str
        The name for the instance.
    filepath : str or Path
        The path to the JSON file containing the EPD data. Defaults to
        'data/input/inputdata/LcaDataTeco.json' in the current working directory.
    standards : list
        Contains available standards for this source
    data : dict
        Contains the EPD data in form of a dictionary using the uuids as key
    dataset_template : EpdDataset

    Parameters
    ----------
    filepath : Path or str
        Path to the oekobaudat csv file. Defaults to: Path.cwd()  / "data" / "input" / "inputdata" / "LcaDataTeco.json"
    """

    def __init__(self, name, filepath=None):
        if not filepath:
            filepath = Path.cwd()  / "data" / "input" / "inputdata" / "LcaDataTeco.json"
        super().__init__(name, filepath)
        self.standards = ["EN15804+A1"]
        self.data = None
        self.dataset_template = None

    def load(self, dataset_template):
        """Initialize the dataset template and load the json file into the data attribute.

        Parameters
        ----------
        dataset_template : EpdDataset
            Type of EpdDataset subclass.
        """
        self.dataset_template = dataset_template()
        with open(self.filepath, "r+") as f:
            self.data = json.load(f)

    def load_epd(self, epd_dataset, epd_id):
        """Load the EPD data from the dict into the data array of an EpdDataset instance by iterating over the
        environmental indicator list and life cycle stages list of the epd_dataset to insert values at correct indices.

        Parameters
        ----------
        epd_dataset : EpdDataset
            The dataset object where EPD data will be loaded.
        epd_id : str
            The unique identifier for the EPD dataset.

        Raises
        ------
        KeyError (1)
            If the given `epd_id` does not exist in the JSON dataset.
        KeyError (2)
            If one of the life cycle stages a1, a2 or a3 could not be found during the calculation of
            life cycle stage a1_a3.
        """
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
                        epd_dataset.data[indicator_index][stage_index] = float(
                            lca_dataset_bind[indicator.abbreviation].get("a1", 0.0)
                            + lca_dataset_bind[indicator.abbreviation].get("a2", 0.0)
                            + lca_dataset_bind[indicator.abbreviation].get("a3", 0.0)
                        )

    def contains_dataset(self, epd_id):
        """Check wether a dataset exists in the loaded json data. Return True if exists, False otherwise"""
        return epd_id in self.data
