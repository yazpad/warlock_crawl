from list_dict_DB import list_dict_DB
from selenium.webdriver.common.by import By

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


MAX_DELAY = 2
PAGE_DELAY = 2

boss_list = ["Maiden of Virtue Normal"]

debuff_list = ["ability-15258-0", "ability-17800-0", "ability-17937-0", "ability-11722-0"]
buff_dict = {"ability-18791-0":"Touch of Shadow", "ability-23271-0": "Ephemeral Power", "ability-17941-0": "Shadow Trance", "ability-18288-0": "Amplify Curse"}
items = [{"name": "yazpad", "fight": "A", "date": 0, "class": "warlock", "server": "Fairbanks", "spec": "ds/ruin", "boss": "Fankriss"}]

DB = list_dict_DB(items)

print(DB.query(name="yazpad"))

TIME_BETWEEN_LOAD = 3

force_reload = []

try:
    loaded_data = pickle.load( open( "save.p", "rb" ) )
except:
    print("Cached data could not be loaded")
    loaded_data = {}


chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--window-size=1920x1080")
sweep_raid_driver = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)
fight_driver = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)
raid_driver = webdriver.Chrome(ChromeDriverManager().install(),options=chrome_options)

def cleanExit():
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
    warlock_dict = {}

    for i in range(1,41):
        try:
            character_img = fight_driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody/tr['+str(i)+']/td[2]/table/tbody/tr/td[1]')
            character_meta = fight_driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody/tr['+str(i)+']/td[2]/table/tbody/tr/td[2]')
        except:
            break

        element_value = character_meta.get_attribute('innerHTML')
        element_value_img = character_img.get_attribute('innerHTML')
        print(element_value_img)
        if "Warlock" in element_value or "Priest-Shadow" in element_value_img:
            split_for_source = element_value.split("setFilterSource('")[1].split("'")[0]
            split_for_name = element_value.split('">')[1].splitlines()[0]
            warlock_dict[split_for_name] = split_for_source
        if "Priest-Shadow" in element_value_img:
            print("Shadow priest found")
    print(warlock_dict)
    return warlock_dict

def getDebuffData(fight_html, fight_text, debuff_data, fight_data):
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

def getPlayerCastData(fight_html, fight_text, warlock_name, warlock_source, player_data):
    print("Starting to gather player cast data: ", warlock_name)
    time.sleep(PAGE_DELAY)
    player_cast_html = fight_html + "&type=casts&source="+str(warlock_source)+"&view=events"
    fight_driver.get(player_cast_html)
    try:
        WebDriverWait(fight_driver, MAX_DELAY).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody[1]/tr[1]/td[1]")))
    except TimeoutException:
        print("Loading took too much time")
        return
    for g in range(1,100):
        try:
            cast_element = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody[1]/tr["+str(g)+"]/td[2]").get_attribute('innerHTML')
            if "casts" in cast_element and "Shadow Bolt" in cast_element:
                cast_time = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody[1]/tr["+str(g)+"]/td[1]").text
                print(warlock_name, "CAST SHADOWBOLT", cast_time, g)
        except Exception as e:
            print(e)
            print("Completed for player", warlock_name)
            return

def getRaidComposition(raid_html, warlock_sources):
    debuff_data={}
    player_data={}

    for k,v in warlock_sources.items():
        player_data[k] = {}

    fight_data = {}

    for fight_num in range(1,12):
        fight_driver.get(raid_html)
        try:
            fight_text = fight_driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[5]/div/div/div/div['+str(fight_num)+']/a/span[1]').text
            print(fight_text)
        except:
            print("SKIPPING", fight_num)
            continue
        if fight_text in boss_list:
            ahref = fight_driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[5]/div/div/div/div['+str(fight_num)+']/a')
            ahref.click()
            fight_html = ahref.get_attribute("href")
            getDebuffData(fight_html,fight_text,debuff_data, fight_data)
            for k,v in warlock_sources.items():
                player_data[k][fight_text]={}
                getPlayerBuffData(fight_html, fight_text, k, v, player_data)
                getPlayerCastData(fight_html, fight_text, k, v, player_data)

    print(player_data)
    print(debuff_data)
    return debuff_data
    


def sweepRaid(raid_html):
    composition = getComposition(raid_html)
    getRaidComposition(raid_html, composition)

def sweepRaids(raid_id, server_id, num_pages = 1):
    try:
        html = "https://classic.warcraftlogs.com/zone/reports?zone="+str(raid_id)+"&boss=0&difficulty=0&class=Any&spec=Any&keystone=0&kills=2&duration=0"
        page_num = random.randint(1,4)
        for i in range(num_pages):

            html = "https://classic.warcraftlogs.com/zone/reports?zone="+str(raid_id)+"&boss=0&difficulty=0&class=Any&spec=Any&keystone=0&kills=2&duration=0&page="+str(random.randint(1,3))
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
                sweepRaid(ahref.get_attribute("href"))
                return
    except:
        print("Failed to sweep raid.")
        cleanExit()

                # element_value_split = element_value.split('"')
                # for e in element_value_split:
                #     try:
                #         if "/reports/" and "damage-done" in e:
                #             fight_page = "https://classic.warcraftlogs.com/"+e+"&type=damage-done"

        # next_fun(html)
    # html_start = "https://classic.warcraftlogs.com/zone/rankings/1005#metric=execution&boss=715&region=6&subregion=13&page=2"
sweepRaids(1007, 5004)
cleanExit()


html_list = []
html_list_bw = []

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
