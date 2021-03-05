# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 15:59:14 2021

@author: Kevin
"""

#run function sportfishScraper for date range, save to dataframe called 'data'

import pandas as pd
import sfr_scraper as sfs

#inputs
wd = "C:/Users/Kevin/Documents/Projects/Portfolio/sportfishingreport_project"
date_list = pd.date_range('2020-01-01','2021-03-03')


#format dates properly
date_list = date_list.format(formatter=lambda x: x.strftime('%Y-%m-%d'))
#print(date_list)

#initialize empty data dataframe
data = pd.DataFrame()


#loop through selected dates, append returned data to end of data
for day in date_list:
    print(day)
    data = data.append(sfs.sportfishing_scraper(wd, day))



#write to csv
sfs.csv_writer(data, "sfr_data_20200101_20210303")

