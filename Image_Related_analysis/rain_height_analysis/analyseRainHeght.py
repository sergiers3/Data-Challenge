import os.path
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import path, dirWithData, csv_separator, areasFile, rainDataFile, dirWithImages, min_rain
from data.stations import regionData


def check_image_dir():
    if not os.path.isdir(path / dirWithImages):
        os.mkdir(path / dirWithImages)


def plot_histogram(rain_measurements, area_name):
    check_image_dir()
    plt.figure(figsize=(35, 10))
    fig, plot = plt.subplots()
    plot.plot(rain_measurements)
    plot.set(xlabel='Rain height', ylabel='Hours',
             title='Rain distribution in ' + area_name)
    x_values = np.arange(min(rain_measurements.index), max(rain_measurements.index) + 1, 1)
    plot.axes.set_xticks(x_values)
    plt.savefig(str(dirWithImages) + str(Path('/')) + area_name + ".png")


def analyse_rain(region):
    # check if files exist
    if not os.path.isfile(path / dirWithData / areasFile):
        print("File " + str(path / dirWithData / areasFile) + " doesn't exist")
        return;
    if not os.path.isfile(path / dirWithData / rainDataFile):
        print("File " + str(path / dirWithData / rainDataFile) + " doesn't exist")
        return;
    # read file with areas and rain data
    areas = pd.read_csv(path / dirWithData / areasFile, delimiter=csv_separator, decimal=',')
    rain = pd.read_csv(path / dirWithData / rainDataFile, delimiter=csv_separator, decimal=',',
                       index_col=1)
    rain['Begin'] = pd.to_datetime(rain['Begin'], format = '%d.%m.%y %H:00')
    # ignore gaps in data
    rain = rain[~rain['Kwaliteit'].isin(["Geen data", "Ongekalibreerd"])]
    # create dictionary of areas and its square in m2
    areas = dict(zip(areas["RGDIDENT"].tolist(), areas["Area"].tolist()))
    for pump_area in region:
        region_area_size = 0
        pump_rain = pd.DataFrame(index=rain.index)
        for area in pump_area['rainAreas']:
            area_name = area[0]
            area_code = area[1]
            region_area_size += areas[area_code]
            pump_rain[area_name] = rain[area_name].map(lambda x: x * areas[area_code])
        # height is taken as average rain height for all the pump
        pump_rain['HEIGHT'] = pump_rain.sum(1) / region_area_size
        # take only data with rain > than min_rain
        pump_rain = pump_rain[(pump_rain['HEIGHT'] > min_rain)]
        # round heights to be able to group it
        pump_rain['HEIGHT'] = pump_rain['HEIGHT'].map(lambda x: round(x, 1))
        # group rain values
        pump_rain_measurements = pump_rain.groupby(['HEIGHT'])['HEIGHT'].count()
        plot_histogram(pump_rain_measurements, pump_area['areaName'])


def main():
    analyse_rain(regionData['Aarle-Rixtel'])


if __name__ == '__main__':
    main()
