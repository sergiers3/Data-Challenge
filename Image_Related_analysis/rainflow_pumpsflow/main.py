import glob
import os.path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy.stats

from config import aggregated_data_dir, weekend_index, confidence_interval, images_dir, path

# the 1-st month is January but not 0-th
short_days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']


def get_file_names(dir):
    extension = 'csv'
    os.chdir(dir)
    result = [i for i in glob.glob('*.{}'.format(extension))]
    os.chdir(str(path))
    return result


def determine_weekend(timestamps):
    result = []
    for timestamp in timestamps:
        if timestamp.dayofweek >= weekend_index:
            result.append(1)
        else:
            result.append(0)
    return result


def get_day_hour(timestamps):
    result = []
    for timestamp in timestamps:
        result.append(str(timestamp.dayofweek) + "-" + str(timestamp.hour))
    return result


def get_day_names(indexes):
    result = []
    for index in indexes:
        result.append(short_days[int(index.split('-')[0])] + '-' + index.split('-')[1])
    return result


def calculate_conf_int(np_data, n):
    np_se = {'flow_dry': scipy.stats.sem(np_data['flow_dry']),
             'flow_wet': scipy.stats.sem(np_data['flow_wet']),
             'rain': scipy.stats.sem(np_data['rain']),
             }
    # idea by https://stackoverflow.com/questions/15033511/compute-a-confidence-interval-from-sample-data
    return {'flow_dry': np_se['flow_dry'] * scipy.stats.t.ppf((1 + confidence_interval) / 2., n - 1),
            'flow_wet': np_se['flow_wet'] * scipy.stats.t.ppf((1 + confidence_interval) / 2., n - 1),
            'rain': np_se['rain'] * scipy.stats.t.ppf((1 + confidence_interval) / 2., n - 1),
            }


def aggregate_data(file, full_week=False, months=[], weekends_mode=0):
    # full_week - False - only hours, True - with day, months - array of months to show
    # weekends_mode : 0 - all days, 1 - only working days, 2 - only weekends
    flow_data = pd.read_csv(aggregated_data_dir / file)
    flow_data['TimeStamp'] = pd.to_datetime(flow_data['TimeStamp'], format="%Y-%m-%d %H:00:00")
    flow_data = flow_data.set_index('TimeStamp')
    rain_volume_column = 'PUMP_VOLUME_' + file.replace('.csv', '')
    if len(months) > 0:
        flow_data = flow_data[flow_data.index.month.isin(months)]
    if not (full_week):
        if weekends_mode == 1:
            flow_data['WEEKEND_FLAG'] = determine_weekend(flow_data.index)
            flow_data = flow_data[flow_data['WEEKEND_FLAG'] == 0]
        if weekends_mode == 2:
            flow_data['WEEKEND_FLAG'] = determine_weekend(flow_data.index)
            flow_data = flow_data[flow_data['WEEKEND_FLAG'] == 1]
    aggregated_flow_data = flow_data.groupby([flow_data.index.hour, flow_data['is_rainy']]).agg(
        {rain_volume_column: 'mean',
         'flow': 'mean'}).reset_index().rename(columns={rain_volume_column: 'rain'})

    if full_week:
        flow_data['DAY-HOUR'] = get_day_hour(flow_data.index)
        aggregated_flow_data = flow_data.groupby([flow_data['DAY-HOUR'], flow_data['is_rainy']]).agg(
            {rain_volume_column: 'mean',
             'flow': 'mean'}).reset_index().rename(columns={rain_volume_column: 'rain'})
        lambda_divide_day_hour = lambda x: pd.Series([int(x['DAY-HOUR'].split('-')[0]),
                                                      int(x['DAY-HOUR'].split('-')[1])])

        aggregated_flow_data[['day_int', 'hour']] = aggregated_flow_data.apply(lambda_divide_day_hour, axis=1)
        aggregated_flow_data = aggregated_flow_data.sort_values(['day_int', 'hour'], ascending=[True, True])
        aggregated_flow_data['TimeStamp'] = get_day_names(aggregated_flow_data['DAY-HOUR'])
        aggregated_flow_data = aggregated_flow_data[['TimeStamp', 'is_rainy', 'flow', 'rain']]
    return aggregated_flow_data


