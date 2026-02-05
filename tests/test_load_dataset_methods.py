from data.epddata.source.oekobaudatcsv import OekobaudatCsv
from data.epddata.source.tecojsonsource import TecoJson
from data.epddata.source.oekobaudatapi import OekobaudatAPI
from data.epddata.epddatamanager import EpdDataManager
from epd.epddataset.en15804A1dataset import En15804A1Dataset
from epd.epddataset.en15804A2dataset import En15804A2Dataset
from utility import get_latest_oekobaudat_csv
from pathlib import Path
import unittest


class TestLoadDatasetMethods(unittest.TestCase):
    """Test methods to load datasets from epd sources"""

    def setUp(self):
        self.epd_datamanager_a1 = EpdDataManager(dataset_template=En15804A1Dataset)
        self.epd_datamanager_a2 = EpdDataManager(dataset_template=En15804A2Dataset)

        self.latest_oekobaudat_dl = get_latest_oekobaudat_csv()
        self.oekobaudat_a1_dl = get_latest_oekobaudat_csv(datastock_uuid="4fb60595-6b0d-4c4f-af9d-403df2bcaf30")

        self.oekobaudat_a1 = OekobaudatCsv(self.oekobaudat_a1_dl)
        self.epd_datamanager_a1.register_source("oekobaudat_a1", self.oekobaudat_a1)
        self.oekobaudat_a1_dropped_duplicates = self.oekobaudat_a1.data.drop_duplicates(subset="UUID")

        self.oekobaudat_a2 = OekobaudatCsv(self.latest_oekobaudat_dl)
        self.epd_datamanager_a2.register_source("oekobaudat_a2", self.oekobaudat_a2)
        self.oekobaudat_a2_dropped_duplicates = self.oekobaudat_a2.data.drop_duplicates(subset="UUID")

        self.oekobaudat_api_a1 = OekobaudatAPI()
        self.epd_datamanager_a1.register_source("oekobaudat_api_a1", self.oekobaudat_api_a1)

        self.oekobaudat_api_a2 = OekobaudatAPI()
        self.epd_datamanager_a2.register_source("oekobaudat_api_a2", self.oekobaudat_api_a2)

        self.teco_json_filepath = Path.cwd() / ".." / "data" / "input" / "inputdata" / "LcaDataTeco.json"
        self.teco_json = TecoJson(filepath=self.teco_json_filepath)
        self.epd_datamanager_a1.register_source("teco_json", self.teco_json)
        self.teco_json.data.pop("version")

        self.test_dataset_a1 = En15804A1Dataset()
        self.test_dataset_a2 = En15804A2Dataset()

    def test_teco_json_load_every_datasets(self):
        for key in self.teco_json.data:
            self.test_dataset_a1.load_lca_dataset(key, self.epd_datamanager_a1, source_key="teco_json")

    def test_teco_json_invalid_lca_id_given(self):
        exception_msg = f"No dataset for given epd id 'test123' was found."
        with self.assertRaises(Exception, msg=exception_msg):
            self.test_dataset_a1.load_lca_dataset("test123", self.epd_datamanager_a1, source_key="teco_json")


    def test_csv_a1_load_every_dataset(self):
        number_of_datasets_a1 = 0
        for index, row in self.oekobaudat_a1_dropped_duplicates.iterrows():
            # print(index)

            self.test_dataset_a1.load_lca_dataset(
                row["UUID"],
                self.epd_datamanager_a1,
                source_key="oekobaudat_a1",
                scenario="use_first"
            )

            number_of_datasets_a1 += 1
        print(f"Datasets A1: {number_of_datasets_a1}")

    def test_csv_a2_load_every_dataset(self):
        """Check with latest Oekobaudat version downloaded via API"""
        number_of_datasets_a2 = 0
        for index, row in self.oekobaudat_a2_dropped_duplicates.iterrows():
            # print(index)

            self.test_dataset_a2.load_lca_dataset(
                row["UUID"],
                self.epd_datamanager_a2,
                source_key="oekobaudat_a2",
                scenario="use_first"
            )

            number_of_datasets_a2 += 1
        print(f"Datasets A2: {number_of_datasets_a2}")

    def test_oekobaudat_api_a1_load_datasets_with_uuid_from_csv(self):
        number_of_datasets_api_a1 = 0
        for index, row in self.oekobaudat_a1_dropped_duplicates.iterrows():
            print(row["UUID"])

            self.test_dataset_a1.load_lca_dataset(
                row["UUID"],
                self.epd_datamanager_a1,
                source_key="oekobaudat_api_a1",
                scenario="use_first"
            )

            number_of_datasets_api_a1 += 1
        print(f"EN15804+A1 compliant datasets loaded via OekobaudatAPI via UUIDs from csv: {number_of_datasets_api_a1}")

    def test_oekobaudat_api_a2_load_datasets_with_uuid_from_csv(self):
        number_of_datasets_api_a2 = 0
        print(len(self.epd_datamanager_a2._fetched_datasets))
        for index, row in self.oekobaudat_a2_dropped_duplicates.iterrows():
            print(row["UUID"])

            self.test_dataset_a2.load_lca_dataset(
                row["UUID"],
                self.epd_datamanager_a2,
                source_key="oekobaudat_api_a2",
                scenario="use_first"
            )

            number_of_datasets_api_a2 += 1
        print(f"EN15804+A2 compliant datasets loaded via OekobaudatAPI via UUIDs from csv: {number_of_datasets_api_a2}")

    def tearDown(self):
        self.latest_oekobaudat_dl.unlink()
        self.oekobaudat_a1_dl.unlink()

if __name__ == '__main__':
    unittest.main(verbosity=2)