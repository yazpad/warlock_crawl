from selenium.webdriver.common.by import By
import traceback
from enums import composition, characterClass
from util import printBossDB, printWrapper, determineComp, cleanExit, getTime, insertIntoDB, existsInDB
from scraper_functions import getDebuffData, getComposition, getPlayerBuffData, getPlayerCastData, getPlayerHitCrit
from ids import server_dict, boss_dict, debuff_list, buff_dict


from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException

from selenium.webdriver.support.ui import WebDriverWait

from selenium import webdriver
import random
import re
import os.path
import pickle
import time
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import sqlite3 as sl
import json

MAX_DELAY = 5

study_options = {
        "name": "default_name",
        "boss": "Gruul the Dragonkiller Normal",
        "sample distribution": "MRU",
        "number of results": float("inf"),
        "gather options": {
            "improved scorch indicator": True,
            "shadow vulnerability indicator": True,
            "fight time": True,
            "dps": True,
            }
        }

sl_db_definition = " \
    CREATE TABLE " + study_options['name'] + " ( \
        raid_html TEXT NOT NULL PRIMARY KEY, \
        composition STRING NOT NULL, \
        player_info TEXT, \
        fight_length INTEGER NOT NULL, \
        isb_ratio REAL NOT NULL, \
        boss_id INTEGER NOT NULL \
    ); "
    

con = sl.connect(study_options['name'] + '.db')

try:
    with con:
        con.execute(sl_db_definition)
except Exception as e:
    print(e)

cursor = con.cursor()
cursor = con.execute('select * from ' + study_options['name'])
output_columns = list(map(lambda x: x[0], cursor.description))
print("Output columns will be: ", output_columns)


PAGE_DELAY = 2

#boss_list = ["Maiden of Virtue Normal"]
#boss_list = ["Prince Malchezaar Normal"]
boss_list = ["Gruul the Dragonkiller Normal"]

TIME_BETWEEN_LOAD = 3

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
sweep_raid_driver = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)
fight_driver = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)

def getRaidComposition(raid_html, warlock_sources, specs, boss_id):
    debuff_data={}
    player_data={}
    success = False
    agg_stats = {"in_isb": 0, "total": 0}
    num_shadow_priests = 0
    num_shadow_warlocks = 0
    num_fire_warlocks = 0
    total_fight_data = {"composition": composition.UNKNOWN, "player_info": [], "fight_length": -1, "isb_ratio": -1, "raid_html": "Not set", "boss_id": boss_id, "has_fire_mage": 0, "has_shadow_priest": 0}


    def appendClassStats(agg_stats, stats):
        agg_stats['total'] += stats['total']
        agg_stats['in_isb'] += stats['in_isb']

    for k,v in warlock_sources.items():
        player_data[k] = {}

    fight_data = {}

    for fight_num in range(1,12):
        fight_driver.get(raid_html)
        try:
            fight_text = fight_driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[5]/div/div/div/div['+str(fight_num)+']/a/span[1]').text
        except:
            continue
        if fight_text in boss_list:
            ahref = fight_driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[5]/div/div/div/div['+str(fight_num)+']/a')
            ahref.click()
            fight_html = ahref.get_attribute("href")
            total_fight_data["raid_html"] = fight_html
            getDebuffData(fight_driver, fight_html,fight_text,debuff_data, fight_data, total_fight_data)
            for k,v in warlock_sources.items():
                print(k, specs[k], "PARSING")
                if specs[k] == "fire_mage":
                    total_fight_data['has_fire_mage'] = 1
                if specs[k] == "shadow":
                    total_fight_data['has_shadow_priest'] = 1
                player_data[k][fight_text]={}
                if specs[k] != "fire_mage":
                    getPlayerBuffData(fight_driver, fight_html, fight_text, k, v, player_data)
                    class_type, cast_stats = getPlayerCastData(fight_driver, fight_html, fight_text, k, v, player_data, debuff_data[boss_list[0]])
                    getPlayerHitCrit(fight_driver, fight_html, fight_text, k, v, player_data, debuff_data[boss_list[0]], total_fight_data, specs)
                    if class_type == characterClass.SHADOW_PRIEST or class_type == characterClass.SHADOW_WARLOCK:
                        appendClassStats(agg_stats, cast_stats)
                        if class_type == characterClass.SHADOW_PRIEST: 
                            num_shadow_priests += 1
                        if class_type == characterClass.SHADOW_WARLOCK: 
                            num_shadow_warlocks += 1
                print(k, specs[k], "FINISHED")
                print()
            print("Finished parsing log")
            success = True
            print("")
            break
    else:
        print("Boss not found in this log")



    comp = determineComp(num_shadow_priests, num_shadow_warlocks)
    print("Composition determined: ", comp)
    total_fight_data['composition'] = comp
    if agg_stats['total'] > 0:
        total_fight_data['isb_ratio'] = agg_stats['in_isb']/agg_stats['total']
    print("Fight info", total_fight_data)
    if success:
        print("ADDING")
        insertIntoDB(con, total_fight_data, study_options)
    return debuff_data
    


def sweepRaid(raid_html, boss_id):
    comp, spec = getComposition(fight_driver, raid_html)
    getRaidComposition(raid_html, comp, spec, boss_id)

def sweepRaids(raid_id, server_id, boss_id, num_pages = 10):
    try:
        html = "https://classic.warcraftlogs.com/zone/reports?zone="+str(raid_id)+"&boss="+str(boss_id)+"&difficulty=0&class=Any&spec=Any&keystone=0&kills=2&duration=0"
        page_num = random.randint(1,4)
        for i in range(num_pages):
            html = "https://classic.warcraftlogs.com/zone/reports?zone="+str(raid_id)+"&boss="+str(boss_id)+"&difficulty=0&class=Any&spec=Any&keystone=0&kills=2&duration=0&page="+str(i)+"&server="+str(server_id)
            print("Sweeping raid", html)
            sweep_raid_driver.get(html)
            sweep_raid_driver.execute_script("return document.documentElement.innerHTML;")
            time.sleep(TIME_BETWEEN_LOAD)
            for n in range(1,100):
                try:
                    ahref = sweep_raid_driver.find_element_by_xpath('/html/body/div[2]/div[3]/div/div[4]/div/div[1]/table/tbody/tr['+str(n)+']/td[1]/a')
                except:
                    print("Failed to find element by xpath. 1")
                    cleanExit(sweep_raid_driver, fight_driver)
                # raid_html = "https://classic.warcraftlogs.com/reports/h7knjxRfvMwcTzda"
                raid_html = ahref.get_attribute("href")
                if existsInDB(con, raid_html, study_options):
                    continue
                try:
                    sweepRaid(raid_html, boss_id)
                except:
                    time.sleep(10)
                    continue
                printBossDB(con, boss_id, study_options)
                time.sleep(5)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        print("Failed to sweep raid.")
        cleanExit(sweep_raid_driver, fight_driver)

sweepRaids(1008, server_dict["herod"], boss_dict["Gruul the Dragonkiller Normal"])

cleanExit(sweep_raid_driver, fight_driver)
