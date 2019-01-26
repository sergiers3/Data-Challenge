import os
from pathlib import Path

# path to all the files
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
data_dir = Path('data/')
aggregate_data_dir = Path('aggregated_data/')
pump_level_raw_data = 'AllLevelAarleWith4070.csv'
csv_separator = ';'
csv_decimal = '.'
min_rain_threshold = 0.5