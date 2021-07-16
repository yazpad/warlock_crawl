server_dict = {"whitemane": 5012, "faerlina": 5003, "thunderfury": 5067, "benediction": 5068, "herod": 5006, "arugal": 5001, "sulfuras": 5060}
debuff_list = ["ability-15258-0", "ability-17800-0", "ability-17937-0", "ability-11722-0", "ability-22959-0"]
debuff_dict = {"ability-15258-0": "shadow_vuln", "ability-17800-0": "isb", "ability-22959-0": "imp_scorch"}
buff_dict = {"ability-18791-0":"Touch of Shadow", "ability-23271-0": "Ephemeral Power", "ability-17941-0": "Shadow Trance", "ability-18288-0": "Amplify Curse"}
boss_raid_id = {"High King Maulgar Normal":  1008,
            "Magtheridon Normal": 1008,
            "Gruul the Dragonkiller Normal": 1008,
            "Attumen the Huntsman Normal": 1007,
            "Moroes Normal": 1007,
            "Maiden of Virtue Normal": 1007,
            "Opera Hall Normal": 1007,
            "The Curator Normal": 1007,
            "Terestian Illhoof Normal": 1007,
            "Shade of Aran Normal": 1007,
            "Netherspite Normal": 1007,
            "Prince Malchezaar Normal": 1007,
            "Nightbane Normal": 1007}


boss_dict = {"High King Maulgar Normal":  649,
            "Magtheridon Normal": 651,
            "Gruul the Dragonkiller Normal": 650,
            "Attumen the Huntsman Normal": 652,
            "Moroes Normal": 653,
            "Maiden of Virtue Normal": 654,
            "Opera Hall Normal": 655,
            "The Curator Normal": 656,
            "Terestian Illhoof Normal": 657,
            "Shade of Aran Normal": 658,
            "Netherspite Normal": 659,
            "Prince Malchezaar Normal": 661,
            "Nightbane Normal": 662}

def destro_shadow_def(warlock_info):
    pet = warlock_info.get('pet')
    if pet is not None:
        return False

    casted_incin = warlock_info.get("casts_incinerate")
    if casted_incin is True:
        return False

    casted_ua = warlock_info.get("casts_ua")
    if casted_ua is True:
        return False

    icon = warlock_info.get("icon")
    if icon is not "destro":
        return False

    casted_sb = warlock_info.get("casts_sb")
    if casted_sb is not True:
        return False
    return True

def destro_fire_def(warlock_info):
    pet = warlock_info.get('pet')
    if pet is not None:
        return False

    casted_sb = warlock_info.get("casts_sb")
    if casted_sb is True:
        return False

    casted_ua = warlock_info.get("casts_ua")
    if casted_ua is True:
        return False

    icon = warlock_info.get("icon")
    if icon is not "destro":
        return False

    casted_incin = warlock_info.get("casts_incinerate")
    if casted_incin is not True:
        return False
    return True

def destro_nightfall_def(warlock_info):
    if pet is "felguard":
        return False

    casted_ua = warlock_info.get("casts_ua")
    if casted_ua is True:
        return False

    if warlock_info.get("instant_corruptions") is not True:
        return False

    if warlock_info.get("icon") is not "destro":
        return False

    return True

def felguard_def(warlock_info):
    if warlock_info.get('pet') is "felguard":
        return True
    return False

def aff_ruin_def(warlock_info):
    if warlock_info.get('has_ruin') is False:
        return False

    if warlock_info.get("icon") is not "aff":
        return False

    return True

def aff_ua_def(warlock_info):
    if warlock_info.get('has_ruin') is True:
        return False

    if warlock_info.get("icon") is not "aff":
        return False

    if warlock_info.get("casts_ua") is not True:
        return False

    return True

def mgi_def(warlock_info):
    if warlock_info.get('pet') is "imp":
        return False

    if warlock_info.get("casts_incinerate") is not True:
        return False

    if warlock_info.get("icon") is not "destro":
        return False

    return True

def sm_ds_def(warlock_info):
    if warlock_info.get("has_ruin") is True:
        return False

    if warlock_info.get("instant_corruption") is not True:
        return False

    if warlock_info.get("icon") is not "aff":
        return False

    if warlock_info.get("touch_of_shadow") is not True:
        return False

    return True

def deep_frost_def(mage_info):
    if mage_info.get("casts_frostbolt") is not True:
        return False

    if mage_info.get("casts_arcane_blast") is True:
        return False

    return True

def arc_frost_def(mage_info):
    if mage_info.get("casts_frostbolt") is not True:
        return False

    if mage_info.get("casts_arcane_blast") is not True:
        return False

    return True

def arc_fire_def(mage_info):
    if mage_info.get("casts_scorch") is not True:
        return False

    if mage_info.get("casts_arcane_blast") is not True:
        return False

    return True

def deep_fire_def(mage_info):
    if mage_info.get("casts_scorch") is not True:
        return False

    if mage_info.get("fire_ball") is not True:
        return False

    if mage_info.get("casts_arcane_blast") is True:
        return False

    return True



warlock_spec_definitions = {"destro_shadow": destr_shadow_def,
        "destro_fire": destro_fire_def,
        "destro_nightfall": destro_nightfall_def,
        "felguard": felguard_def,
        "aff_ruin": aff_ruin_def,
        "aff_ua": aff_ua_def,
        "mgi": mgi_def,
        "sm/ds": sm_ds_def}

mage_spec_definitions = {"deep_frost": deep_frost_def,
        "arc_frost": arc_frost_def,
        "arc_fire": arc_fire_def,
        "deep_fire": deep_fire_def}
