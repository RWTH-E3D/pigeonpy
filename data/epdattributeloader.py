from pathlib import Path
import json
from logic.environmentalindicator import EnvironmentalIndicator
from logic.lifecyclestage import LifeCycleStage

class EpdAttributeLoader:
    def __init__(self):
        self.indicators_a1_path = Path.cwd() / "data" / "input" / "inputdata" / "indicators_en_15804_a1.json"
        self.indicators_a2_path = Path.cwd() / "data" / "input" / "inputdata" / "indicators_en_15804_a2.json"
        self.life_cycle_stages_path = Path.cwd() / "data" / "input" / "inputdata" / "life_cycle_stages_en_15978.json"

        self.indicators_a1 = None
        self.indicators_a2 = None
        self.life_cycle_stages = None
        self._load_indicators()
        self._load_stages()

    def _load_indicators(self):
        with open(self.indicators_a1_path) as a1, open(self.indicators_a2_path) as a2:
            a1_data = json.load(a1)['indicators_en_15804_a1']
            a2_data = json.load(a2)['indicators_en_15804_a2']
            self.indicators_a1 = [EnvironmentalIndicator(**indicator) for indicator in a1_data]
            self.indicators_a2 = [EnvironmentalIndicator(**indicator) for indicator in a2_data]

    def _load_stages(self):
        with open(self.life_cycle_stages_path) as lcs:
            lcs_data = json.load(lcs)['LifeCycleStages']
            self.life_cycle_stages = [LifeCycleStage(**stage) for stage in lcs_data]
