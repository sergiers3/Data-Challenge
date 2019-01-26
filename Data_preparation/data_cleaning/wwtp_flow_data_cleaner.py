import pandas as pd
import config


def read_wwtp_flow_file(file):
    wwtp_flow = pd.read_csv(file, delimiter=";")
    wwtp_flow["TimeStamp"] = pd.to_datetime(wwtp_flow['TimeStamp'], format='%d-%m-%Y %H:%M:%S')
    wwtp_flow.index = wwtp_flow["TimeStamp"]
    return wwtp_flow


def merge_den_bosch_files():
    den_bosch_1 = read_wwtp_flow_file(config.wwtp_flow_dir / config.den_bosch_1)
    den_bosch_2 = read_wwtp_flow_file(config.wwtp_flow_dir / config.den_bosch_2)
    den_bosch_1 = den_bosch_1.resample("1T").mean()
    den_bosch_2 = den_bosch_2.resample("1T").mean()
    den_bosch_1 = den_bosch_1.append(den_bosch_2).dropna()
    den_bosch_1 = den_bosch_1.groupby(den_bosch_1.index).sum()
    den_bosch_1.to_csv(config.wwtp_out_flow_dir / config.den_bosch_1, sep=',')