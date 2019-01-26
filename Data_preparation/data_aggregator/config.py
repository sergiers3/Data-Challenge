from pathlib import Path
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
outflow_dir = Path('data/outflow/')
level_dir = Path('data/level/')
rain_dir = Path('data/rain/')
result_dir = Path('aggregated_data/')

analysis_regions = ["Aarle-Rixtel"]
# variable that stores the time that stations needs to recover in hours
station_recovery_time = 7
# minimum rain value that is accepted as rainy by normative documents
min_rain_height = 0.5