def plot(flow_data, area_name):
    table_rows = ['Average dry', 'AVG+conf dry', 'AVG-conf dry', 'Average wet', 'AVG+conf wet', 'AVG-conf wet', 'Rain',
                  'Rain + conf', 'Rain - conf']
    table_rows_colors = ['#ff7f0d', '#ff7f0d', '#ff7f0d', '#1F77B4', '#1F77B4', '#1F77B4', '#A3BD9C', '#A3BD9C',
                         '#A3BD9C']

    dry = flow_data[flow_data['is_rainy'] == 0]
    wet = flow_data[flow_data['is_rainy'] == 1]
    np_data = {'flow_dry': np.array(dry['flow']),
               'flow_wet': np.array(wet['flow']),
               'rain': np.array(wet['rain']),
               }

    n = len(dry)
    if n < 30:
        x = np.arange(0, n, 1)
    else:
        x = list(dry['TimeStamp'])
    np_h = calculate_conf_int(np_data, n)

    fig, ax = plt.subplots(figsize=((30 if n < 30 else 100), 15))
    # plot dry perionds
    plt.title('Flow of Dry and Wet periods of pumping station in ' + area_name)
    ax.plot(x, np_data['flow_dry'], color='#ff7f0d')
    ax.plot(x, np_data['flow_dry'] + np_h['flow_dry'], "r--", color='#ff7f0d', label="Upper Bond / Lower Bond")
    ax.plot(x, np_data['flow_dry'] - np_h['flow_dry'], "r--", color='#ff7f0d', label="Upper Bond / Lower Bond")
    ax.fill_between(x, np_data['flow_dry'] - np_h['flow_dry'], np_data['flow_dry'] + np_h['flow_dry'], color="#ff7f0d",
                    alpha=.5)

    # plot wet periods
    ax.plot(x, np_data['flow_wet'], color='#1F77B4')
    ax.plot(x, np_data['flow_wet'] + np_h['flow_wet'], "r--", color='#1F77B4', label="Upper Bond / Lower Bond")
    ax.plot(x, np_data['flow_wet'] - np_h['flow_wet'], "r--", color='#1F77B4', label="Upper Bond / Lower Bond")
    ax.fill_between(x, np_data['flow_wet'] - np_h['flow_wet'], np_data['flow_wet'] + np_h['flow_wet'], color="#1F77B4",
                    alpha=.5)

    # plot rain
    ax.plot(x, np_data['rain'], color='#A3BD9C')
    ax.plot(x, np_data['rain'] + np_h['rain'], "r--", color='#A3BD9C', label="Upper Bond / Lower Bond")
    ax.plot(x, np_data['rain'] - np_h['rain'], "r--", color='#A3BD9C', label="Upper Bond / Lower Bond")
    ax.fill_between(x, np_data['rain'] - np_h['rain'], np_data['rain'] + np_h['rain'], color="#A3BD9C", alpha=.5)

    ax.set_xlabel('Hour')
    ax.set_ylabel('Flow (m3/h)')
    ax.set_xticks(x)
    plt.grid(True)

    # round floats
    cell_values = [
        ["%.2f" % x for x in np_data['flow_dry']],
        ["%.2f" % x for x in np_data['flow_dry'] + np_h['flow_dry']],
        ["%.2f" % x for x in np_data['flow_dry'] - np_h['flow_dry']],
        ["%.2f" % x for x in np_data['flow_wet']],
        ["%.2f" % x for x in np_data['flow_wet'] + np_h['flow_wet']],
        ["%.2f" % x for x in np_data['flow_wet'] - np_h['flow_wet']],
        ["%.2f" % x for x in np_data['rain']],
        ["%.2f" % x for x in np_data['rain'] + np_h['rain']],
        ["%.2f" % x for x in np_data['rain'] - np_h['rain']]]
    # plot table
    plt.table(cellText=cell_values,
              rowLabels=table_rows,
              rowColours=table_rows_colors,
              colLabels=x,
              loc='bottom',
              bbox=[0.04, -0.45, 0.95, .28])
    plt.subplots_adjust(left=0.03, bottom=0.4, right=1)
    image_name = area_name + '.png'
    fig.savefig(images_dir / image_name)
    plt.clf()


def main():
    for file_name in get_file_names(aggregated_data_dir):
        plot(aggregate_data(file_name), file_name.replace('.csv', ''))


if __name__ == '__main__':
    main()
