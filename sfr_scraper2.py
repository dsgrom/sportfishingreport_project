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
    import time
    import pandas as pd
    from selenium import webdriver

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
    
    #wait until website loads
    time.sleep(10)

    #testing exiting function early if no catch reported that day (only time class = text_center will exist, I think)
    if driver.find_element_by_xpath(".//*[@class='text-center']").text == "We did not receive any party boat scores today. But here is our most recent score:":
        print(driver.find_element_by_xpath(".//*[@class='text-center']").text)
        return
    
    #initialize final dataframe
    df = pd.DataFrame(columns = ['date', 'location', 'boat_name', 'trip_type', 'num_anglers', 'catch', 'trip_num'])

    #create list of html calls to class = panels
    #each 'panel' on the page has a different area, i.e. one panel for Ventura Coast and one for San Diego and one for LA etc.
    #search all class = 'panel'
    panel_list = driver.find_elements_by_xpath("//*[@class='panel']")

    for panel_index in panel_list: #within each panel (region), there's multiple boats, so for each boat in each panel:
        temp_location_list = None
        boat_list = panel_index.find_elements_by_xpath(".//*[@class='row']") #find each boat
        temp_location_list = panel_index.find_element_by_xpath(".//*[contains(text(),'Fish Counts')]").text #location = region, i.e. OC or SD or LA
        for boat in boat_list: #for each boat, try to collect:

            #setting temp variables to None (empty)
            temp = [] #initialize temp dataframe
            location_val = None
            boatname_val = None
            landing_val = None #not currently used
            city_val = None #not currently used
            anglers_val = None
            catch_val = None
            triptype_val = None
            date_val = None
            tripnum_val = None

            try:
                #get values to input into dataframe
                boatname_val = boat.find_element_by_css_selector("b").text #boatname
                anglers_val = boat.find_element_by_xpath(
                        ".//*[@class='col-xs-3 col-xs-offset-1 col-md-2 col-md-offset-0 col-md-push-3']").text #anglers
                triptype_val = boat.find_element_by_xpath(
                        ".//*[@class='col-xs-3 col-md-2 col-md-push-3']").text #trip type
                catch_val = boat.find_element_by_xpath(
                        ".//*[@class='col-xs-11 col-xs-offset-1 col-md-3 col-md-offset-0 col-md-pull-5']").text #catch
                location_val = temp_location_list[:-12] #location
                date_val = date #date
                
                #if for current dataframe at this point in loop, there isn't a row that satisfies the conditions
                #date, location, boat name, trip type
                #then it's the first trip. if there is then it's the second trip
                if ((df['date'] == date_val) & 
                    (df['location'] == location_val) & 
                    (df['boat_name'] == boatname_val) & 
                    (df['trip_type'] == triptype_val)).any() == True:
                    
                    tripnum_val = 2
                
                else:
                    tripnum_val = 1

                #temp df with values for this row
                temp = pd.DataFrame([[date_val, location_val, boatname_val, triptype_val, anglers_val, catch_val, tripnum_val]],
                                    columns = ['date', 'location', 'boat_name', 'trip_type', 'num_anglers', 'catch', 'trip_num'])
                
                df = df.append(temp)
            except: #need to find breakpoint code instead of try except
                print("well that didn't work...")
        
    driver.close()
    return df;


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