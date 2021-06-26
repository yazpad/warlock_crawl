from list_dict_DB import list_dict_DB
from selenium.webdriver.common.by import By
import traceback
from enums import composition, characterClass


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

con = sl.connect('isb.db')
try:
    with con:
        con.execute("""
            CREATE TABLE USER (
                raid_html TEXT NOT NULL PRIMARY KEY,
                composition STRING NOT NULL,
                warlock_info TEXT,
                shadow_priest_info TEXT,
                fight_length INTEGER NOT NULL,
                isb_ratio REAL NOT NULL,
                boss_id INTEGER NOT NULL
            );
        """)
except:
    "db already detected"


def waitForElement(driver_name, full_xpath):
    try:
        WebDriverWait(driver_name, MAX_DELAY).until(EC.presence_of_element_located((By.XPATH, full_xpath)))
    except TimeoutException:
        print("Loading took too much time", full_xpath)
        return

def printBossDB(boss_id):
    print("Printing db for boss", boss_id)
    with con:
        cursor = con.cursor()
        cursor.execute("SELECT COUNT(*) FROM USER WHERE boss_id == ?", (boss_id,))
        num = cursor.fetchone()
        print("There are ", num, "entries")
        data = con.execute("SELECT * FROM USER WHERE boss_id == ?", (boss_id,))
        for row in data:
            print(row)

def insertIntoDB(fight_info):
    sql = 'INSERT INTO USER (raid_html, composition, warlock_info, shadow_priest_info, fight_length, isb_ratio, boss_id) values(?, ?, ?, ?, ?, ?, ?)'
    data = [(fight_info['raid_html'], str(fight_info['composition']), json.dumps(fight_info['warlock_info']), json.dumps(fight_info['shadow_priest_info']), fight_info['fight_length'], fight_info['isb_ratio'], fight_info['boss_id'])]
    with con:
        try:
            con.executemany(sql, data)
        except:
            print("Attempted to add a fight which exists in DB")
            pass

def existsInDB(raid_html):
    with con:
        curser = con.cursor()
        exists = curser.execute("SELECT rowid FROM USER WHERE raid_html == ?", (raid_html,))
        exists = curser.fetchone()
        if exists:
            print(raid_html, "Already exists in db.")
            return True
        return False
    return False

fight_info = {"raid_html": "sample2", "composition": composition.W3_1SP, "warlock_info": {"as": 3}, "shadow_priest_info": {}, "fight_length": 110, "isb_ratio": .25, "boss_id": 111}
insertIntoDB(fight_info);

# data = [("sample_html22", str(composition.W1_1SP), json.dumps([{"a": str(composition.W2_1SP)}]), json.dumps([]), 11, .25, 10101)]

with con:
    data = con.execute("SELECT * FROM USER WHERE boss_id == 111")
    curser = con.cursor()
    exists = curser.execute("SELECT rowid FROM USER WHERE boss_id == ?", (10101,))
    exists = curser.fetchone()
    print("here",exists)
    for row in data:
        print(row)

PAGE_DELAY = 2

#boss_list = ["Maiden of Virtue Normal"]
#boss_list = ["Prince Malchezaar Normal"]
boss_list = ["Gruul the Dragonkiller Normal"]

debuff_list = ["ability-15258-0", "ability-17800-0", "ability-17937-0", "ability-11722-0"]
buff_dict = {"ability-18791-0":"Touch of Shadow", "ability-23271-0": "Ephemeral Power", "ability-17941-0": "Shadow Trance", "ability-18288-0": "Amplify Curse"}
items = [{"name": "yazpad", "fight": "A", "date": 0, "class": "warlock", "server": "Fairbanks", "spec": "ds/ruin", "boss": "Fankriss"}]

DB = list_dict_DB(items)

print(DB.query())

TIME_BETWEEN_LOAD = 3

force_reload = []

try:
    loaded_data = pickle.load( open( "db.pickle", "rb" ) )
    print(loaded_data)
except:
    print("Cached data could not be loaded")
    loaded_data = list_dict_DB([])


chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
sweep_raid_driver = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)
fight_driver = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)
raid_driver = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)

def cleanExit():
    print("Exiting cleanly...")
    sweep_raid_driver.quit()
    fight_driver.quit()
    raid_driver.quit()
    exit()


