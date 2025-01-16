from study import Study
from pathlib import Path
from data.epddata.source.oekobaudatcsv import OekobaudatCsv
from data.epddata.source.oekobaudatapi import OekobaudatAPI
from logic.epddataset.en15804A2dataset import En15804A2Dataset
import time

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

#Datenbank wird geladen und der Studie zugeordnet
oekobaudatfilepath = Path.cwd()  / "data" / "input" / "inputdata" / "OBD_2024_I_2024-12-10T09_45_06.csv"
oekobaudat = OekobaudatCsv("Ökobaudat", oekobaudatfilepath)

oekobaudat_api = OekobaudatAPI("Ökobaudat API")

# study_doktorandenseminar.epd_datamanager.register_source("oekobaudat", oekobaudat)
study_doktorandenseminar.epd_datamanager.register_source("oekobaudat API", oekobaudat_api)



#Berechnung wird geladen und gestartet
study_doktorandenseminar.load_calculation_input(input_csv_path)
study_doktorandenseminar.run_calculation("building_type")

#Normalisieurngs EPD wird geladen
normalization_epd = En15804A2Dataset()
normalization_epd.load_lca_dataset("f8ff7cbf-f3bb-4499-95e2-8268dd84fab1", study_doktorandenseminar.epd_datamanager)

study_doktorandenseminar.lcia.normalize("test_method", normalization_epd)

toc = time.time()
print('dynamic lca draft run in', round((toc - tic), 2), 'seconds')






