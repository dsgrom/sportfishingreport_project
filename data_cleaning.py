# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 10:19:20 2021

@author: Kevin
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

os.chdir("C:/Users/Kevin/Documents/Projects/Portfolio/sportfishingreport_project")

df = pd.read_csv("sfr_data_20200101_20210309.csv")
#df = pd.read_csv("sfr_data_2019_FY.csv")

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
df2['year'] = df2['date2'].apply(lambda x: x.year)
df2['month'] = df2['date2'].apply(lambda x: x.month)
df2['day'] = df2['date2'].apply(lambda x: x.day)
df2['day_of_week'] = df2['date2'].apply(lambda x: x.strftime('%A'))



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
df2['catch_species'] = df2['catch_species'].apply(lambda x: x.lower().replace('released', "") if pd.notnull(x) else 0) #lowercase all and remove 'released' from elements



#drop intermediate catch columns, lower for all string columns
df2 = df2.drop(['catch2', 'catch3'], axis = 1)
df2['location'] = df2['location'].apply(lambda x: x.lower())
df2['boat_name'] = df2['boat_name'].astype(str).apply(lambda x: x.lower())
df2['trip_type'] = df2['trip_type'].astype(str).apply(lambda x: x.lower())



#export to csv
df2.to_csv('sfr_data_cleaned.csv', index = False)

################################################ end initial cleaning ##################################################



################################################### addtl cleaning #####################################################

#import cleaned data from part 1
df_raw = pd.read_csv("sfr_data_cleaned.csv")
df = df_raw.copy()

#drop redundant columns
df = df.drop(['date', 'catch', 'num_anglers'], axis = 1)
df['restrictions_yn'] = df['restrictions'].apply(lambda x: 1 if pd.notnull(x) else 0)

#remove the florida south, puget sound, lake tahoe, and delta ones since there's so little data
location_list = ['florida south', 'puget sound', 'delta', 'lake tahoe']
df.drop(df.loc[df['location'].isin(location_list)].index, inplace = True) #removes rows



######################################### function to replace trip_type according to above notes #######################################
def trip_type_simplifier(trip_type):
    if trip_type == '2.75 day trip':
        return 'multi-day trip'
    elif trip_type == '1.75 day trip':
        return '2 day trip'
    elif trip_type == '12 hour':
        return 'full day trip'
    #elif trip_type == '4 day trip' or trip_type == '5 day trip':
    elif trip_type in ['3 day trip', '3.5 day trip', '4 day trip', '5 day trip']:
        return 'multi-day trip'
    #elif trip_type == '4 hour' or trip_type == '5 hour' or trip_type == '6 hour':
    elif trip_type in ['4 hour', '5 hour', '6 hour']:
        return '1/2 day trip'
    #elif trip_type == '7 hour' or trip_type == '8 hour':
    elif trip_type in ['7 hour', '8 hour', '3/4 day local', '3/4 day islands']:
        return '3/4 day trip'
    elif trip_type == 'extended 1.5 day trip':
        return '1.5 day trip'
    elif trip_type in ['crab', 'crab combo', 'dungeness crab', 'dungeness crab am']:
        return 'crabbing trip'
    elif trip_type in ['salmon', 'salmon mooching', 'salmon trolling']:
        return 'salmon trip'
    elif trip_type in ['lobster', 'halibut', 'offshore halibut']:
        return 'other trip'
    elif trip_type == None:
        return 'na'
    else:
        return trip_type

