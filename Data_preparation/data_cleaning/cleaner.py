import pump_level_data_cleaner
import rain_data_cleaner
import wwtp_flow_data_cleaner


def main():
    rain_data_cleaner.clean_rain()
    pump_level_data_cleaner.clean_level_data()
    wwtp_flow_data_cleaner.merge_den_bosch_files()


if __name__ == '__main__':
    main()