def getTime(element):
    minutes = int(element[3:5])
    seconds = float(element[6:])
    time_val = minutes*60+seconds
    return time_val

def getComposition(raid_html):
    time.sleep(PAGE_DELAY)
    fight_driver.get(raid_html+"#boss=-2&difficulty=0&type=damage-done")
    fight_driver.execute_script("return document.documentElement.innerHTML;")
    warlock_dict = {}
    spec = {}
    num_found = 0

    try:
        WebDriverWait(fight_driver, MAX_DELAY).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody/tr[2]/td[2]/table/tbody/tr/td[1]")))
    except TimeoutException:
        print("Loading characters took too much time", raid_html+"#boss=-2&difficulty=0&type=damage-done")
        return warlock_dict

    for i in range(1,41):
        try:
            character_img = fight_driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody/tr['+str(i)+']/td[2]/table/tbody/tr/td[1]')
            character_meta = fight_driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody/tr['+str(i)+']/td[2]/table/tbody/tr/td[2]')
            num_found += 1
        except:
            break

        element_value = character_meta.get_attribute('innerHTML')
        element_value_img = character_img.get_attribute('innerHTML')
        if "Warlock" in element_value or "Priest-Shadow" in element_value_img:
            split_for_source = element_value.split("setFilterSource('")[1].split("'")[0]
            split_for_name = element_value.split('">')[1].splitlines()[0]
            warlock_dict[split_for_name] = split_for_source
            if "Priest-Shadow" in element_value_img:
                spec[split_for_name] = "shadow"
                print("Shadow priest found")
            elif "Warlock-Destruction" in element_value_img:
                spec[split_for_name] = "destruction"
                print("Destruction warlock found")
            elif "Warlock-Affliction" in element_value_img:
                spec[split_for_name] = "affliction"
                print("Affliction warlock found")
            elif "Warlock-Demonology" in element_value_img:
                spec[split_for_name] = "demonology"
                print("Demonology warlock found")
            else:
                spec[split_for_name] = "unknown"
                print("Unknown spec: ", element_value_img)


    print(warlock_dict)
    if num_found == 0:
        print("Failed to find any players.., Trying again")
        return getComposition(raid_html)
    return warlock_dict, spec

def getDebuffData(fight_html, fight_text, debuff_data, fight_data, fight_info_dict):
    time.sleep(PAGE_DELAY)
    debuff_data[fight_text]={}
    debuff_data[fight_text]["debuff_set"]=set()
    debuff_html = fight_html + "&type=auras&spells=debuffs&hostility=1"
    fight_driver.get(debuff_html)
    isb_found = False
    print(debuff_html)

    fight_time = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[3]/div/div[1]/div[1]/div/div[2]/span/span[1]").text[1:-1]
    fight_time = int(fight_time[:-3])*60+ int(fight_time[-2:])
    fight_data["fight_time"] = fight_time
    fight_info_dict["fight_length"] = fight_time
    print(fight_data["fight_time"])

    try:
        WebDriverWait(fight_driver, MAX_DELAY).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div/div[1]/table/tbody/tr[1]/td[1]/a[2]")))
    except TimeoutException:
        print("Loading took too much time")
        return
    k = 0
    while True:
        k += 1
        try:
            debuff_meta = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div/div[1]/table/tbody/tr["+str(k)+"]/td[1]/a[2]")

        except:
            break

        element_value = debuff_meta.get_attribute('id')
        if element_value == "ability-17800-0":
            print("ISB FOUND")
            isb_found = True

        if element_value in debuff_list:
            debuff_data[fight_text][element_value] = []
            bar_num = 0
            while True:
                bar_num += 1
                try:
                    bar_value = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div/div[1]/table/tbody/tr["+str(k)+"]/td[3]/div[2]/div["+str(bar_num)+"]").get_attribute("style")
                    left = bar_value.split("left:")[1].split("%;")[0]
                    width = bar_value.split("width:")[1].split("%;")[0]
                    debuff_data[fight_text][element_value].append((float(left)/100.0*fight_time, (float(left)+float(width))/100.0*fight_time))
                except:
                    break
    return isb_found

