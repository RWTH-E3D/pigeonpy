from epd.epddataset.epddataset import EpdDataset
from epd.epddataset.en15804A1dataset import En15804A1Dataset
from epd.epddataset.en15804A2dataset import En15804A2Dataset
import numpy as np

import unittest


epd_dataset_a1_1 = np.full((25,18), 2.0)
epd_dataset_a1_2 = np.full((25,18), 4.0)
epd_dataset_a2_1 = np.full((31,18), 3.0)
epd_dataset_a2_2 = np.full((31,18), 6.0)


class TestEpdDatasetCalculationDunderMethods(unittest.TestCase):
    """Test calculation dunder methods for EpdDataset objects"""

    def setUp(self):
        self.a1_1_EpdDataset_class = EpdDataset()
        self.a1_1_EpdDataset_class.data = epd_dataset_a1_1
        self.a1_2_En15804A1_class = En15804A1Dataset()
        self.a1_2_En15804A1_class.data = epd_dataset_a1_2
        self.a2_1_EpdDataset_class = EpdDataset()
        self.a2_1_EpdDataset_class.data = epd_dataset_a2_1
        self.a2_2_En15804A2_class = En15804A2Dataset()
        self.a2_2_En15804A2_class.data = epd_dataset_a2_2


    def test_add_returned_object_type(self):
        self.assertIsInstance((self.a1_1_EpdDataset_class + self.a1_2_En15804A1_class), EpdDataset)
        self.assertIsInstance((self.a1_2_En15804A1_class + self.a1_1_EpdDataset_class), En15804A1Dataset)
        self.assertIsInstance((self.a2_2_En15804A2_class + self.a2_1_EpdDataset_class), En15804A2Dataset)
        self.assertNotIsInstance(self.a1_1_EpdDataset_class + self.a1_2_En15804A1_class, En15804A1Dataset)
        self.assertNotIsInstance(self.a2_1_EpdDataset_class + self.a2_2_En15804A2_class, En15804A2Dataset)

    def test_add_calculated_data_type(self):
        self.assertIsInstance((self.a1_1_EpdDataset_class + self.a1_2_En15804A1_class).data, np.ndarray)

    def test_add_dunder_method_same_shape(self):
        result = np.full((25,18), 6.0)
        np.testing.assert_array_almost_equal(
            (self.a1_1_EpdDataset_class + self.a1_2_En15804A1_class).data, result, verbose=True)

        help_object = self.a1_1_EpdDataset_class + self.a1_2_En15804A1_class
        self.assertTrue((help_object.data == result).all())
        self.assertEqual((self.a1_1_EpdDataset_class + self.a1_2_En15804A1_class).data.all(), result.all())

    def test_add_dunder_method_diff_shape(self):
        with self.assertRaises(ValueError):
            self.a1_2_En15804A1_class + self.a2_2_En15804A2_class

    def test_add_single_value(self):
        with self.assertRaises(TypeError):
            self.a1_2_En15804A1_class + 5
            self.a1_2_En15804A1_class + 'test'


    """Tests for __sub__ method"""

    def test_sub_returned_object_type(self):
        self.assertIsInstance((self.a1_1_EpdDataset_class - self.a1_2_En15804A1_class), EpdDataset)
        self.assertIsInstance((self.a1_2_En15804A1_class - self.a1_1_EpdDataset_class), En15804A1Dataset)
        self.assertIsInstance((self.a2_2_En15804A2_class - self.a2_1_EpdDataset_class), En15804A2Dataset)
        self.assertNotIsInstance(self.a1_1_EpdDataset_class - self.a1_2_En15804A1_class, En15804A1Dataset)
        self.assertNotIsInstance(self.a2_1_EpdDataset_class - self.a2_2_En15804A2_class, En15804A2Dataset)

    def test_sub_calculated_data_type(self):
        self.assertIsInstance((self.a1_1_EpdDataset_class - self.a1_2_En15804A1_class).data, np.ndarray)

    def test_sub_dunder_method_same_shape(self):
        result = np.full((25,18), (-2.0))
        np.testing.assert_array_almost_equal(
            (self.a1_1_EpdDataset_class - self.a1_2_En15804A1_class).data, result, verbose=True)

        help_object = self.a1_1_EpdDataset_class - self.a1_2_En15804A1_class
        self.assertTrue((help_object.data == result).all())
        self.assertEqual((self.a1_1_EpdDataset_class - self.a1_2_En15804A1_class).data.all(), result.all())

    def test_sub_dunder_method_diff_shape(self):
        with self.assertRaises(ValueError):
            self.a1_2_En15804A1_class - self.a2_2_En15804A2_class

    def test_sub_single_value(self):
        with self.assertRaises(TypeError):
            self.a1_2_En15804A1_class - 5
            self.a1_2_En15804A1_class - 'test'


    """Tests for __mul__ method"""

    def test_mul_returned_object_type(self):
        self.assertIsInstance((self.a1_1_EpdDataset_class * self.a1_2_En15804A1_class), EpdDataset)
        self.assertIsInstance((self.a1_2_En15804A1_class * self.a1_1_EpdDataset_class), En15804A1Dataset)
        self.assertIsInstance((self.a2_2_En15804A2_class * self.a2_1_EpdDataset_class), En15804A2Dataset)
        self.assertNotIsInstance(self.a1_1_EpdDataset_class * self.a1_2_En15804A1_class, En15804A1Dataset)
        self.assertNotIsInstance(self.a2_1_EpdDataset_class * self.a2_2_En15804A2_class, En15804A2Dataset)

        self.assertIsInstance(self.a1_1_EpdDataset_class * 5, EpdDataset)
        self.assertIsInstance(self.a1_2_En15804A1_class * 5, En15804A1Dataset)
        self.assertIsInstance(self.a2_2_En15804A2_class * 5, En15804A2Dataset)

    def test_mul_calculated_data_type(self):
        self.assertIsInstance((self.a1_1_EpdDataset_class * self.a1_2_En15804A1_class).data, np.ndarray)
        self.assertIsInstance((self.a1_2_En15804A1_class * 5).data, np.ndarray)

    def test_mul_same_shape(self):
        result_other_epd = np.full((25,18),8)
        result_other_float = np.full((25,18),20.0)

        np.testing.assert_array_almost_equal(
            (self.a1_1_EpdDataset_class * self.a1_2_En15804A1_class).data, result_other_epd, verbose=True)
        np.testing.assert_array_almost_equal(
            (self.a1_2_En15804A1_class * 5).data, result_other_float, verbose=True)

        help_object_other_epd = self.a1_2_En15804A1_class * self.a1_1_EpdDataset_class
        self.assertTrue((help_object_other_epd.data == result_other_epd).all())
        self.assertEqual((self.a1_1_EpdDataset_class - self.a1_2_En15804A1_class).data.all(), result_other_epd.all())

        help_object_other_float = self.a1_2_En15804A1_class * 5
        self.assertTrue((help_object_other_float.data == result_other_float).all())
        self.assertEqual((self.a1_1_EpdDataset_class - self.a1_2_En15804A1_class).data.all(), result_other_float.all())

    def test_mul_different_shape(self):
        with self.assertRaises(ValueError):
            self.a1_2_En15804A1_class * self.a2_2_En15804A2_class

    def test_mul_raise_type_error(self):
        with self.assertRaises(TypeError):
            self.a1_2_En15804A1_class * 'test'
            self.a1_2_En15804A1_class * np.full((10,10), 'abc')


    """Tests for __truediv__ method"""

    def test_truediv_returned_object_type(self):
        self.assertIsInstance(self.a1_1_EpdDataset_class / 5, EpdDataset)
        self.assertIsInstance(self.a1_2_En15804A1_class / 5, En15804A1Dataset)
        self.assertIsInstance(self.a2_2_En15804A2_class / 5, En15804A2Dataset)

    def test_truediv_calculated_data_type(self):
        self.assertIsInstance((self.a1_2_En15804A1_class / 5).data, np.ndarray)

    def test_truediv_same_shape(self):
        result = np.full((25,18), 0.8)

        np.testing.assert_array_almost_equal(
            (self.a1_2_En15804A1_class / 5).data, result, verbose=True)
        help_object = self.a1_2_En15804A1_class / 5
        self.assertTrue((help_object.data == result).all())
        self.assertEqual((self.a1_1_EpdDataset_class - self.a1_2_En15804A1_class).data.all(), result.all())

    def test_truediv_type_error(self):
        with self.assertRaises(TypeError):
            self.a1_2_En15804A1_class / 'test'
            self.a1_2_En15804A1_class / self.a1_1_EpdDataset_class
            self.a1_2_En15804A1_class / np.full((10, 10), 'abc')

    def test_truediv_value_error(self):
        with self.assertRaises(ValueError):
            self.a1_2_En15804A1_class / self.a2_2_En15804A2_class.data


if __name__ == '__main__':
    unittest.main(verbosity=2)
