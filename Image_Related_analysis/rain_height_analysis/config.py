import os
from pathlib import Path

# path to all the files
path = Path(os.path.dirname(os.path.realpath(__file__)) + '/')
dirWithData = Path('data/')
dirWithImages = Path('images/')
# file with areas. can be areas.csv from GD or default surfacearea_sewersystems.csv
areasFile = 'areas.csv'
# file with rain data
rainDataFile = 'raindataAarle.csv'
csv_separator = ';'
csv_decimal = '.'
min_rain = 0.5