def getPlayerBuffData(fight_html, fight_text, warlock_name, warlock_source, player_data):
    time.sleep(PAGE_DELAY)
    player_data[warlock_name][fight_text]["buffs"] = {}
    player_buff_html = fight_html + "&type=auras&source="+str(warlock_source)
    print(player_buff_html)
    fight_driver.get(player_buff_html)
    try:
        WebDriverWait(fight_driver, MAX_DELAY).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div/div[1]/div[1]")))
    except TimeoutException:
        print("Loading took too much time")
        return
    for g in range(1,5):
        try:
            buff_meta_name = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div/div["+str(g)+"]/div[1]")
        except:
            break
        if buff_meta_name.text == "Damage Buffs":
            print("FOUND DMG BUFFS")
            k = 0
            while True:
                k += 1
                try:
                    buff_row_xpath = "/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div/div["+str(g)+"]/div[2]/div[1]/table/tbody/tr["+str(k)+"]/td[1]/a[2]"
                    buff_meta = fight_driver.find_element_by_xpath(buff_row_xpath)
                except:
                    break

                element_value = buff_meta.get_attribute('id')
                print(element_value)
                if element_value in list(buff_dict.keys()):
                    print(element_value, buff_dict[element_value])
                    player_data[warlock_name][fight_text]["buffs"][element_value] = []
                    bar_num = 0
                    while True:
                        bar_num += 1

                        try:
                            bar_value = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div/div["+str(g)+"]/div[2]/div[1]/table/tbody/tr["+str(k)+"]/td[3]/div[2]/div["+str(bar_num)+"]").get_attribute("style")
                            left = bar_value.split("left:")[1].split("%;")[0]
                            width = bar_value.split("width:")[1].split("%;")[0]
                            player_data[warlock_name][fight_text]["buffs"][element_value].append((float(left)/100.0*fight_time, (float(left)+float(width))/100.0*fight_time))
                        except:
                            break
            break

def getPlayerCastData(fight_html, fight_text, warlock_name, warlock_source, player_data, debuff_data):
    def duringISB(cast_time):
        for bounds in debuff_data["ability-17800-0"]:
            if cast_time > float(bounds[0]) and cast_time < float(bounds[1]):
                return True
        return False

    casted_shadowbolt = False
    casted_incinerate = False
    casted_mindblast = False
    stats = {"in_isb": 0, "total": 0}

    def castTime(raw_cast_time):
        return int(cast_time[-8:-6])*60+ float(cast_time[-5:])

    player_cast_html = fight_html + "&type=casts&source="+str(warlock_source)+"&view=events"
    print("Starting to gather player cast data: ", warlock_name, player_cast_html)
    try:
        time.sleep(PAGE_DELAY)
        fight_driver.get(player_cast_html)
    except:
        print("failed init block in player cast")
    try:
        WebDriverWait(fight_driver, MAX_DELAY).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody[1]/tr[1]/td[1]")))
    except:
        print("Could not get player cast data")
        print(e)
        print(traceback.format_exc())
        return
    print("Searching for casts...")
    for g in range(1,1000):
        try:
            cast_element = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody[1]/tr["+str(g)+"]/td[2]").get_attribute('innerHTML')
            if "casts" in cast_element and "Shadow Bolt" in cast_element:
                cast_time = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody[1]/tr["+str(g)+"]/td[1]").text[1:-1]
                cast_time = castTime(cast_time)
                casted_shadowbolt = True
                if duringISB(cast_time):
                    stats["in_isb"]+=1
                stats["total"]+=1

            if "casts" in cast_element and "Incinerate" in cast_element:
                cast_time = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody[1]/tr["+str(g)+"]/td[1]").text[1:-1]
                cast_time = castTime(cast_time)
                casted_incinerate = True

                if duringISB(cast_time):
                    stats["in_isb"]+=1
                stats["total"]+=1

            if "casts" in cast_element and "Mind Blast" in cast_element:
                cast_time = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody[1]/tr["+str(g)+"]/td[1]").text[1:-1]
                cast_time = castTime(cast_time)
                casted_mindblast = True

                if duringISB(cast_time):
                    stats["in_isb"]+=1
                stats["total"]+=1
        except Exception as e:
            print("Broken exception")
            print(e)
            print(traceback.format_exc())
            break;


    if stats["total"] > 0:
        print("ISB ratio: ", stats["in_isb"]/stats["total"])
    if casted_shadowbolt:
        print("Completed for shadow warlock", warlock_name)
        return characterClass.SHADOW_WARLOCK, stats
    elif casted_incinerate:
        print("Completed for fire warlock", warlock_name)
        return characterClass.FIRE_WARLOCK, stats
    elif casted_mindblast:
        print("Completed for shadowpriest", warlock_name)
        return characterClass.SHADOW_PRIEST, stats
    else:
        print("Completed for unknown class", warlock_name)
    return characterClass.UNKNOWN, stats

