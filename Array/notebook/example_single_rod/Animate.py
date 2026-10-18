# Animate.py
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))   # project root
sys.path.append(ROOT)

from tools.animate_batch import animate_batch

animate_batch(os.path.join(HERE, 'Carpet.csv'))
