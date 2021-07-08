from selenium.webdriver.common.by import By
import traceback
from enums import composition, characterClass
from ids import server_dict, boss_dict, buff_dict, debuff_dict


from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


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
from icecream import ic
ic.configureOutput(includeContext=True)
from util import printWrapper
from config import study_options, display_options

MAX_DELAY = 5
PAGE_DELAY = 2

@printWrapper
def getComposition(fight_driver, raid_html):
    time.sleep(PAGE_DELAY)
    fight_driver.get(raid_html+"#boss=-2&difficulty=0&type=damage-done")
    fight_driver.execute_script("return document.documentElement.innerHTML;")
    player_dict = {}
    spec = {}
    num_found = 0

    try:
        WebDriverWait(fight_driver, MAX_DELAY).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody/tr[2]/td[2]/table/tbody/tr/td[1]")))
    except TimeoutException:
        print("Loading characters took too much time", raid_html+"#boss=-2&difficulty=0&type=damage-done")
        return player_dict, None

    for i in range(1,41):
        try:
            character_img = fight_driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody/tr['+str(i)+']/td[2]/table/tbody/tr/td[1]')
            character_meta = fight_driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody/tr['+str(i)+']/td[2]/table/tbody/tr/td[2]')
            num_found += 1
        except:
            break

        element_value = character_meta.get_attribute('innerHTML')
        element_value_img = character_img.get_attribute('innerHTML')
        if "Warlock" in element_value or "Priest-Shadow" in element_value_img or "Mage-Fire" in element_value_img:
            split_for_source = element_value.split("setFilterSource('")[1].split("'")[0]
            split_for_name = element_value.split('">')[1].splitlines()[0]
            player_dict[split_for_name] = split_for_source
            if "Priest-Shadow" in element_value_img:
                spec[split_for_name] = "shadow"
            elif "Warlock-Destruction" in element_value_img:
                spec[split_for_name] = "destruction"
            elif "Warlock-Affliction" in element_value_img:
                spec[split_for_name] = "affliction"
            elif "Warlock-Demonology" in element_value_img:
                spec[split_for_name] = "demonology"
            elif "Mage-Fire" in element_value_img:
                spec[split_for_name] = "fire_mage"
            else:
                spec[split_for_name] = "unknown"


    if display_options['debug']:
        ic(player_dict, spec)
    if num_found == 0:
        print("Failed to find any players")
        return getComposition(raid_html), None
    return player_dict, spec

@printWrapper
def getDebuffData(fight_driver, fight_html, fight_text, debuff_data, fight_data, fight_info_dict):
    time.sleep(2)
    debuff_data[fight_text]={}
    debuff_data[fight_text]["debuff_set"]=set()
    debuff_html = fight_html + "&type=auras&spells=debuffs&hostility=1"
    fight_driver.get(debuff_html)
    if display_options['debug']:
        ic(debuff_html)

    fight_time = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[3]/div/div[1]/div[1]/div/div[2]/span/span[1]").text[1:-1]
    fight_time = int(fight_time[:-3])*60+ int(fight_time[-2:])
    fight_data["fight_time"] = fight_time
    fight_info_dict["fight_length"] = fight_time

    try:
        WebDriverWait(fight_driver, 5).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div/div[1]/table/tbody/tr[1]/td[1]/a[2]")))
    except TimeoutException:
        ic("Loading took too much time")
        return
    k = 0
    while True:
        k += 1
        try:
            debuff_meta = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div/div[1]/table/tbody/tr["+str(k)+"]/td[1]/a[2]")

        except Exception as e:
            if type(e) != NoSuchElementException:
                ic(e)
            break

        element_value = debuff_meta.get_attribute('id')
        if element_value in debuff_dict.keys():
            debuff_data[fight_text][debuff_dict[element_value]] = []
            bar_num = 0
            while True:
                bar_num += 1
                try:
                    bar_value = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div/div[1]/table/tbody/tr["+str(k)+"]/td[3]/div[2]/div["+str(bar_num)+"]").get_attribute("style")
                    left = bar_value.split("left:")[1].split("%;")[0]
                    width = bar_value.split("width:")[1].split("%;")[0]
                    debuff_data[fight_text][debuff_dict[element_value]].append((float(left)/100.0*fight_time, (float(left)+float(width))/100.0*fight_time))
                except Exception as e:
                    if type(e) != NoSuchElementException:
                        ic(e)
                    break
    return 


