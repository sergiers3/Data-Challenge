import pandas as pd
import os
import glob
import config
from os.path import isfile
import matplotlib.pyplot as plt


def write_dataset_info(df, file):
    file.write("Number of records is: " + str(df.shape[0]) + "\n")
    file.write("Min value is: " + str(df["Value"].min()) + "\n")
    file.write("Max value is: " + str(df["Value"].max()) + "\n")
    file.write("Mean value is: " + str(df["Value"].mean()) + "\n")
    file.write("Min Time Stamp is: " + str(df["TimeStamp"].min()) + "\n")
    file.write("Max Time Stamp is: " + str(df["TimeStamp"].max()) + "\n")


def write_empty_periods(df, file):
    df['time_diff'] = df['TimeStamp'].diff().apply(lambda value: value.total_seconds())
    file.write("\nDates when more than one hour of data missed:\n")
    df_outliers = df[df['time_diff'] > 3600]
    df_outliers = df_outliers.sort_values(by='time_diff', ascending=False)
    for index, row in df_outliers.iterrows():
        file.write("Period end: " + str(row["TimeStamp"]) + " Period length: " +
                str(row['time_diff']) + "\n")


def plot_values(df, image_location):
    plt.plot(df['TimeStamp'], df['time_diff'])
    plt.ylabel('Time')
    plt.ylabel('Time difference')
    plt.savefig(image_location)
    plt.close()

def print_statistics(file, saving_location, image_location):
    df = pd.read_csv(file, sep=";")
    if df["Value"].dtype == object:
        df["Value"] = df["Value"].apply(lambda value: value.replace(",", "."))
        df["Value"] = df["Value"].astype('float64')
    df["TimeStamp"] = pd.to_datetime(df['TimeStamp'], format='%d-%m-%Y %H:%M:%S')
    df = df.sort_values(by = 'TimeStamp')
    f = open(saving_location, "a")
    write_dataset_info(df, f)
    write_empty_periods(df, f)
    f.close()
    plot_values(df, image_location)

def main():
    starting_dir = config.Pathes['start']
    for station_data in os.walk(starting_dir):
        for file in glob.glob(station_data[0] + "\\*.csv"):
            if isfile(file):
                saving_file = config.Pathes['save'] + os.path.basename(file)[:-4] + ".txt"
                image = config.Pathes['save'] + os.path.basename(file)[:-4] + ".png"
                print_statistics(file, saving_file, image)


if __name__ == '__main__':
    main()