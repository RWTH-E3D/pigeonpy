import time
import study
from study import Study
from pathlib import Path
from data.epddata.source.oekobaudatapi import OekobaudatAPI
from logic.epddataset.en15804A2dataset import En15804A2Dataset


tic = time.time()

#input file wird geladen
input_csv_path = Path.cwd() / "data" / "input" / "inputdata" / "input_csv_paper+service_life+headers.csv"

# Studie wird erstellt
standard_dataset = En15804A2Dataset
study_doktorandenseminar = Study(
    study_name="Doktorandenseminar",
    observation_period=50,
    environmental_indicators=["gwp-total", "odp", "pocp"],
    life_cycle_stages=["a1_a3", "b6", "c1", "c2", "c3", "c4", "d"],
    dataset_template=standard_dataset
)


oekobaudat_api = OekobaudatAPI("Ökobaudat API")
study_doktorandenseminar.epd_datamanager.register_source("oekobaudat API", oekobaudat_api)


#Berechnung wird geladen und gestartet
study_doktorandenseminar.load_calculation_input(input_csv_path)
study_doktorandenseminar.run_calculation("building_type")

# Normalisieurngs EPD:
# normalization_epd = En15804A2Dataset()
# normalization_epd.load_lca_dataset("f8ff7cbf-f3bb-4499-95e2-8268dd84fab1", study_doktorandenseminar.epd_datamanager)

normalization_factors = {
    "gwp-total": 9220,
    "odp": 0.022,
    "pocp": 31.7
}
study_doktorandenseminar.lcia.normalize("test_normalization", normalization_factors)

weighting_factors = {
    "gwp-total": 0.33,
    "odp": 0.33,
    "pocp": 0.34
}
study_doktorandenseminar.lcia.weight("test_weighting", weighting_factors, normalization_method="test_normalization")

# print(study_doktorandenseminar.lcia.normalized_results["test_normalization"]["Total result"])
# print(study_doktorandenseminar.lcia.weighted_results["test_weighting"]["Total result"])
# print(study_doktorandenseminar.lcia.weighted_results["test_weighting"]["Total result"].get_sum("gwp-total", ["a1", "a2", "a3"]))
# print(study_doktorandenseminar.lcia.weighted_results["test_weighting"]["Total result"].get_sum("odp", ["a1", "a2", "a3"]))
# print(study_doktorandenseminar.lcia.weighted_results["test_weighting"]["Total result"].get_sum("pocp", ["a1", "a2", "a3"]))

toc = time.time()

print('dynamic lca draft run in', round((toc - tic), 2), 'seconds')
print(study_doktorandenseminar.lcia.result["Total result"])
print(study_doktorandenseminar.lcia.normalized_results["test_normalization"]["Total result"])
print(study_doktorandenseminar.lcia.weighted_results["test_weighting"]["Total result"])







