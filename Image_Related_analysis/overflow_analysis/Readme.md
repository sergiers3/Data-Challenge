# main.ipynb  
This code analyzes the distribution of all well level readings for a year and a half, in order to analyze overflows  
  
# main.py  
The project calculates stress situations on the pumping stations (level = (max level)- 1 m) and percentage of such 
measurements during rainy hours.  
It uses two different approaches:  
* calculations on raw dataset  
* calculations on aggregated dataset  
  
Such analysis provides essential opportunities to analyse potential of overflows on the pumping stations (rainy hours with level>=(max-1)).  
``prepare_level_rain_dataset(region_data, region_name)`` - calculates such ratios which are based on preprocessed data.  
``count_by_rains(aggregated_rain_file)`` - calculates ratios by count of rains with high water level over total count of rains  
``count_by_hours(aggregated_rain_file)`` - calculates ratios by count of rainy hours with high water level over total count of rainy hours    
