import config
import pandas as pd
import os
import glob
import datetime
import matplotlib.pyplot as plt


def get_file_names(directory):
    extension = 'csv'
    os.chdir(directory)
    files = [i for i in glob.glob('*.{}'.format(extension))]
    os.chdir(config.ROOT_DIR)
    return files


def get_day_type(date):
    # W for weekday, H for holiday
    return "W" if date.weekday() < 5 else "H"


def get_lookup_index(date):
    return str(date.hour) + get_day_type(date) + str(date.month)


def read_rain_data(file_name):
    data = pd.read_csv(file_name).dropna()
    data["TimeStamp"] = pd.to_datetime(data["TimeStamp"], format="%Y-%m-%d %H:%M:%S")
    return data


def get_rain_information(rain_df, lookup_data):
    previous_time = rain_start = rain_df.iloc[0]["TimeStamp"]
    rain_aggregated_info = pd.DataFrame(columns=['End', 'Rain_Hours', 'Influence_Hours', 'Total_Outflow', 'Total_Volume'])
    pump_rain_column = [col for col in rain_df.columns if 'PUMP_VOLUME' in col][0]
    pump_rain_height_column = [col for col in rain_df.columns if 'PUMP_AVG_HEIGHT' in col][0]
    is_previous_hour_rainy = False
    total_outflow = 0
    total_volume = 0
    influence_hours = 0
    for index, row in rain_df.iterrows():
        if row[pump_rain_height_column] < config.min_rain_threshold:
            if is_previous_hour_rainy:
                # if flow is not measured during an hour then stop time period as rain
                if (int((row["TimeStamp"] - previous_time).total_seconds() / 3600) > 1) or \
                        (lookup_data.loc[get_lookup_index(row["TimeStamp"])]["MAX_FLOW"] >= row["flow"]):
                    rain_aggregated_info.loc[rain_start] = [previous_time,
                                                            # add one to include the first hour of rain
                                                            (previous_time - rain_start).total_seconds() / 3600 + 1 - influence_hours,
                                                            influence_hours,
                                                            total_outflow,
                                                            total_volume]
                    total_volume = 0
                    total_outflow = 0
                    influence_hours = 0
                    is_previous_hour_rainy = False
                else:
                    influence_hours += 1
                    total_outflow += row["flow"]
                    total_volume += row[pump_rain_column]

        else:
            if not is_previous_hour_rainy:
                rain_start = row["TimeStamp"]
                is_previous_hour_rainy = True
            total_outflow += row["flow"]
            total_volume += row[pump_rain_column]
            influence_hours += 1
            influence_hours = 0
        previous_time = row["TimeStamp"]
    rain_aggregated_info.index.name = 'Start'
    return rain_aggregated_info


def read_lookup_data(file):
    data = pd.read_csv(file)
    data.set_index("Time", inplace=True)
    return data


def calculate_rain_sewage_percentage(rains, lookup_table):
    rains["LookUp_Max_Flow"] = 0
    rains["LookUp_Avg_Flow"] = 0
    rains["Finish_Avg"] = 0
    rains["Finish_Max"] = 0

    for index, row in rains.iterrows():
        if pd.isnull(row["Total_Outflow"]):
            continue
        current_lookup_avg_flow = current_lookup_max_flow = 0
        current_timestamp = index

        while current_timestamp <= row["End"]:
            lookup_index = str(current_timestamp.hour) + get_day_type(current_timestamp) \
                           + str(current_timestamp.month)
            current_lookup_avg_flow += lookup_table.loc[lookup_index]["AVG_FLOW"]
            current_lookup_max_flow += lookup_table.loc[lookup_index]["MAX_FLOW"]
            current_timestamp += datetime.timedelta(hours=1)
        rains.set_value(index, "LookUp_Max_Flow", current_lookup_max_flow)
        # to get number in percent, value is multiplied by 100
        rains.set_value(index, "Finish_Max", max(0, min((row["Total_Outflow"] - current_lookup_max_flow) /
                        row["Total_Volume"] * 100, 100)))
        rains.set_value(index, "LookUp_Avg_Flow", current_lookup_avg_flow)
        rains.set_value(index, "Finish_Avg", max(0, min((row["Total_Outflow"] - current_lookup_avg_flow) /
                        float(row["Total_Volume"]) * 100, 100)))
    return rains


def update_rain_delay(rain_data, rain_info):
    rain_data.set_index("TimeStamp", inplace=True)
    rain_data["is_rainy"] = "0"
    for index, row in rain_info.iterrows():
        # offset is provided in hour, according to data granularity in the file
        offset = 0
        while index + pd.DateOffset(hours = offset) <= row["End"]:
            rain_data.at[index + pd.DateOffset(hours = offset), 'is_rainy'] = "1"
            offset += 1
    return rain_data


def draw_recovery_plots(rain_statistics, station_name):
    fig = plt.figure()
    plt.scatter(rain_statistics["Rain_Hours"], rain_statistics["Total_Volume"], label=None,
                c=rain_statistics["Influence_Hours"], cmap='gist_rainbow',
                linewidth=0, alpha=0.5)
    plt.axis(aspect='equal')
    plt.xlabel('Rain Hours')
    plt.ylabel('Total Volume')
    plt.colorbar(label='Time to recover')
    plt.title('Time to recover for station ' + station_name)
    fig.savefig(config.recovery_dir / (station_name + ".png"))


def draw_finish_in_sewage_plots(rain_statistics, station_name):
    fig = plt.figure()
    plt.scatter(rain_statistics["Rain_Hours"], rain_statistics["Total_Volume"], label=None,
                c=rain_statistics["Finish_Max"], cmap='gist_rainbow',
                linewidth=0, alpha=0.5)
    plt.axis(aspect='equal')
    plt.xlabel('Rain Hours')
    plt.ylabel('Total Volume')
    plt.colorbar(label='Percent of rain absorbed')
    plt.title('Rains flow in sewage in % for ' + station_name)
    fig.savefig(config.sewage_dir / (station_name + ".png"))


def main():
    files = get_file_names(config.aggregate_data_dir)
    for rain_file in files:
        rain_data = read_rain_data(config.aggregate_data_dir / rain_file)
        lookup_data = read_lookup_data(config.lookup_dir / rain_file)
        rain_info = get_rain_information(rain_data, lookup_data)
        rain_data = update_rain_delay(rain_data, rain_info)
        rain_data.to_csv(config.aggregate_data_dir / rain_file)
        rains_statistics = calculate_rain_sewage_percentage(rain_info, lookup_data)
        # get the name without extension
        station_name = os.path.basename(rain_file).split(".")[0]
        draw_recovery_plots(rains_statistics[["Rain_Hours","Total_Volume","Influence_Hours"]], station_name)
        draw_finish_in_sewage_plots(rains_statistics[["Rain_Hours", "Total_Volume", "Finish_Max"]], station_name)
        rains_statistics.to_csv(config.statistics_dir / rain_file)


if __name__ == '__main__':
    main()
