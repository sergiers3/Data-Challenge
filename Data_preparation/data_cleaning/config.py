import os
from pathlib import Path

# path to all the files
path = Path(os.path.dirname(os.path.realpath(__file__)) + '/')
rain_dir = Path('data/rain/')
rain_out_dir = Path('out/rain/')
level_dir = Path('data/level/')
level_out_dir = Path('out/level/')
wwtp_flow_dir = Path('data/wwtp/flow/')
wwtp_out_flow_dir = Path('out/wwtp/flow/')
den_bosch_1 = "DenBosch1.csv"
den_bosch_2 = "DenBosch2.csv"
data_dir = Path('data/')

rainDataRowsToSkip = 2
# file with areas. can be areas.csv from GD or default surfacearea_sewersystems.csv
areas_file = 'areas.csv'
csv_separator = ','
