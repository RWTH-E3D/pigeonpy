import unittest
from pathlib import Path
from data.epddata.source.tecojsonsource import TecoJson
from epd.epddataset.en15804A1dataset import En15804A1Dataset
from study.study import Study

class TestStudySystem(unittest.TestCase):

    def test_study_system_testcase1_total_result(self):
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

        input_json_path = Path.cwd() / "test_data" / "Teco_EN15804A1_testcase1.json"
        input_csv_path = Path.cwd() / "test_data" / "input_testcase1.csv"
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

        test_study.lcia.normalize("test_normalization", normalization_factors)
        test_study.lcia.weight("test_weighting", weighting_factors, normalization_method="test_normalization")

        gwp_a1_a3_total = 2.4 * 3.5 + 2.3 * 3
        odp_c2_total = 2.5e-18 * 2.4
        pocp_c2_total = -0.000006 * 2.4

        gwp_a1_a3_total_normalized = gwp_a1_a3_total / normalization_factors["gwp"]
        odp_c2_total_normalized = odp_c2_total / normalization_factors["odp"]
        pocp_c2_total_normalized = pocp_c2_total / normalization_factors["pocp"]

        gwp_a1_a3_total_weighted = gwp_a1_a3_total_normalized * weighting_factors["gwp"]
        odp_c2_total_weighted = odp_c2_total_normalized * weighting_factors["odp"]
        pocp_c2_total_weighted = pocp_c2_total_normalized * weighting_factors["pocp"]

        self.assertAlmostEqual(test_study.lcia.result["Total result"].get("gwp", "a1_a3"), gwp_a1_a3_total)
        self.assertAlmostEqual(test_study.lcia.result["Total result"].get("odp", "c2"), odp_c2_total, places = 30)
        self.assertAlmostEqual(test_study.lcia.result["Total result"].get("pocp", "c2"), pocp_c2_total, places = 10)
        self.assertAlmostEqual(test_study.lcia.result["Total result"].get("gwp", "d"), 0)

        self.assertAlmostEqual(
            test_study.lcia.normalized_results["test_normalization"]["Total result"].get("gwp", "a1_a3"),
            gwp_a1_a3_total_normalized)
        self.assertAlmostEqual(
            test_study.lcia.normalized_results["test_normalization"]["Total result"].get("odp", "c2"),
            odp_c2_total_normalized)
        self.assertAlmostEqual(
            test_study.lcia.normalized_results["test_normalization"]["Total result"].get("pocp", "c2"),
            pocp_c2_total_normalized)
        self.assertAlmostEqual(test_study.lcia.normalized_results["test_normalization"]["Total result"].get("gwp", "d"),
                               0)

        self.assertAlmostEqual(
            test_study.lcia.weighted_results["test_weighting"]["Total result"].get("gwp", "a1_a3"),
            gwp_a1_a3_total_weighted)
        self.assertAlmostEqual(
            test_study.lcia.weighted_results["test_weighting"]["Total result"].get("odp", "c2"),
            odp_c2_total_weighted)
        self.assertAlmostEqual(
            test_study.lcia.weighted_results["test_weighting"]["Total result"].get("pocp", "c2"),
            pocp_c2_total_weighted)
        self.assertAlmostEqual(test_study.lcia.weighted_results["test_weighting"]["Total result"].get("gwp", "d"), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)