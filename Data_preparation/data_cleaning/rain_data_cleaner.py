import os.path

import pandas as pd

from config import path, rain_dir, csv_separator, areas_file, rainDataRowsToSkip, rain_out_dir, data_dir
from data.stations import regionData


def get_rain_data():
    rain_concatenated = pd.DataFrame()
    for rain_file in os.listdir(str(path / rain_dir)):
        if '.csv' in rain_file:
            rain_concatenated = rain_concatenated.append(pd.read_csv(path / rain_dir / rain_file,
                                                                     delimiter=csv_separator,
                                                                     skiprows=rainDataRowsToSkip))
    # remove uncalibrated and incorrect rows
    rain_concatenated = rain_concatenated[~rain_concatenated['Kwaliteit'].isin(["Geen data", "Ongekalibreerd"])]
    return rain_concatenated


def get_areas():
    areas = pd.read_csv(path / data_dir/  areas_file, delimiter=';', decimal=',')
    # create dictionary of areas and its square in m2
    areas = dict(zip(areas["RGDIDENT"].tolist(), areas["Area"].tolist()))
    return areas


def clearRainData(rain_data, areas, region, region_name):
    region_rain_data = pd.DataFrame(rain_data['Eind'])
    region_dir = path / rain_out_dir / str(region_name + "/")
    if not os.path.exists(region_dir):
        os.makedirs(region_dir)
    for pump in region:
        pump_total_area_size = 0
        pump_area_volumes = []
        pump_rain_data = pd.DataFrame(rain_data['Eind'])
        for area in pump['rainAreas']:
            area_name = area[0]
            area_code = area[1]
            area_size = areas[area_code]
            pump_total_area_size += area_size
            pump_rain_data[area_name]= rain_data[area_name]
            # volume in particular area in m3
            pump_rain_data["VOLUME_" + area_name] = pump_rain_data[area_name].map(
                lambda height: height * area_size) / 10000
            pump_area_volumes.append('VOLUME_' + area_name)
        # calculate general volume for pump area
        pump_rain_data["PUMP_VOLUME_" + pump['areaName']] = pump_rain_data[pump_area_volumes].sum(1)
        pump_rain_data["PUMP_AVG_HEIGHT_" + pump['areaName']] = \
            pump_rain_data["PUMP_VOLUME_" + pump['areaName']] / pump_total_area_size * 10000
        pump_rain_data.to_csv(region_dir/ str(pump['areaName'] + ".csv"), index=False)
        region_rain_data = pd.merge(region_rain_data, pump_rain_data,  how='inner', on=['Eind'])
    region_rain_data.to_csv(path / rain_out_dir / str(region_name + ".csv"), index=False)


def clean_rain():
    rain_concatenated = get_rain_data()
    areas = get_areas()
    for region in regionData:
        clearRainData(rain_concatenated, areas, regionData[region], region)

