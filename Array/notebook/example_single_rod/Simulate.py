import os, sys
HERE = os.path.dirname(os.path.abspath(__file__)) 
ROOT = os.path.dirname(os.path.dirname(HERE)) # project root
sys.path.append(ROOT)

from engine import FieldSequence, RodDescription, SimulationSettings
from tools.run_batch import run_batch

run_batch(os.path.join(HERE, 'Manifest.csv'))