@printWrapper
def getPlayerBuffData(fight_driver, fight_html, fight_text, warlock_name, warlock_source, player_data):
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
    for g in range(1,10):
        try:
            buff_meta_name = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div/div["+str(g)+"]/div[1]")
        except:
            break
        if buff_meta_name.text == "Damage Buffs":
            k = 0
            while True:
                k += 1
                try:
                    buff_row_xpath = "/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div/div["+str(g)+"]/div[2]/div[1]/table/tbody/tr["+str(k)+"]/td[1]/a[2]"
                    buff_meta = fight_driver.find_element_by_xpath(buff_row_xpath)
                except:
                    break

                element_value = buff_meta.get_attribute('id')
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


@printWrapper
def getPlayerCastData(fight_driver, fight_html, fight_text, warlock_name, warlock_source, player_data, debuff_data):
    def duringISB(cast_time):
        for bounds in debuff_data["isb"]:
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
            print("Broken exception", g)
            break;


    if stats["total"] > 0:
        if display_options['debug']:
            print("ISB ratio: ", stats["in_isb"]/stats["total"])
    if casted_shadowbolt:
        if display_options['debug']:
            print("Completed for shadow warlock", warlock_name)
        return characterClass.SHADOW_WARLOCK, stats
    elif casted_incinerate:
        if display_options['debug']:
            print("Completed for fire warlock", warlock_name)
        return characterClass.FIRE_WARLOCK, stats
    elif casted_mindblast:
        if display_options['debug']:
            print("Completed for shadowpriest", warlock_name)
        return characterClass.SHADOW_PRIEST, stats
    else:
        if display_options['debug']:
            print("Completed for unknown class", warlock_name)
    return characterClass.UNKNOWN, stats

@printWrapper
def getPlayerHitCrit(fight_driver, fight_html, fight_text, warlock_name, warlock_source, player_data, total_fight_data, specs):

    casted_shadowbolt = False
    casted_incinerate = False
    casted_mindblast = False
    stats = {"in_isb": 0, "total": 0}

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
    dps_index = None
    for h in range(1,12):
        try:
            if "Crit" in fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/thead/tr/th["+str(h)+"]/div").text:
                crit_index = h
            if "Miss" in fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/thead/tr/th["+str(h)+"]/div").text:
                hit_index = h
            if "DPS" in fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/thead/tr/th["+str(h)+"]/div").text:
                dps_index = h
            if hit_index is not None and crit_index is not None and dps_index is not None:
                break
        except Exception as e:
            if type(e) != NoSuchElementException:
                ic(e)
                print(player_cast_html)
                print(traceback.format_exc())

    dps = None
    try:
        dps = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tfoot/tr/td["+str(dps_index)+"]").text
        dps = dps.replace(',','')
        dps = float(dps)
    except Exception as e:
        print(e)
        print("failed to get dps")
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
                if specs[warlock_name] == "destruction":
                    total_fight_data["player_info"].append({"name": warlock_name, "hit": 1.0 - float(hit[:-1])/100., "crit": float(crit[:-1])/100., "spec": "shadow destro", "dps": dps})
                else:
                    total_fight_data["player_info"].append({"name": warlock_name, "hit": 1.0 - float(hit[:-1])/100., "crit": float(crit[:-1])/100., "spec": specs[warlock_name], "dps": dps})
                break
            if "Mind Blast" in cast_element:
                if hit_index is not None:
                    hit = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody/tr[" + str(g) + "]/td["+str(hit_index)+"]").text
                else:
                    hit = "0%"
                if "-" in hit:
                    hit = "0%"
                total_fight_data["player_info"].append({"name": warlock_name, "hit": 1.0 - float(hit[:-1])/100., "spec": "shadow priest", "dps": dps})
                break 
            if "Incinerate" in cast_element:
                casted_incinerate = True
                total_fight_data["player_info"].append({"name": warlock_name, "dps": dps, "spec": "fire destro"})

        except Exception as e:
            if casted_incinerate:
                break
            print(e)
            print(player_cast_html)
            print(traceback.format_exc())
            break
