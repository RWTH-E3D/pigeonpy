from study import Study
from pathlib import Path
from logic.goalandscope import GoalAndScope
from data.epddata.source.oekobaudatcsv import OekobaudatCsv
from logic.epddataset.en15804A2dataset import En15804A2Dataset
import logic.methods.normalization as norm
import time

def doktorandenseminar_weighting(normalized_result, gwp_perc, fw_perc, rwd_perc):

    gwp_weighted = normalized_result.get("gwp-total", "a1_a3") * gwp_perc
    fw_weighted = normalized_result.get("fw", "a1_a3") * fw_perc
    rwh_weighted = normalized_result.get("rwd", "a1_a3") * rwd_perc

    print(f'GWP_weighted = {gwp_weighted}')
    print(f'FW_weighted = {fw_weighted}')
    print(f'RWD_weighted = {rwh_weighted}')
    print(f'overall = {gwp_weighted + fw_weighted + rwh_weighted}')

tic = time.time()

#input file wird geladen
input_csv_path = Path.cwd() / "data" / "input" / "inputdata" / "input_csv_paper.csv"

# Studie wird erstellt
study_doktorandenseminar = Study("Doktorandenseminar")

#goal and scope wird definiert und der Studie zugeordnet (nicht wichtig für Seminar)
goal_and_scope = GoalAndScope("EN15804+A2", description = "This study is about insulation")
study_doktorandenseminar.goal_and_scope = goal_and_scope

#Datenbank wird geladen und der Studie zugeordnet
oekobaudatfilepath = Path.cwd()  / "data" / "input" / "inputdata" / "OBD_2024_I_2024-12-10T09_45_06.csv"
oekobaudat = OekobaudatCsv("Ökobaudat", oekobaudatfilepath, "EN15804+A2")
study_doktorandenseminar.epd_datamanager.register_source("oekobaudat", oekobaudat)

#Berechnung wird geladen und gestartet
study_doktorandenseminar.load_calculation_input(input_csv_path)
study_doktorandenseminar.run_calculation("building_type")

#Normalisieurngs EPD wird geladen
normalization_epd = En15804A2Dataset()
normalization_epd.load_lca_dataset("f8ff7cbf-f3bb-4499-95e2-8268dd84fab1", study_doktorandenseminar.epd_datamanager)

#EPS: 757297f1-9325-4df4-af51-96510be76bf3
#Mineralwolle: 4fa62445-e59f-4874-99e5-49cec91967e0

#Normalisierung wird durchgeführt
method_tuple_norm = ("normalization", norm.normalize_by_epd, normalization_epd)
study_doktorandenseminar.apply_method(*method_tuple_norm)

print(study_doktorandenseminar.calculation.other_results["normalization"]["type 4"])

#Gewichtung wird durchgeführt
doktorandenseminar_weighting(study_doktorandenseminar.calculation.other_results["normalization"]["type 4"], 0.8, 0.1, 0.1)

toc = time.time()
print('dynamic lca draft run in', round((toc - tic), 2), 'seconds')






