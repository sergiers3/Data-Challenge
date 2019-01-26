import os
import pandas as pd
import config


def clean_level_data():
    for level_file in os.listdir(str(config.path / config.level_dir)):
        if '.csv' in level_file:
            level = pd.read_csv(config.level_dir / level_file, delimiter=";", decimal=",", dtype={'Value': float})
            level = level[level["Value"] > 0.00001]
            level.to_csv(config.level_out_dir / level_file, sep=',')