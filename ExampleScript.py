import time
from study import Study
from pathlib import Path
from data.epddata.source.oekobaudatapi import OekobaudatAPI
from logic.epddataset.en15804A2dataset import En15804A2Dataset

import numpy as np # Löschen, wenn Gewichtungsfaktoren über Funktion erstellt werden


tic = time.time()

#input file wird geladen
input_csv_path = Path.cwd() / "data" / "input" / "inputdata" / "input_csv_paper+service_life+headers.csv"

# Studie wird erstellt
standard_dataset = En15804A2Dataset
study_doktorandenseminar = Study(
    study_name="Doktorandenseminar",
    observation_period=50,
    dataset_template=standard_dataset
)


oekobaudat_api = OekobaudatAPI("Ökobaudat API")

# study_doktorandenseminar.epd_datamanager.register_source("oekobaudat", oekobaudat)
study_doktorandenseminar.epd_datamanager.register_source("oekobaudat API", oekobaudat_api)



#Berechnung wird geladen und gestartet
study_doktorandenseminar.load_calculation_input(input_csv_path)
study_doktorandenseminar.run_calculation("building_type")

#Normalisieurngs EPD wird geladen
normalization_epd = En15804A2Dataset()
normalization_epd.load_lca_dataset("f8ff7cbf-f3bb-4499-95e2-8268dd84fab1", study_doktorandenseminar.epd_datamanager)

normalization_vector = np.array([[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
                                  9220,0,0,0,
                                  0.022,0,0,0,0,
                                  31.7,0,0,0]]).transpose()

study_doktorandenseminar.lcia.normalize("test_normalization", normalization_vector)

weighting_factors = np.array([[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,
                               0.33,0,0,0,
                               0.33,0,0,0,0,
                               0.34,0,0,0]]).transpose()

study_doktorandenseminar.lcia.weight("weighting", weighting_factors, normalization_method = "test_normalization")

weighting_factors = np.full((31, 1), 2.0)
study_doktorandenseminar.lcia.weight(
    "test_weighting",
    weighting_factors=weighting_factors,
    normalization_method="test_normalization")

print(study_doktorandenseminar.lcia.normalized_results["test_normalization"]["Total result"])
print(study_doktorandenseminar.lcia.weighted_results["weighting"]["Total result"])
print(study_doktorandenseminar.lcia.weighted_results["weighting"]["Total result"].get_sum("gwp-total", ["a1", "a2", "a3"]))
print(study_doktorandenseminar.lcia.weighted_results["weighting"]["Total result"].get_sum("odp", ["a1", "a2", "a3"]))
print(study_doktorandenseminar.lcia.weighted_results["weighting"]["Total result"].get_sum("pocp", ["a1", "a2", "a3"]))

toc = time.time()
print('dynamic lca draft run in', round((toc - tic), 2), 'seconds')






