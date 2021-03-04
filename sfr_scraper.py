# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 14:50:17 2021

@author: Kevin
"""


def sportfishScraper (date):
    #initializing packages
    import os
    import pandas as pd

    #import selenium, commented portion is install for selenium through conda
    import selenium
    #!conda install --yes --prefix {sys.prefix} selenium

    #using chrome
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options

    #set working directory
    os.chdir(r"C:\Users\Kevin\Documents\Coding projects\Python\Web scraper")

    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")

    #path to chromedriver.exe
    chrome_driver = os.getcwd() +"\\chromedriver.exe"

    # go to sportfishingreport.com page on date
    driver = webdriver.Chrome(options=chrome_options, executable_path=chrome_driver)
    driver.get("https://www.sportfishingreport.com/dock_totals/boats.php?date=" + date)

    #results containers (empty lists)
    location_list = []
    boatname_list = []
    landing_list = []
    city_list = []
    anglers_list = []
    catch_list = []
    triptype_list = []
    date_list = []

    #create list of html calls to class = panels
    panel_list = driver.find_elements_by_xpath("//*[@class='panel']") #search all class = 'panel', should have 2 for 3/18/2020

    for panel_index in panel_list:
        temp_location_list = None
        row_list = panel_index.find_elements_by_xpath(".//*[@class='row']")
        temp_location_list = panel_index.find_element_by_xpath(".//*[contains(text(),'Fish Counts')]").text #location
        for row_index in row_list:
            try:
                boatname_list.append(row_index.find_element_by_css_selector("b").text) #boatname
                anglers_list.append(row_index.find_element_by_xpath(".//*[@class='col-xs-3 col-xs-offset-1 col-md-2 col-md-offset-0 col-md-push-3']").text) #anglers
                triptype_list.append(row_index.find_element_by_xpath(".//*[@class='col-xs-3 col-md-2 col-md-push-3']").text) #trip type
                catch_list.append(row_index.find_element_by_xpath(".//*[@class='col-xs-11 col-xs-offset-1 col-md-3 col-md-offset-0 col-md-pull-5']").text) #catch
                location_list.append(temp_location_list[:-12]) #location
                date_list.append(date) #date
            except:
                pass
    
    
    df = pd.DataFrame(list(zip(date_list,location_list,boatname_list,triptype_list,anglers_list,catch_list)), 
               columns =['date','location','boat_name','trip_type','num_anglers','catch'])
    
    
    driver.close()
    return df;


#run function sportfishScraper for date range, save to dataframe called 'data'

date_list = pd.date_range('2010-01-01','2020-03-22')
date_list = date_list.format(formatter=lambda x: x.strftime('%Y-%m-%d'))
print(date_list)

#date_list = ['2020-03-16','2020-03-17','2020-03-18']
#print(date_list)

concat_list = []
print(concat_list)

for day in date_list:
    print(day)
    concat_list.append(sportfishScraper(day))
    data.append(data_temp)
    

#print(len(concat_list))
data = pd.concat(concat_list)


#function to write 'data' to csv

def csv_writer (dataframe, csv_name):
    try:
        dataframe.to_csv(csv_name + ".csv",index=False)
    except:
        print("Please enter both a dataframe and output name")

