from data.epddata.source.tecojsonsource import TecoJson
from data.epddata.source.oekobaudatcsv import OekobaudatCsv
from data.epddata.source.oekobaudatapi import OekobaudatApi
from data.epddata.source.epdnorwaycsv import EpdNorwayCsv
from data.epddata.source.epdnorwayapi import EpdNorwayApi
from data.epddata.epddatamanager import EpdDataManager
from epd.epddataset.en15804A1dataset import En15804A1Dataset
from epd.epddataset.en15804A2dataset import En15804A2Dataset
from utility import get_soda4lca_node_datastock
from pathlib import Path
import unittest


class TestLoadDatasetMethods(unittest.TestCase):
    """Test methods to load datasets from epd sources"""

    def setUp(self):
        self.epd_datamanager_a1 = EpdDataManager(dataset_template=En15804A1Dataset)
        self.epd_datamanager_a2 = EpdDataManager(dataset_template=En15804A2Dataset)

        self.test_dataset_a1 = En15804A1Dataset()
        self.test_dataset_a2 = En15804A2Dataset()


    """Teco JSON"""
    def test_teco_json_load_every_datasets(self):
        self.teco_json = TecoJson(
            filepath=Path(__file__).resolve().parents[1] / "data" / "input" / "inputdata" / "LcaDataTeco.json"
        )
        self.epd_datamanager_a1.register_source("teco_json", self.teco_json)
        self.teco_json.data.pop("version")
        
        for key in self.teco_json.data:
            self.test_dataset_a1.load_lca_dataset(key, self.epd_datamanager_a1, source_key="teco_json")

    def test_teco_json_invalid_lca_id_given(self):
        self.teco_json = TecoJson(
            filepath=Path(__file__).resolve().parents[1] / "data" / "input" / "inputdata" / "LcaDataTeco.json"
        )
        self.epd_datamanager_a1.register_source("teco_json", self.teco_json)
        self.teco_json.data.pop("version")
        
        exception_msg = f"No dataset for given epd id 'test123' was found."
        with self.assertRaises(Exception, msg=exception_msg):
            self.test_dataset_a1.load_lca_dataset("test123", self.epd_datamanager_a1, source_key="teco_json")


    """Ökobaudat"""
    def test_oekobaudat_csv_a1_load_every_dataset(self):
        """Based on EN15804+A1 datastock version (4fb60595-6b0d-4c4f-af9d-403df2bcaf30), downloaded with
        get_soda4lca_node_datastock() function."""
        self.oekobaudat_csv_a1_dl = get_soda4lca_node_datastock(
            root="https://oekobaudat.de/OEKOBAU.DAT/resource",
            datastock_uuid="4fb60595-6b0d-4c4f-af9d-403df2bcaf30",
            export_format="csv"
        )
        self.oekobaudat_csv_a1 = OekobaudatCsv(self.oekobaudat_csv_a1_dl)
        self.epd_datamanager_a1.register_source("oekobaudat_csv_a1", self.oekobaudat_csv_a1)
        self.oekobaudat_csv_a1_dropped_duplicates = self.oekobaudat_csv_a1.data.drop_duplicates(subset="UUID")

        number_of_datasets_a1 = 0
        for index, row in self.oekobaudat_csv_a1_dropped_duplicates.iterrows():
            # print(index)

            self.test_dataset_a1.load_lca_dataset(
                row["UUID"],
                self.epd_datamanager_a1,
                source_key="oekobaudat_csv_a1",
                scenario="use_first"
            )

            number_of_datasets_a1 += 1
        print(f"Datasets A1: {number_of_datasets_a1}")

        self.oekobaudat_csv_a1_dl.unlink()

    def test_oekobaudat_csv_a2_load_every_dataset(self):
        """Based on latest available Ökobaudat datastock, downloaded with get_soda4lca_node_datastock() function."""
        self.latest_oekobaudat_dl = get_soda4lca_node_datastock(root="https://oekobaudat.de/OEKOBAU.DAT/resource")
        self.oekobaudat_csv_a2 = OekobaudatCsv(self.latest_oekobaudat_dl)
        self.epd_datamanager_a2.register_source("oekobaudat_csv_a2", self.oekobaudat_csv_a2)
        self.oekobaudat_csv_a2_dropped_duplicates = self.oekobaudat_csv_a2.data.drop_duplicates(subset="UUID")

        number_of_datasets_a2 = 0
        for index, row in self.oekobaudat_csv_a2_dropped_duplicates.iterrows():
            # print(index)

            self.test_dataset_a2.load_lca_dataset(
                row["UUID"],
                self.epd_datamanager_a2,
                source_key="oekobaudat_csv_a2",
                scenario="use_first"
            )

            number_of_datasets_a2 += 1
        print(f"Datasets A2: {number_of_datasets_a2}")

        self.latest_oekobaudat_dl.unlink()

    def test_oekobaudat_api_a1_load_datasets_with_uuid_from_csv(self):
        """Based on EN15804+A1 datastock version (4fb60595-6b0d-4c4f-af9d-403df2bcaf30), downloaded with
        get_soda4lca_node_datastock() function."""
        self.oekobaudat_csv_a1_dl = get_soda4lca_node_datastock(
            root="https://oekobaudat.de/OEKOBAU.DAT/resource",
            datastock_uuid="4fb60595-6b0d-4c4f-af9d-403df2bcaf30",
            export_format="csv"
        )
        self.oekobaudat_csv_a1 = OekobaudatCsv(self.oekobaudat_csv_a1_dl)
        self.epd_datamanager_a1.register_source("oekobaudat_csv_a1", self.oekobaudat_csv_a1)
        self.oekobaudat_csv_a1_dropped_duplicates = self.oekobaudat_csv_a1.data.drop_duplicates(subset="UUID")

        self.oekobaudat_api_a1 = OekobaudatApi()
        self.epd_datamanager_a1.register_source("oekobaudat_api_a1", self.oekobaudat_api_a1)
        
        number_of_datasets_api_a1 = 0
        for index, row in self.oekobaudat_csv_a1_dropped_duplicates.sample(n=100).iterrows():
            print(row["UUID"])

            self.test_dataset_a1.load_lca_dataset(
                row["UUID"],
                self.epd_datamanager_a1,
                source_key="oekobaudat_api_a1",
                scenario="use_first"
            )

            number_of_datasets_api_a1 += 1
        print(f"EN15804+A1 compliant datasets loaded via OekobaudatAPI via UUIDs from csv: {number_of_datasets_api_a1}")

        self.oekobaudat_csv_a1_dl.unlink()

    def test_oekobaudat_api_a2_load_datasets_with_uuid_from_csv(self):
        """Based on latest available Ökobaudat datastock, downloaded with get_soda4lca_node_datastock() function."""
        self.latest_oekobaudat_dl = get_soda4lca_node_datastock(root="https://oekobaudat.de/OEKOBAU.DAT/resource")
        self.oekobaudat_csv_a2 = OekobaudatCsv(self.latest_oekobaudat_dl)
        self.epd_datamanager_a2.register_source("oekobaudat_csv_a2", self.oekobaudat_csv_a2)
        self.oekobaudat_csv_a2_dropped_duplicates = self.oekobaudat_csv_a2.data.drop_duplicates(subset="UUID")

        self.oekobaudat_api_a2 = OekobaudatApi()
        self.epd_datamanager_a2.register_source("oekobaudat_api_a2", self.oekobaudat_api_a2)
        
        number_of_datasets_api_a2 = 0
        print(len(self.epd_datamanager_a2._fetched_datasets))
        for index, row in self.oekobaudat_csv_a2_dropped_duplicates.sample(n=100).iterrows():
            print(row["UUID"])

            self.test_dataset_a2.load_lca_dataset(
                row["UUID"],
                self.epd_datamanager_a2,
                source_key="oekobaudat_api_a2",
                scenario="use_first"
            )

            number_of_datasets_api_a2 += 1
        print(f"EN15804+A2 compliant datasets loaded via OekobaudatAPI via UUIDs from csv: {number_of_datasets_api_a2}")

        self.latest_oekobaudat_dl.unlink()


    """EPD Norway"""
    def test_epdnorway_csv_a1_load_every_dataset(self):
        """Based on the 'PUBLIC' datastock, downloaded with get_soda4lca_node_datastock() function."""
        self.epdnorway_csv_filepath = get_soda4lca_node_datastock(
            root="https://epdnorway.lca-data.com/resource",
            shortname_identifier="PUBLIC",
            export_format="csv"
        )
        self.epdnorway_csv_a1 = EpdNorwayCsv(self.epdnorway_csv_filepath)
        self.epd_datamanager_a1.register_source("epdnorway_csv_a1", self.epdnorway_csv_a1)
        self.epdnorway_csv_a1_dropped_duplicates = self.epdnorway_csv_a1.data.drop_duplicates(subset="UUID")

        number_of_datasets_a1 = 0
        for index, row in self.epdnorway_csv_a1_dropped_duplicates.iterrows():
            # print(index)

            self.test_dataset_a1.load_lca_dataset(
                row["UUID"],
                self.epd_datamanager_a1,
                source_key="epdnorway_csv_a1",
                scenario="use_first"
            )

            number_of_datasets_a1 += 1
        print(f"Loaded datasets for EPD Norway CSV A1: {number_of_datasets_a1}")

        self.epdnorway_csv_filepath.unlink()

    def test_epdnorway_csv_a2_load_every_dataset(self):
        """Based on the 'PUBLIC' datastock, downloaded with get_soda4lca_node_datastock() function."""
        self.epdnorway_csv_filepath = get_soda4lca_node_datastock(
            root="https://epdnorway.lca-data.com/resource",
            shortname_identifier="PUBLIC",
            export_format="csv"
        )
        self.epdnorway_csv_a2 = EpdNorwayCsv(self.epdnorway_csv_filepath)
        self.epd_datamanager_a2.register_source("epdnorway_csv_a2", self.epdnorway_csv_a2)
        self.epdnorway_csv_a2_dropped_duplicates = self.epdnorway_csv_a2.data.drop_duplicates(subset="UUID")

        number_of_datasets_a2 = 0
        for index, row in self.epdnorway_csv_a2_dropped_duplicates.iterrows():
            # print(index)

            self.test_dataset_a2.load_lca_dataset(
                row["UUID"],
                self.epd_datamanager_a2,
                source_key="epdnorway_csv_a2",
                scenario="use_first"
            )

            number_of_datasets_a2 += 1
        print(f"Loaded datasets for EPD Norway CSV A2: {number_of_datasets_a2}")

        self.epdnorway_csv_filepath.unlink()

    def test_epdnorway_api_a1_load_datasets_with_uuid_from_csv(self):
        """Based on the 'PUBLIC' datastock, downloaded with get_soda4lca_node_datastock() function."""
        self.epdnorway_csv_filepath = get_soda4lca_node_datastock(
            root="https://epdnorway.lca-data.com/resource",
            shortname_identifier="PUBLIC",
            export_format="csv"
        )
        self.epdnorway_csv_a1 = EpdNorwayCsv(self.epdnorway_csv_filepath)
        self.epd_datamanager_a1.register_source("epdnorway_csv_a1", self.epdnorway_csv_a1)
        self.epdnorway_csv_a1_dropped_duplicates = self.epdnorway_csv_a1.data.drop_duplicates(subset="UUID")

        self.epdnorway_api_a1 = EpdNorwayApi()
        self.epd_datamanager_a1.register_source("epdnorway_api_a1", self.epdnorway_api_a1)

        number_of_datasets_api_a1 = 0
        for index, row in self.epdnorway_csv_a1_dropped_duplicates.sample(n=100).iterrows():
            print(row["UUID"])

            self.test_dataset_a1.load_lca_dataset(
                row["UUID"],
                self.epd_datamanager_a1,
                source_key="epdnorway_api_a1",
                scenario="use_first"
            )

            number_of_datasets_api_a1 += 1
        print(f"EN15804+A1 compliant datasets loaded with EpdNorwayApi via UUIDs from CSV: {number_of_datasets_api_a1}")

        self.epdnorway_csv_filepath.unlink()

    def test_epdnorway_api_a2_load_datasets_with_uuid_from_csv(self):
        """Based on the 'PUBLIC' datastock, downloaded with get_soda4lca_node_datastock() function."""
        self.epdnorway_csv_filepath = get_soda4lca_node_datastock(
            root="https://epdnorway.lca-data.com/resource",
            shortname_identifier="PUBLIC",
            export_format="csv"
        )
        self.epdnorway_csv_a2 = EpdNorwayCsv(self.epdnorway_csv_filepath)
        self.epd_datamanager_a2.register_source("epdnorway_csv_a2", self.epdnorway_csv_a2)
        self.epdnorway_csv_a2_dropped_duplicates = self.epdnorway_csv_a2.data.drop_duplicates(subset="UUID")

        self.epdnorway_api_a2 = EpdNorwayApi()
        self.epd_datamanager_a2.register_source("epdnorway_api_a2", self.epdnorway_api_a2)

        number_of_datasets_api_a2 = 0
        print(len(self.epd_datamanager_a2._fetched_datasets))
        for index, row in self.epdnorway_csv_a2_dropped_duplicates.sample(n=100).iterrows():
            print(row["UUID"])

            self.test_dataset_a2.load_lca_dataset(
                row["UUID"],
                self.epd_datamanager_a2,
                source_key="epdnorway_api_a2",
                scenario="use_first"
            )

            number_of_datasets_api_a2 += 1
        print(f"EN15804+A2 compliant datasets loaded with EpdNorwayApi via UUIDs from CSV: {number_of_datasets_api_a2}")

        self.epdnorway_csv_filepath.unlink()


if __name__ == '__main__':
    unittest.main(verbosity=2)