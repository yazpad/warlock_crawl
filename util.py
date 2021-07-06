from selenium.webdriver.common.by import By
import traceback
from enums import composition, characterClass
from colorama import Fore, Style



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

def waitForElement(driver_name, full_xpath):
    try:
        WebDriverWait(driver_name, MAX_DELAY).until(EC.presence_of_element_located((By.XPATH, full_xpath)))
    except TimeoutException:
        print("Loading took too much time", full_xpath)
        return

def printBossDB(con, boss_id, study_options):
    print("Printing db for boss", boss_id)
    with con:
        cursor = con.cursor()
        cursor.execute("SELECT COUNT(*) FROM " + study_options['name'] + " WHERE boss_id == ?", (boss_id,))
        num = cursor.fetchone()
        print("There are ", num, "entries")
        data = con.execute("SELECT * FROM " + study_options['name'] + " WHERE boss_id == ?", (boss_id,))
        for row in data:
            print(row)

def printWrapper(function):
    def new_function(*args):
        print("\n" + Fore.GREEN + "Started: ", function.__name__ + Style.RESET_ALL)
        try:
            output = function(*args)
        except Exception as e:
            ic(e)
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

def insertIntoDB(con, fight_info, study_options):
    try:
        sql = 'INSERT INTO ' + study_options['name'] + ' (raid_html, composition, player_info, fight_length, isb_ratio, boss_id) values(?, ?, ?, ?, ?, ?)'
        data = [(fight_info['raid_html'], str(fight_info['composition']), json.dumps(fight_info['player_info']), fight_info['fight_length'], fight_info['isb_ratio'], fight_info['boss_id'])]
        with con:
            try:
                con.executemany(sql, data)
            except:
                print("Attempted to add a fight which exists in DB")
                pass
    except Exception as e:
        ic(e)

    # print("Adding data to fire_vs_shadow...")
    # sql = 'INSERT INTO FIRE_vs_SHADOW (raid_html, composition, warlock_info, fire_destruction_info, shadow_priest_info, fight_length, isb_ratio, boss_id, has_fire_mage, has_shadow_priest) values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'
    # data = [(fight_info['raid_html'], str(fight_info['composition']), json.dumps(fight_info['warlock_info']),json.dumps(fight_info['fire_destruction_info']), json.dumps(fight_info['shadow_priest_info']), fight_info['fight_length'], fight_info['isb_ratio'], fight_info['boss_id'], fight_info['has_fire_mage'], fight_info['has_shadow_priest'])]
    # with con:
    #     try:
    #         con.executemany(sql, data)
    #     except:
    #         print("Attempted to add a fight which exists in DB")
    #         pass

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
