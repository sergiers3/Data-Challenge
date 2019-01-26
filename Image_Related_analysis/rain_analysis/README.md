# Project description
This project was created to address the issues that were mentioned by Waterchap AA En Mass such as __(1)__ finding out how much of the rain
volume finishes in the sewage system and __(2)__ how long rains do affect the pump station outflow. Additionally this project additionally
provides datasets that can be future explored by field experts. This findings as well can improve the initial rain data, especially, 
the automatic calculation of recovery time from previous stages.


## Project requirments
The following python3 modules are required to correctly run the project: 
1. Path
2. Pandas as pd
3. os
4. glob
5. datetime
6. matplotlib.pyplot

## Config Content
For correct project running the following information must be mentioned in config:

1. Root project directory _ROOT_DIR_
2. Aggregated data(in our case it was by one hour) _aggregate_data_dir_
3. Lookup directory _lookup_dir_
4. Folder for newly calculated rain statistics _statistics_dir_
5. Folder with time to recovery scatter plot _recovery_dir_
6. Folder with rain in the sewage percentage scatter plot _sewage_dir_

Aslo _min_rain_threshold_ must be included, in our case it is 0.5 mm.

## Date requirments
Before running the code the following datasets must be reciaved by running projects
1. lookup_creator
2. data_aggregator

## Rain Volume in the sewage system
The calculation is done in a simple way from aggregated_data folder the row regarding each hour measurements of pump flow and level 
and rain volume are recived. We assume that rain happening or still affecting the system if:
1. Average rain measurement for the pump area are higher than threshold 0.5mm(located in config file) or
2. Rain measurements are lower than threshold but the flow during this time is higher than maximum flow that happened during completely dry
period(this data is fetched from lookup table)
If it holds for each hour we update the statistics regarding the outflow during the rain time and lookup outflow during the same time 
but taking only measurement during dry periods. Later the rain in the system is calculated as the module of the difference between real 
outflow and lookup outflow divided by rain volume and multiplied by 100 to get percents. 
Of course this number can not be less than 0 and more than 100 percent.

## Time to recovery
For estimating this statistics the same approach is done as for previous calculation. However in this case we only calculate the hours when
above mentioned conditions hold. 

## Results
The image results are provided in folders recovery_images and sewage_percentage_img. Newly created datasets with these statistics are
located in the folder rain_statistics
