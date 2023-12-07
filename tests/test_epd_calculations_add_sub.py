from logic.epddataset.epddataset import EpdDataset
import numpy as np

import unittest


epd_dataset_a1_1 = np.full((25,17), 2.0)
epd_dataset_a1_2 = np.full((25,17), 4.0)
epd_dataset_a2_1 = np.full((31,17), 3.0)
epd_dataset_a2_2 = np.full((31,17), 6.0)


class TestEpdDatasetAddSubCalculations(unittest.TestCase):
    """Test __add__ and __sub__ methods for EpdDataset objects"""

    def setUp(self):
        self.a1_1 = EpdDataset()
        self.a1_1._data = epd_dataset_a1_1
        self.a1_2 = EpdDataset()
        self.a1_2._data = epd_dataset_a1_2
        self.a2_1 = EpdDataset()
        self.a2_1._data = epd_dataset_a2_1
        self.a2_2 = EpdDataset()
        self.a2_2._data = epd_dataset_a2_2

    def test_add_returned_object_type(self):
        self.assertIsInstance((self.a1_1 + self.a1_2), EpdDataset)

    def test_add_calculated_data_type(self):
        self.assertIsInstance((self.a1_1 + self.a1_2)._data, np.ndarray)

    def test_add_dunder_method_same_shape(self):
        result = np.full((25,17), 6.0)
        np.testing.assert_array_almost_equal((self.a1_1 + self.a1_2)._data, result, verbose=True)

        help_object = self.a1_1 + self.a1_2
        self.assertTrue((help_object._data == result).all())
        self.assertEqual((self.a1_1 + self.a1_2)._data.all(), result.all())

    def test_add_dunder_method_diff_shape(self):
        # self.assertRaises(ValueError, self.a1_1 + self.a2_1)
        pass

    def test_sub_returned_object_type(self):
        self.assertIsInstance((self.a1_1 - self.a1_2), EpdDataset)

    def test_sub_calculated_data_type(self):
        self.assertIsInstance((self.a1_1 - self.a1_2)._data, np.ndarray)

    def test_add_dunder_method_same_shape(self):
        result = np.full((25,17), (-2.0))
        np.testing.assert_array_almost_equal((self.a1_1 - self.a1_2)._data, result, verbose=True)

        help_object = self.a1_1 - self.a1_2
        self.assertTrue((help_object._data == result).all())
        self.assertEqual((self.a1_1 - self.a1_2)._data.all(), result.all())

    def test_add_dunder_method_diff_shape(self):
        # self.assertRaises(ValueError, self.a1_1 - self.a2_1)
        pass


if __name__ == '__main__':
    unittest.main(verbosity=2)
