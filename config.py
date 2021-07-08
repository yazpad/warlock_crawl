# Enter options for study here.  Note that every new study should have a distinct name, otherwise there will be sq database errors


# Below are "study" options, which dictate what is recorded.

# name: [no spaces] Whatever you want to call the study
#       e.g. fire_vs_shadow_dps

# boss: Name of the boss; must be exactly same as shows up in wclogs
#       e.g.: "Gruul the Dragonkiller Normal"

# server: [no spaces] Which server to pull from.
#       e.g. "Thunderfury"

# sample distribution: The type of pages to pull from. 
#       options: 
#               "MRU", this pulls from the Most Recently Updated logs
#               "Fastest", this pull from wclogs by lowest fight times [not implemented yet]
#               

# number of results:  This is the number of results to get before stopping 
#       e.g. float("inf") goes on forever,
#            2 stops at 2 fights

# fight gather options:  Set of flags which determines what fight attributes should be recorded during the scrape
#   improved scorch indicator: [bool] Set to true if you want imp. scorch to be recorded 
#   shadow vulnerability indicator: [bool] Set to true if you want shadow vulnerability (shadow priest) to be recorded 
#   fight time: [bool] Set to true if you want the fight time to be recorded
#   isb_uptime: [bool] Set to true if you want the isb uptime to be recorded.  Note that isb uptime is calculated using the number of shadow spells that are snapshotted during an active ISB on the boss.  This is not yet implemented for multi-target bosses (must be Gruul or Maiden of Virtue).  Also note, that this requires scraping for boss debuffs and player cast times. 
#   isb composition: [bool] Set to true if you want to record isb composition (i.e. 2 shadow locks + 1 shadow priest)

# player gather options:  Set of flags which determines what player attributes should be recorded during the scrape
#   dps: [bool] Set to true if you want the player's dps to be recorded
#   hit: [bool] Set to true if you want the player's hit rate to be recorded (observed hit rate)
#   dps: [bool] Set to true if you want the player's crit rate to be recorded (observed crit rate)

output_options = {
            "num_players" : 10, # This number should be larger than what you expect per raid.  This helps export to gsheets
            "player_info_output_keys" : ['name', 'spec', 'dps'],
        }

display_options = {
            "ic": False,
            "show_db": True, # Warning, this might be ugly in terminal
            "debug": False,
            "show_db_size": True,
        }

study_options = {
        "name": "default_name",
        "boss": "Gruul the Dragonkiller Normal",
        "server": "Thunderfury",
        "sample distribution": "MRU",
        "number of results": float("inf"),
        "fight gather options": {
            "improved scorch indicator": True,
            "shadow vulnerability indicator": True,
            "fight time": True,
            "isb uptime": False,
            "isb composition": False,
            "record server": True,
            },
        "classes to record": ["warlock", "priest"], #Currently only supports these two
        "player gather options": {
            "dps": True,
            "hit": False,
            "crit": False,
            },
        }


# TODO list
# player gather options: calculated SP, INT, 
# player gather options: Gear
# player gather options: pet dps (current dps includes pet dps)
# player gather options: buffs (e.g. flame cap)
# sample distribution: Fastest, 
# server: "Random" 
# filter_by_wipes: "all", "no_wipe", "no_kill"