##################################################### fixing species typos first ##############################################
def species_typo_fixer(catch_species):
    #fish
    if 'rockcod' in catch_species:
        return catch_species.replace('rockcod', 'rockfish')
    elif 'vermillion' in catch_species:
        return catch_species.replace('vermillion', 'vermilion')
    elif catch_species == 'salmon grouper':
        return 'bocaccio'
    elif catch_species == 'chilipepper':
        return 'chilipepper rockfish'
    elif catch_species == 'kelp bass':
        return 'calico bass'
    elif catch_species == 'barred sand bass':
        return 'sand bass'
    elif catch_species == 'blacksmith':
        return 'blacksmith perch'
    elif 'halfmoon' in catch_species:
        return 'blue perch'
    elif catch_species == 'ocean whitefish':
        return 'whitefish'
    elif catch_species in ['chinook salmon', 'chinoook salmon']:
        return 'king salmon'
    elif catch_species == 'mahi mahi':
        return 'dorado'
    elif catch_species == 'california yellowtail':
        return 'yellowtail'
    elif catch_species == 'california barracuda':
        return 'barracuda'
    elif 'bonito' in catch_species:
        return 'bonito'
    elif 'albacore' in catch_species:
        return 'albacore tuna'
    elif catch_species == 'giant seabass':
        return 'black seabass'
    elif catch_species == 'whote seabass':
        return 'white seabass'

    #not sure about these two
    elif catch_species == 'spanish jack':
        return 'jack mackerel'
    elif catch_species == 'spanish mackerel':
        return 'mackerel'
    
    #crab
    elif catch_species == 'dungeoness crab':
        return 'dungeness crab'
    elif catch_species == 'red rock crab':
        return 'rock crab'
    
    #shark
    elif 'dog' in catch_species:
        return 'spiny dogfish shark'
    
    else:
        return catch_species



############################################ function to replace catch_species #######################################
def species_generalizer(catch_species):
    #fish
    #rockfish
    if 'rockfish' in catch_species:
        return 'rockfish'
    if catch_species in ['bocaccio', 'bolina', 'treefish']: #also rockfish
        return 'rockfish'
    #bass, should not include white and black seabass, other huge basses
    elif catch_species in ['calico bass', 'kelp bass', 'sand bass', 'barred sand bass', 'striped bass', 'spotted bay bass', 'spotted sand bass']:
        return 'bass'
    #perch
    elif 'perch' in catch_species:
        return 'perch'
    #salmon
    elif catch_species in ['king salmon', 'silver salmon', 'coho salmon', 'pink salmon', 'chum salmon']:
        return 'salmon'
    #halibut
    elif 'halibut' in catch_species:
        return 'halibut'
    #tuna
    elif catch_species in ['yellowfin tuna', 'bigeye tuna', 'bluefin tuna', 'skipjack tuna', 'albacore tuna']:
        return 'tuna'
    #CHECK THIS ONE TO MAKE SURE IT WORKS
    #swordfish and marlin
    elif 'swordfish' in catch_species or 'marlin' in catch_species:
        return 'billfish'
    
    #baitfish
    elif 'mackerel' in catch_species:
        return 'baitfish'

    #sharks
    elif 'shark' in catch_species:
        return 'shark'

    
    #crab
    elif 'crab' in catch_species:
        return 'crab'
    
    #other
    elif catch_species in ['black croaker', 'sargo', 'black seabass', 'billfish', 'white sturgeon', 'sand sole', 'fantail sole', \
                           'mexican scad', 'wolf eel', 'kelp greenling', 'white croaker', 'starry flounder', 'flounder', 'bat ray', \
                           'bonefish', 'octopus', 'diamond turbot', 'opah', 'yellowfin croaker', 'sunfish', 'brown smoothhound', \
                           'broomtail grouper', 'snowy grouper']:
        return 'other'

    #to catch others and na's, but wonder if i can replace above with the below as else return other?
    else:
        return catch_species
    
    

################################################### applying above functions: #################################################
#simplify trip type
df['trip_type'] = df['trip_type'].apply(trip_type_simplifier)

#strip leading/trailing whitespace from catch_species
df.catch_species = df.catch_species.apply(lambda x: x.strip() if pd.notnull(x) else x)
#fix species typos
df['catch_species'] = df['catch_species'].apply(lambda x: species_typo_fixer(x) if pd.notnull(x) else x)

#run catch_species through generalizer
df['catch_species_general'] = df['catch_species'].apply(lambda x: species_generalizer(x) if pd.notnull(x) else x)



#export to csv
df.to_csv('sfr_data_cleaned_v2.csv', index = False)
#df.to_csv('sfr_data_cleaned_2019.csv', index = False)






    
    
