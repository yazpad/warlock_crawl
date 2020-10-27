from selenium import webdriver
import re
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os.path

import pickle
import time
from selenium.webdriver.chrome.options import Options

from webdriver_manager.chrome import ChromeDriverManager
from googleapiclient.discovery import build
# import googleapiclient.discovery
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

TIME_BETWEEN_LOAD = 3

force_reload = []

try:
    loaded_data = pickle.load( open( "save.p", "rb" ) )
except:
    print("Cached data could not be loaded")
    loaded_data = {}

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
html_start = "https://classic.warcraftlogs.com/zone/rankings/1005#metric=execution&boss=715&region=6&subregion=13&page=2"


SAMPLE_SPREADSHEET_ID = '1jTCV60O5IqptgtR34BFUA-snymcsFZ_-nAwQ5XrSVpw'
SAMPLE_RANGE_NAME = 'sheet1!A2:A1000'
SAMPLE_RANGE_NAME_BW = 'sheet1!J2:J1000'

html_list = []
html_list_bw = []

num = 0
bw_html_list = []
no_bw_html_list = []
data = {}
data['horde'] = {True: [], False:[]}
data['alliance'] = {True: [], False:[]}

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
driver = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)
driver2 = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)
driver3 = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)
driver4 = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)
char_gear_driver = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)


def findPages():
    last_page_num = 2
    for p in range(1,100):
        try:
            main_p = html_start.replace("page=2","page="+str(p))
            html1 = driver.page_source
            driver.get(main_p)
            time.sleep(TIME_BETWEEN_LOAD)
            html2 = driver.execute_script("return document.documentElement.innerHTML;")
            val = driver.find_elements_by_xpath('/html/body/div[2]/div[3]/div[2]/div[2]/div/div[3]/div[1]/table/tbody/tr')
            for v in val:
                try:
                    element_value = v.get_attribute('innerHTML')
                    element_value_split = element_value.split('"')
                    for e in element_value_split:
                        try:
                            if "reports" and "damage-done" in e:
                                fight_page = "https://classic.warcraftlogs.com/"+e+"&type=damage-done"

                                # GO TO FIGHT PAGE
                                driver2.get(fight_page)
                                time.sleep(TIME_BETWEEN_LOAD)
                                chars = driver2.find_elements_by_xpath('/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[2]/table/tbody/tr')
                                
                                for char in chars:
                                    try:
                                        char_val = char.get_attribute('innerHTML')
                                        if "Warlock" in char_val:
                                            result = re.search("('(.*)')", char_val)
                                            char_num = str(result.group(1)[1:-1])
                                            char_page = fight_page + "&source="+char_num + "&view=events"
                                            char_page = char_page.replace("damage-done","casts")

                                            char_gear_page = fight_page + "&source="+char_num
                                            char_gear_page = char_gear_page.replace("damage-done","summary")


                                            ####
                                            faction = ""
                                            r7 = False
                                            ####

                                            # GO TO WARLOCK CAST PAGE
                                            driver3.get(char_page)
                                            # GO TO WARLOCK GEAR PAGE
                                            char_gear_driver.get(char_gear_page)
                                            time.sleep(TIME_BETWEEN_LOAD)

                                            ##### GET r7
                                            try:
                                                gloves = char_gear_driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[3]/div[2]/div/table/tbody/tr[10]').get_attribute('innerHTML')
                                            except:
                                                continue
                                            faction_img = char_gear_driver.find_element_by_xpath('/html/body/ul/li[12]/a/span/span[1]').get_attribute('class')
                                            if "Dreadweave" in gloves:
                                                r7 = True
                                            if "faction-0" in faction_img:
                                                faction = "alliance"
                                            elif "faction-1" in faction_img:
                                                faction = "horde"
                                            else:
                                                print("ERROR FACTION", faction_img, gloves)

                                            ## BEGIN PARSING CASTS
                                            cast_rows = driver3.find_elements_by_xpath('/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody[1]/tr')
                                            start_cast = None
                                            for cast_row in cast_rows:
                                                cast_str = cast_row.get_attribute('innerHTML')
                                                try:
                                                    time_str = cast_str.split("main-table-number")[1]
                                                except:
                                                    print("failed to split", cast_str)
                                                    continue

                                                minutes = int(time_str[5:7])
                                                seconds = float(time_str[8:14])
                                                time_val = minutes*60+seconds
                                                if start_cast is not None:
                                                    if time_val - start_cast > 2.5:
                                                        start_cast = None

                                                if start_cast is None:
                                                    if "begins casting" in cast_str and "Searing Pain" in cast_str:
                                                        start_cast = time_val
                                                else:
                                                    if "casts" in cast_str and "Searing Pain" in cast_str:
                                                        data[faction][r7].append(time_val - start_cast)
                                                        start_cast = None
                                            calculate()
                                    except:
                                        continue
                        except:
                            continue
                except:
                    continue
        except:
            continue


def calculate():
    info = {}
    print("------------------------------------------------------")
    avgs = {"alliance":{True:0, False:0}, "horde":{True:0, False:0}}
    for faction in ["alliance", "horde"]:
        for r7 in [True, False]:
            if len(data[faction][r7]) > 0:
                avgs[faction][r7] = sum(data[faction][r7])/len(data[faction][r7])
                print("avgs: ", faction, r7, avgs[faction][r7], ", # Samples", len(data[faction][r7]))
    # print("List of non-burning wish parses: ", no_bw_html_list)
    # print("BW dmg", data["BW"])
    # print("non-BW dmg", data["NO_BW"])
    # print("Calculating -----------------------------")
    # print("BW AVG: ", bw_avg)
    # print("NOBW AVG: ", no_bw_avg)
    # print("RATIO: ",  bw_avg/no_bw_avg)
    # pickle.dump(bw_html_list,open("bw_html_list","wb"))
    # pickle.dump(no_bw_html_list,open("nobw_html_list","wb"))
    # pickle.dump(data["BW"],open("bw_dmg","wb"))
    # pickle.dump(data["NO_BW"],open("non bw_dmg","wb"))
    # pickle.dump(data["NO_BW"],open("non bw_dmg","wb"))


def gatherData(fight):
    dmg_list = []
    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    #chrome_options.add_argument("--window-size=1920x1080")
    driver4 = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)

    summary_html = fight

    driver4.get(summary_html)
    html1 = driver4.page_source
    time.sleep(1.0)
    html2 = driver4.execute_script("return document.documentElement.innerHTML;")
    val = driver4.find_elements_by_xpath('//*[@id="DataTables_Table_0"]/tbody[1]/tr')
    for v in val:
        element_value = v.get_attribute('innerHTML')
        if "Goblin Sapper Charge" in element_value and "(O: " not in element_value:
            try:
                dmg = element_value.split('rgb(92%, 27%, 38%)">')[1][:3]
                if "*" not in dmg:
                    dmg_list.append(float(dmg))
            except:
                print("ERROR", element_value.split('rgb(92%, 27%, 38%)">'))
    return dmg_list

findPages()
