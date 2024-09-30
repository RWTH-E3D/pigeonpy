from study import Study
from pathlib import Path
from logic.goalandscope import GoalAndScope
from data.epddata.source.oekobaudatcsv import OekobaudatCsv
#from logic.epddataset.en15804A2dataset import En15804A2Dataset
#import logic.methods.normalization
#import logic.methods.wheighting

input_csv_path = Path.cwd() / "data" / "input" / "inputdata" / "input_data_dynamic_csv_V2.CSV"

goal_and_scope = GoalAndScope("EN15804+A2", description = "This study is about huhu")

test_study = Study("test-studie")
oekobaudatfilepath = Path.cwd()  / "data" / "input" / "inputdata" / "OBD_2023_I_2024-01-09T12_49_34.csv"
test_source = OekobaudatCsv("Ökobaudat", oekobaudatfilepath, "EN15804+A2")
test_study.epd_datamanager.register_source("oekobaudat", test_source)
test_study.goal_and_scope = goal_and_scope
test_study.load_calculation_input(input_csv_path)
test_study.run_calculation("Year Installation for components or occurence for consumption")

#normalize_by_epd

#test_study.apply_method(normalize_by_epd)

print(test_study.calculation.result[1996])


#test_study.calculation.run("Category1")

