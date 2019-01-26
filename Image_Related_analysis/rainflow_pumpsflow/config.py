import os
from pathlib import Path

# path to all the files
path = Path(os.path.dirname(os.path.realpath(__file__)) + '/')
aggregated_data_dir = Path('aggregated_data/')
images_dir = Path('images/')
weekend_index = 5
confidence_interval = 0.95
