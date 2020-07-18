import json
from src import CFG_PATH
from src import ARTEMIS_PATH
from src import APPLY_PATH
from src import FFA_PATH
from src import LEADCACH_PATH

titan = None

class Titan():
    def __init__(self):
        self.config = None
        self.artemis = None
        self.appcache = None
        self.ffas = None
        self.lead = None
        self.update()
        self.client = None
    def update(self):
        with open(CFG_PATH, 'r') as f:
            self.config = json.loads(f.read())
        with open(ARTEMIS_PATH, 'r') as f:
            self.artemis = json.loads(f.read())
        with open(APPLY_PATH, 'r') as f:
            self.appcache = json.loads(f.read())
        with open(FFA_PATH, 'r') as f:
            self.ffas = json.loads(f.read())
        with open(LEADCACH_PATH, 'r') as f:
            self.lead = json.loads(f.read())
    def save(self):
        with open(CFG_PATH, 'w') as f:
            json.dump(self.config, f)
        self.update()
    def save_apply(self):
        with open(APPLY_PATH, 'w') as f:
            json.dump(self.appcache, f)
        self.update()
    def save_ffas(self):
        with open(FFA_PATH, 'w') as f:
            json.dump(self.ffas, f)
        self.update()
    def save_lead(self):
        with open(LEADCACH_PATH, 'w') as f:
            json.dump(self.lead, f)
        self.update()
if not titan:
    titan = Titan()