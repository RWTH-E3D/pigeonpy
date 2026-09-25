import unittest
from pathlib import Path
from pigeonpy.data.epddata.source.tecojsonsource import TecoJson
from pigeonpy.epd.epddataset.en15804A1dataset import En15804A1Dataset
from pigeonpy.study.study import Study

class TestStudySystem(unittest.TestCase):
    """Tests for calculating results with the study class"""

    def test_study_system_testcase1_total_result(self):
        """Test calculation of the total_result"""

        #normalization
        normalization_factors = {
            "gwp": 9220,
            "odp": 0.022,
            "pocp": 31.7
        }

        # Weighting
        weighting_factors = {
            "gwp": 0.33,
            "odp": 0.33,
            "pocp": 0.34
        }

        input_json_path = Path(__file__).resolve().parents[1] / "tests" / "test_data" / "Teco_EN15804A1_testcase1.json"
        input_csv_path = Path(__file__).resolve().parents[1] / "tests" / "test_data" / "input_testcase1.csv"
        test_study = Study(
            study_name="test_study",
            environmental_indicators=["gwp", "pocp", "odp"],
            life_cycle_stages=["a1_a3", "c2", "d"],
            observation_period=50,
            dataset_template=En15804A1Dataset
        )

        teco_json = TecoJson(input_json_path)

        test_study.epd_datamanager.register_source("teco_json", teco_json)

        test_study.load_calculation_input(input_csv_path)
        test_study.run_calculation()

        test_study.normalize("test_normalization", normalization_factors)
        test_study.weight("test_weighting", weighting_factors, normalization_method="test_normalization")

        gwp_a1_a3_total = 2.4 * 3.5 + 2.3 * 3
        odp_c2_total = 2.5e-18 * 2.4
        pocp_c2_total = -0.000006 * 2.4

        gwp_a1_a3_total_normalized = gwp_a1_a3_total / normalization_factors["gwp"]
        odp_c2_total_normalized = odp_c2_total / normalization_factors["odp"]
        pocp_c2_total_normalized = pocp_c2_total / normalization_factors["pocp"]

        gwp_a1_a3_total_weighted = gwp_a1_a3_total_normalized * weighting_factors["gwp"]
        odp_c2_total_weighted = odp_c2_total_normalized * weighting_factors["odp"]
        pocp_c2_total_weighted = pocp_c2_total_normalized * weighting_factors["pocp"]

        self.assertAlmostEqual(test_study.result["indicator_values"]["total_result"].get("gwp", "a1_a3"), gwp_a1_a3_total)
        self.assertAlmostEqual(test_study.result["indicator_values"]["total_result"].get("odp", "c2"), odp_c2_total, places = 30)
        self.assertAlmostEqual(test_study.result["indicator_values"]["total_result"].get("pocp", "c2"), pocp_c2_total, places = 10)
        self.assertAlmostEqual(test_study.result["indicator_values"]["total_result"].get("gwp", "d"), 0)

        self.assertAlmostEqual(
            test_study.result["test_normalization"]["total_result"].get("gwp", "a1_a3"),
            gwp_a1_a3_total_normalized)
        self.assertAlmostEqual(
            test_study.result["test_normalization"]["total_result"].get("odp", "c2"),
            odp_c2_total_normalized)
        self.assertAlmostEqual(
            test_study.result["test_normalization"]["total_result"].get("pocp", "c2"),
            pocp_c2_total_normalized)
        self.assertAlmostEqual(test_study.result["test_normalization"]["total_result"].get("gwp", "d"),
                               0)

        self.assertAlmostEqual(
            test_study.result["test_weighting"]["total_result"].get("gwp", "a1_a3"),
            gwp_a1_a3_total_weighted)
        self.assertAlmostEqual(
            test_study.result["test_weighting"]["total_result"].get("odp", "c2"),
            odp_c2_total_weighted)
        self.assertAlmostEqual(
            test_study.result["test_weighting"]["total_result"].get("pocp", "c2"),
            pocp_c2_total_weighted)
        self.assertAlmostEqual(test_study.result["test_weighting"]["total_result"].get("gwp", "d"), 0)

    def test_study_system_testcase1_partitions(self):
        """Test the calculation of results based on partitions."""

        # normalization
        normalization_factors = {
            "gwp": 9220,
            "odp": 0.022,
            "pocp": 31.7
        }

        # Weighting
        weighting_factors = {
            "gwp": 0.33,
            "odp": 0.33,
            "pocp": 0.34
        }

        input_json_path = Path(__file__).resolve().parents[1] / "tests" / "test_data" / "Teco_EN15804A1_testcase1.json"
        input_csv_path = Path(__file__).resolve().parents[1] / "tests" / "test_data" / "input_testcase1.csv"
        test_study = Study(
            study_name="test_study",
            environmental_indicators=["gwp", "pocp", "odp"],
            life_cycle_stages=["a1_a3", "c2", "d"],
            observation_period=50,
            dataset_template=En15804A1Dataset
        )

        teco_json = TecoJson(input_json_path)

        test_study.epd_datamanager.register_source("teco_json", teco_json)

        test_study.load_calculation_input(input_csv_path)
        test_study.run_calculation("partition1", ("partition1", "partition2"), "partition2")

        test_study.normalize("test_normalization", normalization_factors)
        test_study.weight("test_weighting", weighting_factors, normalization_method="test_normalization")

        gwp_a1_a3_subset1 = 1.4 * 3.5
        gwp_a1_a3_subset2 = 1 * 3.5 + 1.3 * 3 + 1 * 3
        gwp_a1_a3_subset1A = 1.4 * 3.5
        gwp_a1_a3_subset2B = 1 * 3.5
        gwp_a1_a3_subset2A = 1.3 * 3 + 1 * 3
        gwp_a1_a3_subsetA = 1.4 * 3.5 + 1.3 * 3 + 1* 3
        gwp_a1_a3_subsetB = 1 * 3.5

        self.assertAlmostEqual(test_study.result["indicator_values"]["partition1"]["subset1"].get("gwp", "a1_a3"), gwp_a1_a3_subset1)
        self.assertAlmostEqual(test_study.result["indicator_values"]["partition1"]["subset2"].get("gwp", "a1_a3"), gwp_a1_a3_subset2)
        self.assertAlmostEqual(test_study.result["indicator_values"][("partition1", "partition2")][("subset1", "subsetA")].get("gwp", "a1_a3"), gwp_a1_a3_subset1A)
        self.assertAlmostEqual(test_study.result["indicator_values"][("partition1", "partition2")][("subset2", "subsetB")].get("gwp", "a1_a3"), gwp_a1_a3_subset2B)
        self.assertAlmostEqual(test_study.result["indicator_values"][("partition1", "partition2")][("subset2", "subsetA")].get("gwp", "a1_a3"), gwp_a1_a3_subset2A)
        self.assertAlmostEqual(test_study.result["indicator_values"]["partition2"]["subsetA"].get("gwp", "a1_a3"), gwp_a1_a3_subsetA)
        self.assertAlmostEqual(test_study.result["indicator_values"]["partition2"]["subsetB"].get("gwp", "a1_a3"), gwp_a1_a3_subsetB)

        gwp_a1_a3_subset2B_normalized = gwp_a1_a3_subset2B / normalization_factors["gwp"]
        self.assertAlmostEqual(test_study.result["test_normalization"][("partition1", "partition2")][("subset2", "subsetB")].get("gwp", "a1_a3"),gwp_a1_a3_subset2B_normalized)

        gwp_a1_a3_subsset2B_weighted = gwp_a1_a3_subset2B_normalized * weighting_factors["gwp"]
        self.assertAlmostEqual(test_study.result["test_weighting"][("partition1", "partition2")][
                                   ("subset2", "subsetB")].get("gwp", "a1_a3"), gwp_a1_a3_subsset2B_weighted)


if __name__ == '__main__':
    unittest.main(verbosity=2)