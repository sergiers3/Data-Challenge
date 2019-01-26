# Rainflow-pump outflow analysis  
  
This code provides repeatable visual analysis of average dry and wet pump outflow in comparison with rain flows.  
The project consists of 2 methods: aggregate_data(file_name, full_week=False, months=[], weekends_mode=0):) and plot(aggregated_dataset, region_name).  
In details, full_week can be False for analysis by hours or True for weekofweek-hour visualisaiton;  
months - array with list of months. By default it is empty and uses the whole dataset. E.g. months=[1,2,12] will analyse only winter months;  
eekends_mode provides an opportunity to filter weekends. So, weekends_mode=0 is used to analyse the whole week, weekends_mode=1 to analyse only working days,
weekends_mode=2 to analyse only weekends.  