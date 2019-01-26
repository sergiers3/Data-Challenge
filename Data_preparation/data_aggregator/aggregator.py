from pathlib import Path

import pandas as pd
import config
import numpy
from data.stations import region_data


def get_aggregated_flow(all_pumps_flow, pump_name):
    pump_flow = pd.DataFrame(all_pumps_flow[(all_pumps_flow["Tag Name"] == pump_name)])
    if len(pump_flow.index) == 0:
        return pd.DataFrame()
    # all data belongs to the same station, no need to keep the tag name
    del pump_flow["Tag Name"]
    pump_flow["TimeStamp"] = pd.to_datetime(pump_flow["TimeStamp"], format='%d-%m-%Y %H:%M:%S')
    pump_flow = pump_flow.sort_values(by=['TimeStamp'])

    pump_flow = pump_flow.set_index('TimeStamp')
    # sample first by 5 minutes and then by one hour
    pump_flow = pump_flow.resample('5T').mean()
    pump_flow = pump_flow[~numpy.isnan(pump_flow)].resample('60T').mean()
    return pump_flow


def get_aggregated_level(pump_level_file):
    if not Path(pump_level_file).is_file():
        return pd.DataFrame()
    pump_level = pd.read_csv(pump_level_file, sep=",", index_col=[0])
    pump_level = pump_level.rename(columns={'Value': 'level'})
    del pump_level["Tag Name"]
    pump_level["TimeStamp"] = pd.to_datetime(pump_level["TimeStamp"], format='%Y-%m-%d %H:%M:%S')
    pump_level = pump_level.sort_values(by=['TimeStamp'])

    pump_level = pump_level.set_index('TimeStamp')
    max_level = pump_level.resample('5T').max()
    max_level = max_level[~numpy.isnan(max_level)].resample('60T').max()
    # sample first by 5 minutes and then by one hour
    pump_level = pump_level.resample('5T').mean()
    pump_level = pump_level[~numpy.isnan(pump_level)].resample('60T').mean()
    pump_level["Max_level"] = max_level
    return pump_level


def get_rain_data(rain_file):
    if not Path(rain_file).is_file():
        return pd.DataFrame()
    rain_data = pd.read_csv(rain_file, sep=",")
    rain_data["Eind"] = pd.to_datetime(rain_data["Eind"], format='%d-%m-%Y %H:%M:%S')
    rain_data = rain_data.set_index('Eind')
    return rain_data


def set_rain_flag(pump_data):
    time_since_rain = config.station_recovery_time
    previous_time_point = pump_data.index[0]
    avg_height_column = [col for col in pump_data.columns if 'PUMP_AVG_HEIGHT' in col][0]
    pump_data["is_rainy"] = 0
    # timestamp is stored in index column
    for index, row in pump_data.iterrows():
        row_time = pd.to_datetime(index)
        if row[avg_height_column] >= config.min_rain_height:
            time_since_rain = 0
            pump_data.at[index, 'is_rainy'] = 1
        else:
            time_since_rain += (row_time - previous_time_point).total_seconds() / 3600
            if time_since_rain < config.station_recovery_time:
                pump_data.at[index, 'is_rainy'] = 1
        previous_time_point = row_time
    return pump_data



def aggregate_data(region_data, region_name):
    all_pumps_flow = pd.read_csv(config.outflow_dir / "flow.csv", sep=",")
    all_pumps_flow = all_pumps_flow.rename(columns={'Value': 'flow'})
    for pump_station in region_data:
        pump_aggregated_data = get_aggregated_flow(all_pumps_flow, pump_station["pumpStation"])
        if len(pump_aggregated_data.index) == 0:
            continue
        pump_level_data = get_aggregated_level(config.level_dir / str(pump_station["areaName"] + ".csv"))
        pump_rain_data = get_rain_data(config.rain_dir/ region_name/ str(pump_station["areaName"] + ".csv"))
        if len(pump_level_data) > 0:
            pump_aggregated_data = pd.merge(pump_aggregated_data, pump_level_data, how="inner",
                                        left_index=True, right_index=True)
        if len(pump_rain_data) > 0:
            pump_aggregated_data = pd.merge(pump_aggregated_data, pump_rain_data, how="inner",
                                        left_index=True, right_index=True)
        pump_aggregated_data.index.name = 'TimeStamp'
        pump_aggregated_data = set_rain_flag(pump_aggregated_data)
        pump_aggregated_data.to_csv(config.result_dir / str(pump_station["areaName"] + ".csv"))


if __name__ == '__main__':
    for region in config.analysis_regions:
        aggregate_data(region_data[region], region)