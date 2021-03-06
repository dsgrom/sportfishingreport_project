# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 10:19:20 2021

@author: Kevin
"""

import pandas as pd
import numpy as np

df = pd.read_csv("sfr_data_20200101_20210303.csv")
df2 = df.copy()
df.dtypes #check types, seems data imported as all strings



################################################ begin initial cleaning ##################################################
#cleaning list:
#(DONE) types: 'date' to date type, 'num_anglers' to numeric
#(DONE) indicator for "released"
#(DONE) catch parsing, expand dataset with duplicate rows so catch is 1 column, separate species and catch volume
#i.e. 2020-01-01 LA Spitfire is 3 rows: 50 ssand bass, 11 sculpin, 6 calico bass



#date2 as datetime type
df2['date2'] = pd.to_datetime(df2['date'], format = '%Y-%m-%d')
df2.dtypes



#num_anglers to numeric
df2['anglers'] = df2['num_anglers'].apply(lambda x: x.split('A')[0]).astype(int)
df2.dtypes



#catch parsing, must be done before release indicator, otherwise all of that boat's catch will say released
df2['catch2'] = df2['catch'].astype(str).apply(lambda x: x.split(',')) #separate comma separated string elements into a list
df2 = df2.explode('catch2') #explode list to elongate datatable, i.e. if catch has 3 different species, elongate to 3 rows
df2['catch2'] = df2['catch2'].str.strip() #strip leading and trailing whitespace



#indicator for released, needs to be done after parsing out individual fish counts from big string to avoid wrong labeling
df2['released'] = df2['catch2'].apply(lambda x: 1 if 'released' in x.lower() else 0)



#cut off weight limit pieces from species name
#splits string on '(', keeps second part of split which should be weight restrictions if available. else empty
restrictions = df2['catch2'].apply(lambda x: x.split('(')[1] if '(' in x.lower() else '')
restrictions = restrictions.apply(lambda x: x.replace(')', "")) #remove ')'
df2['restrictions'] = restrictions
df2['catch3'] = df2['catch2'].apply(lambda x: x.split('(')[0]) #remove restrictions from catch column

restrictions.value_counts() #see unique values and how many of each there are



#separate catch further into one column for species (str) and one column for catch amount (int)
df2['catch_count'] = pd.to_numeric(df2['catch3'].str.extract('(\d+)')[0], errors = 'coerce') #parse catch integer count to new column
df2['catch_species'] = df2['catch3'].str.extract('(\D+)')[0] #parse catch species into new column
df2['catch_species'] = df2['catch_species'].str.strip() #remove whitespace from species
df2['catch_species'] = df2['catch_species'].apply(lambda x: x.lower().replace('released', "")) #lowercase all and remove 'released' from elements



#drop intermediate catch columns, lower for all string columns
df2 = df2.drop(['catch2', 'catch3'], axis = 1)
df2['location'] = df2['location'].apply(lambda x: x.lower())
df2['boat_name'] = df2['boat_name'].astype(str).apply(lambda x: x.lower())
df2['trip_type'] = df2['trip_type'].astype(str).apply(lambda x: x.lower())



#export to csv
df2.to_csv('sfr_data_cleaned.csv', index = False)

df_check = pd.read_csv('sfr_data_cleaned.csv')

################################################ end initial cleaning ##################################################



#check boat_name and trip_type for duplicates/conslidate where possible
#if possible and if I can find it, merge in (ideally daily by region) SST data
#other oceanographic indicators that I can find (ideally daily by region) for free?
#check for typos and look at value counts
#some weird trip types?
#one instance of 'Puget Sound', one instance of 'Florida South' (??), can maybe delete these rows

#check for possible typos in boat_name and trip_type
print(sorted(df2['boat_name'].unique().astype(str))) #no typos as far as I can see
#might be able to consolidate some, need more research on what each trip type is and regional differences in names
print(sorted(df2['trip_type'].unique().astype(str)))