def getPlayerHitCrit(fight_html, fight_text, warlock_name, warlock_source, player_data, debuff_data, total_fight_data, specs):

    casted_shadowbolt = False
    casted_incinerate = False
    casted_mindblast = False
    stats = {"in_isb": 0, "total": 0}

    print("Starting to gather player crit/hit data: ", warlock_name)
    time.sleep(PAGE_DELAY)
    player_cast_html = fight_html + "&type=damage-done&source="+str(warlock_source)
    fight_driver.get(player_cast_html)
    try:
        WebDriverWait(fight_driver, MAX_DELAY).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody/tr[1]/td[1]/table/tbody/tr/td[2]/a/span")))
    except TimeoutException:
        print("Loading took too much time")
        return

    crit_index = None
    hit_index = None
    for h in range(1,10):
        try:
            if "Crit" in fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/thead/tr/th["+str(h)+"]/div").text:
                crit_index = h
            if "Miss" in fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/thead/tr/th["+str(h)+"]/div").text:
                hit_index = h
            if hit_index is not None and crit_index is not None:
                break
        except Exception as e:
            print(e)
            print(player_cast_html)
            print(traceback.format_exc())
    for g in range(1,100):
        try:
            cast_element = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody/tr["+str(g)+"]/td[1]/table/tbody/tr/td[2]").text
            if "Shadow Bolt" in cast_element:
                if crit_index is not None:
                    crit = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody/tr["+str(g)+"]/td["+str(crit_index)+"]").text
                else:
                    crit = "0%"
                if hit_index is not None:
                    hit = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody/tr[" + str(g) + "]/td["+str(hit_index)+"]").text
                else:
                    hit = "0%"
                if "-" in hit:
                    hit = "0%"
                if "-" in crit:
                    crit = "0%"
                total_fight_data["warlock_info"].append({"name": warlock_name, "hit": 1.0 - float(hit[:-1])/100., "crit": float(crit[:-1])/100., "spec": specs[warlock_name]})
                print("sb", warlock_name, hit, crit)
                return
            if "Mind Blast" in cast_element:
                if hit_index is not None:
                    hit = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody/tr[" + str(g) + "]/td["+str(hit_index)+"]").text
                else:
                    hit = "0%"
                if "-" in hit:
                    hit = "0%"
                total_fight_data["shadow_priest_info"].append({"name": warlock_name, "hit": 1.0 - float(hit[:-1])/100., "spec": specs[warlock_name]})
                print(warlock_name, hit)
                return 
            if "Incinerate" in cast_element:
                casted_incinerate = True

        except Exception as e:
            if casted_incinerate:
                print("Warlock", warlock_name, "was a firelock")
                return
            print(e)
            print(player_cast_html)
            print(traceback.format_exc())
            return


