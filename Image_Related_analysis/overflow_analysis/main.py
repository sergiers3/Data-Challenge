import glob
import os
from pathlib import Path

import pandas as pd

import config
from config import ROOT_DIR, data_dir, min_rain_threshold, csv_decimal, pump_level_raw_data
from config import aggregate_data_dir
from data.stations import flowData


def get_file_names(directory):
    extension = 'csv'
    os.chdir(directory)
    files = [i for i in glob.glob('*.{}'.format(extension))]
    os.chdir(config.ROOT_DIR)
    return files


def count_rains(rain_flags):
    rains_count = 0
    if len(rain_flags) > 0:
        last_mode = rain_flags[0]
        for flag in rain_flags:
            if last_mode == 0 and flag == 1:
                rains_count += 1
            if flag != last_mode:
                last_mode = flag
    return rains_count


def prepare_level_rain_dataset(region, region_name):
    pump_level = pd.read_csv(ROOT_DIR / data_dir / pump_level_raw_data, delimiter=';', decimal=csv_decimal, engine='c',
                             index_col=1, parse_dates=True,
                             date_parser=lambda x: pd.datetime.strptime(x, '%d-%m-%Y %H:%M:%S'))
    areas = []
    ratios = []
    for area in region:
        level = pump_level.copy()
        level = level[level['Tag Name'] == area['levelTag']]
        if len(level) == 0:
            continue
        level['Eind'] = level.index.strftime("%d-%m-%Y %H:00:00")
        df_rain_file = str(ROOT_DIR / data_dir / Path(region_name)) + str(Path('/')) + area['areaName'] + '.csv'
        df_rain = pd.read_csv(df_rain_file, delimiter=',', decimal=csv_decimal)
        level_rain = pd.merge(level, df_rain, left_on="Eind", right_on="Eind")
        max_level = level_rain['Value'].max() - 1
        without_rain = level_rain[level_rain['PUMP_AVG_HEIGHT_' + area['areaName']] > min_rain_threshold]
        rainy_periods = len(without_rain)
        without_rain = without_rain[without_rain['Value'] > max_level]
        meter_less_max = len(without_rain)
        ratio_higher_max_1 = meter_less_max / rainy_periods
        print(area['areaName'])
        print(">max-1m " + str(round(ratio_higher_max_1 * 100, 2)))
        print("<=max-1m " + str(round(100 - ratio_higher_max_1 * 100, 2)))


def count_by_rains(rain_file):
    rain = pd.read_csv(aggregate_data_dir / rain_file)
    count_of_rains = count_rains(rain['is_rainy'])
    max_minus_one_m = rain['Max_level'].max() - 1
    rain = rain[rain['level'] > max_minus_one_m]
    print(rain_file)
    rains_during_high_period = count_rains(list(rain['is_rainy']))
    print(">max-1m " + str(round(rains_during_high_period / count_of_rains * 100, 2)))
    print("<=max-1m " + str(100 - round(rains_during_high_period / count_of_rains * 100, 2)))


def count_by_hours(rain_file):
    rain = pd.read_csv(aggregate_data_dir / rain_file)
    count_of_rains = len(rain)
    max_minus_one_m = rain['Max_level'].max() - 1
    rain = rain[rain['level'] > max_minus_one_m]
    print(rain_file)
    rains_during_high_period = len(rain)
    print(">max-1m " + str(round(rains_during_high_period / count_of_rains * 100, 2)))
    print("<=max-1m " + str(100 - round(rains_during_high_period / count_of_rains * 100, 2)))


def main():
    files = get_file_names(aggregate_data_dir)
    print("RAW by hours")
    prepare_level_rain_dataset(flowData['Aarle-Rixtel'], 'Aarle-Rixtel')
    print("Aggregated by rains")
    for rain_file in files:
        count_by_rains(rain_file)
    print("Aggregated by hours")
    for rain_file in files:
        count_by_hours(rain_file)


if __name__ == '__main__':
    main()
