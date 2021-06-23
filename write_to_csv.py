import sqlite3 as sl
import csv
from json import loads

from enums import composition
    
con = sl.connect('isb.db')

with con:
    csvWriter = csv.writer(open("output.csv", "w"), quoting = csv.QUOTE_NONE,  delimiter='\t', quotechar='', escapechar='|')
    cursor = con.cursor()
    cursor.execute("SELECT COUNT(*) FROM USER")
    num = cursor.fetchone()
    print("There are ", num, "entries")
    data = con.execute("SELECT * FROM USER")
    for row in data:
        out = ""
        for item in row:
            out += str(item) + "\t"
        print(out)
        csvWriter.writerow([out])