def getRaidComposition(raid_html, warlock_sources, specs, boss_id):
    debuff_data={}
    player_data={}
    agg_stats = {"in_isb": 0, "total": 0}
    num_shadow_priests = 0
    num_shadow_warlocks = 0
    total_fight_data = {"composition": composition.UNKNOWN, "warlock_info": [], "shadow_priest_info": [], "fight_length": -1, "isb_ratio": -1, "raid_html": "Not set", "boss_id": boss_id}

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
            print(fight_text)
        except:
            continue
        if fight_text in boss_list:
            ahref = fight_driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[5]/div/div/div/div['+str(fight_num)+']/a')
            ahref.click()
            fight_html = ahref.get_attribute("href")
            total_fight_data["raid_html"] = fight_html
            getDebuffData(fight_html,fight_text,debuff_data, fight_data, total_fight_data)
            for k,v in warlock_sources.items():
                player_data[k][fight_text]={}
                getPlayerBuffData(fight_html, fight_text, k, v, player_data)
                class_type, cast_stats = getPlayerCastData(fight_html, fight_text, k, v, player_data, debuff_data[boss_list[0]])
                getPlayerHitCrit(fight_html, fight_text, k, v, player_data, debuff_data[boss_list[0]], total_fight_data, specs)
                if class_type == characterClass.SHADOW_PRIEST or class_type == characterClass.SHADOW_WARLOCK:
                    appendClassStats(agg_stats, cast_stats)
                    if class_type == characterClass.SHADOW_PRIEST: 
                        num_shadow_priests += 1
                    if class_type == characterClass.SHADOW_WARLOCK: 
                        num_shadow_warlocks += 1


    comp = determineComp(num_shadow_priests, num_shadow_warlocks)
    print("Composition determined: ", comp)
    total_fight_data['composition'] = comp
    #total_fight_data['fight_length'] = comp
    #total_fight_data['warlock_info'] = HIT and CRIT
    #total_fight_data['shadow_priest_info'] = HIT and CRIT
    if agg_stats['total'] > 0:
        total_fight_data['isb_ratio'] = agg_stats['in_isb']/agg_stats['total']
    print("Fight info", total_fight_data)
    if total_fight_data["composition"] is not composition.UNKNOWN:
        insertIntoDB(total_fight_data)
    return debuff_data
    


def sweepRaid(raid_html, boss_id):
    comp, spec = getComposition(raid_html)
    getRaidComposition(raid_html, comp, spec, boss_id)

def sweepRaids(raid_id, server_id, boss_id, num_pages = 10):
    try:
        html = "https://classic.warcraftlogs.com/zone/reports?zone="+str(raid_id)+"&boss="+str(boss_id)+"&difficulty=0&class=Any&spec=Any&keystone=0&kills=2&duration=0"
        page_num = random.randint(1,4)
        for i in range(num_pages):
            html = "https://classic.warcraftlogs.com/zone/reports?zone="+str(raid_id)+"&boss="+str(boss_id)+"&difficulty=0&class=Any&spec=Any&keystone=0&kills=2&duration=0&page="+str(random.randint(1,5))+"&server="+str(server_id)
            print("Sweeping raid", html)
            sweep_raid_driver.get(html)
            sweep_raid_driver.execute_script("return document.documentElement.innerHTML;")
            time.sleep(TIME_BETWEEN_LOAD)
            for n in range(1,100):
                try:
                    ahref = sweep_raid_driver.find_element_by_xpath('/html/body/div[2]/div[3]/div/div[4]/div/div[1]/table/tbody/tr['+str(n)+']/td[1]/a')
                except:
                    print("Failed to find element by xpath. 1")
                    cleanExit()
                # raid_html = "https://classic.warcraftlogs.com/reports/h7knjxRfvMwcTzda"
                raid_html = ahref.get_attribute("href")
                if existsInDB(raid_html):
                    continue
                try:
                    sweepRaid(raid_html, boss_id)
                except:
                    time.sleep(10)
                    continue
                printBossDB(boss_id)
                time.sleep(5)
    except Exception as e:
        print(e)
        print(traceback.format_exc())
        print("Failed to sweep raid.")
        cleanExit()

                # element_value_split = element_value.split('"')
                # for e in element_value_split:
                #     try:
                #         if "/reports/" and "damage-done" in e:
                #             fight_page = "https://classic.warcraftlogs.com/"+e+"&type=damage-done"

        # next_fun(html)
    # html_start = "https://classic.warcraftlogs.com/zone/rankings/1005#metric=execution&boss=715&region=6&subregion=13&page=2"
server_dict = {"whitemane": 5012, "faerlina": 5003, "thunderfury": 5067}
boss_dict = {"Maiden of Virtue Normal": 654, "Prince Malchezaar Normal": 661, "Gruul the Dragonkiller Normal": 650}
sweepRaids(1008, server_dict["whitemane"], boss_dict["Gruul the Dragonkiller Normal"])

cleanExit()
