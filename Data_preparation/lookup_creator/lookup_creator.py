import config
import os
import glob
import pandas as pd
import numpy as np


def get_file_names():
    extension = 'csv'
    os.chdir(config.result_dir)
    return [i for i in glob.glob('*.{}'.format(extension))]


def get_dry_periods(file):
    station_data = pd.read_csv(file)
    station_data = station_data[station_data["is_rainy"] == 0]
    station_data["TimeStamp"] = pd.to_datetime(station_data["TimeStamp"], format='%Y-%m-%d %H:%M:%S')
    return station_data


def create_lookup_dict():
    dict = {}
    # range does not initialise the last element
    for month in range(1, 13):
        for day in ["H", "W"]:
            for hour in range(0, 24):
                dict[str(hour)+ str(day) + str(month)] = []
    return dict


def fill_lookup_dict(data):
    dict = create_lookup_dict()
    level_presented = True if 'level' in data.columns else False
    for index, row in data.iterrows():
        day = "W"
        if not row["TimeStamp"].weekday() < 5:
            day = "H"
        key = str(row["TimeStamp"].hour) + day + str(row["TimeStamp"].month)
        if level_presented:
            dict[key].append({"flow": row["flow"], "level": row["level"]})
        else:
            dict[key].append({"flow": row["flow"], "level": float('nan')})
    return dict


def get_statistics(data):
    if len(data) != 0 and not np.isnan(data).all():
        data = [x for x in data if not pd.isnull(x)]
        return [np.mean(data), np.min(data), np.max(data)]
    else:
        return [np.nan, np.nan, np.nan]


def calculate_statistics(lookup_dict):
    statistics = pd.DataFrame(index= lookup_dict.keys(),
                               columns=['AVG_FLOW', 'MIN_FLOW', 'MAX_FLOW', 'AVG_LEVEL', 'MIN_LEVEL',
                                        'MAX_LEVEL', 'COUNT'] )
    for key, value in lookup_dict.items():
        flow_measures = []
        level_measures = []
        for measurement in value:
            flow_measures.append(measurement["flow"])
            level_measures.append(measurement["level"])
        df_entry = get_statistics(flow_measures)
        df_entry.extend(get_statistics(level_measures))
        df_entry.append(len(flow_measures))
        statistics.loc[key] = df_entry
    statistics.index.name = 'Time'
    if statistics["AVG_LEVEL"].isnull().all():
        statistics.drop(['AVG_LEVEL', 'MIN_LEVEL', 'MAX_LEVEL'], axis=1, inplace=True)
    return statistics



def main():
    station_files = get_file_names()
    for file in station_files:
        station_data = get_dry_periods(file)
        lookup = fill_lookup_dict(station_data)
        statistics = calculate_statistics(lookup)
        statistics.to_csv(config.ROOT_DIR / config.lookup_dir / os.path.basename(file))




if __name__ == '__main__':
    main()