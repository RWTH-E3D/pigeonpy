from study import Study
from pathlib import Path
from logic.goalandscope import GoalAndScope
from data.epddata.source.oekobaudatcsv import OekobaudatCsv
from methods import normalization

input_csv_path = Path("C:/Users/Cuypers/Documents/dynamic_lca_draft/data/input/inputdata/input_data_dynamic_csv_V2.CSV")

goal_and_scope = GoalAndScope("EN15804+A2", description = "This study is about huhu")

test_study = Study("test-studie")
oekobaudatfilepath = Path("C:/Users/Cuypers/Documents/dynamic_lca_draft/data/input/inputdata/OBD_2023_I_2024-01-09T12_49_34.csv")
test_source = OekobaudatCsv("Ökobaudat", oekobaudatfilepath, "EN15804+A2")
test_study.epd_datamanager.register_source("oekobaudat", test_source)
test_study.goal_and_scope = goal_and_scope
test_study.load_calculation_input(input_csv_path)
test_study.run_calculation("Year Installation for components or occurence for consumption")

test_study.apply_method(method)

print(test_study.calculation.result[1996])


#test_study.calculation.run("Category1")




#calculator.import_calculation(input_csv_path)

#test = calculator.calculate("Category1")



# two_single_categorizations = test.add_study(study_name="2 Single Categorizations",
#                                             input_csv_path=input_csv_path,
#                                             used_standard="A2",
#                                             lca_input_format="csv")  # Alternativ: 'teco_json'
# tuple_categorization = test.add_study("test categorization",
#                                       ("Category1", "Year Installation for components or occurence for consumption"),
#                                       "test categorization 2",
#                                       study_name="Tuple Categorization",
#                                       input_csv_path=input_csv_path,
#                                       used_standard="A2",
#                                       lca_input_format="csv")
#
# example_study = test.add_study(study_name="Nur ein Beispiel",
#                                input_csv_path=input_csv_path,
#                                used_standard="A1",
#                                lca_input_format="teco_json")
# test.remove_study(study_name="Nur ein Beispiel")
#
# two_single_categorizations.add_categorizations("Category1", "Year Disposal")
# tuple_categorization.remove_categorizations("test categorization", "test categorization 2")
#
# two_single_categorizations.exclude_stages("a1", "a2", "c1", "c2")
# two_single_categorizations.exclude_stages(["b1", "b2", "d"])
# two_single_categorizations.exclude_indicators("pere", "perm")
# two_single_categorizations.exclude_indicators(["pert", "penre"])
#
# test.calculate_all_studies()
