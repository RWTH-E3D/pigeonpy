from data.dataclass import DataClass
from logic.epddataset.en15804A1dataset import En15804A1Dataset
from logic.epddataset.en15804A2dataset import En15804A2Dataset
from data.input.lca_dataset_input import load_lca_dataset_json
from data.input.lca_dataset_input import load_lca_dataset_csv
import numpy as np

import unittest


class TestLoadDatasetMethods(unittest.TestCase):
    """Test functions from lca_dataset_input.py module"""

    def setUp(self):
        self.dataclass_teco_json = DataClass(file_format="teco_json", used_standard="A1")
        self.teco_json_lca_data_bind = self.dataclass_teco_json.lca_data_bind
        self.teco_json_lca_data_bind.pop("version")

        self.dataclass_csv_a1 = DataClass(file_format="csv", used_standard="A1")
        self.csv_a1_lca_data_bind = self.dataclass_csv_a1.lca_data_bind
        self.csv_a1_lca_data_bind_dropped_duplicates = self.csv_a1_lca_data_bind.drop_duplicates(subset="UUID")

        self.dataclass_csv_a2 = DataClass(file_format="csv", used_standard="A2")

        self.test_dataset_a1 = En15804A1Dataset()
        self.test_dataset_a2 = En15804A2Dataset()

    def test_teco_json_load_every_datasets(self):
        for key, value in self.teco_json_lca_data_bind.items():
            load_lca_dataset_json(self.test_dataset_a1, key, self.dataclass_teco_json)

    def test_teco_json_invalid_lca_id_given(self):
        exception_msg = (f"No dataset for combination of given lca id 'test123', file format "
                        f"'teco_json' and standard En15804+A1 was found. "
                        f"Please enter a valid lca id or try another file format.")
        with self.assertRaises(Exception, msg=exception_msg):
            load_lca_dataset_json(self.test_dataset_a1, "test123", self.dataclass_teco_json)


    def test_csv_a1_load_every_dataset(self):
        for index, row in self.csv_a1_lca_data_bind_dropped_duplicates.iterrows():
            print(index)
            load_lca_dataset_csv(self.test_dataset_a2, row["UUID"], self.dataclass_csv_a1)



if __name__ == '__main__':
    unittest.main(verbosity=2)