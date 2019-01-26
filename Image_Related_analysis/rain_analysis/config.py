from pathlib import Path
import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
aggregate_data_dir = Path('aggregated_data/')
lookup_dir = Path('lookup/')
statistics_dir = Path('rain_statistics/')
recovery_dir = Path('recovery_images/')
sewage_dir = Path('sewage_percentage_img/')

min_rain_threshold = 0.5