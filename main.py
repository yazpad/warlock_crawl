from selenium.webdriver.common.by import By
import traceback
from enums import composition, characterClass
from util import printBossDB, printWrapper, determineComp, cleanExit, getTime, insertIntoDB, existsInDB, generateStudySQLSchema, getRaidID, printDBSize
from scraper_functions import getDebuffData, getComposition, getPlayerBuffData, getPlayerCastData, getPlayerHitCrit
from ids import server_dict, boss_dict, debuff_list, buff_dict

from icecream import ic
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
from config import study_options, display_options

raid_id = getRaidID()
schema, record_key = generateStudySQLSchema()
con = sl.connect(study_options['name'] + '.db')
try:
    with con:
        con.execute(schema)
except Exception as e:
    ic(e)

cursor = con.cursor()
cursor = con.execute('select * from ' + study_options['name'])
output_columns = list(map(lambda x: x[0], cursor.description))
print("Output columns will be: ", output_columns)

PAGE_DELAY = 2
MAX_DELAY = 5
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
    total_fight_data = {"composition": composition.UNKNOWN, "player_info": [], "fight_length": -1, "isb_ratio": 0, "raid_html": "Not set", "boss_id": boss_id, "imp_scorch": 0, "shadow_vuln": 0} #Todo dynamically create this


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
        if fight_text == study_options['boss']:
            print(fight_text)
            ahref = fight_driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[5]/div/div/div/div['+str(fight_num)+']/a')
            ahref.click()
            fight_html = ahref.get_attribute("href")
            total_fight_data["raid_html"] = fight_html
            getDebuffData(fight_driver, fight_html,fight_text,debuff_data, fight_data, total_fight_data)
            for k,v in warlock_sources.items():
                if "mage" in specs[k]:
                    continue
                if "priest" in specs[k] and "priest" not in study_options['classes to record']:
                    continue
                if "warlock" in specs[k] and "warlock" not in study_options['classes to record']:
                    continue
                try:
                    if study_options['fight gather options']['improved scorch indicator']:
                        if debuff_data[fight_text].get("imp_scorch") is not None:
                            total_fight_data['imp_scorch'] = 1
                    if study_options['fight gather options']['shadow vulnerability indicator']:
                        if debuff_data[fight_text].get("shadow_vuln") is not None:
                            total_fight_data['shadow_vuln'] = 1

                    player_data[k][fight_text]={}
                    getPlayerBuffData(fight_driver, fight_html, fight_text, k, v, player_data)

                    # \Todo move reqs inside functions
                    if study_options['player gather options']['hit'] or study_options['player gather options']['dps'] or study_options['player gather options']['crit']:
                        getPlayerHitCrit(fight_driver, fight_html, fight_text, k, v, player_data, total_fight_data, specs)

                    if study_options['fight gather options']['isb uptime']:
                        class_type, cast_stats = getPlayerCastData(fight_driver, fight_html, fight_text, k, v, player_data, debuff_data[fight_text])
                        if class_type == characterClass.SHADOW_PRIEST or class_type == characterClass.SHADOW_WARLOCK:
                            appendClassStats(agg_stats, cast_stats)
                            if class_type == characterClass.SHADOW_PRIEST: 
                                num_shadow_priests += 1
                            if class_type == characterClass.SHADOW_WARLOCK: 
                                num_shadow_warlocks += 1
                except Exception as e:
                    ic(e)
            print("Finished parsing log")
            success = True
            break
    else:
        print("Boss not found in this log", fight_text, study_options['boss'],raid_html)



    try:
        # Todo, change this to ISB comp
        if study_options['fight gather options']["isb composition"]:
            comp = determineComp(num_shadow_priests, num_shadow_warlocks)
            print("Composition determined: ", comp)
            total_fight_data['composition'] = comp

        if study_options['fight gather options']['isb uptime']:
            if agg_stats['total'] > 0:
                total_fight_data['isb_ratio'] = agg_stats['in_isb']/agg_stats['total']

        if success: #Todo add check function against config
            if display_options['debug']:
                print("Data to be added...", total_fight_data)
            insertIntoDB(con, total_fight_data, study_options, record_key)
        elif display_options['debug']:
            print("Failure to parse...", total_fight_data)
    except Exception as e:
        ic(e)
    return debuff_data
    

def sweepRaid(raid_html, boss_id):
    comp, spec = getComposition(fight_driver, raid_html)
    getRaidComposition(raid_html, comp, spec, boss_id)

def sweepRaids(raid_id, server_id, boss_id, num_pages = 100):
    try:
        html = "https://classic.warcraftlogs.com/zone/reports?zone="+str(raid_id)+"&boss="+str(boss_dict[boss_id])+"&difficulty=0&class=Any&spec=Any&keystone=0&kills=2&duration=0"
        for i in range(num_pages):
            html = "https://classic.warcraftlogs.com/zone/reports?zone="+str(raid_id)+"&boss="+str(boss_dict[boss_id])+"&difficulty=0&class=Any&spec=Any&keystone=0&kills=2&duration=0&page="+str(i)+"&server="+str(server_id)
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
                raid_html = ahref.get_attribute("href")
                if existsInDB(con, raid_html, study_options):
                    continue
                try:
                    sweepRaid(raid_html, boss_id)
                except:
                    time.sleep(10)
                    continue
                printDBSize(con)
                printBossDB(con, boss_id)
                time.sleep(5)
    except Exception as e:
        ic(e)
        print(traceback.format_exc())
        print("Failed to sweep raid.")
        cleanExit(sweep_raid_driver, fight_driver)

sweepRaids(raid_id, study_options['server'], study_options['boss']) #\Todo enabel multiple search.  Normal search doesn't work very well anyways

cleanExit(sweep_raid_driver, fight_driver)
