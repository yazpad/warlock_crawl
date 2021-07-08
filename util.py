from selenium.webdriver.common.by import By
import traceback
from enums import composition, characterClass
from colorama import Fore, Style
from ids import boss_raid_id, debuff_dict



from selenium.webdriver.support import expected_conditions as EC

from selenium.common.exceptions import TimeoutException

from selenium.webdriver.support.ui import WebDriverWait

from icecream import ic

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
from prettytable import PrettyTable


def waitForElement(driver_name, full_xpath):
    try:
        WebDriverWait(driver_name, MAX_DELAY).until(EC.presence_of_element_located((By.XPATH, full_xpath)))
    except TimeoutException:
        print("Loading took too much time", full_xpath)
        return

def printDBSize(con, boss_id=None):
    if display_options['show_db_size']:
        with con:
            cursor = con.cursor()
            if boss_id == None:
                cursor.execute("SELECT COUNT(*) FROM " + study_options['name'])
            else:
                cursor.execute("SELECT COUNT(*) FROM " + study_options['name'] + " WHERE boss_id == ?", (boss_id,))
            print("DB size: ", cursor.fetchone()[0])

def getDBHeaders(con):
    with con:
        cursor = con.cursor()
        cursor = con.execute('select * from ' + study_options['name'])
        return list(map(lambda x: x[0], cursor.description))

def printBossDB(con, boss_id):
    if display_options['show_db']:
        print("Printing db for boss", boss_id)
        with con:
            data = con.execute("SELECT * FROM " + study_options['name'] + " WHERE boss_id == ?", (boss_id,))
            #t = PrettyTable(getDBHeaders(con))
            for row in data:
                print(row)
                #ic(row)
                #t.add_row(row)
            #print(t)

def printWrapper(function):
    def new_function(*args):
        if display_options['debug']: 
            print("\n" + Fore.GREEN + "Started: ", function.__name__ + Style.RESET_ALL)
        try:
            output = function(*args)
        except Exception as e:
            ic(e)
        if display_options['debug']: 
            print(Fore.GREEN + "Finished: ", function.__name__ + "\n" + Style.RESET_ALL)
        return output
    return new_function


def determineComp(num_shadow_priests, num_shadow_warlocks):
    if num_shadow_warlocks == 1:
        if num_shadow_priests == 0:
            return composition.W1_0SP
        if num_shadow_priests == 1:
            return composition.W1_1SP
        if num_shadow_priests == 2:
            return composition.W1_2SP
        if num_shadow_priests == 3:
            return composition.W1_3SP
    if num_shadow_warlocks == 2:
        if num_shadow_priests == 0:
            return composition.W2_0SP
        if num_shadow_priests == 1:
            return composition.W2_1SP
        if num_shadow_priests == 2:
            return composition.W2_2SP
        if num_shadow_priests == 3:
            return composition.W2_3SP
    if num_shadow_warlocks == 3:
        if num_shadow_priests == 0:
            return composition.W3_0SP
        if num_shadow_priests == 1:
            return composition.W3_1SP
        if num_shadow_priests == 2:
            return composition.W3_2SP
        if num_shadow_priests == 3:
            return composition.W3_3SP
    if num_shadow_warlocks == 4:
        if num_shadow_priests == 0:
            return composition.W4_0SP
        if num_shadow_priests == 1:
            return composition.W4_1SP
        if num_shadow_priests == 2:
            return composition.W4_2SP
        if num_shadow_priests == 3:
            return composition.W4_3SP
    if num_shadow_warlocks == 5:
        if num_shadow_priests == 0:
            return composition.W5_0SP
        if num_shadow_priests == 1:
            return composition.W5_1SP
        if num_shadow_priests == 2:
            return composition.W5_2SP
        if num_shadow_priests == 3:
            return composition.W5_3SP
    return composition.UNKNOWN

def cleanExit(sweep_raid_driver, fight_driver):
    print("Exiting cleanly...")
    sweep_raid_driver.quit()
    fight_driver.quit()
    exit()

def getTime(element):
    minutes = int(element[3:5])
    seconds = float(element[6:])
    time_val = minutes*60+seconds
    return time_val

def insertIntoDB(con, fight_info, study_options, record_key):
    try:
        sql = 'INSERT INTO ' + study_options['name'] + ' ('
        for i in range(len(record_key)):
            sql += record_key[i]
            if i < len(record_key) - 1:
                sql += ', '
        sql += ') values('

        for i in range(len(record_key)):
            sql += '?'
            if i < len(record_key) - 1:
                sql += ', '

        sql += ')'
    except Exception as e: 
        ic(e)

    try:
        data = []
        for item in record_key:
            if item == 'composition':
                data.append(str(fight_info[item]))
            elif item == 'player_info':
                data.append(json.dumps((fight_info[item])))
            else:
                data.append(fight_info[item])
        data = [tuple(data)]
    except Exception as e:
        ic(e)

    with con:
        try:
            con.executemany(sql, data)
        except Exception as e:
            ic(e)

def existsInDB(con, raid_html, study_options):
    with con:
        curser = con.cursor()
        exists = curser.execute("SELECT rowid FROM " + study_options['name'] + " WHERE raid_html == ?", (raid_html,))
        exists = curser.fetchone()
        if exists:
            print(raid_html, "Already exists in db.")
            return True
        return False
    return False

def generateStudySQLSchema():
    schema = " \
        CREATE TABLE " + study_options['name'] + " ( \
            raid_html TEXT NOT NULL PRIMARY KEY,"
    record_list = ["raid_html"]

    if study_options['fight gather options']['isb composition']:
        schema += "composition STRING NOT NULL,"
        record_list.append("composition")
    if study_options['fight gather options']['fight time']:
        schema += "fight_length INTEGER NOT NULL,"
        record_list.append("fight_length")
    if study_options['fight gather options']['isb uptime']:
        schema += "isb_ratio REAL NOT NULL,"
        record_list.append("isb_ratio")
    if study_options['fight gather options']['improved scorch indicator']:
        schema += "imp_scorch INTEGER NOT NULL,"
        record_list.append("imp_scorch")
    if study_options['fight gather options']['shadow vulnerability indicator']:
        schema += "shadow_vuln INTEGER NOT NULL,"
        record_list.append("shadow_vuln")
    if study_options['fight gather options']['record server']:
        schema += "server REAL NOT NULL,"
        record_list.append("server")

    schema += "boss_id INTEGER NOT NULL,"
    record_list.append("boss_id")

    schema += "player_info TEXT);"
    record_list.append("player_info")

    return schema, record_list
    
def getRaidID():
    if boss_raid_id.get(study_options['boss']) is not None:
        return boss_raid_id[study_options['boss']]
    else:
        print("Raid ID not found from boss list...")
