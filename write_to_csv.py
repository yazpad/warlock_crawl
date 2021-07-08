import sqlite3 as sl
import csv
from json import loads

from enums import composition
from config import study_options
    
con = sl.connect(study_options['name']+ '.db')

with con:
    csvWriter = csv.writer(open("output.csv", "w"), quoting = csv.QUOTE_NONE,  delimiter='\t', quotechar='', escapechar='|')
    cursor = con.cursor()
    cursor.execute("SELECT COUNT(*) FROM "  + study_options["name"])
    num = cursor.fetchone()
    print("There are ", num, "entries")
    data = con.execute("SELECT * FROM "  + study_options["name"])
    out = " "
    for row in data:
        out += "\n"
        for i in range(len(row)):
            item = row[i]
            if i == len(row) -1:
                val = loads(item)
                print(row)
                for player_data in val:
                    for k in sorted(player_data): 
                        out += str(player_data[k]) + "\t"
            else:
                out += str(item) + "\t"
    print(out)
    csvWriter.writerow([out])
