import sqlite3 as sl
import csv
from json import loads

from enums import composition
from config import study_options, output_options
from util import getDBHeaders
    
con = sl.connect(study_options['name']+ '.db')


with con:
    csvWriter = csv.writer(open("output.csv", "w"), quoting = csv.QUOTE_NONE,  delimiter='\t', quotechar='', escapechar='|')
    cursor = con.cursor()
    cursor.execute("SELECT COUNT(*) FROM "  + study_options["name"])
    num = cursor.fetchone()
    print("There are ", num, "entries")
    data = con.execute("SELECT * FROM "  + study_options["name"])
    out = " "
    headers = getDBHeaders(con)
    for h in headers:
        if h == "player_info":
            continue
        out += h + "\t"
    for i in range(output_options['num_players']):
        for key in output_options['player_info_output_keys']:
            out += key + "_" + str(i) + "\t"

    for row in data:
        out += "\n"
        for i in range(len(row)):
            item = row[i]
            if i == len(row) -1:
                val = loads(item)
                print(row)
                count = 0 
                for player_data in val:
                    count += 1
                    for key in output_options['player_info_output_keys']:
                        if player_data.get(key) is not None:
                            out += str(player_data[key]) + "\t"
                        else:
                            print("Warning: player", player_data["name"], " was missing ", key, " Make sure that output options match study options")
                            out += " \t"
                # This is required for keeping columns aligned in gsheets
                while count < output_options['num_players']:
                    count += 1
                    for key in output_options['player_info_output_keys']:
                        out += " \t"
            else:
                out += str(item) + "\t"
    print(out)
    csvWriter.writerow([out])
