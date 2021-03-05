# -*- coding: utf-8 -*-
"""
Created on Thu Mar  4 14:50:17 2021


@author: Kevin

Resources:
https://medium.com/@invest_gs/python-web-scraping-with-selenium-in-50-lines-of-code-free-tutorial-abe02e85ade9
https://medium.com/the-andela-way/introduction-to-web-scraping-using-selenium-7ec377a8cf72
"""


def sportfishing_scraper(wd, date):
    """
    Scrape location (city), boat name, trip type, number of anglers, and catch for a given date from sportfishingreport.com's party boat scores page
    Each webpage has one day's worth of catch records; this function only returns counts for one given day
    
    Note: missing landings, will hopefully add that in soon
    
    Returns dataframe (essentially 1 row of data)
    
    date must be entered in format "2021-03-03" (build in failsafe to first check if date is in correct format?)
    """
    #code for installing selenium through conda
    #!conda install --yes --prefix {sys.prefix} selenium

    #import packages
    import os
    import pandas as pd
#    import selenium
    from selenium import webdriver
#    from selenium.webdriver.chrome.options import Options #redundant?

    #set working directory
    os.chdir(wd)

    chrome_options = webdriver.ChromeOptions() #initialize webdriver in chrome
    chrome_options.add_argument("--headless") #prevents opening a new Chrome window every time
    chrome_options.add_argument("--window-size=1920x1080") #window size?

    #path to chromedriver.exe, need to make sure this is up to date for current version of chrome, self note to automate that
    chrome_driver = os.getcwd() +"\\chromedriver.exe"

    #navigate in ch rome to sportfishingreport.com dock totals page from chosen date
    driver = webdriver.Chrome(options=chrome_options, executable_path=chrome_driver)
    url = "https://www.sportfishingreport.com/dock_totals/boats.php?date=" + date
    driver.get(url)

    #results containers (empty lists)
    location_list = []
    boatname_list = []
    landing_list = [] #not currently used
    city_list = [] #not currently used
    anglers_list = []
    catch_list = []
    triptype_list = []
    date_list = []

    #create list of html calls to class = panels
    #each 'panel' on the page has a different area, i.e. one panel for Ventura Coast and one for San Diego and one for LA etc.
    #search all class = 'panel'
    panel_list = driver.find_elements_by_xpath("//*[@class='panel']")

    for panel_index in panel_list: #within each panel (region), there's multiple boats, so for each boat in each panel:
        temp_location_list = None
        row_list = panel_index.find_elements_by_xpath(".//*[@class='row']") #find each boat
        temp_location_list = panel_index.find_element_by_xpath(".//*[contains(text(),'Fish Counts')]").text #location = region, i.e. OC or SD or LA
        for row_index in row_list: #for each boat, try to collect:
            try:
                #landing
                #city
                boatname_list.append(row_index.find_element_by_css_selector("b").text) #boatname
                anglers_list.append(row_index.find_element_by_xpath(
                        ".//*[@class='col-xs-3 col-xs-offset-1 col-md-2 col-md-offset-0 col-md-push-3']").text) #anglers
                triptype_list.append(row_index.find_element_by_xpath(
                        ".//*[@class='col-xs-3 col-md-2 col-md-push-3']").text) #trip type
                catch_list.append(row_index.find_element_by_xpath(
                        ".//*[@class='col-xs-11 col-xs-offset-1 col-md-3 col-md-offset-0 col-md-pull-5']").text) #catch
                location_list.append(temp_location_list[:-12]) #location
                date_list.append(date) #date
            except:
                pass
    
    
    fish_counts_df = pd.DataFrame(list(zip(date_list,location_list,boatname_list,triptype_list,anglers_list,catch_list)), 
               columns =['date','location','boat_name','trip_type','num_anglers','catch'])
    
    
    driver.close()
    return fish_counts_df;


#function to write 'data' to csv
def csv_writer (dataframe, csv_name):
    """
    Writes dataframe to csv file.
    csv_name should not include ".csv"
    """
    
    try:
        dataframe.to_csv(csv_name + ".csv",index=False)
    except:
        print("Please enter both a dataframe and output name")