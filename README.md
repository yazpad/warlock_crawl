# warlock_crawl
Gather warlock data on wclogs using python3 and selenium.

e.g. results: [Warlock spec comparison at Gruul](https://docs.google.com/spreadsheets/d/1eddYWdusO0IWOEWGogHrkeZ0IXYlRBI4pBv39HNu-0k/edit?usp=sharing)

## Requirements

prettytable==2.1.0

icecream==2.1.1

colorama==0.4.3

numpy==1.20.1

selenium==3.141.0

webdriver_manager==3.4.2

scipy==1.7.0

matplotlib==3.4.2

scikit_learn==0.24.2

## Usage
`python3 main.py`

As the program finishes parsing a log, it will automatically be added to a local database `___.db` based on the name specified in config.py

## Configuration
In config.py you can modify options regarding what is recorded when gathering data

## Exporting
`python3 write_to_csv.py`

This will write the db specified in config.py to a .csv file.  This csv file can be imported to google sheets using the custom delimiter, "|". (vertical bar/pipe)
