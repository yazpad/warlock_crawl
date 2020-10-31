from list_dict_DB import list_dict_DB
from selenium import webdriver
import random
import re
import os.path
import pickle
import time
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager


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

def getTime(element):
    minutes = int(element[3:5])
    seconds = float(element[6:])
    time_val = minutes*60+seconds
    return time_val

def getWarlockList(raid_html):
    fight_driver.get(raid_html+"#boss=-2&difficulty=0&type=damage-done")
    warlock_dict = {}

    for i in range(1,41):
        try:
            character_meta = fight_driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody/tr['+str(i)+']/td[2]/table/tbody/tr/td[2]')
        except:
            break

        element_value = character_meta.get_attribute('innerHTML')
        if "Warlock" in element_value:
            split_for_source = element_value.split("setFilterSource('")[1].split("'")[0]
            split_for_name = element_value.split('">')[1].splitlines()[0]
            warlock_dict[split_for_name] = split_for_source
    print(warlock_dict)
    return warlock_dict

def getRaidComposition(raid_html):

    def checkForBuffs(buff_id, element):
        if str(buff_id) in element_value: # Shadow Weaving
            debuff_data[boss_id]["debuff_set"].add(buff_id)
            if debuff_data[boss_id].get(buff_id) is None:
                debuff_data[boss_id][buff_id] = []
            time = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody[1]/tr["+str(k-1)+"]/td[1]").text
            dec_time = getTime(time)
            print("Time!", getTime(time))
            if "is afflicted by" in element_value:
                if debuff_status.get(buff_id) is None:
                    debuff_status[buff_id] = True #Active
                    debuff_data[boss_id][buff_id].append([dec_time])
                elif debuff_status.get(buff_id) is False:
                    debuff_status[buff_id] = True 
                    debuff_data[boss_id][buff_id].append([dec_time])
                elif debuff_status.get(buff_id) is True:
                    print(buff_id, "Error on parsing buffs. Already on")
            elif "fades from" in element_value:
                if debuff_status.get(buff_id) is True:
                    if ") fades" not in element_value:
                        debuff_status[buff_id] = False 
                        debuff_data[boss_id][buff_id][-1].append(dec_time)
                else:
                    print(buff_id, "Error on parsing buffs")
            return True

    boss_ids=[17]
    buff_ids = [15258, 17800, 17937]
    debuff_data={}


    boss_list = ["Twin Emperors Normal", "The Prophet Skeram Normal", "Battleguard Sartura Normal", "Fankriss the Unyielding Normal", "C'thun Normal", "Ouro Normal", "Viscidus Normal", "Silithid Royalty Normal"]

    print(raid_html)
    boss_dict = {}
    for fight_num in range(1,12):
        fight_driver.get(raid_html)
        try:
            fight_text = fight_driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[5]/div/div/div/div['+str(fight_num)+']/a/span[1]').text
        except:
            print("SKIPPING", fight_num)
            continue
        if fight_text in boss_list:
            ahref = fight_driver.find_element_by_xpath('/html/body/div[2]/div[2]/div[5]/div/div/div/div['+str(fight_num)+']/a')
            ahref.click()
            fight_html = ahref.get_attribute("href")
            boss_dict[fight_text] = fight_html

    print(boss_dict)
    return


    for boss_id in boss_ids:
        debuff_data[boss_id]={}
        debuff_data[boss_id]["debuff_set"]=set()
        fight_driver.get(raid_html+"#fight="+str(boss_id)+"&type=auras&spells=debuffs&hostility=1")

        debuff_status = {}

        fight_time = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[3]/div/div[1]/div[1]/div/div[2]/span/span[1]").text[1:-1]
        print(fight_time[:-3],fight_time[-2:])
        print(int(fight_time[:-3])*60,int(fight_time[-2:]))
        fight_time = int(fight_time[:-3])*60+ int(fight_time[-2:])
        print(fight_time)
        return

        k = 1
        pages = 1
        while True:
            try:
                debuff_meta = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody[1]/tr["+str(k)+"]/td[2]")

            except:
                try:
                    next_page = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/a[4]")
                    pages+=1
                    fight_driver.get(next_page.get_attribute("href"))
                except:
                    print("pages", pages)
                    break
            k += 1

            element_value = debuff_meta.get_attribute('innerHTML')
            for buff_id in buff_ids:
                if checkForBuffs(buff_id, element_value):
                    break
            # if "17800" in element_value: # Shadow Weaving (add the others?)
            #     debuff_data[boss_id]["debuff_set"].add(17800)
            #     time = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody[1]/tr["+str(k-1)+"]/td[1]").text
            #     print("Time!", getTime(time))
            #     continue
            # if "17937" in element_value: # CoS 
            #     debuff_data[boss_id]["debuff_set"].add(17937)
            #     time = fight_driver.find_element_by_xpath("/html/body/div[2]/div[2]/div[6]/div[3]/div[1]/div[7]/div[3]/div[2]/div[1]/table/tbody[1]/tr["+str(k-1)+"]/td[1]").text
            #     print("Time!", getTime(time))
            #     continue
    print(debuff_data)
    return debuff_data
    


def sweepRaid(raid_html):
    warlock_sources = getWarlockList(raid_html)
    getRaidComposition(raid_html)
    # Get list of fights from raid_id
    # Keep local data of warlock here, it will be used to determine spec and other factors
    # at the end of this function, load list_dict
    pass
    # damage done -> gather all warlocks
    # By boss -> get relevant debuffs, CoS, Shadow vuln, etc,
    # By Boss/player -> get raid data (flask, spec), get player data (sp, crit, hit, dps, isb uptime)
    # for fight_id in fight_ids[raid_id]:
    #     /html/body/div[2]/div[2]/div[5]/div/div/div/div[3]/a

def sweepRaids(raid_id, server_id, num_pages = 1):

    html = "https://classic.warcraftlogs.com/zone/reports?zone="+str(raid_id)+"&region=6&subregion=11&page=2000&server="+str(server_id)
    page_num = random.randint(1,10)
    for i in range(num_pages):
        html = "https://classic.warcraftlogs.com/zone/reports?zone="+str(raid_id)+"&region=6&subregion=13&page="+str(random.randint(1,10))+"&server="+str(server_id)
        sweep_raid_driver.get(html)
        sweep_raid_driver.execute_script("return document.documentElement.innerHTML;")
        time.sleep(TIME_BETWEEN_LOAD)
        for n in range(1,100):
            ahref = sweep_raid_driver.find_element_by_xpath('/html/body/div[2]/div[3]/div/div[4]/div/div[1]/table/tbody/tr['+str(n)+']/td[1]/a')
            sweepRaid(ahref.get_attribute("href"))
            return

                # element_value_split = element_value.split('"')
                # for e in element_value_split:
                #     try:
                #         if "/reports/" and "damage-done" in e:
                #             fight_page = "https://classic.warcraftlogs.com/"+e+"&type=damage-done"

        # next_fun(html)
    # html_start = "https://classic.warcraftlogs.com/zone/rankings/1005#metric=execution&boss=715&region=6&subregion=13&page=2"
sweepRaids(1005, 5004)
sweep_raid_driver.quit()
fight_driver.quit()
raid_driver.quit()
exit()



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
