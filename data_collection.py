# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 15:59:14 2021

@author: Kevin
"""

#run function sportfishScraper for date range, save to dataframe called 'data'


#set working directory
import pandas as pd
import os

wd = "C:/Users/Kevin/Documents/Projects/Portfolio/sportfishingreport_project"
os.chdir(wd)

#inputs
import sfr_scraper2 as sfs

date_list = pd.date_range('2019-01-01','2019-12-31')


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
sfs.csv_writer(data, "sfr_data_2019_FY")

